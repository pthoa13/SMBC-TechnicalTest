"""URL helpers for generated static pages."""

from __future__ import annotations

import os
from pathlib import Path


def relative_url(from_file: Path, to_file: Path) -> str:
    return Path(os.path.relpath(to_file, start=from_file.parent)).as_posix()
