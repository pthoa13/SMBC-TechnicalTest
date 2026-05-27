"""Copy bundled static assets into rendered output."""

from __future__ import annotations

import shutil
from pathlib import Path

from brightlearn_site.paths import STATIC_DIR


def copy_static_assets(output_assets_dir: Path, static_dir: Path = STATIC_DIR) -> None:
    if output_assets_dir.exists():
        shutil.rmtree(output_assets_dir)
    shutil.copytree(static_dir, output_assets_dir)
