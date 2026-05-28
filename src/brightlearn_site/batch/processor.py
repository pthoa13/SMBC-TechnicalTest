"""Single-file batch processing for BrightLearn JSON inputs."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from brightlearn_site.batch.file_state import is_supported_batch_file
from brightlearn_site.exceptions import BrightLearnError
from brightlearn_site.loader import load_json_file
from brightlearn_site.normalizer import normalize_dataset
from brightlearn_site.site.planner import build_render_plan, output_root_for_input
from brightlearn_site.site.renderer import render_plan
from brightlearn_site.translation.service import EnglishOnlyTranslationService, TranslationService

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class BatchProcessResult:
    input_path: Path
    output_root: Path | None
    success: bool
    message: str
    skipped: bool = False
    error_type: str | None = None


def process_batch_file(
    input_path: Path,
    output_dir: Path,
    *,
    translation_service: TranslationService | None = None,
) -> BatchProcessResult:
    """Process one batch JSON file through the shared static render pipeline."""
    if not is_supported_batch_file(input_path):
        message = "Ignored unsupported batch file."
        LOGGER.info("%s file=%s", message, input_path.name)
        return BatchProcessResult(
            input_path=input_path,
            output_root=None,
            success=False,
            skipped=True,
            message=message,
        )

    output_root = output_root_for_input(input_path, output_dir)
    LOGGER.info("Batch processing started. file=%s output=%s", input_path.name, output_root)

    try:
        data = load_json_file(input_path)
        dataset = normalize_dataset(data)
        plan = build_render_plan(dataset, input_path, output_dir)
        render_plan(
            plan,
            translation_service=translation_service or EnglishOnlyTranslationService(),
        )
    except (OSError, json.JSONDecodeError, TypeError, ValidationError, BrightLearnError) as error:
        message = "Batch processing failed."
        LOGGER.error("%s file=%s error=%s", message, input_path.name, error)
        return BatchProcessResult(
            input_path=input_path,
            output_root=output_root,
            success=False,
            message=str(error),
            error_type=type(error).__name__,
        )

    message = "Batch processing succeeded."
    LOGGER.info("%s file=%s output=%s", message, input_path.name, output_root)
    return BatchProcessResult(
        input_path=input_path,
        output_root=output_root,
        success=True,
        message=message,
    )
