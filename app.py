#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA 航空座位图 API 服务
提供航空公司机型座位图查询的 RESTful API 接口

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import os
import re
import json
import logging
import uuid
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Tuple, Any

from flask import Flask, request, jsonify, send_file, abort, make_response
from flask_cors import CORS
from flask_caching import Cache
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError, RequestEntityTooLarge
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
import hashlib
import io
import mimetypes
import psutil
import threading
from collections import defaultdict, deque

# 导入现有模块
from main import AerolopaCrawler
from config import (
    BASE_URL, DATA_DIR, LOGS_DIR, REQUEST_TIMEOUT, REQUEST_DELAY,
    MAX_RETRIES, USER_AGENT, AIRCRAFT_KEYWORDS, IMAGE_FORMATS,
    LOG_LEVEL, LOG_FORMAT
)
from airlines_config import (
    AIRLINES, get_airline_info, get_all_airlines, get_supported_iata_codes
)

# Flask应用配置
app = Flask(__name__)
app.config.update({
    'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
    'SEND_FILE_MAX_AGE_DEFAULT': 31536000,  # 1年缓存
    'JSON_AS_ASCII': False,  # 支持中文JSON
    'JSONIFY_PRETTYPRINT_REGULAR': True,  # 格式化JSON输出
    'PERMANENT_SESSION_LIFETIME': timedelta(hours=24),  # 会话超时
    # 缓存配置
    'CACHE_TYPE': 'simple',  # 可以改为 'redis' 或 'memcached'
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1小时
    'CACHE_KEY_PREFIX': 'aerolopa_',
    # 图片优化配置
    'IMAGE_CACHE_TIMEOUT': 86400,  # 24小时
    'IMAGE_QUALITY': 85,  # JPEG质量
    'IMAGE_MAX_SIZE': (1920, 1080),  # 最大尺寸
    'ENABLE_IMAGE_COMPRESSION': True
})

# CORS配置
CORS(app, 
     origins=['*'],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     max_age=86400  # 预检请求缓存24小时
)

# 初始化缓存
cache = Cache(app)

# 日志配置
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, 'api.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 请求计数器和性能监控（简单的内存存储，生产环境应使用Redis）
request_counts = {}
request_timestamps = {}

# 性能监控数据
performance_metrics = {
    'total_requests': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'avg_response_time': 0.0,
    'response_times': deque(maxlen=1000),  # 保留最近1000次请求的响应时间
    'error_counts': defaultdict(int),
    'endpoint_stats': defaultdict(lambda: {'count': 0, 'avg_time': 0.0, 'times': deque(maxlen=100)}),
    'start_time': datetime.now()
}

# 系统监控锁
metrics_lock = threading.Lock()

# 图片缓存目录
IMAGE_CACHE_DIR = os.path.join(DATA_DIR, '.cache', 'images')
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

# 全局爬虫实例
crawler = AerolopaCrawler()

# API 版本和基础信息
API_VERSION = "v1"
API_BASE_PATH = f"/api/{API_VERSION}"


class APIError(Exception):
    """API 自定义异常类"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or f"API_{status_code}"
        self.details = details or {}
        self.error_id = str(uuid.uuid4())[:8]


def validate_iata_code(iata_code: str) -> bool:
    """验证IATA航空公司代码格式
    
    Returns:
        bool: 是否有效
    """
    if not iata_code:
        return False
    
    if not isinstance(iata_code, str):
        return False
    
    # 去除空格并转换为大写
    iata_code = iata_code.strip().upper()
    
    # 长度检查
    if len(iata_code) < 2 or len(iata_code) > 3:
        return False
    
    # 格式检查：只允许字母和数字
    if not re.match(r'^[A-Z0-9]{2,3}$', iata_code):
        return False
    
    # 检查是否在支持列表中（转换为小写进行比较）
    supported_codes = get_supported_iata_codes()
    if iata_code.lower() not in supported_codes:
        return False
    
    return True


def validate_iata_code_with_message(iata_code: str) -> Tuple[bool, str]:
    """验证IATA航空公司代码格式（带错误信息）
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not iata_code:
        return False, "IATA代码不能为空"
    
    if not isinstance(iata_code, str):
        return False, "IATA代码必须是字符串类型"
    
    # 去除空格并转换为大写
    iata_code = iata_code.strip().upper()
    
    # 长度检查
    if len(iata_code) < 2 or len(iata_code) > 3:
        return False, "IATA代码长度必须是2-3位"
    
    # 格式检查：只允许字母和数字
    if not re.match(r'^[A-Z0-9]{2,3}$', iata_code):
        return False, "IATA代码只能包含大写字母和数字"
    
    # 检查是否在支持列表中（转换为小写进行比较）
    supported_codes = get_supported_iata_codes()
    if iata_code.lower() not in supported_codes:
        return False, f"不支持的航空公司代码: {iata_code}"
    
    return True, ""


def validate_aircraft_model(aircraft_model: str) -> bool:
    """验证机型格式
    
    Returns:
        bool: 是否有效
    """
    if not aircraft_model:
        return False
    
    if not isinstance(aircraft_model, str):
        return False
    
    # 去除首尾空格
    aircraft_model = aircraft_model.strip()
    
    # 长度检查
    if len(aircraft_model) < 2:
        return False
    
    if len(aircraft_model) > 20:
        return False
    
    # 格式检查：允许字母、数字、连字符、空格和常见符号
    if not re.match(r'^[A-Za-z0-9\-\s\.\+]+$', aircraft_model):
        return False
    
    # 检查是否包含至少一个字母或数字
    if not re.search(r'[A-Za-z0-9]', aircraft_model):
        return False
    
    return True


