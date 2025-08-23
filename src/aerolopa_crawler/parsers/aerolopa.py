from __future__ import annotations

import re
from typing import Any, Dict

from . import Parser


class AerolopaParser:
    """Example HTML parser for Aerolopa-like pages.

    Keeps dependencies minimal. Extracts a page title if present and returns
    a basic record including URL and content length. Replace with domain-specific
    parsing as needed.
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

