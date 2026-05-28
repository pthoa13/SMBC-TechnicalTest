import json
import logging
from pathlib import Path

from brightlearn_site.batch.file_state import (
    FileSnapshot,
    is_supported_batch_file,
    iter_supported_batch_files,
    read_file_snapshot,
    wait_until_file_stable,
)
from brightlearn_site.batch.processor import process_batch_file
from brightlearn_site.batch.watcher import process_existing_files, process_stable_file
from brightlearn_site.translation.service import EnglishOnlyTranslationService

FIXTURE_PATH = Path("tests/fixtures/minimal_books.json")


def test_supported_batch_file_accepts_json(tmp_path: Path) -> None:
    input_file = tmp_path / "books.json"
    input_file.write_text("{}", encoding="utf-8")

    assert is_supported_batch_file(input_file)


def test_supported_batch_file_ignores_hidden_and_temporary_files(tmp_path: Path) -> None:
    hidden_file = tmp_path / ".books.json"
    temp_file = tmp_path / "books.tmp.json"
    partial_file = tmp_path / "books.json.part"
    for path in [hidden_file, temp_file, partial_file]:
        path.write_text("{}", encoding="utf-8")

    assert not is_supported_batch_file(hidden_file)
    assert not is_supported_batch_file(temp_file)
    assert not is_supported_batch_file(partial_file)


def test_supported_batch_file_ignores_unsupported_extensions(tmp_path: Path) -> None:
    input_file = tmp_path / "books.txt"
    input_file.write_text("{}", encoding="utf-8")

    assert not is_supported_batch_file(input_file)


def test_iter_supported_batch_files_does_not_recurse(tmp_path: Path) -> None:
    direct_file = tmp_path / "direct.json"
    nested_dir = tmp_path / "nested"
    nested_file = nested_dir / "nested.json"
    nested_dir.mkdir()
    direct_file.write_text("{}", encoding="utf-8")
    nested_file.write_text("{}", encoding="utf-8")

    assert list(iter_supported_batch_files(tmp_path)) == [direct_file]


def test_wait_until_file_stable_returns_true_for_matching_snapshots(tmp_path: Path) -> None:
    input_file = tmp_path / "books.json"
    input_file.write_text("{}", encoding="utf-8")
    snapshots = iter(
        [
            FileSnapshot(size=10, modified_ns=1),
            FileSnapshot(size=10, modified_ns=1),
        ]
    )

    assert wait_until_file_stable(
        input_file,
        interval_seconds=0,
        stable_checks=1,
        timeout_seconds=1,
        snapshot_reader=lambda _path: next(snapshots),
    )


def test_wait_until_file_stable_returns_false_for_changing_file(tmp_path: Path) -> None:
    input_file = tmp_path / "books.json"
    input_file.write_text("{}", encoding="utf-8")
    counter = 0

    def read_changing_snapshot(_path: Path) -> FileSnapshot:
        nonlocal counter
        counter += 1
        return FileSnapshot(size=counter, modified_ns=counter)

    assert not wait_until_file_stable(
        input_file,
        interval_seconds=0.001,
        stable_checks=1,
        timeout_seconds=0.01,
        snapshot_reader=read_changing_snapshot,
    )


def test_process_batch_file_renders_valid_fixture(tmp_path: Path) -> None:
    input_file = tmp_path / "BrightLearn Books (2).json"
    input_file.write_text(FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    output_dir = tmp_path / "rendered"

    result = process_batch_file(
        input_file,
        output_dir,
        translation_service=EnglishOnlyTranslationService(),
    )

    assert result.success
    assert result.output_root == output_dir / "brightlearn-books-2"
    assert (output_dir / "brightlearn-books-2" / "index.html").exists()


def test_process_batch_file_returns_failure_for_malformed_json(
    tmp_path: Path,
    caplog,
) -> None:
    input_file = tmp_path / "bad.json"
    input_file.write_text("{", encoding="utf-8")

    with caplog.at_level(logging.ERROR):
        result = process_batch_file(
            input_file,
            tmp_path / "rendered",
            translation_service=EnglishOnlyTranslationService(),
        )

    assert not result.success
    assert result.error_type == "JSONDecodeError"
    assert "Batch processing failed" in caplog.text
    assert "bad.json" in caplog.text


def test_process_batch_file_returns_failure_for_unsupported_schema(tmp_path: Path) -> None:
    input_file = tmp_path / "wrong-schema.json"
    input_file.write_text(json.dumps({"books": "not-a-list"}), encoding="utf-8")

    result = process_batch_file(
        input_file,
        tmp_path / "rendered",
        translation_service=EnglishOnlyTranslationService(),
    )

    assert not result.success
    assert result.error_type == "ValidationError"


def test_process_batch_file_returns_failure_for_unexpected_render_error(
    tmp_path: Path,
    monkeypatch,
) -> None:
    input_file = tmp_path / "books.json"
    input_file.write_text(FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    def fail_render(*args, **kwargs):
        raise RuntimeError("template failure")

    monkeypatch.setattr("brightlearn_site.batch.processor.render_plan", fail_render)

    result = process_batch_file(
        input_file,
        tmp_path / "rendered",
        translation_service=EnglishOnlyTranslationService(),
    )

    assert not result.success
    assert result.error_type == "RuntimeError"
    assert "template failure" in result.message


def test_process_batch_file_skips_unsupported_file(tmp_path: Path) -> None:
    input_file = tmp_path / "books.txt"
    input_file.write_text("{}", encoding="utf-8")

    result = process_batch_file(input_file, tmp_path / "rendered")

    assert result.skipped
    assert not result.success


def test_process_stable_file_ignores_unsupported_candidate(tmp_path: Path) -> None:
    input_file = tmp_path / "books.txt"
    input_file.write_text("{}", encoding="utf-8")

    assert (
        process_stable_file(
            input_file,
            tmp_path / "rendered",
            translation_service=EnglishOnlyTranslationService(),
            stability_interval_seconds=0,
            stability_timeout_seconds=0,
        )
        is None
    )


def test_process_stable_file_ignores_unchanged_snapshot(tmp_path: Path) -> None:
    input_file = tmp_path / "books.json"
    input_file.write_text(FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    snapshot = read_file_snapshot(input_file)

    result = process_stable_file(
        input_file,
        tmp_path / "rendered",
        translation_service=EnglishOnlyTranslationService(),
        stability_interval_seconds=0,
        stability_timeout_seconds=1,
        last_processed_snapshot=snapshot,
    )

    assert result is None
    assert not (tmp_path / "rendered" / "books" / "index.html").exists()


def test_process_existing_files_scans_supported_files_on_startup(tmp_path: Path) -> None:
    input_dir = tmp_path / "batch-process"
    nested_dir = input_dir / "nested"
    input_dir.mkdir()
    nested_dir.mkdir()
    (input_dir / "books.json").write_text(
        FIXTURE_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    (nested_dir / "nested.json").write_text(
        FIXTURE_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    results = process_existing_files(
        input_dir,
        tmp_path / "rendered",
        translation_service=EnglishOnlyTranslationService(),
        stability_interval_seconds=0,
        stability_timeout_seconds=1,
    )

    assert len(results) == 1
    assert results[0].success
    assert (tmp_path / "rendered" / "books" / "index.html").exists()
    assert not (tmp_path / "rendered" / "nested" / "index.html").exists()
