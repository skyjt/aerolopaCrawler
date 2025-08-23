"""API路由模块

定义所有API端点的路由处理逻辑。
"""

import os
import time
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_caching import Cache

from ..config import Config
from ..airlines import AirlineManager, get_airline_info, get_all_airlines
from ..aerolopa_crawler import AerolopaCrawler
from .exceptions import APIError
from .validators import (
    validate_request_params, validate_image_params,
    validate_iata_code_with_message, validate_aircraft_model_with_message
)
from .utils import (
    check_local_seatmap_cache, filter_aircraft_images,
    optimize_image, get_cached_image, save_cached_image,
    calculate_cache_stats, calculate_data_stats, clear_cache_directory
)
from .decorators import error_handler, rate_limit, log_request, cache_response


# 创建蓝图
api_bp = Blueprint('api', __name__)
main_bp = Blueprint('main', __name__)

# 全局变量
request_counter = 0
start_time = datetime.now()
crawler_instance = None


def get_crawler() -> AerolopaCrawler:
    """获取全局爬虫实例"""
    global crawler_instance
    if crawler_instance is None:
        config = Config()
        crawler_instance = AerolopaCrawler(config)
    return crawler_instance


@main_bp.route('/')
@log_request
def index():
    """根路径 - API信息"""
    return jsonify({
        'name': 'AeroLOPA API',
        'version': '2.0.0',
        'description': '航空座位图数据API服务',
        'endpoints': {
            'airlines': '/api/v1/airlines',
            'airline_info': '/api/v1/airlines/<iata_code>',
            'seatmap': '/api/v1/seatmap',
            'image': '/image/<iata_code>/<filename>',
            'health': '/health',
            'docs': '/docs',
            'metrics': '/metrics',
            'system': '/system',
            'stats': '/stats'
        },
        'timestamp': datetime.now().isoformat()
    })


@main_bp.route('/health')
@log_request
def health_check():
    """健康检查端点"""
    global request_counter, start_time
    
    config = Config()
    
    # 检查目录状态
    directories_status = {
        'images_dir': {
            'path': config.image.cache_dir,
            'exists': os.path.exists(config.image.cache_dir),
            'writable': os.access(config.image.cache_dir, os.W_OK) if os.path.exists(config.image.cache_dir) else False
        },
        'output_dir': {
            'path': config.crawler.output_dir,
            'exists': os.path.exists(config.crawler.output_dir),
            'writable': os.access(config.crawler.output_dir, os.W_OK) if os.path.exists(config.crawler.output_dir) else False
        }
    }
    
    # 系统资源
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    uptime = datetime.now() - start_time
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime': str(uptime),
        'request_count': request_counter,
        'system': {
            'memory_usage': f"{memory.percent}%",
            'memory_available': f"{memory.available / (1024**3):.2f} GB",
            'disk_usage': f"{disk.percent}%",
            'disk_free': f"{disk.free / (1024**3):.2f} GB"
        },
        'directories': directories_status,
        'supported_airlines': len(get_all_airlines())
    })


@api_bp.route('/airlines')
@log_request
@cache_response(timeout=3600)  # 缓存1小时
def get_airlines():
    """获取支持的航空公司列表"""
    airlines = get_all_airlines()
    return jsonify({
        'success': True,
        'data': airlines,
        'count': len(airlines),
        'timestamp': datetime.now().isoformat()
    })


@api_bp.route('/airlines/<iata_code>')
@log_request
@cache_response(timeout=3600)
def get_airline_details(iata_code: str):
    """获取指定航空公司信息"""
    # 验证IATA代码
    validate_iata_code_with_message(iata_code)
    
    airline_info = get_airline_info(iata_code.upper())
    if not airline_info:
        raise APIError(
            f"不支持的航空公司代码: {iata_code.upper()}",
            404,
            "AIRLINE_NOT_FOUND"
        )
    
    return jsonify({
        'success': True,
        'data': airline_info,
        'timestamp': datetime.now().isoformat()
    })


