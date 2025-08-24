from __future__ import annotations

import pytest

# 为本文件的所有测试应用标记
pytestmark = [pytest.mark.unit]

from aerolopa_crawler.normalizers import normalize_record


def test_normalize_record_trims_and_defaults():
    rec = {
        "url": "  https://example.com/page  ",
        "title": "  Sample Title  ",
        "content_length": "10",
        "_source": "unit",
        "extra": 123,
    }
    out = normalize_record(rec)
    assert out["url"] == "https://example.com/page"
    assert out["title"] == "Sample Title"
    assert out["content_length"] == 10
    assert out["source"] == "unit"
    assert out["extra"] == 123

