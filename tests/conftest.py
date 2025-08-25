from __future__ import annotations

import sys
from pathlib import Path


# 确保从项目根目录运行测试时可以导入 `src/` 以及顶级包 `aerolopa_crawler`
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
# 先把项目根目录加入 sys.path，这样可以通过 `src.*` 方式导入
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# 再把 src 目录加入 sys.path，这样可以直接通过 `aerolopa_crawler.*` 方式导入
if SRC.exists() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
