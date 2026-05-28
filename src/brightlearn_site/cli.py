"""Command-line interface for the BrightLearn site generator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pydantic import ValidationError

from brightlearn_site.loader import load_json_file
from brightlearn_site.normalizer import normalize_dataset
from brightlearn_site.site.planner import build_render_plan, output_root_for_input
from brightlearn_site.site.renderer import render_plan
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

    watch = subparsers.add_parser("watch", help="Watch batch-process for JSON files.")
    watch.add_argument("--input-dir", default="batch-process")
    watch.add_argument("--output-dir", default="rendered")

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
            return _render_command(Path(args.input_json), Path(args.output_dir))
        if args.command == "watch":
            print("Batch watcher is part of Spec 003 and is not implemented yet.", file=sys.stderr)
            return 2
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


def _render_command(input_path: Path, output_dir: Path) -> int:
    data = load_json_file(input_path)
    dataset = normalize_dataset(data)
    plan = build_render_plan(dataset, input_path, output_dir)
    render_plan(plan)
    print(f"Rendered {len(dataset.books)} books to {output_root_for_input(input_path, output_dir)}")
    return 0
