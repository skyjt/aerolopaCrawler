from __future__ import annotations

import logging
from typing import Iterable, Optional

from .http import HttpClient
from .normalizers import normalize_record
from .parsers import Parser
from .storage import Storage
from .throttle import Throttle


class Crawler:
    """协调抓取、解析、规范化与存储的流程"""

    def __init__(
        self,
        client: HttpClient,
        parser: Parser,
        storage: Storage,
        throttle: Throttle,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.client = client
        self.parser = parser
        self.storage = storage
        self.throttle = throttle
        self.logger = logger or logging.getLogger(__name__)

    def run(self, urls: Iterable[str]) -> int:
        count = 0
        for url in urls:
            url = url.strip()
            if not url:
                continue
            try:
                self.throttle.wait()
                html = self.client.get_text(url)
                parsed = self.parser.parse(url, html)
                normalized = normalize_record(parsed)
                self.storage.write(normalized)
                count += 1
                self.logger.debug("ok: %s", url)
            except Exception as exc:  # noqa: BLE001 - surface errors
                self.logger.error("fail: %s -> %s", url, exc)
        return count
