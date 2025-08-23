from __future__ import annotations

import os
import sys
from pathlib import Path


# Ensure `src/` is importable when running tests from repo root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

