from pathlib import Path

from brightlearn_site.cli import main
from brightlearn_site.translation.service import EnglishOnlyTranslationService


def test_validate_command_reports_valid_dataset(capsys) -> None:
    exit_code = main(["validate", "tests/fixtures/minimal_books.json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Valid BrightLearn dataset: 1 books" in captured.out


def test_render_command_writes_expected_output(tmp_path: Path, capsys) -> None:
    exit_code = main(
        [
            "render",
            "tests/fixtures/minimal_books.json",
            "--output-dir",
            str(tmp_path),
            "--skip-translations",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Rendered 1 books" in captured.out
    assert (tmp_path / "minimal_books" / "index.html").exists()


def test_render_command_writes_logs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    input_path = Path(__file__).resolve().parent / "fixtures" / "minimal_books.json"

    exit_code = main(
        [
            "render",
            str(input_path),
            "--output-dir",
            "rendered",
            "--skip-translations",
        ]
    )

    log_file = tmp_path / "logs" / "app.log"
    assert exit_code == 0
    assert log_file.exists()
    assert "Render command started" in log_file.read_text(encoding="utf-8")


def test_render_command_without_api_key_warns_and_falls_back(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setenv("LLM_API_KEY", "")
    monkeypatch.setenv("TRANSLATION_CACHE_PATH", str(tmp_path / "cache.json"))

    exit_code = main(
        [
            "render",
            "tests/fixtures/minimal_books.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "rendering English summaries only" in captured.err


def test_render_command_treats_placeholder_api_key_as_missing(
    tmp_path: Path,
    capsys,
    monkeypatch,
) -> None:
    monkeypatch.setenv("LLM_API_KEY", "your_api_key_here")
    monkeypatch.setenv("TRANSLATION_CACHE_PATH", str(tmp_path / "cache.json"))

    exit_code = main(
        [
            "render",
            "tests/fixtures/minimal_books.json",
            "--output-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "rendering English summaries only" in captured.err


def test_watch_command_wires_batch_watcher_without_real_llm(
    tmp_path: Path,
    monkeypatch,
) -> None:
    calls = []

    def fake_run_watch(input_dir, output_dir, *, translation_service):
        calls.append((input_dir, output_dir, translation_service))
        return 0

    monkeypatch.setattr("brightlearn_site.cli.run_watch", fake_run_watch)

    exit_code = main(
        [
            "watch",
            "--input-dir",
            str(tmp_path / "batch-process"),
            "--output-dir",
            str(tmp_path / "rendered"),
            "--skip-translations",
        ]
    )

    assert exit_code == 0
    assert len(calls) == 1
    assert calls[0][0] == tmp_path / "batch-process"
    assert calls[0][1] == tmp_path / "rendered"
    assert isinstance(calls[0][2], EnglishOnlyTranslationService)
