from pathlib import Path

from brightlearn_site.loader import load_json_file


def test_load_json_file_returns_object() -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))

    assert data["source"] == "Test"
