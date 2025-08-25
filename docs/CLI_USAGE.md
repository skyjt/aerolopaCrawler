# AeroLOPA Crawler CLI 使用指南

本文档详细介绍如何使用 AeroLOPA Crawler 的命令行界面进行批量座位图抓取。

## 📋 目录
- [概述](#概述)
- [基本用法](#基本用法)
- [详细使用示例](#详细使用示例)
- [输出结构详解](#输出结构详解)
- [高级功能](#高级功能)
- [故障排除](#故障排除)
- [性能优化](#性能优化)
- [集成示例](#集成示例)
- [更多信息](#更多信息)

## 概述

AeroLOPA Crawler 提供了强大的命令行工具，支持批量抓取航空公司座位图数据。通过 `main.py` 入口文件，您可以轻松地抓取单个或多个航空公司的座位图。

## 基本用法

### 入口文件

```bash
python main.py [选项]
```

### 命令行选项

| 选项 | 描述 | 示例 |
|------|------|------|
| `--airline <code>` | 抓取指定航空公司的座位图 | `--airline AA` |
| `--all-airlines` | 抓取所有支持的航空公司 | `--all-airlines` |
| `--list-airlines` | 列出所有支持的航空公司代码 | `--list-airlines` |
| `--verbose` | 显示详细的抓取过程信息 | `--verbose` |
| `--output-dir <path>` | 指定输出目录（默认：data/） | `--output-dir ./output` |
| `--stats` | 显示抓取统计信息 | `--stats` |

## 详细使用示例

### 1. 抓取单个航空公司

```bash
# 抓取 American Airlines 的座位图
python main.py --airline AA

# 抓取 Delta Airlines 的座位图并显示详细信息
python main.py --airline DL --verbose

# 抓取 United Airlines 的座位图到指定目录
python main.py --airline UA --output-dir ./my_data
```

**输出说明：**
- 座位图图片保存到 `data/seatmaps/AA/` 目录
- 结构化数据写入 `data/seatmaps.db`（SQLite）与 `data/results.jsonl`（JSON Lines）
- 显示抓取进度和统计信息

### 2. 抓取所有航空公司

```bash
# 抓取所有支持的航空公司
python main.py --all-airlines

# 抓取所有航空公司并显示统计信息
python main.py --all-airlines --stats --verbose
```

**输出说明：**
- 依次抓取所有支持的航空公司座位图
- 每个航空公司生成独立的图片目录；结构化数据统一写入 `seatmaps.db` 与 `results.jsonl`
- 显示总体抓取统计信息

### 3. 查看支持的航空公司

```bash
# 列出所有支持的航空公司代码
python main.py --list-airlines
```

**输出示例：**
```
支持的航空公司代码：
AA - American Airlines
DL - Delta Air Lines
UA - United Airlines
WN - Southwest Airlines
AS - Alaska Airlines
...
```

## 输出结构详解

### 目录结构

```
data/
├── seatmaps/                 # 座位图图片根目录
│   ├── AA/                  # American Airlines 图片
│   │   ├── boeing-737-800/  # 按机型分类
│   │   ├── airbus-a320/
│   │   └── ...
│   ├── DL/                  # Delta Airlines 图片
│   └── ...
├── seatmaps.db              # 结构化数据（SQLite 数据库）
├── results.jsonl            # 结构化数据（JSON Lines，每行一个 JSON 对象）
└── crawler_log.txt          # 抓取日志文件
```

### 数据存储格式

当前版本支持两种结构化数据存储格式，二者可同时生成：

1) SQLite 数据库（`seatmaps.db`）
- 用于高效查询与统计（如 CLI `--stats` 的记录数统计）
- 主要表：`seatmaps`（包含座位图的结构化信息）
- 典型字段：`airline_code`、`airline_name`、`aircraft_model`、`seatmap_url`、`image_filename`、`downloaded_at`、`file_size_bytes`

2) JSON Lines（`results.jsonl`）
- 每行一个 JSON 对象，便于流式处理与追踪抓取过程
- 典型记录示例：

```json
{"airline_code":"AA","aircraft_model":"Boeing 737-800","seatmap_url":"https://...","image_filename":"boeing-737-800_001.jpg","downloaded_at":"2024-01-20T10:30:45Z","file_size_bytes":245760}
```

提示：历史 CSV 导出已取消，不再生成新的 CSV 文件；已有历史 CSV 文件无需迁移，仍可按需保留。

## 高级功能

### 1. 自定义配置

您可以通过环境变量或配置文件自定义爬虫行为：

```bash
# 设置请求延迟（秒）
export AEROLOPA_DELAY=2

# 设置最大重试次数
export AEROLOPA_MAX_RETRIES=3

# 设置输出目录
export AEROLOPA_OUTPUT_DIR=./custom_output
```

### 2. 错误处理

爬虫具有完善的错误处理机制：

- **网络错误**：自动重试，最多重试3次
- **解析错误**：跳过有问题的页面，继续处理其他页面
- **文件错误**：自动创建必要的目录结构

### 3. 进度监控

使用 `--verbose` 选项可以查看详细的抓取进度：

```bash
python main.py --airline AA --verbose
```

输出示例：
```
[INFO] 开始抓取 American Airlines (AA)
[INFO] 发现 25 个飞机型号
[INFO] 正在处理: Boeing 737-800 (1/25)
[INFO] 下载图片: boeing-737-800_001.jpg
[INFO] 处理完成: Boeing 737-800
...
[INFO] 抓取完成！共处理 25 个型号，下载 156 张图片
```

## 故障排除

### 常见问题

1. **网络连接问题**
   ```bash
   # 增加重试次数和延迟
   python main.py --airline AA --verbose
   ```

2. **权限问题**
   ```bash
   # 确保输出目录有写权限
   chmod 755 data/
   ```

3. **依赖缺失**
   ```bash
   # 重新安装依赖
   pip install -r requirements.txt
   ```

### 日志文件

详细的运行日志保存在 `data/crawler_log.txt` 文件中，包含：
- 抓取开始和结束时间
- 处理的URL列表
- 错误和警告信息
- 性能统计数据

## 性能优化

### 1. 并发控制

为避免对目标网站造成过大压力，爬虫默认使用适当的延迟：
- 页面请求间隔：1-2秒
- 图片下载间隔：0.5-1秒

### 2. 内存使用

对于大规模抓取，建议：
- 分批处理航空公司
- 定期清理临时文件
- 监控内存使用情况

### 3. 存储空间

预估存储需求：
- 单个航空公司：50-200MB
- 所有航空公司：2-5GB

## 集成示例

### 1. 定时任务

```bash
#!/bin/bash
# 每日更新脚本
cd /path/to/aerolopaCrawler
source .venv/bin/activate
python main.py --all-airlines --stats > daily_update.log 2>&1
```

### 2. Python 脚本集成

```python
import subprocess
import sys

def crawl_airline(airline_code):
    """抓取指定航空公司数据"""
    cmd = [sys.executable, 'main.py', '--airline', airline_code]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0

# 使用示例
if crawl_airline('AA'):
    print("American Airlines 数据抓取成功")
else:
    print("抓取失败")
```

## 更多信息

- **API 服务模式**：参见 [API_USAGE.md](API_USAGE.md)
- **开发指南**：参见 [DEVELOPMENT.md](DEVELOPMENT.md)
- **测试指南**：参见 [TESTING.md](TESTING.md)