def validate_aircraft_model_with_message(aircraft_model: str) -> Tuple[bool, str]:
    """验证机型格式（带错误信息）
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not aircraft_model:
        return False, "机型名称不能为空"
    
    if not isinstance(aircraft_model, str):
        return False, "机型名称必须是字符串类型"
    
    # 去除首尾空格
    aircraft_model = aircraft_model.strip()
    
    # 长度检查
    if len(aircraft_model) < 2:
        return False, "机型名称长度不能少于2位"
    
    if len(aircraft_model) > 20:
        return False, "机型名称长度不能超过20位"
    
    # 格式检查：允许字母、数字、连字符、空格和常见符号
    if not re.match(r'^[A-Za-z0-9\-\s\.\+]+$', aircraft_model):
        return False, "机型名称包含无效字符，只允许字母、数字、连字符、空格和点号"
    
    # 检查是否包含至少一个字母或数字
    if not re.search(r'[A-Za-z0-9]', aircraft_model):
        return False, "机型名称必须包含至少一个字母或数字"
    
    return True, ""


def standardize_aircraft_model(aircraft_model: str) -> str:
    """标准化机型名称"""
    if not aircraft_model:
        return ""
    
    # 移除多余空格，转换为大写
    model = re.sub(r'\s+', ' ', aircraft_model.strip().upper())
    
    # 标准化常见机型格式
    replacements = {
        'BOEING 737': 'B 737',
        'AIRBUS A320': 'A A320',
        'BOEING': 'B',
        'AIRBUS': 'A',
        'EMBRAER': 'E',
        'BOMBARDIER': 'CRJ',
        'MCDONNELL DOUGLAS': 'MD',
    }
    
    for old, new in replacements.items():
        model = model.replace(old, new)
    
    # 处理连字符格式 (B-737 -> B737)
    model = re.sub(r'([A-Z])-([0-9])', r'\1\2', model)
    
    # 处理多余空格
    model = re.sub(r'\s+', ' ', model).strip()
    
    return model


def validate_request_params(data: Dict) -> Dict:
    """验证请求参数
    
    Args:
        data: 请求参数字典
    
    Returns:
        Dict: 标准化后的参数字典
        
    Raises:
        APIError: 当参数验证失败时抛出
    """
    validated_params = {}
    
    # 验证航空公司代码
    airline = data.get('airline', '').strip() if data.get('airline') else ''
    if not airline:
        raise APIError("缺少必需参数: airline", 400, "MISSING_AIRLINE")
    
    is_valid, error_msg = validate_iata_code_with_message(airline)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_IATA_CODE")
    
    validated_params['airline'] = airline.upper()
    
    # 验证机型
    aircraft = data.get('aircraft', '').strip() if data.get('aircraft') else ''
    if not aircraft:
        raise APIError("缺少必需参数: aircraft", 400, "MISSING_AIRCRAFT")
    
    is_valid, error_msg = validate_aircraft_model_with_message(aircraft)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_AIRCRAFT_MODEL")
    
    validated_params['aircraft'] = aircraft
    validated_params['standardized_aircraft'] = standardize_aircraft_model(aircraft)
    
    # 验证返回格式
    return_format = data.get('format', 'json').lower()
    allowed_formats = ['json', 'image', 'metadata']
    if return_format not in allowed_formats:
        raise APIError(f"不支持的返回格式: {return_format}，支持的格式: {', '.join(allowed_formats)}", 400, "INVALID_FORMAT")
    
    validated_params['format'] = return_format
    
    # 验证强制刷新参数
    force_refresh = data.get('force_refresh', False)
    if isinstance(force_refresh, str):
        force_refresh = force_refresh.lower() in ['true', '1', 'yes']
    elif not isinstance(force_refresh, bool):
        force_refresh = False
    validated_params['force_refresh'] = force_refresh
    
    # 验证其他可选参数
    if 'limit' in data and data['limit'] is not None:
        try:
            limit = int(data['limit'])
            if limit < 1 or limit > 100:
                raise APIError("limit参数必须在1-100之间", 400, "INVALID_LIMIT")
            validated_params['limit'] = limit
        except (ValueError, TypeError):
            raise APIError("limit参数必须是有效的整数", 400, "INVALID_LIMIT")
    
    return validated_params


def error_handler(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API错误 [{e.error_id}]: {e.message} (状态码: {e.status_code})")
            error_response = {
                'success': False,
                'error': {
                    'code': e.error_code,
                    'message': e.message,
                    'error_id': e.error_id
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # 添加详细信息（仅在开发模式下）
            if app.debug and e.details:
                error_response['error']['details'] = e.details
                
            return jsonify(error_response), e.status_code
            
        except RequestEntityTooLarge as e:
            logger.warning(f"请求体过大: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PAYLOAD_TOO_LARGE',
                    'message': '请求体过大'
                },
                'timestamp': datetime.now().isoformat()
            }), 413
            
        except Exception as e:
            error_id = str(uuid.uuid4())[:8]
            logger.exception(f"未处理的异常 [{error_id}]: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': '服务器内部错误',
                    'error_id': error_id
                },
                'timestamp': datetime.now().isoformat()
            }), 500
    return wrapper


def rate_limit(max_requests: int = 100, window_seconds: int = 3600):
    """请求频率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = datetime.now()
            
            # 清理过期的请求记录
            cutoff_time = current_time - timedelta(seconds=window_seconds)
            if client_ip in request_timestamps:
                request_timestamps[client_ip] = [
                    timestamp for timestamp in request_timestamps[client_ip]
                    if timestamp > cutoff_time
                ]
            
            # 检查请求频率
            if client_ip not in request_timestamps:
                request_timestamps[client_ip] = []
            
            if len(request_timestamps[client_ip]) >= max_requests:
                logger.warning(f"请求频率超限: IP {client_ip} 在 {window_seconds}s 内请求了 {len(request_timestamps[client_ip])} 次")
                raise APIError(
                    "请求过于频繁，请稍后再试",
                    429,
                    "TOO_MANY_REQUESTS",
                    {'retry_after': window_seconds}
                )
            
            # 记录当前请求
            request_timestamps[client_ip].append(current_time)
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_request(func):
    """请求日志装饰器（增强版，包含性能监控）"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        endpoint = request.endpoint or 'unknown'
        
        logger.info(f"请求开始: {request.method} {request.url} - IP: {client_ip} - UA: {user_agent[:100]}")
        
        # 更新总请求计数
        with metrics_lock:
            performance_metrics['total_requests'] += 1
        
        try:
            response = func(*args, **kwargs)
            duration = (datetime.now() - start_time).total_seconds()
            
            # 记录响应状态
            status_code = getattr(response, 'status_code', 200)
            logger.info(f"请求完成: {request.method} {request.url} - 状态: {status_code} - 耗时: {duration:.3f}s")
            
            # 更新性能指标
            with metrics_lock:
                if 200 <= status_code < 400:
                    performance_metrics['successful_requests'] += 1
                else:
                    performance_metrics['failed_requests'] += 1
                    performance_metrics['error_counts'][status_code] += 1
                
                # 更新响应时间统计
                performance_metrics['response_times'].append(duration)
                if performance_metrics['response_times']:
                    performance_metrics['avg_response_time'] = sum(performance_metrics['response_times']) / len(performance_metrics['response_times'])
                
                # 更新端点统计
                endpoint_stat = performance_metrics['endpoint_stats'][endpoint]
                endpoint_stat['count'] += 1
                endpoint_stat['times'].append(duration)
                if endpoint_stat['times']:
                    endpoint_stat['avg_time'] = sum(endpoint_stat['times']) / len(endpoint_stat['times'])
            
            # 性能警告
            if duration > 5.0:
                logger.warning(f"慢请求警告: {request.method} {request.url} - 耗时: {duration:.3f}s")
            elif duration > 10.0:
                logger.error(f"超慢请求: {request.method} {request.url} - 耗时: {duration:.3f}s")
            
            return response
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            
            # 更新失败统计
            with metrics_lock:
                performance_metrics['failed_requests'] += 1
                performance_metrics['error_counts']['exception'] += 1
            
            logger.error(f"请求失败: {request.method} {request.url} - 耗时: {duration:.3f}s - 错误: {str(e)}")
            raise
    
    return wrapper


@app.route('/', methods=['GET'])
def index():
    """API 根路径 - 返回服务信息"""
    return jsonify({
        'service': 'AeroLOPA 航空座位图 API',
        'version': API_VERSION,
        'status': 'running',
        'endpoints': {
            'health': '/health',
            'airlines': f'{API_BASE_PATH}/airlines',
            'seatmap': f'{API_BASE_PATH}/seatmap',
            'docs': '/docs'
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/health', methods=['GET'])
@log_request
def health_check():
    """健康检查端点（增强版）"""
    try:
        # 检查系统资源
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # 检查数据目录
        data_dir_exists = os.path.exists(DATA_DIR)
        logs_dir_exists = os.path.exists(LOGS_DIR)
        cache_dir_exists = os.path.exists(IMAGE_CACHE_DIR)
        
        # 计算运行时间
        uptime = datetime.now() - performance_metrics['start_time']
        
        # 健康状态评估
        health_status = 'healthy'
        warnings = []
        
        if cpu_percent > 90:
            health_status = 'warning'
            warnings.append(f'CPU使用率过高: {cpu_percent:.1f}%')
        
        if memory.percent > 90:
            health_status = 'warning'
            warnings.append(f'内存使用率过高: {memory.percent:.1f}%')
        
        if disk.percent > 90:
            health_status = 'warning'
            warnings.append(f'磁盘使用率过高: {disk.percent:.1f}%')
        
        if not all([data_dir_exists, logs_dir_exists, cache_dir_exists]):
            health_status = 'error'
            warnings.append('必要目录不存在')
        
        return jsonify({
            'status': health_status,
            'timestamp': datetime.now().isoformat(),
            'version': API_VERSION,
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime).split('.')[0],
            'system': {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_available_mb': round(memory.available / 1024 / 1024, 1),
                'disk_percent': round(disk.percent, 1),
                'disk_free_gb': round(disk.free / 1024 / 1024 / 1024, 1)
            },
            'directories': {
                'data_dir': data_dir_exists,
                'logs_dir': logs_dir_exists,
                'cache_dir': cache_dir_exists
            },
            'warnings': warnings
        })
        
    except Exception as e:
        logger.error(f'健康检查失败: {str(e)}')
        return jsonify({
            'status': 'error',
            'timestamp': datetime.now().isoformat(),
            'version': API_VERSION,
            'error': str(e)
        }), 500


@app.route(f'{API_BASE_PATH}/airlines', methods=['GET'])
@error_handler
@log_request
def get_airlines():
    """获取支持的航空公司列表"""
    try:
        airlines_list = get_all_airlines()
        supported_codes = get_supported_iata_codes()
        
        return jsonify({
            'success': True,
            'data': {
                'airlines': airlines_list,
                'supported_codes': supported_codes,
                'total_count': len(airlines_list)
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        raise APIError(f"获取航空公司列表失败: {str(e)}", 500, "AIRLINES_FETCH_ERROR")


@app.route(f'{API_BASE_PATH}/airlines/<iata_code>', methods=['GET'])
@error_handler
@log_request
def get_airline_info_api(iata_code: str):
    """获取指定航空公司信息"""
    is_valid, error_msg = validate_iata_code_with_message(iata_code)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_IATA_CODE")
    
    airline_info = get_airline_info(iata_code.upper())
    
    if not airline_info or airline_info.get('chinese') == f'未知航司({iata_code.upper()})':
        raise APIError(f"不支持的航空公司代码: {iata_code}", 404, "AIRLINE_NOT_FOUND")
    
    # 构建返回数据，添加iata_code字段并统一字段名称
    response_data = {
        'iata_code': iata_code.upper(),
        'chinese_name': airline_info.get('chinese', ''),
        'english_name': airline_info.get('english', '')
    }
    
    return jsonify({
        'success': True,
        'data': response_data,
        'timestamp': datetime.now().isoformat()
    })


@app.route(f'{API_BASE_PATH}/seatmap', methods=['GET', 'POST'])
@rate_limit(max_requests=50, window_seconds=3600)  # 每小时最多50次请求
@cache.cached(timeout=1800, query_string=True)  # 缓存30分钟，基于查询字符串
@error_handler
@log_request
def get_seatmap():
    """获取航空公司机型座位图"""
    # 获取请求参数
    if request.method == 'POST':
        data = request.get_json() or {}
    else:
        data = {
            'airline': request.args.get('airline'),
            'aircraft': request.args.get('aircraft'),
            'format': request.args.get('format', 'json'),
            'force_refresh': request.args.get('force_refresh', 'false'),
            'limit': request.args.get('limit')
        }
    
    # 统一参数验证（现在会直接抛出APIError异常）
    validated_params = validate_request_params(data)
    
    # 提取验证后的参数
    iata_code = validated_params['airline']
    aircraft_model = validated_params['aircraft']
    standardized_aircraft = validated_params['standardized_aircraft']
    return_format = validated_params['format']
    force_refresh = validated_params['force_refresh']
    limit = validated_params.get('limit', 50)  # 默认限制50张图片
    
    # 验证航空公司是否支持
    airline_info = get_airline_info(iata_code)
    if not airline_info or airline_info.get('chinese') == f'未知航司({iata_code.upper()})':
        raise APIError(f"不支持的航空公司代码: {iata_code}", 404, "AIRLINE_NOT_SUPPORTED")
    
    try:
        # 使用爬虫获取座位图数据
        logger.info(f"开始获取座位图: {iata_code.upper()} - {standardized_aircraft}")
        
        # 检查本地是否已有数据（如果不强制刷新）
        local_images = []
        if not force_refresh:
            local_images = _check_local_seatmap_cache(iata_code.upper(), standardized_aircraft)
        
        # 如果本地没有数据或强制刷新，则爬取新数据
        if not local_images or force_refresh:
            logger.info(f"爬取新的座位图数据: {iata_code.upper()}")
            crawl_result = crawler.crawl_airline_seatmaps(iata_code.upper())
            
            if crawl_result:
                # 过滤匹配的机型图片
                local_images = _filter_aircraft_images(crawl_result, standardized_aircraft)
                logger.info(f"找到 {len(local_images)} 张匹配的座位图")
            else:
                logger.warning(f"未能获取到航空公司 {iata_code.upper()} 的数据")
        
        # 应用limit限制
        if local_images and limit:
            local_images = local_images[:limit]
        
        # 构建返回数据
        seatmap_data = {
            'airline': {
                'iata_code': iata_code,
                'chinese_name': airline_info['chinese'],
                'english_name': airline_info['english']
            },
            'aircraft': {
                'original_model': aircraft_model,
                'standardized_model': standardized_aircraft
            },
            'seatmap': {
                'images': local_images,
                'metadata': {
                    'last_updated': datetime.now().isoformat(),
                    'source': 'AeroLOPA',
                    'force_refresh': force_refresh,
                    'total_images': len(local_images),
                    'limit_applied': limit if limit else None
                }
            }
        }
        
        if return_format == 'json':
            return jsonify({
                'success': True,
                'data': seatmap_data,
                'timestamp': datetime.now().isoformat()
            })
        else:
            raise APIError(f"不支持的返回格式: {return_format}", 400, "UNSUPPORTED_FORMAT")
            
    except Exception as e:
        logger.exception(f"获取座位图失败: {str(e)}")
        raise APIError(f"获取座位图失败: {str(e)}", 500, "SEATMAP_FETCH_ERROR")


@app.route('/docs', methods=['GET'])
def api_docs():
    """API 文档接口"""
    docs = {
        'title': 'AeroLOPA 航空座位图 API 文档',
        'version': API_VERSION,
        'base_url': API_BASE_PATH,
        'endpoints': {
            'GET /': {
                'description': '获取API服务信息',
                'parameters': None,
                'response': 'JSON格式的服务信息'
            },
            'GET /health': {
                'description': '健康检查',
                'parameters': None,
                'response': 'JSON格式的健康状态'
            },
            f'GET {API_BASE_PATH}/airlines': {
                'description': '获取支持的航空公司列表',
                'parameters': None,
                'response': 'JSON格式的航空公司列表'
            },
            f'GET {API_BASE_PATH}/airlines/<iata_code>': {
                'description': '获取指定航空公司信息',
                'parameters': {
                    'iata_code': '航空公司IATA代码 (2-3位字母数字)'
                },
                'response': 'JSON格式的航空公司详细信息'
            },
            f'GET {API_BASE_PATH}/seatmap': {
                'description': '获取航空公司机型座位图',
                'parameters': {
                    'airline': '航空公司IATA代码 (必需)',
                    'aircraft': '机型名称 (必需)',
                    'format': '返回格式 (可选，默认json)',
                    'force_refresh': '强制刷新 (可选，默认false)'
                },
                'response': 'JSON格式的座位图数据或图片文件'
            },
            f'GET {API_BASE_PATH}/image/<iata_code>/<filename>': {
                'description': '获取航空公司座位图图片文件',
                'parameters': {
                    'iata_code': '航空公司IATA代码（路径参数）',
                    'filename': '图片文件名（路径参数）',
                    'quality': '图片质量（查询参数，1-100，默认85）',
                    'width': '图片宽度（查询参数，像素）',
                    'height': '图片高度（查询参数，像素）',
                    'compress': '是否启用压缩（查询参数，true/false，默认true）'
                },
                'response': {
                    'success': '返回图片文件',
                    'headers': {
                        'Content-Type': '图片MIME类型',
                        'Cache-Control': '缓存控制',
                        'X-Cache': '缓存状态（HIT/MISS/BYPASS）',
                        'X-Optimized': '是否已优化（true/false）'
                    }
                }
            },
            f'GET {API_BASE_PATH}/stats': {
                'description': '获取API统计信息',
                'parameters': None,
                'response': 'JSON格式的API统计数据，包括性能指标、系统资源、缓存信息等'
            },
            f'GET {API_BASE_PATH}/metrics': {
                'description': '获取实时性能指标',
                'parameters': None,
                'response': 'JSON格式的实时性能数据，包括请求统计、响应时间分布、错误统计等'
            },
            f'GET {API_BASE_PATH}/system': {
                'description': '获取系统资源使用情况',
                'parameters': None,
                'response': 'JSON格式的系统资源信息，包括CPU、内存、磁盘使用情况等'
            },
            f'POST {API_BASE_PATH}/cache/clear': {
                'description': '清理API缓存',
                'parameters': None,
                'response': 'JSON格式的缓存清理结果'
            }
        },
        'error_codes': {
            'MISSING_AIRLINE': '缺少航空公司参数',
            'MISSING_AIRCRAFT': '缺少机型参数',
            'INVALID_IATA_CODE': '无效的IATA代码格式',
            'INVALID_AIRCRAFT_MODEL': '无效的机型格式',
            'AIRLINE_NOT_FOUND': '航空公司未找到',
            'AIRLINE_NOT_SUPPORTED': '不支持的航空公司',
            'SEATMAP_FETCH_ERROR': '座位图获取失败',
            'UNSUPPORTED_FORMAT': '不支持的返回格式',
            'TOO_MANY_REQUESTS': '请求频率超限',
            'PAYLOAD_TOO_LARGE': '请求体过大',
            'UNAUTHORIZED': '未授权访问',
            'FORBIDDEN': '禁止访问',
            'METHOD_NOT_ALLOWED': '请求方法不被允许',
            'INTERNAL_ERROR': '服务器内部错误',
            'BAD_GATEWAY': '网关错误',
            'SERVICE_UNAVAILABLE': '服务暂时不可用',
            'GATEWAY_TIMEOUT': '网关超时'
        },
        'rate_limits': {
            'seatmap_api': '每小时50次请求',
            'image_api': '每小时200次请求',
            'general_api': '每小时100次请求'
        }
    }
    
    return jsonify(docs)


@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': '请求的资源不存在'
        },
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(400)
def bad_request(error):
    """400错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'BAD_REQUEST',
            'message': '请求参数错误',
            'details': str(error.description) if hasattr(error, 'description') else None
        },
        'timestamp': datetime.now().isoformat()
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    """401错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'UNAUTHORIZED',
            'message': '未授权访问'
        },
        'timestamp': datetime.now().isoformat()
    }), 401


@app.errorhandler(403)
def forbidden(error):
    """403错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'FORBIDDEN',
            'message': '禁止访问'
        },
        'timestamp': datetime.now().isoformat()
    }), 403


