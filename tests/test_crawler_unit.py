from __future__ import annotations

import json
from pathlib import Path

from aerolopa_crawler.crawler import Crawler
from aerolopa_crawler.parsers.aerolopa import AerolopaParser
from aerolopa_crawler.storage import Storage
from aerolopa_crawler.throttle import Throttle


class DummyHttpClient:
    def __init__(self, html: str) -> None:
        self._html = html

    def get_text(self, url: str, headers=None) -> str:  # noqa: ARG002 - parity with real client
        return self._html


def test_crawler_processes_and_writes(tmp_path: Path):
    html = "<html><head><title>Unit Test</title></head><body>Hello</body></html>"
    client = DummyHttpClient(html)
    parser = AerolopaParser()
    storage = Storage(output_dir=str(tmp_path))
    throttle = Throttle(delay=0.0)

    c = Crawler(client=client, parser=parser, storage=storage, throttle=throttle)
    n = c.run(["https://example.com/"])
    assert n == 1

    out = Path(storage.path)
    assert out.exists()
    data = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert data and data[0]["title"] == "Unit Test"

