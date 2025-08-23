"""AeroLOPA航空座位图爬虫包

一个用于爬取航空公司座位图的Python包。
"""

__version__ = "0.2.0"

# 导出统一配置模块
from .config import Config, CrawlerConfig, APIConfig, LoggingConfig, ImageConfig, load_config

# 导出航司管理模块
from .airlines import AirlineManager, get_airline_info, get_all_airlines, get_supported_iata_codes

# 导出统一爬虫实现
from .aerolopa_crawler import AerolopaCrawler

# 导出CLI模块
from . import cli

# 导出API模块
from . import api
from .api import create_app, run_app, APIError

__all__ = [
    # 版本信息
    '__version__',
    
    # 配置管理
    'Config',
    'CrawlerConfig', 
    'APIConfig',
    'LoggingConfig',
    'ImageConfig',
    'load_config',
    
    # 航司管理
    'AirlineManager',
    'get_airline_info',
    'get_all_airlines', 
    'get_supported_iata_codes',
    
    # 爬虫实现
    'AerolopaCrawler',
    
    # CLI模块
    'cli',
    
    # API模块
    'api',
    'create_app',
    'run_app',
    'APIError'
]