@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': '请求方法不被允许',
            'allowed_methods': error.valid_methods if hasattr(error, 'valid_methods') else None
        },
        'timestamp': datetime.now().isoformat()
    }), 405


@app.errorhandler(413)
def payload_too_large(error):
    """413错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'PAYLOAD_TOO_LARGE',
            'message': '请求体过大'
        },
        'timestamp': datetime.now().isoformat()
    }), 413


@app.errorhandler(429)
def too_many_requests(error):
    """429错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'TOO_MANY_REQUESTS',
            'message': '请求过于频繁，请稍后再试'
        },
        'timestamp': datetime.now().isoformat()
    }), 429


@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    error_id = str(uuid.uuid4())[:8]
    logger.exception(f"Internal server error [{error_id}]: {str(error)}")
    return jsonify({
        'success': False,
        'error': {
            'code': 'INTERNAL_ERROR',
            'message': '服务器内部错误',
            'error_id': error_id
        },
        'timestamp': datetime.now().isoformat()
    }), 500


@app.errorhandler(502)
def bad_gateway(error):
    """502错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'BAD_GATEWAY',
            'message': '网关错误'
        },
        'timestamp': datetime.now().isoformat()
    }), 502


@app.errorhandler(503)
def service_unavailable(error):
    """503错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'SERVICE_UNAVAILABLE',
            'message': '服务暂时不可用'
        },
        'timestamp': datetime.now().isoformat()
    }), 503


