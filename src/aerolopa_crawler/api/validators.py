"""API验证器模块

提供请求参数验证功能。
"""

import re
from typing import Tuple, Dict, Any, Optional
from flask import request

from ..airlines import get_supported_iata_codes
from .exceptions import APIError


# 机型关键词配置
AIRCRAFT_KEYWORDS = [
    'A320', 'A321', 'A330', 'A340', 'A350', 'A380',
    'B737', 'B747', 'B757', 'B767', 'B777', 'B787',
    'E170', 'E175', 'E190', 'E195',
    'CRJ', 'ERJ', 'ATR', 'Q400'
]


def validate_iata_code(iata_code: str) -> Tuple[bool, Optional[str]]:
    """验证IATA代码格式
    
    Args:
        iata_code: 要验证的IATA代码
        
    Returns:
        (是否有效, 错误消息)
    """
    if not iata_code:
        return False, "IATA代码不能为空"
    
    if not isinstance(iata_code, str):
        return False, "IATA代码必须是字符串"
    
    # IATA代码应该是2-3个字母
    if not re.match(r'^[A-Za-z]{2,3}$', iata_code):
        return False, "IATA代码格式无效，应为2-3个字母"
    
    return True, None


def validate_iata_code_with_message(iata_code: str) -> str:
    """验证IATA代码并返回标准化的代码
    
    Args:
        iata_code: 要验证的IATA代码
        
    Returns:
        标准化的IATA代码（大写）
        
    Raises:
        APIError: 当IATA代码无效时
    """
    is_valid, error_msg = validate_iata_code(iata_code)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_IATA_CODE")
    
    return iata_code.upper()


def validate_aircraft_model(aircraft_model: str) -> Tuple[bool, Optional[str]]:
    """验证机型格式
    
    Args:
        aircraft_model: 要验证的机型
        
    Returns:
        (是否有效, 错误消息)
    """
    if not aircraft_model:
        return False, "机型不能为空"
    
    if not isinstance(aircraft_model, str):
        return False, "机型必须是字符串"
    
    # 机型长度限制
    if len(aircraft_model) > 20:
        return False, "机型名称过长（最多20个字符）"
    
    # 机型格式检查：允许字母、数字、连字符和空格
    if not re.match(r'^[A-Za-z0-9\-\s]+$', aircraft_model):
        return False, "机型格式无效，只允许字母、数字、连字符和空格"
    
    return True, None


def validate_aircraft_model_with_message(aircraft_model: str) -> str:
    """验证机型并返回标准化的机型
    
    Args:
        aircraft_model: 要验证的机型
        
    Returns:
        标准化的机型名称
        
    Raises:
        APIError: 当机型无效时
    """
    is_valid, error_msg = validate_aircraft_model(aircraft_model)
    if not is_valid:
        raise APIError(error_msg, 400, "INVALID_AIRCRAFT_MODEL")
    
    return aircraft_model.strip()


def validate_request_params(required_params: Dict[str, Any], optional_params: Dict[str, Any] = None) -> Dict[str, Any]:
    """验证请求参数
    
    Args:
        required_params: 必需参数及其验证规则
        optional_params: 可选参数及其默认值
        
    Returns:
        验证后的参数字典
        
    Raises:
        APIError: 当参数验证失败时
    """
    params = {}
    optional_params = optional_params or {}
    
    # 获取请求数据
    if request.method == 'GET':
        request_data = request.args
    else:
        request_data = request.get_json() or {}
    
    # 验证必需参数
    for param_name, validator in required_params.items():
        value = request_data.get(param_name)
        
        if value is None:
            if param_name == 'airline':
                raise APIError("缺少航空公司参数", 400, "MISSING_AIRLINE")
            elif param_name == 'aircraft':
                raise APIError("缺少机型参数", 400, "MISSING_AIRCRAFT")
            else:
                raise APIError(f"缺少必需参数: {param_name}", 400, "MISSING_PARAMETER")
        
        # 执行验证
        if callable(validator):
            try:
                params[param_name] = validator(value)
            except APIError:
                raise
            except Exception as e:
                raise APIError(f"参数 {param_name} 验证失败: {str(e)}", 400, "PARAMETER_VALIDATION_ERROR")
        else:
            params[param_name] = value
    
    # 处理可选参数
    for param_name, default_value in optional_params.items():
        value = request_data.get(param_name, default_value)
        params[param_name] = value
    
    # 特殊验证：航空公司支持检查
    if 'airline' in params:
        supported_codes = get_supported_iata_codes()
        if params['airline'] not in supported_codes:
            raise APIError(
                f"不支持的航空公司: {params['airline']}", 
                400, 
                "AIRLINE_NOT_SUPPORTED",
                {'supported_airlines': supported_codes}
            )
    
    # 验证返回格式
    if 'format' in params:
        valid_formats = ['json', 'html']
        if params['format'] not in valid_formats:
            raise APIError(
                f"不支持的返回格式: {params['format']}", 
                400, 
                "UNSUPPORTED_FORMAT",
                {'supported_formats': valid_formats}
            )
    
    return params


def validate_image_params() -> Dict[str, Any]:
    """验证图片请求参数
    
    Returns:
        验证后的图片参数
    """
    params = {}
    
    # 质量参数
    quality = request.args.get('quality', type=int)
    if quality is not None:
        if not (1 <= quality <= 100):
            raise APIError("图片质量必须在1-100之间", 400, "INVALID_QUALITY")
        params['quality'] = quality
    
    # 尺寸参数
    width = request.args.get('width', type=int)
    height = request.args.get('height', type=int)
    
    if width is not None:
        if not (1 <= width <= 4000):
            raise APIError("图片宽度必须在1-4000像素之间", 400, "INVALID_WIDTH")
        params['width'] = width
    
    if height is not None:
        if not (1 <= height <= 4000):
            raise APIError("图片高度必须在1-4000像素之间", 400, "INVALID_HEIGHT")
        params['height'] = height
    
    # 压缩参数
    compress = request.args.get('compress', 'true').lower() == 'true'
    params['compress'] = compress
    
    return params