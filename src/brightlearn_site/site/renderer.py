"""Jinja2 renderer for static pages."""

from __future__ import annotations

import shutil
import uuid
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from brightlearn_site.models import SummaryTranslations
from brightlearn_site.paths import TEMPLATE_DIR
from brightlearn_site.site.asset_copier import copy_static_assets
from brightlearn_site.site.planner import BookPage, RenderPlan, RenderTarget, SectionPage
from brightlearn_site.site.urls import asset_url, relative_url
from brightlearn_site.translation.service import EnglishOnlyTranslationService, TranslationService


def create_template_environment(template_dir: Path = TEMPLATE_DIR) -> Environment:
    return Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_plan(plan: RenderPlan, translation_service: TranslationService | None = None) -> None:
    staging_root = _staging_root_for(plan.output_root)
    if staging_root.exists():
        shutil.rmtree(staging_root)

    try:
        staging_root.mkdir(parents=True, exist_ok=True)
        copy_static_assets(staging_root / "assets")

        translation_service = translation_service or EnglishOnlyTranslationService()
        translations = _build_translation_context(plan, translation_service)
        environment = create_template_environment()
        for target in plan.targets:
            _render_target(environment, plan, target, translations, staging_root)

        if plan.output_root.exists():
            shutil.rmtree(plan.output_root)
        staging_root.replace(plan.output_root)
    except Exception:
        if staging_root.exists():
            shutil.rmtree(staging_root)
        raise


def _render_target(
    environment: Environment,
    plan: RenderPlan,
    target: RenderTarget,
    translations: dict[str, SummaryTranslations],
    staging_root: Path,
) -> None:
    template = environment.get_template(target.template_name)
    context = _base_context(plan, target, translations) | target.context
    staged_output_path = _staged_path(plan.output_root, staging_root, target.output_path)
    staged_output_path.parent.mkdir(parents=True, exist_ok=True)
    staged_output_path.write_text(template.render(context), encoding="utf-8")


def _staging_root_for(output_root: Path) -> Path:
    return output_root.parent / f".{output_root.name}.tmp-{uuid.uuid4().hex}"


def _staged_path(output_root: Path, staging_root: Path, output_path: Path) -> Path:
    return staging_root / output_path.relative_to(output_root)


def _base_context(
    plan: RenderPlan,
    target: RenderTarget,
    translations: dict[str, SummaryTranslations],
) -> dict[str, object]:
    active_translation: SummaryTranslations | None = None
    book_page = target.context.get("book_page")
    if isinstance(book_page, BookPage):
        active_translation = translations[book_page.slug]

    return {
        "asset_base": relative_url(target.output_path, plan.output_root / "assets"),
        "home_url": relative_url(target.output_path, plan.output_root / "index.html"),
        "css_url": asset_url(target.output_path, plan.output_root, "css/styles.css"),
        "js_url": asset_url(target.output_path, plan.output_root, "js/app.js"),
        "favicon_url": asset_url(target.output_path, plan.output_root, "img/favicon.svg"),
        "url_for": lambda path: relative_url(target.output_path, path),
        "breadcrumbs": _breadcrumbs(plan, target),
        "navigation": _navigation(plan, target),
        "summary_translations": active_translation,
        "page_title": _page_title(target),
    }


def _build_translation_context(
    plan: RenderPlan,
    translation_service: TranslationService,
) -> dict[str, SummaryTranslations]:
    return {
        book_page.slug: translation_service.translate_book(book_page.book)
        for book_page in plan.book_pages
    }


def _page_title(target: RenderTarget) -> str:
    if "section_page" in target.context:
        section_page = target.context["section_page"]
        if isinstance(section_page, SectionPage):
            return f"{section_page.section.title} | {section_page.book.book_title}"
    if "book_page" in target.context:
        book_page = target.context["book_page"]
        if isinstance(book_page, BookPage):
            return book_page.book.book_title
    return "BrightLearn Books"


def _breadcrumbs(plan: RenderPlan, target: RenderTarget) -> list[dict[str, str]]:
    crumbs = [
        {
            "label": "All Books",
            "href": relative_url(target.output_path, plan.output_root / "index.html"),
        }
    ]

    book_page = target.context.get("book_page")
    if isinstance(book_page, BookPage):
        crumbs.append(
            {
                "label": book_page.book.book_title,
                "href": relative_url(target.output_path, book_page.output_path),
            }
        )

    section_page = target.context.get("section_page")
    if isinstance(section_page, SectionPage):
        crumbs.append(
            {
                "label": section_page.section.title,
                "href": relative_url(target.output_path, section_page.output_path),
            }
        )

    return crumbs


def _navigation(plan: RenderPlan, target: RenderTarget) -> dict[str, object]:
    active_book = target.context.get("book_page")
    active_section = target.context.get("section_page")
    previous_section: SectionPage | None = None
    next_section: SectionPage | None = None

    if isinstance(active_book, BookPage) and isinstance(active_section, SectionPage):
        sections = active_book.section_pages
        current_index = sections.index(active_section)
        if current_index > 0:
            previous_section = sections[current_index - 1]
        if current_index < len(sections) - 1:
            next_section = sections[current_index + 1]

    return {
        "book_pages": plan.book_pages,
        "active_book": active_book if isinstance(active_book, BookPage) else None,
        "active_section": active_section if isinstance(active_section, SectionPage) else None,
        "previous_section": previous_section,
        "next_section": next_section,
    }
