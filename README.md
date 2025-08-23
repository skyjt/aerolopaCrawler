# AeroLOPA 航空座位图 API

## 项目简介

AeroLOPA 航空座位图 API 是一个基于 Flask 的 RESTful API 服务，提供航空公司座位图数据的获取和管理功能。该 API 集成了网络爬虫技术，能够实时获取各大航空公司的座位图信息，并提供高性能的图片服务。

## 主要功能

- 🛫 **航空公司信息查询**：支持查询航空公司基本信息和支持列表
- 🪑 **座位图数据获取**：根据航空公司和机型获取对应的座位图
- 🖼️ **图片服务**：提供高性能的图片访问，支持缓存、压缩和尺寸调整
- 📊 **性能监控**：实时性能指标、系统资源监控和健康检查
- 🔒 **安全防护**：请求频率限制、参数验证和错误处理
- 📝 **完整日志**：详细的请求日志和性能统计

## 技术栈

- **后端框架**：Flask 3.0+
- **缓存系统**：Flask-Caching (支持 Redis/Memcached)
- **图片处理**：Pillow (PIL)
- **系统监控**：psutil
- **网络请求**：requests + beautifulsoup4
- **数据解析**：lxml
- **其他工具**：tqdm, retrying, urllib3

## 快速开始

### 环境要求

- Python 3.8+
- pip 或 conda 包管理器

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动服务

```bash
python app.py
```

服务将在 `http://localhost:5000` 启动。

### 基本使用

1. **检查服务状态**
```bash
curl http://localhost:5000/health
```

2. **获取支持的航空公司列表**
```bash
curl http://localhost:5000/api/v1/airlines
```