@api_bp.route('/seatmap', methods=['GET', 'POST'])
@error_handler
@rate_limit(max_requests=30, window_seconds=3600)
@log_request
def get_seatmap():
    """获取航空公司机型座位图"""
    global request_counter
    request_counter += 1
    
    # 获取参数
    if request.method == 'POST':
        data = request.get_json() or {}
        airline = data.get('airline', '').strip().upper()
        aircraft = data.get('aircraft', '').strip()
        format_type = data.get('format', 'json').lower()
        force_refresh = data.get('force_refresh', False)
    else:
        airline = request.args.get('airline', '').strip().upper()
        aircraft = request.args.get('aircraft', '').strip()
        format_type = request.args.get('format', 'json').lower()
        force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # 验证参数
    if not airline:
        raise APIError("缺少航空公司参数", 400, "MISSING_AIRLINE")
    if not aircraft:
        raise APIError("缺少机型参数", 400, "MISSING_AIRCRAFT")
    
    # 验证IATA代码和机型
    validate_iata_code_with_message(airline)
    validate_aircraft_model_with_message(aircraft)
    
    # 验证航空公司支持
    from ..airlines import get_supported_iata_codes
    supported_codes = get_supported_iata_codes()
    if airline not in supported_codes:
        raise APIError(
            f"不支持的航空公司: {airline}", 
            400, 
            "AIRLINE_NOT_SUPPORTED",
            {'supported_airlines': supported_codes}
        )
    
    config = Config()
    
    # 检查本地缓存（如果不强制刷新）
    if not force_refresh:
        cached_images = check_local_seatmap_cache(config.image.cache_dir, airline, aircraft)
        if cached_images:
            return jsonify({
                'success': True,
                'source': 'cache',
                'airline': airline,
                'aircraft': aircraft,
                'images': cached_images,
                'count': len(cached_images),
                'timestamp': datetime.now().isoformat()
            })
    
    # 执行爬取
    try:
        crawler = get_crawler()
        results = crawler.crawl_airline_seatmaps(
            airline_code=airline,
            aircraft_model=aircraft
        )
        
        if not results or not results.get('images'):
            raise APIError(
                f"未找到 {airline} {aircraft} 的座位图数据",
                404,
                "SEATMAP_NOT_FOUND"
            )
        
        # 过滤匹配的图片
        filtered_images = filter_aircraft_images(results['images'], aircraft)
        
        if not filtered_images:
            raise APIError(
                f"未找到匹配的 {aircraft} 座位图",
                404,
                "AIRCRAFT_NOT_FOUND"
            )
        
        # 限制图片数量
        max_images = 10
        if len(filtered_images) > max_images:
            filtered_images = filtered_images[:max_images]
        
        return jsonify({
            'success': True,
            'source': 'crawled',
            'airline': airline,
            'aircraft': aircraft,
            'images': filtered_images,
            'count': len(filtered_images),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        if isinstance(e, APIError):
            raise
        
        raise APIError(
            f"爬取座位图时发生错误: {str(e)}",
            500,
            "CRAWL_ERROR"
        )


@main_bp.route('/image/<iata_code>/<filename>')
@error_handler
@log_request
def serve_image(iata_code: str, filename: str):
    """提供图片文件服务"""
    # 验证参数
    validate_iata_code_with_message(iata_code)
    
    # 获取查询参数
    width = request.args.get('width', type=int)
    height = request.args.get('height', type=int)
    quality = request.args.get('quality', 85, type=int)
    format_type = request.args.get('format', '').lower()
    
    validate_image_params(width, height, quality, format_type)
    
    config = Config()
    
    # 构建图片路径
    image_path = os.path.join(config.image.cache_dir, iata_code.upper(), filename)
    
    if not os.path.exists(image_path):
        raise APIError(
            f"图片文件不存在: {filename}",
            404,
            "IMAGE_NOT_FOUND"
        )
    
    # 检查是否需要优化
    if width or height or quality != 85 or format_type:
        # 生成缓存键
        cache_key = f"{iata_code}_{filename}_{width}_{height}_{quality}_{format_type}"
        
        # 尝试从缓存获取
        cached_image = get_cached_image(config.image.cache_dir, cache_key)
        if cached_image:
            return send_file(cached_image, as_attachment=False)
        
        # 优化图片并缓存
        try:
            optimized_path = optimize_image(
                image_path, width, height, quality, format_type
            )
            
            if optimized_path != image_path:
                # 保存到缓存
                save_cached_image(config.image.cache_dir, cache_key, optimized_path)
                return send_file(optimized_path, as_attachment=False)
        
        except Exception as e:
            current_app.logger.warning(f"图片优化失败: {str(e)}")
    
    # 返回原始图片
    return send_file(image_path, as_attachment=False)


@main_bp.route('/metrics')
@log_request
def get_metrics():
    """获取实时性能指标"""
    global request_counter, start_time
    
    uptime = datetime.now() - start_time
    memory = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return jsonify({
        'uptime_seconds': int(uptime.total_seconds()),
        'request_count': request_counter,
        'requests_per_minute': round(request_counter / max(uptime.total_seconds() / 60, 1), 2),
        'memory_usage_percent': memory.percent,
        'memory_available_gb': round(memory.available / (1024**3), 2),
        'cpu_usage_percent': cpu_percent,
        'timestamp': datetime.now().isoformat()
    })


@main_bp.route('/system')
@log_request
def get_system_info():
    """获取系统资源使用情况"""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return jsonify({
        'cpu': {
            'usage_percent': cpu_percent,
            'count': psutil.cpu_count()
        },
        'memory': {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'usage_percent': memory.percent
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2),
            'usage_percent': disk.percent
        },
        'timestamp': datetime.now().isoformat()
    })


@main_bp.route('/cache/clear', methods=['POST'])
@error_handler
@log_request
def clear_cache():
    """清理缓存"""
    try:
        config = Config()
        
        # 清理Flask缓存
        cache = current_app.extensions.get('cache')
        if cache:
            cache.clear()
        
        # 清理图片缓存目录
        cleared_files = clear_cache_directory(config.image.cache_dir)
        
        return jsonify({
            'success': True,
            'message': '缓存清理完成',
            'cleared_files': cleared_files,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        raise APIError(
            f"清理缓存时发生错误: {str(e)}",
            500,
            "CACHE_CLEAR_ERROR"
        )


@main_bp.route('/stats')
@log_request
def get_enhanced_stats():
    """获取增强版API统计信息"""
    global request_counter, start_time
    
    config = Config()
    
    # 基础统计
    uptime = datetime.now() - start_time
    
    # 缓存统计
    cache_stats = calculate_cache_stats(config.image.cache_dir)
    
    # 数据目录统计
    data_stats = calculate_data_stats(config.image.cache_dir)
    
    # 系统资源
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return jsonify({
        'api': {
            'version': '2.0.0',
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_human': str(uptime),
            'request_count': request_counter,
            'requests_per_minute': round(request_counter / max(uptime.total_seconds() / 60, 1), 2),
            'start_time': start_time.isoformat()
        },
        'cache': cache_stats,
        'data': data_stats,
        'system': {
            'cpu_usage_percent': cpu_percent,
            'memory_usage_percent': memory.percent,
            'memory_available_gb': round(memory.available / (1024**3), 2),
            'disk_usage_percent': disk.percent,
            'disk_free_gb': round(disk.free / (1024**3), 2)
        },
        'config': {
            'images_dir': config.image.cache_dir,
            'cache_dir': config.image.cache_dir,
            'supported_airlines': len(get_all_airlines())
        },
        'timestamp': datetime.now().isoformat()
    })


@main_bp.route('/docs')
@log_request
def api_docs():
    """API文档"""
    docs = {
        'title': 'AeroLOPA API Documentation',
        'version': '2.0.0',
        'description': '航空座位图数据API服务文档',
        'base_url': request.host_url.rstrip('/'),
        'endpoints': {
            'GET /': {
                'description': 'API基本信息',
                'parameters': {},
                'response': 'API信息和端点列表'
            },
            'GET /health': {
                'description': '健康检查',
                'parameters': {},
                'response': '系统状态和资源使用情况'
            },
            'GET /api/v1/airlines': {
                'description': '获取支持的航空公司列表',
                'parameters': {},
                'response': '航空公司列表'
            },
            'GET /api/v1/airlines/<iata_code>': {
                'description': '获取指定航空公司信息',
                'parameters': {
                    'iata_code': '航空公司IATA代码（2位字母）'
                },
                'response': '航空公司详细信息'
            },
            'GET|POST /api/v1/seatmap': {
                'description': '获取航空公司机型座位图',
                'parameters': {
                    'airline': '航空公司IATA代码（必需）',
                    'aircraft': '机型名称（必需）',
                    'format': '返回格式（json，默认）',
                    'force_refresh': '强制刷新（true/false，默认false）'
                },
                'response': '座位图数据和图片列表'
            },
            'GET /image/<iata_code>/<filename>': {
                'description': '获取座位图图片',
                'parameters': {
                    'iata_code': '航空公司IATA代码',
                    'filename': '图片文件名',
                    'width': '图片宽度（可选）',
                    'height': '图片高度（可选）',
                    'quality': '图片质量1-100（可选，默认85）',
                    'format': '图片格式（jpeg/png/webp，可选）'
                },
                'response': '图片文件'
            },
            'GET /metrics': {
                'description': '获取实时性能指标',
                'parameters': {},
                'response': '性能指标数据'
            },
            'GET /system': {
                'description': '获取系统资源使用情况',
                'parameters': {},
                'response': '系统资源数据'
            },
            'POST /cache/clear': {
                'description': '清理缓存',
                'parameters': {},
                'response': '清理结果'
            },
            'GET /stats': {
                'description': '获取增强版API统计信息',
                'parameters': {},
                'response': '详细统计信息'
            }
        },
        'error_codes': {
            'INVALID_IATA_CODE': '无效的IATA代码',
            'INVALID_AIRCRAFT_MODEL': '无效的机型名称',
            'MISSING_PARAMETER': '缺少必需参数',
            'AIRLINE_NOT_FOUND': '航空公司不存在',
            'SEATMAP_NOT_FOUND': '座位图不存在',
            'AIRCRAFT_NOT_FOUND': '机型不存在',
            'IMAGE_NOT_FOUND': '图片不存在',
            'TOO_MANY_REQUESTS': '请求频率超限',
            'CRAWL_ERROR': '爬取错误',
            'INTERNAL_ERROR': '服务器内部错误'
        },
        'rate_limits': {
            '/api/v1/seatmap': '每小时30次请求',
            'other_endpoints': '每小时50次请求'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(docs)