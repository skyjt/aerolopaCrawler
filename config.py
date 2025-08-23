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

# 图片相关配置
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
DEFAULT_IMAGE_EXT = '.jpg'

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FILE = 'crawler.log'