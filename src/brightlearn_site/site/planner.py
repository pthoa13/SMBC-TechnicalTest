"""Render plan generation for static site output."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from brightlearn_site.models import Book, BookDataset, Chapter, Section
from brightlearn_site.slugify import slugify_file_stem, unique_slug


@dataclass(frozen=True)
class RenderTarget:
    template_name: str
    output_path: Path
    context: dict[str, object]


@dataclass(frozen=True)
class SectionPage:
    book: Book
    chapter: Chapter
    section: Section
    slug: str
    output_path: Path
    source_url: str
    page_number: int


@dataclass(frozen=True)
class BookPage:
    book: Book
    slug: str
    output_path: Path
    section_pages: list[SectionPage]


@dataclass(frozen=True)
class RenderPlan:
    output_root: Path
    targets: list[RenderTarget]
    book_pages: list[BookPage]


def output_root_for_input(input_path: Path, output_dir: Path) -> Path:
    return output_dir / slugify_file_stem(input_path.stem, fallback="dataset")


def build_render_plan(dataset: BookDataset, input_path: Path, output_dir: Path) -> RenderPlan:
    output_root = output_root_for_input(input_path, output_dir)
    dataset_index = output_root / "index.html"

    book_pages = _build_book_pages(dataset, output_root)
    targets: list[RenderTarget] = [
        RenderTarget(
            template_name="dataset_index.html",
            output_path=dataset_index,
            context={
                "dataset": dataset,
                "dataset_title": dataset.source or "BrightLearn Books",
                "book_pages": book_pages,
            },
        )
    ]

    for book_page in book_pages:
        targets.append(
            RenderTarget(
                template_name="book_index.html",
                output_path=book_page.output_path,
                context={"book_page": book_page, "book": book_page.book},
            )
        )
        for section_page in book_page.section_pages:
            targets.append(
                RenderTarget(
                    template_name="section.html",
                    output_path=section_page.output_path,
                    context={
                        "section_page": section_page,
                        "book_page": book_page,
                        "book": book_page.book,
                        "chapter": section_page.chapter,
                        "section": section_page.section,
                    },
                )
            )

    return RenderPlan(output_root=output_root, targets=targets, book_pages=book_pages)


def _build_book_pages(dataset: BookDataset, output_root: Path) -> list[BookPage]:
    used_book_slugs: set[str] = set()
    book_pages: list[BookPage] = []

    for book in dataset.books:
        book_slug = unique_slug(book.book_title, used_book_slugs, fallback="book")
        book_output = output_root / "books" / book_slug / "index.html"
        section_pages = _build_section_pages(book, book_output.parent)
        book_pages.append(
            BookPage(
                book=book,
                slug=book_slug,
                output_path=book_output,
                section_pages=section_pages,
            )
        )

    return book_pages


def _build_section_pages(book: Book, book_dir: Path) -> list[SectionPage]:
    used_section_slugs: set[str] = set()
    section_pages: list[SectionPage] = []
    page_number = 1

    for chapter in book.table_of_contents:
        for section in chapter.sections:
            section_slug = unique_slug(section.title, used_section_slugs, fallback="section")
            section_pages.append(
                SectionPage(
                    book=book,
                    chapter=chapter,
                    section=section,
                    slug=section_slug,
                    output_path=book_dir / "sections" / f"{section_slug}.html",
                    source_url=str(section.url),
                    page_number=page_number,
                )
            )
            page_number += 1

    return section_pages
