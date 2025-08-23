from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any, Dict


class Storage:
    """Simple storage that writes JSON Lines to a file.

    Files are appended to `<output_dir>/results.jsonl`.
    """

    def __init__(self, output_dir: str = "data") -> None:
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self._path = os.path.join(self.output_dir, "results.jsonl")

    @property
    def path(self) -> str:
        return self._path

    def write(self, record: Dict[str, Any]) -> None:
        payload = {
            "_ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            **record,
        }
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")

