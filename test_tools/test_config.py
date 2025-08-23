#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA API 测试配置

测试相关的配置参数和常量

Author: AeroLOPA Crawler Team
Version: 1.0.0
Date: 2024
"""

import os

# 测试环境配置
TEST_CONFIG = {
    # API服务器配置
    'API_BASE_URL': 'http://localhost:5000',
    'API_TIMEOUT': 30,
    'API_RETRY_COUNT': 3,
    'API_RETRY_DELAY': 1,
    
    # 测试数据配置
    'TEST_AIRLINES': [
        'CA',  # 中国国际航空
        'CZ',  # 中国南方航空
        'MU',  # 中国东方航空
        '3U',  # 四川航空
        'AA',  # 美国航空
        'UA',  # 美国联合航空
        'DL',  # 达美航空
    ],
    
    'TEST_AIRCRAFT_MODELS': [
        'A320',
        'A321',
        'A330',
        'A350',
        'A380',
        'B737',
        'B747',
        'B777',
        'B787',
        'CRJ900',
        'E190'
    ],
    
    # 性能测试配置
    'PERFORMANCE_TEST': {
        'CONCURRENT_USERS': [1, 5, 10, 20, 50],
        'REQUEST_COUNTS': [10, 50, 100, 200],
        'LOAD_TEST_DURATION': 60,  # 秒
        'MAX_RESPONSE_TIME': 5.0,  # 秒
        'MIN_SUCCESS_RATE': 95.0,  # 百分比
        'MAX_ERROR_RATE': 5.0,     # 百分比
    },
    
    # 压力测试配置
    'STRESS_TEST': {
        'CONCURRENT_LEVELS': [1, 5, 10, 20, 50, 100, 200],
        'REQUESTS_PER_LEVEL': 50,
        'MIN_SUCCESS_RATE_THRESHOLD': 80.0,  # 低于此值停止测试
        'COOLDOWN_SECONDS': 2,  # 每个级别之间的休息时间
    },
    
    # 负载测试配置
    'LOAD_TEST': {
        'DURATION_SECONDS': 30,
        'CONCURRENT_USERS': 5,
        'REQUEST_INTERVAL': 0.1,  # 秒
    }
}

# 测试用例配置
TEST_CASES = {
    'UNIT_TESTS': {
        'validation': {
            'valid_iata_codes': ['CA', 'CZ', 'MU', '3U', 'AA', 'UA', 'DL', 'LH', 'AF', 'BA'],
            'invalid_iata_codes': ['', None, 'A', 'ABCD', '123', 'a1', 'CA1', '!@', 'XX'],
            'valid_aircraft_models': [
                'A320', 'A321', 'A330', 'A350', 'A380',
                'B737', 'B747', 'B777', 'B787',
                'CRJ900', 'E190', 'ATR72'
            ],
            'invalid_aircraft_models': [
                '', None, 'A', 'A' * 25, '!@#$%', '中文机型', '123ABC'
            ],
            'aircraft_standardization': [
                ('boeing 737', 'B 737'),
                ('airbus a320', 'A A320'),
                ('B-737', 'B737'),
                ('A-320', 'A320'),
                ('  a350  900  ', 'A350 900'),
                ('Boeing 777-300ER', 'B 777-300ER'),
                ('AIRBUS A380-800', 'A A380-800')
            ]
        }
    },
    
    'API_TESTS': {
        'endpoints': [
            {
                'name': '根路径',
                'path': '/',
                'method': 'GET',
                'expected_status': 200,
                'expected_fields': ['service', 'version', 'endpoints']
            },
            {
                'name': '健康检查',
                'path': '/health',
                'method': 'GET',
                'expected_status': 200,
                'expected_fields': ['status', 'timestamp', 'version']
            },
            {
                'name': '航空公司列表',
                'path': '/api/v1/airlines',
                'method': 'GET',
                'expected_status': 200,
                'expected_fields': ['success', 'data']
            },
            {
                'name': 'API文档',
                'path': '/docs',
                'method': 'GET',
                'expected_status': 200,
                'expected_fields': ['title', 'version', 'endpoints']
            }
        ],
        
        'error_cases': [
            {
                'name': '404错误',
                'path': '/nonexistent-endpoint',
                'method': 'GET',
                'expected_status': 404,
                'expected_error_code': 'NOT_FOUND'
            },
            {
                'name': '缺少airline参数',
                'path': '/api/v1/seatmap',
                'method': 'GET',
                'params': {'aircraft': 'A320'},
                'expected_status': 400,
                'expected_error_code': 'MISSING_AIRLINE'
            },
            {
                'name': '缺少aircraft参数',
                'path': '/api/v1/seatmap',
                'method': 'GET',
                'params': {'airline': 'CA'},
                'expected_status': 400,
                'expected_error_code': 'MISSING_AIRCRAFT'
            },
            {
                'name': '无效IATA代码',
                'path': '/api/v1/seatmap',
                'method': 'GET',
                'params': {'airline': 'INVALID', 'aircraft': 'A320'},
                'expected_status': 400,
                'expected_error_code': 'INVALID_IATA_CODE'
            },
            {
                'name': '无效机型',
                'path': '/api/v1/seatmap',
                'method': 'GET',
                'params': {'airline': 'CA', 'aircraft': '!@#$'},
                'expected_status': 400,
                'expected_error_code': 'INVALID_AIRCRAFT_MODEL'
            }
        ]
    },
    
    'PERFORMANCE_TESTS': {
        'light_endpoints': [
            {'path': '/health', 'name': '健康检查'},
            {'path': '/api/v1/airlines', 'name': '航空公司列表'}
        ],
        'heavy_endpoints': [
            {
                'path': '/api/v1/seatmap',
                'name': '座位图查询',
                'params': {'airline': 'CA', 'aircraft': 'A320'}
            }
        ]
    }
}

# 测试环境检查
ENVIRONMENT_CHECKS = {
    'required_packages': [
        'requests',
        'flask',
        'beautifulsoup4',
        'lxml',
        'pillow',
        'tqdm',
        'retrying'
    ],
    
    'required_files': [
        'app.py',
        'main.py',
        'config.py',
        'airlines_config.py',
        'requirements.txt'
    ],
    
    'required_directories': [
        'data',
        'logs'
    ]
}

# 测试报告配置
REPORT_CONFIG = {
    'output_format': 'markdown',
    'include_details': True,
    'include_performance_charts': False,  # 需要额外的图表库
    'max_error_examples': 5,
    'timestamp_format': '%Y-%m-%d %H:%M:%S'
}

# 测试数据生成配置
TEST_DATA_CONFIG = {
    'mock_responses': {
        'seatmap_success': {
            'images': [
                {
                    'filename': 'CA_A320_seatmap.jpg',
                    'file_path': '/test/path/CA_A320_seatmap.jpg',
                    'url': '/api/v1/image/CA/CA_A320_seatmap.jpg',
                    'size': 1024000,
                    'modified_time': '2024-01-01T12:00:00',
                    'source_url': 'https://example.com/image.jpg'
                }
            ]
        },
        
        'airline_info': {
            'CA': {
                'iata_code': 'CA',
                'chinese_name': '中国国际航空',
                'english_name': 'Air China'
            }
        }
    },
    
    'test_files': {
        'create_temp_images': True,
        'image_formats': ['jpg', 'png'],
        'image_sizes': [(800, 600), (1024, 768)]
    }
}

# 获取配置函数
def get_test_config(section=None):
    """获取测试配置"""
    if section:
        return TEST_CONFIG.get(section, {})
    return TEST_CONFIG

def get_test_cases(category=None):
    """获取测试用例"""
    if category:
        return TEST_CASES.get(category, {})
    return TEST_CASES

def get_environment_checks():
    """获取环境检查配置"""
    return ENVIRONMENT_CHECKS

def get_report_config():
    """获取报告配置"""
    return REPORT_CONFIG

def get_test_data_config():
    """获取测试数据配置"""
    return TEST_DATA_CONFIG

# 测试环境变量
TEST_ENV_VARS = {
    'FLASK_ENV': 'testing',
    'TESTING': 'true',
    'LOG_LEVEL': 'DEBUG'
}

def setup_test_environment():
    """设置测试环境变量"""
    for key, value in TEST_ENV_VARS.items():
        os.environ[key] = value

def cleanup_test_environment():
    """清理测试环境变量"""
    for key in TEST_ENV_VARS.keys():
        if key in os.environ:
            del os.environ[key]