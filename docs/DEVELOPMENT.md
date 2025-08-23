# AeroLOPA API 开发文档

## 📋 目录
- [项目架构](#项目架构)
- [代码结构](#代码结构)
- [贡献指南](#贡献指南)
- [更多信息](#更多信息)

## 项目架构

### 整体架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   客户端应用     │    │   Flask API     │    │   数据爬虫       │
│                │    │                │    │                │
│ - Web 前端      │◄──►│ - RESTful API   │◄──►│ - 网站爬虫       │
│ - 移动应用      │    │ - 缓存系统      │    │ - 数据解析       │
│ - 第三方集成    │    │ - 图片优化      │    │ - 数据存储       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   文件系统       │
                       │                │
                       │ - 图片文件      │
                       │ - 缓存文件      │
                       │ - 日志文件      │
                       └─────────────────┘
```

### 技术栈

#### 后端技术
- **Web 框架**: Flask 3.0+
- **缓存系统**: Flask-Caching (支持 Redis/Memcached/Simple)
- **图片处理**: Pillow (PIL)
- **系统监控**: psutil
- **HTTP 客户端**: requests
- **HTML 解析**: BeautifulSoup4 + lxml
- **进度显示**: tqdm
- **重试机制**: retrying

#### 开发工具
- **测试框架**: pytest
- **代码格式化**: black
- **代码检查**: flake8
- **类型检查**: mypy
- **依赖管理**: pip + requirements.txt

## 代码结构

### 目录结构

```
aerolopaCrawler/
├── app.py                     # 主应用文件
├── requirements.txt           # 依赖包列表
├── README.md                 # 项目说明
├── API_USAGE.md              # API 使用说明
├── DEVELOPMENT.md            # 开发文档
├── .gitignore               # Git 忽略文件
├── data/                    # 数据目录
│   ├── airlines/            # 航空公司数据
│   └── seatmaps/           # 座位图文件
├── cache/                   # 缓存目录
│   ├── images/             # 图片缓存
│   └── flask/              # Flask 缓存
├── logs/                    # 日志目录
│   ├── app.log             # 应用日志
│   └── error.log           # 错误日志
├── tests/                   # 测试目录
│   ├── test_api.py         # API 测试
│   ├── test_crawler.py     # 爬虫测试
│   └── test_utils.py       # 工具测试
└── crawler/                 # 爬虫模块（如果分离）
    ├── __init__.py
    ├── base_crawler.py
    └── airline_crawlers.py
```

### 核心模块

#### 1. 应用初始化 (app.py:1-100)

```python
# Flask 应用配置
app = Flask(__name__)
app.config.update({
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'IMAGE_QUALITY': 85,
    'ENABLE_IMAGE_COMPRESSION': True,
    # ... 其他配置
})

# 缓存初始化
cache = Cache(app)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. 数据模型和验证 (app.py:100-200)

```python
# 自定义异常类
class APIError(Exception):
    def __init__(self, message, code=None, status_code=400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

# 验证函数
def validate_iata_code(code):
    """验证 IATA 代码格式"""
    if not code or len(code) != 2 or not code.isalpha():
        raise APIError("无效的 IATA 代码格式", "INVALID_IATA_CODE")
    return code.upper()

def validate_aircraft_model(model):
    """验证机型格式"""
    if not model or len(model) < 2:
        raise APIError("无效的机型格式", "INVALID_AIRCRAFT_MODEL")
    return standardize_aircraft_model(model)
```

#### 3. 装饰器系统 (app.py:200-300)

```python
# 请求验证装饰器
def validate_request_params(required_params=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 参数验证逻辑
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 错误处理装饰器
def error_handler(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return jsonify({
                'success': False,
                'error': {
                    'code': e.code,
                    'message': e.message
                },
                'timestamp': datetime.utcnow().isoformat()
            }), e.status_code
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': '服务器内部错误'
                },
                'timestamp': datetime.utcnow().isoformat()
            }), 500
    return decorated_function

# 频率限制装饰器
def rate_limit(max_requests=100, window=3600):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 频率限制逻辑
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 日志记录装饰器
def log_request(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = f(*args, **kwargs)
            # 记录成功请求
            return result
        except Exception as e:
            # 记录失败请求
            raise
        finally:
            # 记录性能指标
            pass
    return decorated_function
```

#### 4. 图片处理系统 (app.py:400-600)

```python
# 图片优化函数
def _optimize_image(image_data, quality=85, max_size=None):
    """优化图片：压缩、调整尺寸、格式转换"""
    try:
        # 打开图片
        image = Image.open(io.BytesIO(image_data))
        
        # 转换为 RGB 模式
        if image.mode in ('RGBA', 'P'):
            image = image.convert('RGB')
        
        # 自动旋转
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if exif is not None:
                orientation = exif.get(274)
                if orientation == 3:
                    image = image.rotate(180, expand=True)
                elif orientation == 6:
                    image = image.rotate(270, expand=True)
                elif orientation == 8:
                    image = image.rotate(90, expand=True)
        
        # 调整尺寸
        if max_size:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 保存优化后的图片
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.warning(f"图片优化失败: {str(e)}")
        return image_data

# 缓存管理
def _get_cached_image(cache_key, cache_path):
    """从缓存获取图片"""
    if os.path.exists(cache_path):
        # 检查缓存是否过期
        cache_age = time.time() - os.path.getmtime(cache_path)
        if cache_age < app.config['IMAGE_CACHE_TIMEOUT']:
            with open(cache_path, 'rb') as f:
                return f.read()
    return None

def _save_cached_image(image_data, cache_path):
    """保存图片到缓存"""
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'wb') as f:
            f.write(image_data)
    except Exception as e:
        logger.warning(f"缓存保存失败: {str(e)}")
```

#### 5. API 路由系统 (app.py:600-1000)

```python
# 主要 API 路由
@app.route('/api/v1/seatmap', methods=['GET', 'POST'])
@error_handler
@rate_limit(max_requests=50, window=3600)
@log_request
@validate_request_params(['airline', 'aircraft'])
@cache.cached(timeout=1800, query_string=True)
def get_seatmap():
    """获取座位图数据"""
    # 实现逻辑
    pass

@app.route('/api/v1/image/<iata_code>/<filename>')
@error_handler
@rate_limit(max_requests=200, window=3600)
@log_request
def serve_image(iata_code, filename):
    """图片服务接口"""
    # 实现逻辑
    pass
```

#### 6. 监控系统 (app.py:1000-1200)

```python
# 性能指标收集
performance_metrics = {
    'requests': {
        'total': 0,
        'success': 0,
        'failed': 0
    },
    'response_times': deque(maxlen=1000),
    'errors': defaultdict(int),
    'endpoints': defaultdict(lambda: {
        'count': 0,
        'avg_time': 0,
        'errors': 0
    }),
    'start_time': time.time()
}

# 监控接口
@app.route('/api/v1/metrics')
@error_handler
def get_metrics():
    """获取实时性能指标"""
    # 计算统计数据
    pass

@app.route('/api/v1/system')
@error_handler
def get_system_info():
    """获取系统资源信息"""
    # 系统监控数据
    pass
```

## 开发指南

### 环境搭建

#### 1. 开发环境要求

```bash
# Python 版本
Python >= 3.8

# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 开发依赖
pip install pytest black flake8 mypy
```

#### 2. 项目配置

```bash
# 创建必要目录
mkdir -p data/airlines data/seatmaps
mkdir -p cache/images cache/flask
mkdir -p logs
mkdir -p tests

# 设置环境变量（可选）
export FLASK_ENV=development
export FLASK_DEBUG=True
```

### 代码规范

#### 1. Python 代码规范

遵循 PEP 8 标准：

```python
# 导入顺序
import os
import sys
from datetime import datetime

from flask import Flask, request, jsonify
from PIL import Image

# 常量定义
API_VERSION = '1.0.0'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 类定义
class APIError(Exception):
    """API 自定义异常类
    
    Args:
        message (str): 错误消息
        code (str, optional): 错误代码
        status_code (int, optional): HTTP 状态码
    """
    
    def __init__(self, message: str, code: str = None, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

# 函数定义
def validate_iata_code(code: str) -> str:
    """验证 IATA 代码格式
    
    Args:
        code (str): IATA 代码
        
    Returns:
        str: 标准化的 IATA 代码
        
    Raises:
        APIError: 当代码格式无效时
    """
    if not code or len(code) != 2 or not code.isalpha():
        raise APIError("无效的 IATA 代码格式", "INVALID_IATA_CODE")
    return code.upper()
```

#### 2. 文档字符串规范

使用 Google 风格的文档字符串：

```python
def get_seatmap_data(airline: str, aircraft: str, force_refresh: bool = False) -> dict:
    """获取座位图数据
    
    从本地数据或通过爬虫获取指定航空公司和机型的座位图数据。
    
    Args:
        airline (str): 航空公司 IATA 代码，如 'CA'
        aircraft (str): 机型名称，如 'A320'
        force_refresh (bool, optional): 是否强制刷新数据。默认为 False。
        
    Returns:
        dict: 包含座位图信息的字典，格式如下：
            {
                'images': [{'filename': str, 'url': str, 'size': int}],
                'metadata': {'last_updated': str, 'source': str}
            }
            
    Raises:
        APIError: 当航空公司不支持或数据获取失败时
        
    Example:
        >>> data = get_seatmap_data('CA', 'A320')
        >>> print(len(data['images']))
        5
    """
    pass
```

#### 3. 错误处理规范

```python
# 统一的错误处理
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Specific error occurred: {str(e)}")
    raise APIError("具体错误描述", "SPECIFIC_ERROR_CODE", 400)
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    raise APIError("服务器内部错误", "INTERNAL_ERROR", 500)

# 资源清理
try:
    with open(file_path, 'r') as f:
        data = f.read()
except FileNotFoundError:
    raise APIError("文件未找到", "FILE_NOT_FOUND", 404)
except PermissionError:
    raise APIError("文件访问权限不足", "PERMISSION_DENIED", 403)
```

### 测试指南

#### 1. 测试结构

```python
# tests/test_api.py
import pytest
import requests
from unittest.mock import patch, MagicMock

class TestAPI:
    """API 接口测试类"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        from app import app
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] in ['healthy', 'warning', 'error']
    
    def test_get_airlines(self, client):
        """测试获取航空公司列表"""
        response = client.get('/api/v1/airlines')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'airlines' in data['data']
    
    @patch('app.crawler')
    def test_get_seatmap(self, mock_crawler, client):
        """测试获取座位图数据"""
        # 模拟爬虫返回数据
        mock_crawler.get_seatmap_data.return_value = {
            'images': [{'filename': 'test.jpg', 'url': '/test.jpg'}],
            'metadata': {'source': 'test'}
        }
        
        response = client.get('/api/v1/seatmap?airline=CA&aircraft=A320')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
```

#### 2. 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_api.py

# 运行特定测试方法
pytest tests/test_api.py::TestAPI::test_health_check

# 生成覆盖率报告
pytest --cov=app tests/

# 详细输出
pytest -v tests/
```

### 性能优化

#### 1. 缓存策略

```python
# 多层缓存架构

# 1. Flask 应用级缓存
@cache.cached(timeout=300, query_string=True)
def expensive_operation():
    pass

# 2. 图片文件缓存
def get_cached_image(cache_key):
    cache_path = os.path.join(IMAGE_CACHE_DIR, cache_key)
    if os.path.exists(cache_path):
        return cache_path
    return None

# 3. 浏览器缓存
@app.after_request
def add_cache_headers(response):
    if request.endpoint == 'serve_image':
        response.cache_control.max_age = 3600
        response.cache_control.public = True
    return response
```

#### 2. 数据库优化

```python
# 批量操作
def batch_update_airlines(airlines_data):
    """批量更新航空公司数据"""
    with db.transaction():
        for airline in airlines_data:
            db.update_airline(airline)

# 连接池
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///data.db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### 3. 异步处理

```python
from concurrent.futures import ThreadPoolExecutor
import asyncio

# 异步图片处理
executor = ThreadPoolExecutor(max_workers=4)

def process_image_async(image_data, callback):
    """异步处理图片"""
    future = executor.submit(_optimize_image, image_data)
    future.add_done_callback(callback)
    return future

# 批量下载
async def batch_download_images(urls):
    """批量下载图片"""
    async with aiohttp.ClientSession() as session:
        tasks = [download_image(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    return results
```

### 部署指南

#### 1. 生产环境配置

```python
# config.py
class ProductionConfig:
    DEBUG = False
    TESTING = False
    
    # 数据库配置
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # 缓存配置
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.environ.get('REDIS_URL')
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/aerolopa/app.log'
```

#### 2. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p data cache logs

# 设置环境变量
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - redis
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

volumes:
  redis_data:
```

#### 3. 监控和日志

```python
# 日志配置
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """配置日志系统"""
    if not app.debug:
        # 文件日志
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # 错误日志
        error_handler = RotatingFileHandler(
            'logs/error.log',
            maxBytes=10240000,
            backupCount=10
        )
        error_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('AeroLOPA API startup')
```

### 安全指南

#### 1. 输入验证

```python
from werkzeug.utils import secure_filename
import re

def validate_filename(filename):
    """验证文件名安全性"""
    # 检查文件名长度
    if len(filename) > 255:
        raise APIError("文件名过长", "FILENAME_TOO_LONG")
    
    # 检查危险字符
    if re.search(r'[<>:"/\\|?*]', filename):
        raise APIError("文件名包含非法字符", "INVALID_FILENAME")
    
    # 使用 Werkzeug 的安全文件名
    return secure_filename(filename)

def validate_image_type(file_data):
    """验证图片类型"""
    try:
        image = Image.open(io.BytesIO(file_data))
        if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            raise APIError("不支持的图片格式", "UNSUPPORTED_FORMAT")
        return True
    except Exception:
        raise APIError("无效的图片文件", "INVALID_IMAGE")
```

#### 2. 访问控制

```python
from functools import wraps
from flask import request, abort

def require_api_key(f):
    """API 密钥验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or not validate_api_key(api_key):
            abort(401)
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_by_ip(max_requests=100, window=3600):
    """基于 IP 的频率限制"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            # 实现频率限制逻辑
            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### 故障排除

#### 1. 常见问题

**问题**: 图片加载缓慢
```python
# 解决方案：优化图片处理
def optimize_image_loading():
    # 1. 启用图片缓存
    app.config['ENABLE_IMAGE_COMPRESSION'] = True
    
    # 2. 调整图片质量
    app.config['IMAGE_QUALITY'] = 75
    
    # 3. 设置合理的最大尺寸
    app.config['IMAGE_MAX_SIZE'] = (1200, 800)
```

**问题**: 内存使用过高
```python
# 解决方案：内存管理
def manage_memory():
    # 1. 限制缓存大小
    from cachetools import TTLCache
    image_cache = TTLCache(maxsize=100, ttl=3600)
    
    # 2. 及时释放资源
    def process_image(image_data):
        try:
            image = Image.open(io.BytesIO(image_data))
            # 处理图片
            result = process(image)
        finally:
            if 'image' in locals():
                image.close()
        return result
```

#### 2. 调试工具

```python
# 性能分析
import cProfile
import pstats

def profile_endpoint(f):
    """性能分析装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if app.debug:
            profiler = cProfile.Profile()
            profiler.enable()
            
            try:
                result = f(*args, **kwargs)
            finally:
                profiler.disable()
                stats = pstats.Stats(profiler)
                stats.sort_stats('cumulative')
                stats.print_stats(10)
            
            return result
        else:
            return f(*args, **kwargs)
    return decorated_function

# 内存监控
import tracemalloc

def monitor_memory():
    """监控内存使用"""
    tracemalloc.start()
    
    # 应用逻辑
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
    tracemalloc.stop()
```

## 贡献指南

### 1. 开发流程

1. **Fork 项目**
2. **创建特性分支**: `git checkout -b feature/amazing-feature`
3. **编写代码和测试**
4. **运行测试**: `pytest tests/`
5. **代码格式化**: `black app.py`
6. **代码检查**: `flake8 app.py`
7. **提交更改**: `git commit -m 'Add amazing feature'`
8. **推送分支**: `git push origin feature/amazing-feature`
9. **创建 Pull Request**

### 2. 代码审查

- 确保所有测试通过
- 代码覆盖率不低于 80%
- 遵循项目代码规范
- 添加必要的文档和注释
- 性能影响评估

### 3. 发布流程

1. **更新版本号**
2. **更新 CHANGELOG**
3. **创建 Release Tag**
4. **部署到生产环境**
5. **监控系统状态**

---

## 更多信息

- 项目说明：[README.md](../README.md)
- 更多说明文档：[文档导航](README.md)
