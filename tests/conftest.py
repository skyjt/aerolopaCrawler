from __future__ import annotations

import sys
from pathlib import Path


# 确保从项目根目录运行测试时可以导入 `src/`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