@app.errorhandler(504)
def gateway_timeout(error):
    """504错误处理"""
    return jsonify({
        'success': False,
        'error': {
            'code': 'GATEWAY_TIMEOUT',
            'message': '网关超时'
        },
        'timestamp': datetime.now().isoformat()
    }), 504


def _check_local_seatmap_cache(iata_code: str, aircraft_model: str) -> List[Dict[str, Any]]:
    """检查本地座位图缓存"""
    try:
        airline_dir = os.path.join(DATA_DIR, iata_code)
        if not os.path.exists(airline_dir):
            return []
        
        images = []
        for filename in os.listdir(airline_dir):
            if any(filename.lower().endswith(ext) for ext in IMAGE_FORMATS):
                # 检查文件名是否包含机型信息
                if _is_aircraft_match(filename, aircraft_model):
                    file_path = os.path.join(airline_dir, filename)
                    file_stats = os.stat(file_path)
                    
                    images.append({
                        'filename': filename,
                        'file_path': file_path,
                        'url': f'/api/v1/image/{iata_code}/{filename}',
            'optimized_urls': {
                'thumbnail': f'/api/v1/image/{iata_code}/{filename}?width=300&compress=true',
                'medium': f'/api/v1/image/{iata_code}/{filename}?width=800&compress=true',
                'high_quality': f'/api/v1/image/{iata_code}/{filename}?quality=95&compress=true'
            },
                        'size': file_stats.st_size,
                        'modified_time': datetime.fromtimestamp(file_stats.st_mtime).isoformat(),
                        'aircraft_match': True
                    })
        
        return images
    except Exception as e:
        logger.error(f"检查本地缓存失败: {str(e)}")
        return []


