# AeroLOPA Crawler

轻量、模块化的AeroLOPA座位图爬虫与API工程。提供清晰的代码结构、完善的测试与文档，并支持通过CLI与REST API两种方式使用。

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

2) 运行爬虫（CLI）
- `python -m src.main --url https://example.com --output-dir data -v`
- 或 `python -m aerolopa_crawler --url https://example.com --output-dir data -v`

3) 运行API服务（可选）
- `python app.py` 启动本地API服务，默认端口 5000

4) 质量保障
- 规范: `ruff check .` / `black --check .`
- 类型: `mypy src`
- 测试: `pytest -q`（覆盖率针对 `src/`）

## 文档

- API 使用说明：参见 docs/API_USAGE.md
- 开发指南：参见 docs/DEVELOPMENT.md
- 测试指南：参见 docs/TESTING.md
- 辅助说明（如代理/子代理）：参见 docs/AGENTS.md

如需更多文档，请在 docs/ 目录中查看。

## 说明

- 根目录中的旧版爬虫与API整合材料已被梳理并模块化，CLI 与 API 可以分开使用。
- 如果你只需要爬虫能力，直接使用 `src/` 下的 CLI；如需对外提供服务，可启用 `app.py`。
