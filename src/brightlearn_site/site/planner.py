"""Render plan generation for static site output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RenderTarget:
    template_name: str
    output_path: Path


@dataclass(frozen=True)
class RenderPlan:
    output_root: Path
    targets: list[RenderTarget]
