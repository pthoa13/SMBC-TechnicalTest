"""Conservative JSON repair helpers."""

from __future__ import annotations


def extract_json_object(raw: str) -> str | None:
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    return raw[start : end + 1]


def repair_json(raw: str) -> str:
    return extract_json_object(raw) or raw
