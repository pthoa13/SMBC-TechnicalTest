"""Watch ``batch-process`` for BrightLearn JSON files."""

from __future__ import annotations

import logging
import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from brightlearn_site.batch.file_state import (
    FileSnapshot,
    is_supported_batch_file,
    iter_supported_batch_files,
    read_file_snapshot,
    wait_until_file_stable,
)
from brightlearn_site.batch.processor import BatchProcessResult, process_batch_file
from brightlearn_site.translation.service import TranslationService

LOGGER = logging.getLogger(__name__)


class BatchFileEventHandler(FileSystemEventHandler):
    def __init__(
        self,
        *,
        input_dir: Path,
        output_dir: Path,
        translation_service: TranslationService,
        stability_interval_seconds: float = 0.25,
        stability_timeout_seconds: float = 10.0,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.translation_service = translation_service
        self.stability_interval_seconds = stability_interval_seconds
        self.stability_timeout_seconds = stability_timeout_seconds
        self._processed_snapshots: dict[Path, FileSnapshot] = {}

    def on_created(self, event: FileSystemEvent) -> None:
        self._handle_event(event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._handle_event(event)

    def on_moved(self, event: FileSystemEvent) -> None:
        destination = getattr(event, "dest_path", "")
        if destination:
            self._process_candidate(Path(destination))

    def _handle_event(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        self._process_candidate(Path(event.src_path))

    def _process_candidate(self, path: Path) -> BatchProcessResult | None:
        if path.parent.resolve() != self.input_dir.resolve():
            LOGGER.info("Ignored nested batch event. file=%s", path.name)
            return None
        resolved_path = path.resolve()
        result = process_stable_file(
            path,
            self.output_dir,
            translation_service=self.translation_service,
            stability_interval_seconds=self.stability_interval_seconds,
            stability_timeout_seconds=self.stability_timeout_seconds,
            last_processed_snapshot=self._processed_snapshots.get(resolved_path),
        )
        if result and result.success:
            self._processed_snapshots[resolved_path] = read_file_snapshot(path)
        return result


def process_existing_files(
    input_dir: Path,
    output_dir: Path,
    *,
    translation_service: TranslationService,
    stability_interval_seconds: float = 0.25,
    stability_timeout_seconds: float = 10.0,
) -> list[BatchProcessResult]:
    results: list[BatchProcessResult] = []
    for path in iter_supported_batch_files(input_dir):
        result = process_stable_file(
            path,
            output_dir,
            translation_service=translation_service,
            stability_interval_seconds=stability_interval_seconds,
            stability_timeout_seconds=stability_timeout_seconds,
        )
        if result is not None:
            results.append(result)
    return results


def process_stable_file(
    path: Path,
    output_dir: Path,
    *,
    translation_service: TranslationService,
    stability_interval_seconds: float = 0.25,
    stability_timeout_seconds: float = 10.0,
    last_processed_snapshot: FileSnapshot | None = None,
) -> BatchProcessResult | None:
    if not is_supported_batch_file(path):
        LOGGER.info("Ignored unsupported batch file. file=%s", path.name)
        return None

    LOGGER.info("Batch file detected. file=%s", path.name)
    if not wait_until_file_stable(
        path,
        interval_seconds=stability_interval_seconds,
        timeout_seconds=stability_timeout_seconds,
    ):
        LOGGER.error("Batch file did not become stable before timeout. file=%s", path.name)
        return BatchProcessResult(
            input_path=path,
            output_root=None,
            success=False,
            message="File did not become stable before timeout.",
            error_type="FileNotStable",
        )

    try:
        current_snapshot = read_file_snapshot(path)
    except OSError as error:
        LOGGER.error(
            "Batch file could not be read after stability check. file=%s error=%s",
            path.name,
            error,
        )
        return BatchProcessResult(
            input_path=path,
            output_root=None,
            success=False,
            message=str(error),
            error_type=type(error).__name__,
        )
    if current_snapshot == last_processed_snapshot:
        LOGGER.info("Ignored unchanged batch file event. file=%s", path.name)
        return None

    return process_batch_file(path, output_dir, translation_service=translation_service)


def run_watch(
    input_dir: Path,
    output_dir: Path,
    *,
    translation_service: TranslationService,
) -> int:
    input_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.info("Batch watcher starting. input=%s output=%s", input_dir, output_dir)
    process_existing_files(input_dir, output_dir, translation_service=translation_service)

    event_handler = BatchFileEventHandler(
        input_dir=input_dir,
        output_dir=output_dir,
        translation_service=translation_service,
    )
    observer = Observer()
    observer.schedule(event_handler, str(input_dir), recursive=False)
    observer.start()

    try:
        while observer.is_alive():
            time.sleep(0.5)
    except KeyboardInterrupt:
        LOGGER.info("Batch watcher shutdown requested.")
    finally:
        observer.stop()
        observer.join()
        LOGGER.info("Batch watcher stopped.")

    return 0