3. **获取座位图数据**
```bash
curl "http://localhost:5000/api/v1/seatmap?airline=CA&aircraft=A320"
```

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:5000`
- **API Version**: `v1`
- **Content-Type**: `application/json`
- **字符编码**: `UTF-8`

### 认证

当前版本无需认证，但实施了请求频率限制。

### 响应格式

所有 API 响应都遵循统一的 JSON 格式：

```json
{
  "success": true,
  "data": {},
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

错误响应格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": "详细信息（可选）"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 核心接口

#### 1. 服务信息

**GET /**

获取 API 服务基本信息。

**响应示例：**
```json
{
  "service": "AeroLOPA 航空座位图 API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "airlines": "/api/v1/airlines",
    "seatmap": "/api/v1/seatmap",
    "docs": "/docs"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### 2. 健康检查

**GET /health**

检查服务运行状态和系统资源使用情况。

**响应示例：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "version": "1.0.0",
  "uptime_seconds": 3600,
  "uptime_human": "1:00:00",
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "memory_available_mb": 2048.5,
    "disk_percent": 65.3,
    "disk_free_gb": 50.2
  },
  "directories": {
    "data_dir": true,
    "logs_dir": true,
    "cache_dir": true
  },
  "warnings": []
}
```

#### 3. 航空公司列表

**GET /api/v1/airlines**

获取支持的航空公司列表。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "airlines": [
      {
        "iata_code": "CA",
        "chinese_name": "中国国际航空",
        "english_name": "Air China"
      }
    ],
    "supported_codes": ["CA", "CZ", "MU"],
    "total_count": 50
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### 4. 航空公司信息

**GET /api/v1/airlines/{iata_code}**

获取指定航空公司的详细信息。

**路径参数：**
- `iata_code` (string): 航空公司 IATA 代码

**响应示例：**
```json
{
  "success": true,
  "data": {
    "iata_code": "CA",
    "chinese_name": "中国国际航空",
    "english_name": "Air China",
    "country": "中国"
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### 5. 座位图数据

**GET /api/v1/seatmap**
**POST /api/v1/seatmap**

获取指定航空公司和机型的座位图数据。

**查询参数：**
- `airline` (string, 必需): 航空公司 IATA 代码
- `aircraft` (string, 必需): 机型名称
- `format` (string, 可选): 返回格式，默认 "json"
- `force_refresh` (boolean, 可选): 是否强制刷新，默认 false
- `limit` (integer, 可选): 图片数量限制，默认 50

**请求示例：**
```bash
GET /api/v1/seatmap?airline=CA&aircraft=A320&limit=10
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "airline": {
      "iata_code": "CA",
      "chinese_name": "中国国际航空",
      "english_name": "Air China"
    },
    "aircraft": {
      "original_model": "A320",
      "standardized_model": "A320"
    },
    "seatmap": {
      "images": [
        {
          "filename": "CA_A320_001.jpg",
          "url": "/api/v1/image/CA/CA_A320_001.jpg",
          "optimized_urls": {
            "thumbnail": "/api/v1/image/CA/CA_A320_001.jpg?width=200&height=150&quality=70",
            "medium": "/api/v1/image/CA/CA_A320_001.jpg?width=800&height=600&quality=80",
            "high_quality": "/api/v1/image/CA/CA_A320_001.jpg?quality=95"
          },
          "size": 1024000,
          "dimensions": "1920x1080"
        }
      ],
      "metadata": {
        "last_updated": "2024-01-01T12:00:00.000000",
        "source": "AeroLOPA",
        "force_refresh": false,
        "total_images": 5,
        "limit_applied": 10
      }
    }
  },
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

#### 6. 图片服务

**GET /api/v1/image/{iata_code}/{filename}**

获取航空公司座位图图片文件，支持实时优化和缓存。

**路径参数：**
- `iata_code` (string): 航空公司 IATA 代码
- `filename` (string): 图片文件名

**查询参数：**
- `quality` (integer, 可选): 图片质量 (1-100)，默认 85
- `width` (integer, 可选): 图片宽度（像素）
- `height` (integer, 可选): 图片高度（像素）
- `compress` (boolean, 可选): 是否启用压缩，默认 true

**请求示例：**
```bash
GET /api/v1/image/CA/CA_A320_001.jpg?width=800&height=600&quality=80
```

**响应头：**
- `Content-Type`: 图片 MIME 类型
- `Cache-Control`: 缓存控制策略
- `X-Cache`: 缓存状态 (HIT/MISS/BYPASS)
- `X-Optimized`: 是否已优化 (true/false)

### 监控接口

#### 7. API 统计信息

**GET /api/v1/stats**

获取 API 的详细统计信息，包括性能指标、系统资源、缓存状态等。

#### 8. 实时性能指标

**GET /api/v1/metrics**

获取实时性能指标，包括请求统计、响应时间分布、错误统计等。

#### 9. 系统资源信息

**GET /api/v1/system**

获取系统资源使用情况，包括 CPU、内存、磁盘使用情况等。

#### 10. 缓存管理

**POST /api/v1/cache/clear**

清理 API 缓存，包括 Flask 缓存和图片缓存。

### 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|---------|------------|------|
| MISSING_AIRLINE | 400 | 缺少航空公司参数 |
| MISSING_AIRCRAFT | 400 | 缺少机型参数 |
| INVALID_IATA_CODE | 400 | 无效的 IATA 代码格式 |
| INVALID_AIRCRAFT_MODEL | 400 | 无效的机型格式 |
| AIRLINE_NOT_FOUND | 404 | 航空公司未找到 |
| AIRLINE_NOT_SUPPORTED | 404 | 不支持的航空公司 |
| SEATMAP_FETCH_ERROR | 500 | 座位图获取失败 |
| UNSUPPORTED_FORMAT | 400 | 不支持的返回格式 |
| TOO_MANY_REQUESTS | 429 | 请求频率超限 |
| PAYLOAD_TOO_LARGE | 413 | 请求体过大 |
| UNAUTHORIZED | 401 | 未授权访问 |
| FORBIDDEN | 403 | 禁止访问 |
| METHOD_NOT_ALLOWED | 405 | 请求方法不被允许 |
| INTERNAL_ERROR | 500 | 服务器内部错误 |
| BAD_GATEWAY | 502 | 网关错误 |
| SERVICE_UNAVAILABLE | 503 | 服务暂时不可用 |
| GATEWAY_TIMEOUT | 504 | 网关超时 |

### 请求频率限制

| 接口类型 | 限制 |
|---------|------|
| 座位图 API | 每小时 50 次请求 |
| 图片 API | 每小时 200 次请求 |
| 一般 API | 每小时 100 次请求 |

## 配置说明

### 环境变量

可以通过环境变量配置以下参数：

```bash
# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=True

# 缓存配置
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300

# 图片优化配置
IMAGE_QUALITY=85
IMAGE_MAX_SIZE=1920,1080
ENABLE_IMAGE_COMPRESSION=True
```

### 应用配置

主要配置项在 `app.py` 中定义：

```python
# API 配置
API_VERSION = '1.0.0'
API_BASE_PATH = '/api/v1'

# 缓存配置
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
app.config['CACHE_KEY_PREFIX'] = 'aerolopa_'

# 图片优化配置
app.config['IMAGE_CACHE_TIMEOUT'] = 3600
app.config['IMAGE_QUALITY'] = 85
app.config['IMAGE_MAX_SIZE'] = (1920, 1080)
app.config['ENABLE_IMAGE_COMPRESSION'] = True
```

## 部署指南

### 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd aerolopaCrawler

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

### 生产环境

推荐使用 Gunicorn + Nginx 部署：

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Nginx 配置示例：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # 静态文件缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

构建和运行：

```bash
docker build -t aerolopa-api .
docker run -p 5000:5000 aerolopa-api
```

## 性能优化

### 缓存策略

1. **Flask 缓存**：API 响应缓存，减少重复计算
2. **图片缓存**：本地文件缓存，避免重复处理
3. **浏览器缓存**：合理的 Cache-Control 头部设置

### 图片优化

1. **动态压缩**：根据请求参数实时调整图片质量和尺寸
2. **格式转换**：自动转换为最优的图片格式
3. **渐进式加载**：支持渐进式 JPEG

### 监控和日志

1. **性能监控**：实时性能指标收集和分析
2. **错误追踪**：详细的错误日志和异常处理
3. **系统监控**：CPU、内存、磁盘使用情况监控

## 开发指南

### 项目结构

```
aerolopaCrawler/
├── app.py                 # 主应用文件
├── requirements.txt       # 依赖包列表
├── README.md             # 项目文档
├── data/                 # 数据目录
├── logs/                 # 日志目录
├── cache/                # 缓存目录
├── test_tools/           # 测试工具
└── crawler/              # 爬虫模块
```

### 代码规范

1. **PEP 8**：遵循 Python 代码规范
2. **类型注解**：使用类型注解提高代码可读性
3. **文档字符串**：为函数和类添加详细的文档字符串
4. **错误处理**：完善的异常处理机制

### 测试

运行测试：

```bash
# 运行所有测试
python -m pytest test_tools/

# 运行特定测试
python -m pytest test_tools/test_api.py

# 生成覆盖率报告
python -m pytest --cov=app test_tools/
```

### 贡献指南

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 常见问题

### Q: 如何增加新的航空公司支持？

A: 需要在爬虫模块中添加对应的航空公司爬取逻辑，并更新航空公司列表。

### Q: 图片加载缓慢怎么办？

A: 可以调整图片质量参数，使用缩略图，或者配置 CDN 加速。

### Q: API 请求频率限制如何调整？

A: 修改 `@rate_limit` 装饰器的参数，或者在配置中调整限制值。

### Q: 如何监控 API 性能？

A: 使用 `/api/v1/metrics` 和 `/api/v1/system` 接口获取实时性能数据。

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**AeroLOPA 航空座位图 API** - 让航空座位图数据触手可及！