# AeroLOPA Crawler

轻量、模块化的AeroLOPA座位图爬虫与API工程。提供清晰的代码结构、完善的测试与文档，支持**批量数据抓取**和**REST API服务**两种使用模式。

## 功能特性

- 🚀 **批量抓取模式**：支持单个或多个航空公司的座位图批量下载
- 🌐 **API服务模式**：提供RESTful API接口，支持实时查询
- 📊 **数据导出**：自动生成CSV格式的座位图数据
- 🖼️ **图片下载**：自动下载并保存座位图图片
- 🔧 **灵活配置**：支持环境变量和配置文件自定义

## 目录结构

- `src/` — 包代码与入口
  - `aerolopa_crawler/` — 爬虫核心模块（`cli.py`、`crawler.py`、`http.py`、`parsers/` 等）
  - `main.py` — 模块入口：`python -m src.main`
- `app.py` — 可选：Flask API 服务（提供座位图查询接口）
- `tests/` — 单元测试与集成测试

- `configs/` — 运行配置与 `.env.example`
- `data/` — 缓存输出/样例数据（已被git忽略）
- `docs/` — 文档目录（API、开发、测试等）

## 安装

### 环境要求
- Python 3.8+
- 操作系统：Windows、macOS、Linux

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

### API服务模式
```bash
# 启动API服务
python app.py

# 访问API文档
# http://localhost:5000/api/docs
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

## 使用指南

- 📖 **CLI详细用法**：[docs/CLI_USAGE.md](docs/CLI_USAGE.md) - 命令行工具完整使用指南
- 🌐 **API接口文档**：[docs/API_USAGE.md](docs/API_USAGE.md) - REST API详细说明
- 🛠️ **开发指南**：[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) - 项目开发和贡献指南
- 🧪 **测试指南**：[docs/TESTING.md](docs/TESTING.md) - 测试框架和用例说明

## 文档

- API 使用说明：参见 docs/API_USAGE.md
- 开发指南：参见 docs/DEVELOPMENT.md
- 测试指南：参见 docs/TESTING.md
- 辅助说明（如代理/子代理）：参见 docs/AGENTS.md

如需更多文档，请在 docs/ 目录中查看。

## 说明

- 根目录中的旧版爬虫与API整合材料已被梳理并模块化，CLI 与 API 可以分开使用。
- 如果你只需要爬虫能力，直接使用 `src/` 下的 CLI；如需对外提供服务，可启用 `app.py`。