def _filter_aircraft_images(crawl_result: Dict, aircraft_model: str) -> List[Dict[str, Any]]:
    """从爬取结果中过滤匹配的机型图片"""
    images = []
    
    try:
        # crawl_result 应该包含爬取到的图片信息
        if 'images' in crawl_result:
            for img_info in crawl_result['images']:
                if _is_aircraft_match(img_info.get('filename', ''), aircraft_model):
                    images.append({
                        'filename': img_info.get('filename', ''),
                        'file_path': img_info.get('file_path', ''),
                        'url': img_info.get('url', ''),
                        'size': img_info.get('size', 0),
                        'modified_time': img_info.get('modified_time', ''),
                        'aircraft_match': True,
                        'source_url': img_info.get('source_url', '')
                    })
        
        return images
    except Exception as e:
        logger.error(f"过滤机型图片失败: {str(e)}")
        return []


def _is_aircraft_match(filename: str, aircraft_model: str) -> bool:
    """检查文件名是否匹配指定机型"""
    if not filename or not aircraft_model:
        return False
    
    # 将文件名和机型都转换为大写进行比较
    filename_upper = filename.upper()
    aircraft_upper = aircraft_model.upper()
    
    # 直接匹配
    if aircraft_upper in filename_upper:
        return True
    
    # 使用配置中的关键词进行匹配
    for keyword in AIRCRAFT_KEYWORDS:
        if keyword.upper() in aircraft_upper and keyword.upper() in filename_upper:
            return True
    
    # 提取数字部分进行匹配（如A320, B737等）
    import re
    aircraft_numbers = re.findall(r'\d+', aircraft_upper)
    filename_numbers = re.findall(r'\d+', filename_upper)
    
    if aircraft_numbers and filename_numbers:
        for num in aircraft_numbers:
            if num in filename_numbers:
                return True
    
    return False


