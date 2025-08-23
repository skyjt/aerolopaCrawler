"""API异常处理模块

定义API服务的自定义异常类。
"""

from typing import Optional, Dict, Any


class APIError(Exception):
    """API自定义异常类
    
    用于统一处理API错误，包含错误消息、HTTP状态码和错误代码。
    """
    
    def __init__(self, message: str, status_code: int = 400, error_code: str = "API_ERROR", details: Optional[Dict[str, Any]] = None):
        """初始化API异常
        
        Args:
            message: 错误消息
            status_code: HTTP状态码
            error_code: 错误代码
            details: 额外的错误详情
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式
        
        Returns:
            包含错误信息的字典
        """
        result = {
            'code': self.error_code,
            'message': self.message
        }
        
        if self.details:
            result['details'] = self.details
            
        return result
    
    def __str__(self) -> str:
        return f"APIError({self.error_code}): {self.message}"
    
    def __repr__(self) -> str:
        return f"APIError(message='{self.message}', status_code={self.status_code}, error_code='{self.error_code}')"