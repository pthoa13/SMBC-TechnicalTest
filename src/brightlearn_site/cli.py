"""Command-line interface for the BrightLearn site generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from brightlearn_site.batch.watcher import run_watch
from brightlearn_site.loader import load_json_file
from brightlearn_site.logging_config import configure_logging
from brightlearn_site.normalizer import normalize_dataset
from brightlearn_site.settings import load_settings
from brightlearn_site.site.planner import build_render_plan, output_root_for_input
from brightlearn_site.site.renderer import render_plan
from brightlearn_site.translation.service import (
    EnglishOnlyTranslationService,
    SummaryTranslationService,
)
from brightlearn_site.validator import validate_dataset


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brightlearn-site",
        description="Render BrightLearn book JSON into a static website.",
    )
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="Validate a BrightLearn JSON file.")
    validate.add_argument("input_json")

    render = subparsers.add_parser("render", help="Render a BrightLearn JSON file.")
    render.add_argument("input_json")
    render.add_argument("--output-dir", default="rendered")
    render.add_argument(
        "--skip-translations",
        action="store_true",
        help="Render English summaries only without calling the remote LLM.",
    )

    watch = subparsers.add_parser("watch", help="Watch batch-process for JSON files.")
    watch.add_argument("--input-dir", default="batch-process")
    watch.add_argument("--output-dir", default="rendered")
    watch.add_argument(
        "--skip-translations",
        action="store_true",
        help="Render English summaries only without calling the remote LLM.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "validate":
            return _validate_command(Path(args.input_json))
        if args.command == "render":
            return _render_command(
                Path(args.input_json),
                Path(args.output_dir),
                skip_translations=args.skip_translations,
            )
        if args.command == "watch":
            return _watch_command(
                Path(args.input_dir),
                Path(args.output_dir),
                skip_translations=args.skip_translations,
            )
    except (OSError, json.JSONDecodeError, TypeError, ValidationError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2


def _validate_command(input_path: Path) -> int:
    data = load_json_file(input_path)
    dataset = validate_dataset(data)
    print(f"Valid BrightLearn dataset: {len(dataset.books)} books")
    return 0


def _render_command(input_path: Path, output_dir: Path, *, skip_translations: bool) -> int:
    data = load_json_file(input_path)
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, input_path, output_dir)
    settings = load_settings()
    translation_service = _translation_service(settings, skip_translations=skip_translations)
    render_plan(plan, translation_service=translation_service)
    print(f"Rendered {len(dataset.books)} books to {output_root_for_input(input_path, output_dir)}")
    return 0


def _watch_command(input_dir: Path, output_dir: Path, *, skip_translations: bool) -> int:
    configure_logging()
    settings = load_settings()
    translation_service = _translation_service(settings, skip_translations=skip_translations)
    return run_watch(input_dir, output_dir, translation_service=translation_service)


def _translation_service(settings, *, skip_translations: bool):
    if skip_translations:
        return EnglishOnlyTranslationService()
    if not settings.llm_api_key:
        print(
            "LLM_API_KEY is not configured; rendering English summaries only.",
            file=sys.stderr,
        )
        return EnglishOnlyTranslationService()
    return SummaryTranslationService(settings=settings)
