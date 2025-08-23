"""Flask应用工厂模块

创建和配置Flask应用实例。
"""

import os
import logging
from datetime import datetime
from typing import Optional

from flask import Flask, jsonify
from flask_cors import CORS
from flask_caching import Cache

from ..config import Config
from .routes import api_bp, main_bp
from .exceptions import APIError


def create_app(config: Optional[Config] = None) -> Flask:
    """创建Flask应用实例
    
    Args:
        config: 配置对象，如果为None则使用默认配置
        
    Returns:
        配置好的Flask应用实例
    """
    app = Flask(__name__)
    
    # 使用配置
    if config is None:
        config = Config()
    
    # Flask配置
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'aerolopa-secret-key-2024'),
        'JSON_AS_ASCII': False,
        'JSON_SORT_KEYS': False,
        'JSONIFY_PRETTYPRINT_REGULAR': True,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 300
    })
    
    # 初始化扩展
    _init_extensions(app)
    
    # 注册蓝图
    _register_blueprints(app)
    
    # 注册错误处理器
    _register_error_handlers(app)
    
    # 配置日志
    _configure_logging(app, config)
    
    # 确保必要目录存在
    _ensure_directories(config)
    
    # 存储配置到应用上下文
    app.config['AEROLOPA_CONFIG'] = config
    
    return app


def _init_extensions(app: Flask) -> None:
    """初始化Flask扩展"""
    # CORS配置
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 缓存配置
    cache = Cache()
    cache.init_app(app)


def _register_blueprints(app: Flask) -> None:
    """注册蓝图"""
    # 注册主蓝图
    app.register_blueprint(main_bp)
    
    # 注册API蓝图
    app.register_blueprint(api_bp, url_prefix='/api/v1')


def _register_error_handlers(app: Flask) -> None:
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': '请求格式错误'
            },
            'timestamp': datetime.now().isoformat()
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': '未授权访问'
            },
            'timestamp': datetime.now().isoformat()
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': '禁止访问'
            },
            'timestamp': datetime.now().isoformat()
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '资源不存在'
            },
            'timestamp': datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': '请求方法不允许'
            },
            'timestamp': datetime.now().isoformat()
        }), 405
    
    @app.errorhandler(413)
    def payload_too_large(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAYLOAD_TOO_LARGE',
                'message': '请求体过大'
            },
            'timestamp': datetime.now().isoformat()
        }), 413
    
    @app.errorhandler(429)
    def too_many_requests(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOO_MANY_REQUESTS',
                'message': '请求频率超限'
            },
            'timestamp': datetime.now().isoformat()
        }), 429
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': '服务器内部错误'
            },
            'timestamp': datetime.now().isoformat()
        }), 500
    
    @app.errorhandler(502)
    def bad_gateway(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_GATEWAY',
                'message': '网关错误'
            },
            'timestamp': datetime.now().isoformat()
        }), 502
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVICE_UNAVAILABLE',
                'message': '服务不可用'
            },
            'timestamp': datetime.now().isoformat()
        }), 503
    
    @app.errorhandler(504)
    def gateway_timeout(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'GATEWAY_TIMEOUT',
                'message': '网关超时'
            },
            'timestamp': datetime.now().isoformat()
        }), 504
    
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        return jsonify({
            'success': False,
            'error': error.to_dict(),
            'timestamp': datetime.now().isoformat()
        }), error.status_code


def _configure_logging(app: Flask, config: Config) -> None:
    """配置日志"""
    if not app.debug:
        # 确保日志目录存在
        logs_dir = config.logging.log_dir
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)
        
        # 设置日志文件路径
        log_file = config.logging.file_path or os.path.join(logs_dir, 'aerolopa_api.log')
        
        # 生产环境日志配置
        logging.basicConfig(
            level=getattr(logging, config.logging.level.upper()),
            format=config.logging.format,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(log_file)
            ]
        )
    
    # 设置Flask日志级别
    app.logger.setLevel(getattr(logging, config.logging.level.upper()))
    
    # 记录启动信息
    app.logger.info("AeroLOPA API服务启动")
    app.logger.info(f"图片目录: {config.image.cache_dir}")
    app.logger.info(f"输出目录: {config.crawler.output_dir}")


def _ensure_directories(config: Config) -> None:
    """确保必要的目录存在"""
    directories = [
        config.image.cache_dir,
        config.crawler.output_dir,
        config.logging.log_dir
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def run_app(host: str = '0.0.0.0', port: int = 5000, debug: bool = False) -> None:
    """运行Flask应用
    
    Args:
        host: 主机地址
        port: 端口号
        debug: 是否开启调试模式
    """
    app = create_app()
    
    print(f"\n🚀 AeroLOPA API服务启动")
    print(f"📍 地址: http://{host}:{port}")
    print(f"📚 文档: http://{host}:{port}/docs")
    print(f"💚 健康检查: http://{host}:{port}/health")
    print(f"📊 统计信息: http://{host}:{port}/stats")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n按 Ctrl+C 停止服务\n")
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\n👋 AeroLOPA API服务已停止")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {str(e)}")
        raise


if __name__ == '__main__':
    # 开发环境直接运行
    run_app(debug=True)