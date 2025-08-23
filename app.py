#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AeroLOPA 航空座位图 API 服务 - 主入口文件
使用模块化API实现

Author: AeroLOPA Crawler Team
Version: 2.0.0
Date: 2024
"""

from src.aerolopa_crawler.api import create_app, run_app

# 创建Flask应用实例
app = create_app()

if __name__ == '__main__':
    # 启动API服务
    run_app()
