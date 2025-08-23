from __future__ import annotations

import threading
import time
from typing import Optional


class Throttle:
    """Simple wall-clock throttle to respect crawl delays.

    Ensures at least `delay` seconds between successive `wait()` calls
    across threads in a single process.
    """

    def __init__(self, delay: float) -> None:
        self.delay = max(0.0, delay)
        self._lock = threading.Lock()
        self._last_at: Optional[float] = None

    def wait(self) -> None:
        if self.delay <= 0:
            return
        with self._lock:
            now = time.monotonic()
            if self._last_at is None:
                self._last_at = now
                return
            elapsed = now - self._last_at
            remaining = self.delay - elapsed
            if remaining > 0:
                time.sleep(remaining)
            self._last_at = time.monotonic()
