"""Command-line interface placeholders for the BrightLearn site generator."""

from __future__ import annotations

import argparse


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

    raise NotImplementedError(f"Command '{args.command}' will be implemented in the next phase.")
