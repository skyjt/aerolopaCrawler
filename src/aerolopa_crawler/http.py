from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Dict, Optional


class HttpClient:
    """轻量级 HTTP 客户端，支持重试与超时

    使用标准库 `urllib.request`，避免额外依赖；提供基本的文本和 JSON 请求
    """

    def __init__(
        self,
        timeout: float = 15.0,
        retries: int = 2,
        user_agent: str = "aerolopa-crawler/0.1 (+https://example.com)",
    ) -> None:
        self.timeout = timeout
        self.retries = max(0, retries)
        self.user_agent = user_agent

    def _build_request(
        self, url: str, headers: Optional[Dict[str, str]] = None
    ) -> urllib.request.Request:
        hdrs = {"User-Agent": self.user_agent}
        if headers:
            hdrs.update(headers)
        return urllib.request.Request(url, headers=hdrs, method="GET")

    def get_text(self, url: str, headers: Optional[Dict[str, str]] = None) -> str:
        attempt = 0
        while True:
            try:
                req = self._build_request(url, headers)
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    charset = resp.headers.get_content_charset() or "utf-8"
                    return resp.read().decode(charset, errors="replace")
            except (urllib.error.URLError, urllib.error.HTTPError):
                if attempt >= self.retries:
                    raise
                backoff = min(2**attempt, 4)
                time.sleep(backoff)
                attempt += 1

    def get_json(self, url: str, headers: Optional[Dict[str, str]] = None) -> object:
        text = self.get_text(url, headers=headers)
        return json.loads(text)
