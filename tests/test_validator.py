from pathlib import Path

from brightlearn_site.loader import load_json_file
from brightlearn_site.validator import validate_dataset


def test_validate_dataset_accepts_minimal_fixture() -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = validate_dataset(data)

    assert len(dataset.books) == 1
