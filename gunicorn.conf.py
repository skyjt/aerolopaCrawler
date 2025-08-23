# -*- coding: utf-8 -*-
"""Gunicorn 配置文件

该配置适用于生产环境，确保在多进程模式下稳定运行。
"""

# 监听地址与端口
bind = "0.0.0.0:8000"

# 工作进程数量，可按 CPU 核心数调整
workers = 4

# 超时时间（秒），防止长时间挂起
timeout = 120

# 日志级别
loglevel = "info"

# 访问日志输出到标准输出
accesslog = "-"

# 错误日志输出到标准错误
errorlog = "-"
