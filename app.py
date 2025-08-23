#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AeroLOPA 航空座位图 API 服务 - WSGI 入口

该文件供 Gunicorn 等 WSGI 服务器加载使用。
"""

from src.aerolopa_crawler.api import create_app

# 创建 Flask 应用实例，供生产环境的 Gunicorn 等 WSGI 服务器使用
app = create_app()

if __name__ == "__main__":
    # 开发环境下使用 Flask 内置服务器启动
    from src.aerolopa_crawler.api import run_app

    run_app()
