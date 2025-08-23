from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    base_url: str = ""
    timeout: float = 15.0
    retries: int = 2
    delay: float = 0.5  # polite crawl delay (seconds)
    user_agent: str = (
        "aerolopa-crawler/0.1 (+https://example.com; compatible)"
    )
    output_dir: str = "data"


def _maybe_load_dotenv() -> None:
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv()
    except Exception:
        # Optional dependency; ignore if not installed.
        pass


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from environment and optional file.

    The function prioritizes environment variables with prefix `AEROLOPA_`.
    YAML/JSON file parsing can be added if needed; currently environment-first.
    """
    _maybe_load_dotenv()

    # Future hook: parse YAML/JSON at config_path and merge.
    # Keep simple and dependency-light by using env only for now.

    def getenv_float(name: str, default: float) -> float:
        val = os.getenv(name)
        if val is None:
            return default
        try:
            return float(val)
        except ValueError:
            return default

    def getenv_int(name: str, default: int) -> int:
        val = os.getenv(name)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            return default

    cfg = Config(
        base_url=os.getenv("AEROLOPA_BASE_URL", ""),
        timeout=getenv_float("AEROLOPA_TIMEOUT", 15.0),
        retries=getenv_int("AEROLOPA_RETRIES", 2),
        delay=getenv_float("AEROLOPA_DELAY", 0.5),
        user_agent=os.getenv(
            "AEROLOPA_USER_AGENT",
            "aerolopa-crawler/0.1 (+https://example.com; compatible)",
        ),
        output_dir=os.getenv("AEROLOPA_OUTPUT_DIR", "data"),
    )
    return cfg

