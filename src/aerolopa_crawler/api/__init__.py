"""API服务模块

提供模块化的Flask API服务实现。"""

from .app import create_app, run_app
from .exceptions import APIError
from .validators import (
    validate_iata_code,
    validate_iata_code_with_message,
    validate_aircraft_model,
    validate_aircraft_model_with_message,
    validate_request_params,
    validate_image_params
)
from .utils import (
    standardize_aircraft_model,
    generate_cache_key,
    optimize_image,
    get_cached_image,
    save_cached_image,
    check_local_seatmap_cache,
    filter_aircraft_images,
    is_aircraft_match,
    calculate_cache_stats,
    calculate_data_stats,
    clear_cache_directory
)
from .decorators import (
    error_handler,
    rate_limit,
    log_request,
    cache_response,
    require_json,
    validate_content_length
)
from .routes import api_bp, main_bp


__all__ = [
    # 应用工厂
    'create_app',
    'run_app',
    
    # 异常
    'APIError',
    
    # 验证器
    'validate_iata_code',
    'validate_iata_code_with_message', 
    'validate_aircraft_model',
    'validate_aircraft_model_with_message',
    'validate_request_params',
    'validate_image_params',
    
    # 工具函数
    'standardize_aircraft_model',
    'generate_cache_key',
    'optimize_image',
    'get_cached_image',
    'save_cached_image',
    'check_local_seatmap_cache',
    'filter_aircraft_images',
    'is_aircraft_match',
    'calculate_cache_stats',
    'calculate_data_stats',
    'clear_cache_directory',
    
    # 装饰器
    'error_handler',
    'rate_limit',
    'log_request',
    'cache_response',
    'require_json',
    'validate_content_length',
    
    # 蓝图
    'api_bp',
    'main_bp'
]