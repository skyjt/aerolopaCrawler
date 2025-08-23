"""API装饰器模块

提供错误处理、限流、日志记录等装饰器。
"""

import time
import uuid
import logging
from datetime import datetime
from functools import wraps
from collections import defaultdict, deque
from typing import Callable

from flask import request, jsonify, g

from .exceptions import APIError


# 全局变量
request_counts = defaultdict(deque)  # 存储每个IP的请求时间戳
logger = logging.getLogger(__name__)


def error_handler(f: Callable) -> Callable:
    """统一错误处理装饰器
    
    处理API异常、请求体过大和未处理的异常。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return jsonify({
                'success': False,
                'error': e.to_dict(),
                'timestamp': datetime.now().isoformat()
            }), e.status_code
        except Exception as e:
            # 生成错误ID用于追踪
            error_id = str(uuid.uuid4())[:8]
            logger.exception(f"Unhandled error [{error_id}]: {str(e)}")
            
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': '服务器内部错误',
                    'error_id': error_id
                },
                'timestamp': datetime.now().isoformat()
            }), 500
    
    return decorated_function


def rate_limit(max_requests: int = 50, window_seconds: int = 3600) -> Callable:
    """请求频率限制装饰器
    
    Args:
        max_requests: 时间窗口内最大请求数
        window_seconds: 时间窗口大小（秒）
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取客户端IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if not client_ip:
                client_ip = 'unknown'
            
            current_time = time.time()
            
            # 清理过期的请求记录
            cutoff_time = current_time - window_seconds
            while request_counts[client_ip] and request_counts[client_ip][0] < cutoff_time:
                request_counts[client_ip].popleft()
            
            # 检查是否超过限制
            if len(request_counts[client_ip]) >= max_requests:
                raise APIError(
                    f"请求频率超限，每{window_seconds//60}分钟最多{max_requests}次请求",
                    429,
                    "TOO_MANY_REQUESTS"
                )
            
            # 记录当前请求
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def log_request(f: Callable) -> Callable:
    """请求日志记录装饰器
    
    记录请求信息和性能指标。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求信息
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        endpoint = request.endpoint or 'unknown'
        method = request.method
        
        # 存储到g对象中，供其他地方使用
        g.request_start_time = start_time
        g.client_ip = client_ip
        g.user_agent = user_agent
        g.endpoint = endpoint
        
        try:
            # 执行原函数
            result = f(*args, **kwargs)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 记录成功请求
            logger.info(
                f"{method} {request.path} - {client_ip} - {response_time:.3f}s - Success"
            )
            
            # 更新性能指标（如果有的话）
            if hasattr(g, 'performance_metrics'):
                _update_performance_metrics(endpoint, response_time, True)
            
            return result
            
        except Exception as e:
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 记录失败请求
            error_type = type(e).__name__
            logger.error(
                f"{method} {request.path} - {client_ip} - {response_time:.3f}s - Error: {error_type}"
            )
            
            # 更新性能指标（如果有的话）
            if hasattr(g, 'performance_metrics'):
                _update_performance_metrics(endpoint, response_time, False, error_type)
            
            raise
    
    return decorated_function


def _update_performance_metrics(endpoint: str, response_time: float, success: bool, error_type: str = None):
    """更新性能指标

    Args:
        endpoint: 端点名称
        response_time: 响应时间
        success: 是否成功
        error_type: 错误类型（如果失败）
    """
    # 这里可以集成到实际的性能监控系统，目前仅记录日志
    if success:
        logger.debug(f"Performance: {endpoint} - {response_time:.3f}s - Success")
    else:
        logger.debug(f"Performance: {endpoint} - {response_time:.3f}s - Error: {error_type}")


def require_json(f: Callable) -> Callable:
    """要求JSON请求体的装饰器
    
    确保POST/PUT请求包含有效的JSON数据。
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            if not request.is_json:
                raise APIError(
                    "请求必须包含JSON数据",
                    400,
                    "INVALID_CONTENT_TYPE"
                )
            
            try:
                request.get_json(force=True)
            except Exception:
                raise APIError(
                    "无效的JSON格式",
                    400,
                    "INVALID_JSON"
                )
        
        return f(*args, **kwargs)
    
    return decorated_function


def cache_response(timeout: int = 300) -> Callable:
    """响应缓存装饰器
    
    Args:
        timeout: 缓存超时时间（秒）
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{request.endpoint}:{request.full_path}"
            
            try:
                from flask import current_app
                cache = current_app.extensions.get('cache')
                
                if cache:
                    # 尝试从缓存获取
                    cached_result = cache.get(cache_key)
                    if cached_result is not None:
                        return cached_result
                    
                    # 执行函数并缓存结果
                    result = f(*args, **kwargs)
                    cache.set(cache_key, result, timeout=timeout)
                    return result
                else:
                    # 如果没有缓存系统，直接执行
                    return f(*args, **kwargs)
                    
            except Exception as e:
                logger.warning(f"Cache operation failed: {str(e)}")
                # 缓存失败时直接执行原函数
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def validate_content_length(max_length: int = 1024 * 1024) -> Callable:
    """验证请求内容长度的装饰器
    
    Args:
        max_length: 最大内容长度（字节）
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            content_length = request.content_length
            if content_length and content_length > max_length:
                raise APIError(
                    f"请求体过大，最大允许 {max_length // 1024} KB",
                    413,
                    "PAYLOAD_TOO_LARGE"
                )
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator