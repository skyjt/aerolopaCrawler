from __future__ import annotations

from typing import Protocol


class Parser(Protocol):
    """Parser interface for turning HTML into structured records."""

    def parse(self, url: str, html: str) -> dict:
        ...

