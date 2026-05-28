"""File filtering and stability helpers for batch inputs."""

from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

TEMPORARY_SUFFIXES = {
    ".crdownload",
    ".download",
    ".part",
    ".partial",
    ".swp",
    ".temp",
    ".tmp",
}


@dataclass(frozen=True)
class FileSnapshot:
    size: int
    modified_ns: int


def is_supported_batch_file(path: Path) -> bool:
    """Return true for direct, non-temporary JSON files supported by batch mode."""
    return path.is_file() and path.suffix.lower() == ".json" and not is_hidden_or_temporary(path)


def is_hidden_or_temporary(path: Path) -> bool:
    name = path.name
    return (
        name.startswith(".")
        or name.endswith("~")
        or path.suffix.lower() in TEMPORARY_SUFFIXES
        or any(name.lower().endswith(f"{suffix}.json") for suffix in TEMPORARY_SUFFIXES)
    )


def iter_supported_batch_files(input_dir: Path) -> Iterable[Path]:
    """Yield supported JSON files directly under ``input_dir`` without recursion."""
    if not input_dir.exists():
        return []
    return sorted(path for path in input_dir.iterdir() if is_supported_batch_file(path))


def wait_until_file_stable(
    path: Path,
    *,
    interval_seconds: float = 0.25,
    stable_checks: int = 2,
    timeout_seconds: float = 10.0,
    snapshot_reader: Callable[[Path], FileSnapshot] | None = None,
) -> bool:
    """Wait until a file's size and modified timestamp remain unchanged."""
    if stable_checks < 1:
        raise ValueError("stable_checks must be at least 1.")
    if interval_seconds < 0:
        raise ValueError("interval_seconds must be non-negative.")
    if timeout_seconds < 0:
        raise ValueError("timeout_seconds must be non-negative.")

    read_snapshot = snapshot_reader or read_file_snapshot
    deadline = time.monotonic() + timeout_seconds
    previous: FileSnapshot | None = None
    matching_checks = 0

    while time.monotonic() <= deadline:
        try:
            current = read_snapshot(path)
        except OSError:
            previous = None
            matching_checks = 0
        else:
            if current == previous:
                matching_checks += 1
                if matching_checks >= stable_checks:
                    return True
            else:
                previous = current
                matching_checks = 0

        time.sleep(interval_seconds)

    return False


def read_file_snapshot(path: Path) -> FileSnapshot:
    stat = path.stat()
    return FileSnapshot(size=stat.st_size, modified_ns=stat.st_mtime_ns)
