"""Input schema validation entry points."""

from __future__ import annotations

from typing import Any

from brightlearn_site.models import BookDataset


def validate_dataset(data: dict[str, Any]) -> BookDataset:
    return BookDataset.model_validate(data)
