#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
"""

# 基础配置
BASE_URL = "https://www.aerolopa.com"
DATA_DIR = "data"

# 请求配置
REQUEST_TIMEOUT = 30
REQUEST_DELAY = 1  # 请求间隔（秒）
MAX_RETRIES = 3
RETRY_DELAY = 2000  # 重试延迟（毫秒）

# 用户代理
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

# 航司代码列表（可根据需要扩展）
AIRLINES = [
    # 主要航司
    'aa',  # American Airlines
    'ba',  # British Airways
    'ua',  # United Airlines
    'ac',  # Air Canada
    'af',  # Air France
    'dl',  # Delta Air Lines
    'lh',  # Lufthansa
    'nh',  # ANA
    'sq',  # Singapore Airlines
    'cx',  # Cathay Pacific
    'qf',  # Qantas
    'ek',  # Emirates
    'qr',  # Qatar Airways
    'tk',  # Turkish Airlines
    'vs',  # Virgin Atlantic
    'ks',  # JetBlue
    'oz',  # Asiana Airlines
    'jl',  # JAL
    'ca',  # Air China
    'mu',  # China Eastern
    # 可以根据需要添加更多航司
]

# 机型识别关键词
AIRCRAFT_TYPES = [
    'A319', 'A320', 'A321', 'A330', 'A340', 'A350', 'A380',
    'B737', 'B747', 'B757', 'B767', 'B777', 'B787',
    '737', '747', '757', '767', '777', '787',
    'CRJ', 'ERJ', 'E190', 'DHC', 'ATR', 'MD80', 'MD90'
]

# 机型关键词映射（用于标准化）
AIRCRAFT_KEYWORDS = {
    'A319': ['A319', 'a319', 'Airbus A319'],
    'A320': ['A320', 'a320', 'Airbus A320'],
    'A321': ['A321', 'a321', 'Airbus A321'],
    'A330': ['A330', 'a330', 'Airbus A330'],
    'A340': ['A340', 'a340', 'Airbus A340'],
    'A350': ['A350', 'a350', 'Airbus A350'],
    'A380': ['A380', 'a380', 'Airbus A380'],
    'B737': ['B737', 'b737', '737', 'Boeing 737'],
    'B747': ['B747', 'b747', '747', 'Boeing 747'],
    'B757': ['B757', 'b757', '757', 'Boeing 757'],
    'B767': ['B767', 'b767', '767', 'Boeing 767'],
    'B777': ['B777', 'b777', '777', 'Boeing 777'],
    'B787': ['B787', 'b787', '787', 'Boeing 787'],
}

# 图片相关配置
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
DEFAULT_IMAGE_EXT = '.jpg'
IMAGE_FORMATS = ['JPEG', 'PNG', 'GIF', 'WEBP']

# 日志配置
LOGS_DIR = 'logs'
LOG_LEVEL = 'INFO'
LOG_FILE = 'aerolopa.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# API配置
API_VERSION = '1.0.0'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
IMAGE_CACHE_DIR = 'cache/images'
IMAGE_CACHE_TIMEOUT = 3600  # 1小时
ENABLE_IMAGE_COMPRESSION = True
IMAGE_QUALITY = 85
IMAGE_MAX_SIZE = (1200, 800)

# 缓存配置
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300

# 速率限制配置
RATE_LIMIT_STORAGE_URL = 'memory://'
RATE_LIMIT_DEFAULT = '100 per hour'