def _generate_cache_key(iata_code: str, filename: str, **kwargs) -> str:
    """生成缓存键"""
    key_data = f"{iata_code}_{filename}"
    for k, v in sorted(kwargs.items()):
        key_data += f"_{k}_{v}"
    return hashlib.md5(key_data.encode()).hexdigest()


def _optimize_image(image_path: str, quality: int = None, max_size: tuple = None) -> bytes:
    """优化图片：压缩和调整尺寸"""
    try:
        with Image.open(image_path) as img:
            # 转换为RGB模式（如果需要）
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # 调整尺寸
            if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 自动旋转
            img = ImageOps.exif_transpose(img)
            
            # 保存到内存
            output = io.BytesIO()
            img_format = 'JPEG'
            save_kwargs = {
                'format': img_format,
                'quality': quality or app.config['IMAGE_QUALITY'],
                'optimize': True
            }
            
            img.save(output, **save_kwargs)
            return output.getvalue()
            
    except Exception as e:
        logger.error(f"图片优化失败 {image_path}: {str(e)}")
        # 如果优化失败，返回原始文件内容
        with open(image_path, 'rb') as f:
            return f.read()


def _get_cached_image(cache_key: str) -> Optional[bytes]:
    """从缓存获取图片"""
    try:
        cache_file = os.path.join(IMAGE_CACHE_DIR, f"{cache_key}.jpg")
        if os.path.exists(cache_file):
            # 检查缓存是否过期
            cache_time = os.path.getmtime(cache_file)
            if datetime.now().timestamp() - cache_time < app.config['IMAGE_CACHE_TIMEOUT']:
                with open(cache_file, 'rb') as f:
                    return f.read()
            else:
                # 删除过期缓存
                os.remove(cache_file)
        return None
    except Exception as e:
        logger.error(f"读取图片缓存失败: {str(e)}")
        return None


