# AeroLOPA Crawler

轻量、模块化的 AeroLOPA 座位图爬虫与 API 工程。项目提供清晰的代码结构、完善的测试与文档，支持**批量数据抓取**和**REST API 服务**两种使用模式。

## 📋 目录
- [核心功能](#核心功能)
- [目录结构](#目录结构)
- [环境准备](#环境准备)
- [安装步骤](#安装步骤)
- [快速开始](#快速开始)
  - [批量抓取模式](#批量抓取模式)
  - [API 服务模式](#api-服务模式)
  - [开发与测试](#开发与测试)
- [文档导航](#文档导航)
- [说明](#说明)

## 核心功能

- 🚀 **批量抓取模式**：支持单个或多个航空公司的座位图批量下载
- 🌐 **API 服务模式**：提供 RESTful API 接口，支持实时查询
- 📊 **数据导出**：自动生成 CSV 格式的座位图数据
- 🖼️ **图片下载**：自动下载并保存座位图图片
- 💾 **图片缓存**：API 优先读取 `data` 目录图片，超过 24 小时自动从官网更新
- 🔧 **灵活配置**：支持环境变量和配置文件自定义

## 目录结构

- `src/` — 包代码与入口  
  - `aerolopa_crawler/` — 爬虫核心模块（`cli.py`、`crawler.py`、`http.py`、`parsers/` 等）  
  - `main.py` — 模块入口：`python -m src.main`
- `app.py` — Flask API 服务（提供座位图查询接口）
- `tests/` — 单元测试与集成测试
- `configs/` — 运行配置与 `.env.example`
- `data/` — 缓存输出/样例数据（已被 git 忽略）
- `docs/` — 文档目录（API、开发、测试等）

## 环境准备

- Python 3.8+
- Windows、macOS 或 Linux

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/your-username/aerolopaCrawler.git
cd aerolopaCrawler
```

### 2. 创建虚拟环境

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. 安装依赖

```bash
# 基础运行环境
pip install -r requirements.txt

# 开发环境（可选）
pip install -r requirements-dev.txt
```

## 快速开始

### 批量抓取模式

```bash
# 抓取指定航空公司的座位图
python main.py --airline AA

# 抓取所有支持的航空公司
python main.py --all-airlines

# 查看支持的航空公司列表
python main.py --list-airlines
```

### API 服务模式

```bash
# 开发环境启动（Flask 内置服务器）
python app.py

# 生产环境启动（Gunicorn）
gunicorn app:app -c gunicorn.conf.py

# 访问 API 文档
# http://localhost:8000/api/docs
```

### 开发与测试

```bash
# 代码检查
ruff check .

# 类型检查
mypy src

# 运行测试
pytest -q
```

## 文档导航

- [CLI 使用指南](docs/CLI_USAGE.md) — 命令行工具完整使用说明
- [API 使用说明](docs/API_USAGE.md) — REST API 详细说明
- [开发文档](docs/DEVELOPMENT.md) — 项目架构与贡献指南
- [测试文档](docs/TESTING.md) — 测试框架与示例
- 更多文档请查看 [docs/README.md](docs/README.md)

## 说明

- 根目录中的旧版爬虫与 API 整合材料已被梳理并模块化，CLI 与 API 可以分开使用。
- 如果你只需要爬虫能力，直接使用 `src/` 下的 CLI；如需对外提供服务，可启用 `app.py`。

