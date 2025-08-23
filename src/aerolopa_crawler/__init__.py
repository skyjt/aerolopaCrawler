"""Aerolopa Crawler package.

Provides a modular crawler with clear separation of concerns:
- config: load/validate runtime settings
- http: HTTP client
- throttle: polite crawling
- parsers: HTML parsers
- normalizers: data normalization helpers
- storage: persistence utilities
- crawler: orchestration
"""

from .crawler import Crawler
from .config import Config, load_config

__all__ = [
    "Crawler",
    "Config",
    "load_config",
]

__version__ = "0.1.0"

