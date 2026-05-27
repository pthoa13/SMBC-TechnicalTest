"""Jinja2 renderer for static pages."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from brightlearn_site.paths import TEMPLATE_DIR


def create_template_environment(template_dir: Path = TEMPLATE_DIR) -> Environment:
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )
