# Repository Guidelines

## Project Structure & Module Organization
- `src/`: package code and entry points (e.g., `src/aerolopa_crawler/`, `src/main.py`).
- `tests/`: mirrors `src/` for unit/integration tests.
- `scripts/`: dev/ops utilities (e.g., data refresh, lint hooks).
- `configs/`: runtime configs (YAML/JSON); exclude secrets.
- `data/`: small cached inputs/outputs and fixtures (avoid large files).

## Build, Test, and Development Commands
- Create venv (PowerShell): `python -m venv .venv; .\.venv\Scripts\Activate.ps1`
- Install deps: `pip install -r requirements.txt` (or `poetry install`).
- Run locally: `python -m src.main` or `python -m aerolopa_crawler` (match actual entry).
- Lint/format: `ruff check .` and `black .` (auto-fix: `ruff --fix .`).
- Type-check: `mypy src`.
- Tests: `pytest -q` (coverage: `pytest --cov=src --cov-report=term-missing`).

## Coding Style & Naming Conventions
- Indentation 4 spaces, UTF-8, Unix line endings.
- Names: modules/files `snake_case.py`, classes `PascalCase`, functions/vars `snake_case`.
- Imports: stdlib → third-party → local, separated by blank lines.
- Keep functions focused; prefer pure helpers for parsing/normalization.

## Testing Guidelines
- Framework: `pytest`; fixtures in `tests/conftest.py`.
- Test names: `test_<module>_<behavior>()`; files mirror module path.
- Aim ≥ 85% coverage on core parsing/normalization; include regression cases.
- Avoid live network: use `responses`/`pytest-httpserver` or recorded fixtures.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (e.g., `feat:`, `fix:`, `chore:`, `test:`) with small, atomic diffs.
- PRs: clear description, linked issue, scope of change, how to test, and before/after notes (logs, sample JSON, CLI output). Include screenshots when HTML changes affect parsing.
- CI must pass: lint, type-check, tests, and coverage.

## Security & Configuration Tips
- Use `.env` + `python-dotenv`; never commit tokens/cookies. Add to `.gitignore` and provide `.env.example`.
- Respect robots/ToS; throttle via configurable delays and concurrency.
- Determinism: seed randomness, freeze versions in `requirements.txt`, and pin scraper selectors with comments referencing source URLs.

