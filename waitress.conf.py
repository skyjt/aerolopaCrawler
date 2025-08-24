# -*- coding: utf-8 -*-
"""Waitress 配置文件

该配置适用于Windows环境的生产部署，作为gunicorn的替代方案。
Waitress是纯Python实现的WSGI服务器，完全兼容Windows系统。
"""

# 监听地址与端口
host = "0.0.0.0"
port = 8000

# 线程配置
threads = 4  # 线程数量，可按CPU核心数调整

# 连接配置
connection_limit = 1000  # 最大连接数
cleanup_interval = 30    # 清理间隔（秒）

# 超时配置
channel_timeout = 120    # 通道超时（秒）
log_socket_errors = True # 记录socket错误

# 缓冲区配置
recv_bytes = 65536      # 接收缓冲区大小
send_bytes = 18000      # 发送缓冲区大小

# URL配置
url_scheme = "http"     # URL协议
url_prefix = ""         # URL前缀

# 其他配置
ident = "waitress"      # 服务器标识
expose_tracebacks = False  # 生产环境不暴露错误堆栈

# 日志配置（通过环境变量或应用程序处理）
# Waitress本身的日志较少，主要依赖应用程序的日志系统