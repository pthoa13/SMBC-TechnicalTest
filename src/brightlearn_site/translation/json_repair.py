"""Conservative JSON repair helpers."""

from __future__ import annotations


def repair_json(raw: str) -> str:
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return raw
    return raw[start : end + 1]
