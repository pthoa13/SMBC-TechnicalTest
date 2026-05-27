"""Normalize raw BrightLearn JSON into internal models."""

from __future__ import annotations

from typing import Any

from brightlearn_site.models import BookDataset
from brightlearn_site.validator import validate_dataset


def normalize_dataset(data: dict[str, Any]) -> BookDataset:
    return validate_dataset(data)
