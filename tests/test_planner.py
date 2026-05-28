from pathlib import Path

from brightlearn_site.loader import load_json_file
from brightlearn_site.normalizer import normalize_dataset
from brightlearn_site.site.planner import build_render_plan, output_root_for_input


def test_output_root_uses_input_file_stem() -> None:
    output_root = output_root_for_input(
        Path("data/samples/brightlearn_books.json"),
        Path("rendered"),
    )

    assert output_root == Path("rendered/brightlearn_books")


def test_render_plan_creates_duplicate_safe_book_slugs() -> None:
    data = load_json_file(Path("tests/fixtures/duplicate_titles.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(
        dataset,
        Path("tests/fixtures/duplicate_titles.json"),
        Path("rendered"),
    )

    assert [book_page.slug for book_page in plan.book_pages] == [
        "duplicate-title",
        "duplicate-title-2",
    ]


def test_render_plan_includes_section_targets() -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), Path("rendered"))

    output_paths = {target.output_path for target in plan.targets}

    assert Path("rendered/minimal_books/index.html") in output_paths
    assert Path("rendered/minimal_books/books/sample-book/index.html") in output_paths
    assert (
        Path("rendered/minimal_books/books/sample-book/sections/sample-section.html")
        in output_paths
    )
