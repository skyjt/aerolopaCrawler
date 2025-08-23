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

## 快速开始

1) 创建虚拟环境并安装依赖
- PowerShell: `python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1`
- 安装: `pip install -r requirements.txt`（开发环境额外安装 `pip install -r requirements-dev.txt`）

2) 批量抓取模式
```bash
# 抓取指定航空公司的座位图
python main.py --airline AA

# 抓取所有支持的航空公司
python main.py --all-airlines

# 查看支持的航空公司列表
python main.py --list-airlines
```

3) 运行API服务（可选）
- `python app.py` 启动本地API服务，默认端口 5000

4) 质量保障
- 规范: `ruff check .` / `black --check .`
- 类型: `mypy src`
- 测试: `pytest -q`（覆盖率针对 `src/`）

## 批量抓取功能

### 命令行选项

| 选项 | 描述 | 示例 |
|------|------|------|
| `--airline <code>` | 抓取指定航空公司的座位图 | `--airline AA` |
| `--all-airlines` | 抓取所有支持的航空公司 | `--all-airlines` |
| `--list-airlines` | 列出所有支持的航空公司代码 | `--list-airlines` |

### 使用示例

**1. 抓取单个航空公司**
```bash
python main.py --airline AA
```
输出：下载American Airlines的所有座位图到 `data/seatmaps/` 目录，生成 `data/seatmaps_AA.csv` 数据文件。

**2. 抓取所有航空公司**
```bash
python main.py --all-airlines
```
输出：依次抓取所有支持的航空公司座位图，每个航空公司生成独立的CSV文件。

**3. 查看支持的航空公司**
```bash
python main.py --list-airlines
```
输出：显示所有支持的航空公司代码列表，如：AA, DL, UA, WN等。

### 输出结构

```
data/
├── seatmaps/           # 座位图图片目录
│   ├── AA/            # 按航空公司分类
│   ├── DL/
│   └── ...
├── seatmaps_AA.csv    # American Airlines数据
├── seatmaps_DL.csv    # Delta Airlines数据
└── ...
```

## API服务模式

启动API服务后，可通过HTTP接口查询座位图数据：

```bash
# 启动API服务
python app.py

# 查询示例
curl http://localhost:5000/api/seatmaps?airline=AA
```

## 文档

- API 使用说明：参见 docs/API_USAGE.md
- 开发指南：参见 docs/DEVELOPMENT.md
- 测试指南：参见 docs/TESTING.md
- 辅助说明（如代理/子代理）：参见 docs/AGENTS.md

如需更多文档，请在 docs/ 目录中查看。

## 说明

- 根目录中的旧版爬虫与API整合材料已被梳理并模块化，CLI 与 API 可以分开使用。
- 如果你只需要爬虫能力，直接使用 `src/` 下的 CLI；如需对外提供服务，可启用 `app.py`。