def _save_cached_image(cache_key: str, image_data: bytes) -> bool:
    """保存图片到缓存"""
    try:
        cache_file = os.path.join(IMAGE_CACHE_DIR, f"{cache_key}.jpg")
        with open(cache_file, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        logger.error(f"保存图片缓存失败: {str(e)}")
        return False


@app.route(f'{API_BASE_PATH}/image/<iata_code>/<filename>', methods=['GET'])
@rate_limit(max_requests=200, window_seconds=3600)  # 图片服务允许更高频率
@error_handler
@log_request
def serve_image(iata_code: str, filename: str):
    """提供图片文件服务（支持缓存和优化）"""
    is_valid, error_msg = validate_iata_code(iata_code)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_IATA_CODE")
    
    # 安全文件名检查
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        raise APIError("无效的文件名", 400, "INVALID_FILENAME")
    
    # 检查文件扩展名
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    file_ext = os.path.splitext(filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise APIError(f"不支持的文件格式: {file_ext}", 400, "UNSUPPORTED_FILE_FORMAT")
    
    file_path = os.path.join(DATA_DIR, iata_code.upper(), filename)
    
    # 路径安全检查
    if not os.path.abspath(file_path).startswith(os.path.abspath(DATA_DIR)):
        raise APIError("非法的文件路径", 400, "INVALID_FILE_PATH")
    
    if not os.path.exists(file_path):
        raise APIError("图片文件不存在", 404, "IMAGE_NOT_FOUND")
    
    try:
        # 获取查询参数
        quality = request.args.get('quality', type=int)
        width = request.args.get('width', type=int)
        height = request.args.get('height', type=int)
        compress = request.args.get('compress', 'true').lower() == 'true'
        
        # 生成缓存键
        cache_params = {
            'quality': quality,
            'width': width,
            'height': height,
            'compress': compress
        }
        cache_key = _generate_cache_key(iata_code, filename, **cache_params)
        
        # 尝试从缓存获取
        if compress and app.config['ENABLE_IMAGE_COMPRESSION']:
            cached_data = _get_cached_image(cache_key)
            if cached_data:
                response = make_response(cached_data)
                response.headers['Content-Type'] = 'image/jpeg'
                response.headers['Cache-Control'] = 'public, max-age=86400'
                response.headers['X-Cache'] = 'HIT'
                return response
        
        # 处理图片
        if compress and app.config['ENABLE_IMAGE_COMPRESSION']:
            # 确定最大尺寸
            max_size = None
            if width and height:
                max_size = (width, height)
            elif width or height:
                # 保持宽高比
                with Image.open(file_path) as img:
                    aspect_ratio = img.width / img.height
                    if width:
                        max_size = (width, int(width / aspect_ratio))
                    else:
                        max_size = (int(height * aspect_ratio), height)
            else:
                max_size = app.config['IMAGE_MAX_SIZE']
            
            # 优化图片
            optimized_data = _optimize_image(file_path, quality, max_size)
            
            # 保存到缓存
            _save_cached_image(cache_key, optimized_data)
            
            # 返回优化后的图片
            response = make_response(optimized_data)
            response.headers['Content-Type'] = 'image/jpeg'
            response.headers['Cache-Control'] = 'public, max-age=86400'
            response.headers['X-Cache'] = 'MISS'
            response.headers['X-Optimized'] = 'true'
            return response
        else:
            # 返回原始文件
            response = make_response(send_file(file_path, as_attachment=False))
            response.headers['Cache-Control'] = 'public, max-age=86400'
            response.headers['X-Cache'] = 'BYPASS'
            return response
            
    except Exception as e:
        logger.error(f"发送图片文件失败: {str(e)}")
        raise APIError("图片文件发送失败", 500, "IMAGE_SERVE_ERROR")


@app.route(f'{API_BASE_PATH}/metrics', methods=['GET'])
@error_handler
@log_request
def get_metrics():
    """获取实时性能指标"""
    try:
        with metrics_lock:
            # 计算最近的响应时间统计
            recent_times = list(performance_metrics['response_times'])
            
            if recent_times:
                min_time = min(recent_times)
                max_time = max(recent_times)
                avg_time = sum(recent_times) / len(recent_times)
                
                # 计算百分位数
                sorted_times = sorted(recent_times)
                p50 = sorted_times[int(len(sorted_times) * 0.5)]
                p90 = sorted_times[int(len(sorted_times) * 0.9)]
                p95 = sorted_times[int(len(sorted_times) * 0.95)]
                p99 = sorted_times[int(len(sorted_times) * 0.99)]
            else:
                min_time = max_time = avg_time = p50 = p90 = p95 = p99 = 0
            
            # 计算请求频率（每分钟请求数）
            uptime_minutes = max((datetime.now() - performance_metrics['start_time']).total_seconds() / 60, 1)
            requests_per_minute = performance_metrics['total_requests'] / uptime_minutes
            
            metrics_data = {
                'requests': {
                    'total': performance_metrics['total_requests'],
                    'successful': performance_metrics['successful_requests'],
                    'failed': performance_metrics['failed_requests'],
                    'success_rate': round((performance_metrics['successful_requests'] / max(performance_metrics['total_requests'], 1)) * 100, 2),
                    'requests_per_minute': round(requests_per_minute, 2)
                },
                'response_times': {
                    'min': round(min_time, 3),
                    'max': round(max_time, 3),
                    'avg': round(avg_time, 3),
                    'p50': round(p50, 3),
                    'p90': round(p90, 3),
                    'p95': round(p95, 3),
                    'p99': round(p99, 3),
                    'sample_size': len(recent_times)
                },
                'errors': dict(performance_metrics['error_counts']),
                'endpoints': {}
            }
            
            # 端点详细统计
            for endpoint, stats in performance_metrics['endpoint_stats'].items():
                endpoint_times = list(stats['times'])
                if endpoint_times:
                    metrics_data['endpoints'][endpoint] = {
                        'count': stats['count'],
                        'avg_time': round(stats['avg_time'], 3),
                        'min_time': round(min(endpoint_times), 3),
                        'max_time': round(max(endpoint_times), 3)
                    }
        
        return jsonify({
            'success': True,
            'data': metrics_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取性能指标失败: {str(e)}")
        raise APIError("获取性能指标失败", 500, "METRICS_ERROR")


@app.route(f'{API_BASE_PATH}/system', methods=['GET'])
@error_handler
@log_request
def get_system_info():
    """获取系统资源使用情况"""
    try:
        # 获取系统资源信息
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        # 获取进程信息
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # 计算运行时间
        uptime = datetime.now() - performance_metrics['start_time']
        uptime_seconds = int(uptime.total_seconds())
        
        system_data = {
            'system': {
                'cpu_percent': round(cpu_percent, 2),
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': round(memory.percent, 2)
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'used': disk.used,
                    'percent': round((disk.used / disk.total) * 100, 2)
                }
            },
            'process': {
                'memory_rss': process_memory.rss,
                'memory_vms': process_memory.vms,
                'cpu_percent': round(process.cpu_percent(), 2),
                'num_threads': process.num_threads(),
                'uptime_seconds': uptime_seconds,
                'uptime_formatted': str(uptime).split('.')[0]  # 去掉微秒
            },
            'directories': {
                'data_exists': os.path.exists('data'),
                'cache_exists': os.path.exists(IMAGE_CACHE_DIR),
                'test_tools_exists': os.path.exists('test_tools')
            }
        }
        
        return jsonify({
            'success': True,
            'data': system_data,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"获取系统信息失败: {str(e)}")
        raise APIError("获取系统信息失败", 500, "SYSTEM_INFO_ERROR")


@app.route(f'{API_BASE_PATH}/cache/clear', methods=['POST'])
@error_handler
@log_request
def clear_cache():
    """清理缓存"""
    try:
        # 清理Flask缓存
        cache.clear()
        
        # 清理图片缓存
        cleared_files = 0
        if os.path.exists(IMAGE_CACHE_DIR):
            for filename in os.listdir(IMAGE_CACHE_DIR):
                file_path = os.path.join(IMAGE_CACHE_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    cleared_files += 1
        
        logger.info(f"缓存清理完成，删除了 {cleared_files} 个缓存文件")
        
        return jsonify({
            'success': True,
            'message': '缓存清理完成',
            'data': {
                'cleared_files': cleared_files,
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"缓存清理失败: {str(e)}")
        raise APIError("缓存清理失败", 500, "CACHE_CLEAR_ERROR")


@app.route(f'{API_BASE_PATH}/stats', methods=['GET'])
@error_handler
@log_request
def get_stats():
    """获取API统计信息（增强版）"""
    try:
        # 计算缓存统计
        cache_files = 0
        cache_size = 0
        if os.path.exists(IMAGE_CACHE_DIR):
            for filename in os.listdir(IMAGE_CACHE_DIR):
                file_path = os.path.join(IMAGE_CACHE_DIR, filename)
                if os.path.isfile(file_path):
                    cache_files += 1
                    cache_size += os.path.getsize(file_path)
        
        # 计算数据目录统计
        data_files = 0
        data_size = 0
        if os.path.exists(DATA_DIR):
            for root, dirs, files in os.walk(DATA_DIR):
                if '.cache' in root:  # 跳过缓存目录
                    continue
                for file in files:
                    if any(file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']):
                        file_path = os.path.join(root, file)
                        data_files += 1
                        data_size += os.path.getsize(file_path)
        
        # 获取性能指标
        with metrics_lock:
            current_metrics = {
                'total_requests': performance_metrics['total_requests'],
                'successful_requests': performance_metrics['successful_requests'],
                'failed_requests': performance_metrics['failed_requests'],
                'success_rate': round((performance_metrics['successful_requests'] / max(performance_metrics['total_requests'], 1)) * 100, 2),
                'avg_response_time': round(performance_metrics['avg_response_time'], 3),
                'error_counts': dict(performance_metrics['error_counts']),
                'endpoint_stats': {}
            }
            
            # 处理端点统计
            for endpoint, stats in performance_metrics['endpoint_stats'].items():
                current_metrics['endpoint_stats'][endpoint] = {
                    'count': stats['count'],
                    'avg_time': round(stats['avg_time'], 3)
                }
        
        # 计算运行时间
        uptime = datetime.now() - performance_metrics['start_time']
        
        # 获取系统资源信息
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('.')
            
            system_info = {
                'cpu_percent': round(cpu_percent, 1),
                'memory_percent': round(memory.percent, 1),
                'memory_used_mb': round(memory.used / 1024 / 1024, 1),
                'memory_total_mb': round(memory.total / 1024 / 1024, 1),
                'disk_percent': round(disk.percent, 1),
                'disk_used_gb': round(disk.used / 1024 / 1024 / 1024, 1),
                'disk_total_gb': round(disk.total / 1024 / 1024 / 1024, 1)
            }
        except Exception as e:
            logger.warning(f'获取系统信息失败: {str(e)}')
            system_info = {'error': '无法获取系统信息'}
        
        return jsonify({
            'success': True,
            'data': {
                'performance': current_metrics,
                'uptime': {
                    'seconds': int(uptime.total_seconds()),
                    'human': str(uptime).split('.')[0],
                    'start_time': performance_metrics['start_time'].isoformat()
                },
                'system': system_info,
                'storage': {
                    'cache': {
                        'files': cache_files,
                        'size_bytes': cache_size,
                        'size_mb': round(cache_size / 1024 / 1024, 2)
                    },
                    'data': {
                        'files': data_files,
                        'size_bytes': data_size,
                        'size_mb': round(data_size / 1024 / 1024, 2)
                    }
                },
                'configuration': {
                    'supported_airlines': len(SUPPORTED_AIRLINES),
                    'image_compression': app.config['ENABLE_IMAGE_COMPRESSION'],
                    'cache_timeout': app.config['IMAGE_CACHE_TIMEOUT'],
                    'max_content_length': app.config['MAX_CONTENT_LENGTH']
                },
                'timestamp': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise APIError("获取统计信息失败", 500, "STATS_ERROR")


if __name__ == '__main__':
    # 确保必要的目录存在
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # 启动开发服务器
    logger.info("Starting AeroLOPA API Server...")
    logger.info(f"图片缓存目录: {IMAGE_CACHE_DIR}")
    logger.info(f"图片优化: {'启用' if app.config['ENABLE_IMAGE_COMPRESSION'] else '禁用'}")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )