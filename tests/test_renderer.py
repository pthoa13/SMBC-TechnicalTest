import re
from pathlib import Path

import pytest

from brightlearn_site.loader import load_json_file
from brightlearn_site.models import SummaryTranslations
from brightlearn_site.normalizer import normalize_dataset
from brightlearn_site.site.planner import build_render_plan
from brightlearn_site.site.renderer import create_template_environment, render_plan


class FakeTranslationService:
    def translate_book(self, book):
        return SummaryTranslations(
            en=book.description,
            es="ES summary",
            fr="FR summary",
            de="DE summary",
        )


class FailingTranslationService:
    def translate_book(self, book):
        raise RuntimeError("translation boom")


def test_template_environment_loads_base_template() -> None:
    env = create_template_environment()

    assert env.get_template("base.html")


def test_render_plan_writes_static_pages(tmp_path: Path) -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), tmp_path)

    render_plan(plan)

    dataset_index = tmp_path / "minimal_books" / "index.html"
    book_index = tmp_path / "minimal_books" / "books" / "sample-book" / "index.html"
    section_page = (
        tmp_path
        / "minimal_books"
        / "books"
        / "sample-book"
        / "sections"
        / "sample-section.html"
    )

    assert dataset_index.exists()
    assert book_index.exists()
    assert section_page.exists()
    assert (tmp_path / "minimal_books" / "assets" / "css" / "styles.css").exists()

    assert "Sample Book" in dataset_index.read_text(encoding="utf-8")
    assert "A short sample description." in book_index.read_text(encoding="utf-8")
    assert "Open original BrightLearn section" in section_page.read_text(encoding="utf-8")


def test_render_sample_dataset_creates_all_book_and_section_pages(tmp_path: Path) -> None:
    data = load_json_file(Path("data/samples/brightlearn_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("data/samples/brightlearn_books.json"), tmp_path)

    render_plan(plan)

    assert (tmp_path / "brightlearn_books" / "index.html").exists()
    assert len(plan.book_pages) == 5
    for book_page in plan.book_pages:
        assert book_page.output_path.exists()
        for section_page in book_page.section_pages:
            assert section_page.output_path.exists()


def test_render_book_page_embeds_translation_ui(tmp_path: Path) -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), tmp_path)

    render_plan(plan, translation_service=FakeTranslationService())

    book_index = tmp_path / "minimal_books" / "books" / "sample-book" / "index.html"
    html = book_index.read_text(encoding="utf-8")

    assert 'data-language="en"' in html
    assert 'data-language="es"' in html
    assert 'img/flags/en.svg' in html
    assert 'img/flags/es.svg' in html
    assert 'img/flags/fr.svg' in html
    assert 'img/flags/de.svg' in html
    assert 'data-summary-es="ES summary"' in html
    assert 'data-summary-fr="FR summary"' in html
    assert 'data-summary-de="DE summary"' in html


def test_render_book_page_falls_back_to_english_translation_note(tmp_path: Path) -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), tmp_path)

    render_plan(plan)

    book_index = tmp_path / "minimal_books" / "books" / "sample-book" / "index.html"
    html = book_index.read_text(encoding="utf-8")

    assert "Translations are unavailable. Showing the English summary." in html
    assert "A short sample description." in html


def test_render_sidebar_groups_outline_by_chapter_without_duplicate_numbering(
    tmp_path: Path,
) -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), tmp_path)

    render_plan(plan)

    book_index = tmp_path / "minimal_books" / "books" / "sample-book" / "index.html"
    html = book_index.read_text(encoding="utf-8")

    assert re.search(r'<details\s+class="sidebar-book"\s+open\b', html)
    assert "sidebar-outline" in html
    assert "Book overview" in html
    assert "Chapter 1: Sample Chapter" in html
    assert "Sample Section" in html
    assert "1. Sample Section" not in html


def test_render_plan_keeps_existing_output_if_render_fails(tmp_path: Path) -> None:
    data = load_json_file(Path("tests/fixtures/minimal_books.json"))
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, Path("tests/fixtures/minimal_books.json"), tmp_path)

    render_plan(plan)
    dataset_index = tmp_path / "minimal_books" / "index.html"
    original_html = dataset_index.read_text(encoding="utf-8")

    with pytest.raises(RuntimeError):
        render_plan(plan, translation_service=FailingTranslationService())

    assert dataset_index.exists()
    assert dataset_index.read_text(encoding="utf-8") == original_html
    assert not list(tmp_path.glob(".minimal_books.tmp-*"))
