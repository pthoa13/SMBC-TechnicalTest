from pathlib import Path

from brightlearn_site.cli import main


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
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Rendered 1 books" in captured.out
    assert (tmp_path / "minimal_books" / "index.html").exists()
