#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AeroLOPA API服务启动脚本

跨平台生产环境启动脚本，自动检测操作系统并选择合适的WSGI服务器：
- Linux/macOS: 使用 gunicorn
- Windows: 使用 waitress
"""

import os
import sys
import platform
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app


def get_system_info():
    """获取系统信息"""
    return {
        'platform': platform.system(),
        'python_version': platform.python_version(),
        'architecture': platform.architecture()[0]
    }


def start_with_gunicorn(host='0.0.0.0', port=8000, workers=4):
    """使用Gunicorn启动服务（Linux/macOS）"""
    try:
        import gunicorn.app.wsgiapp as wsgi
        
        print(f"🚀 使用 Gunicorn 启动 AeroLOPA API 服务")
        print(f"📍 地址: http://{host}:{port}")
        print(f"👥 工作进程: {workers}")
        
        # 构建gunicorn参数
        sys.argv = [
            'gunicorn',
            '--bind', f'{host}:{port}',
            '--workers', str(workers),
            '--timeout', '120',
            '--access-logfile', '-',
            '--error-logfile', '-',
            '--log-level', 'info',
            'app:app'
        ]
        
        wsgi.run()
        
    except ImportError:
        print("❌ Gunicorn 未安装，请运行: pip install gunicorn")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Gunicorn 启动失败: {e}")
        sys.exit(1)


def start_with_waitress(host='0.0.0.0', port=8000, threads=4):
    """使用Waitress启动服务（Windows）"""
    try:
        from waitress import serve
        
        print(f"🚀 使用 Waitress 启动 AeroLOPA API 服务")
        print(f"📍 地址: http://{host}:{port}")
        print(f"🧵 线程数: {threads}")
        print(f"📚 文档: http://{host}:{port}/docs")
        print(f"💚 健康检查: http://{host}:{port}/health")
        print(f"📊 统计信息: http://{host}:{port}/stats")
        print("\n按 Ctrl+C 停止服务\n")
        
        # 从配置文件加载参数
        config_file = project_root / 'waitress.conf.py'
        config = {}
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                exec(f.read(), config)
        
        serve(
            app,
            host=config.get('host', host),
            port=config.get('port', port),
            threads=config.get('threads', threads),
            connection_limit=config.get('connection_limit', 1000),
            cleanup_interval=config.get('cleanup_interval', 30),
            channel_timeout=config.get('channel_timeout', 120),
            log_socket_errors=config.get('log_socket_errors', True),
            recv_bytes=config.get('recv_bytes', 65536),
            send_bytes=config.get('send_bytes', 18000),
            url_scheme=config.get('url_scheme', 'http'),
            ident=config.get('ident', 'waitress'),
            expose_tracebacks=config.get('expose_tracebacks', False)
        )
        
    except ImportError:
        print("❌ Waitress 未安装，请运行: pip install waitress")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 AeroLOPA API服务已停止")
    except Exception as e:
        print(f"❌ Waitress 启动失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='AeroLOPA API服务启动脚本')
    parser.add_argument('--host', default='0.0.0.0', help='监听地址 (默认: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='监听端口 (默认: 8000)')
    parser.add_argument('--workers', type=int, default=4, help='工作进程数/线程数 (默认: 4)')
    parser.add_argument('--server', choices=['auto', 'gunicorn', 'waitress'], 
                       default='auto', help='指定WSGI服务器 (默认: auto)')
    parser.add_argument('--info', action='store_true', help='显示系统信息')
    
    args = parser.parse_args()
    
    # 显示系统信息
    if args.info:
        info = get_system_info()
        print("=== 系统信息 ===")
        for key, value in info.items():
            print(f"{key}: {value}")
        return
    
    # 检测操作系统并选择WSGI服务器
    system = platform.system()
    
    if args.server == 'auto':
        if system == 'Windows':
            server_choice = 'waitress'
        else:
            server_choice = 'gunicorn'
    else:
        server_choice = args.server
    
    print(f"🖥️  操作系统: {system}")
    print(f"🔧 WSGI服务器: {server_choice}")
    print("=" * 50)
    
    # 启动服务
    if server_choice == 'gunicorn':
        start_with_gunicorn(args.host, args.port, args.workers)
    elif server_choice == 'waitress':
        start_with_waitress(args.host, args.port, args.workers)
    else:
        print(f"❌ 不支持的服务器类型: {server_choice}")
        sys.exit(1)


if __name__ == '__main__':
    main()