from __future__ import annotations

import time
import pytest

# 为本文件的所有测试应用标记
pytestmark = [pytest.mark.unit]

from aerolopa_crawler.throttle import Throttle


def test_throttle_enforces_minimum_delay():
    t = Throttle(delay=0.03)
    start = time.perf_counter()
    t.wait()
    t.wait()
    elapsed = time.perf_counter() - start
    assert elapsed >= 0.03 - 0.005  # allow tiny scheduling tolerance

