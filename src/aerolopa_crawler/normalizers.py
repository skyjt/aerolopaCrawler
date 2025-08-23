from __future__ import annotations

from typing import Any, Dict


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize parsed records to a stable schema.

    - Trim strings
    - Ensure required keys
    - Add defaults for missing optional fields
    """
    out: Dict[str, Any] = {}
    out["url"] = str(record.get("url", "")).strip()
    title = record.get("title")
    out["title"] = str(title).strip() if isinstance(title, str) else title
    out["content_length"] = int(record.get("content_length", 0))
    out["source"] = record.get("_source") or record.get("source") or "unknown"
    # Carry-through any extra fields unchanged
    for k, v in record.items():
        if k not in out:
            out[k] = v
    return out

