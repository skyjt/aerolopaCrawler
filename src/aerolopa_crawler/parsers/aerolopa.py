from __future__ import annotations

import re
from typing import Any, Dict


class AerolopaParser:
    """示例 HTML 解析器

    依赖最小化：提取页面标题，并返回包含 URL 与内容长度的基础记录
    """

    _TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)

    def parse(self, url: str, html: str) -> Dict[str, Any]:
        m = self._TITLE_RE.search(html)
        title = m.group(1).strip() if m else None
        return {
            "url": url,
            "title": title,
            "content_length": len(html),
            "_source": "aerolopa",
        }
