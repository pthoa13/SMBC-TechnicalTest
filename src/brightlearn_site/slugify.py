"""Filesystem-safe slug generation."""

from __future__ import annotations

import re
import unicodedata

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def slugify(value: str, fallback: str = "item") -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value).strip("-").lower()
    slug = re.sub(r"-{2,}", "-", slug)

    if not slug:
        slug = fallback

    if slug.upper() in WINDOWS_RESERVED_NAMES:
        slug = f"{slug}-item"

    return slug[:120].rstrip("-") or fallback


def unique_slug(value: str, used_slugs: set[str], fallback: str = "item") -> str:
    """Return a filesystem-safe slug that is unique within ``used_slugs``."""
    base_slug = slugify(value, fallback=fallback)
    slug = base_slug
    counter = 2

    while slug in used_slugs:
        suffix = f"-{counter}"
        slug = f"{base_slug[: 120 - len(suffix)].rstrip('-')}{suffix}"
        counter += 1

    used_slugs.add(slug)
    return slug


def slugify_file_stem(value: str, fallback: str = "dataset") -> str:
    """Return a safe output folder name while preserving filename underscores."""
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9_]+", "-", ascii_value).strip("-_").lower()
    slug = re.sub(r"-{2,}", "-", slug)

    if not slug:
        slug = fallback

    if slug.upper() in WINDOWS_RESERVED_NAMES:
        slug = f"{slug}-item"

    return slug[:120].rstrip("-_") or fallback
