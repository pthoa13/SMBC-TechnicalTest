# Implementation Report: Batch Processing

## Related Spec

`docs/specs/003-batch-processing.md`

## Related Plan

`docs/plans/003-batch-processing-plan.md`

## Related Tasks

`docs/tasks/003-batch-processing-tasks.md`

## Summary

Implemented batch processing for BrightLearn JSON files placed in `batch-process/`.
Batch mode now scans existing JSON files on startup, watches for new or changed JSON files,
waits for file stability, and renders each compatible dataset into
`rendered/<source-file-stem>/` using the existing renderer and translation pipeline.

Translation was skipped during watcher validation with `--skip-translations` to avoid accidental
batch API calls. Direct render validation for Spec 002 later confirmed real OpenAI-compatible
translations and cache behavior.

## What Changed

- Added batch file filtering and stability checks.
- Added a single-file batch processor that reuses the direct render pipeline.
- Added watcher mode backed by `watchdog`.
- Added CLI support for `python -m brightlearn_site watch`.
- Added `--skip-translations` support for watcher mode to avoid accidental API calls during local
  smoke tests.
- Added batch-focused tests for filtering, file stability, rendering, malformed input handling,
  unsupported schema handling, startup scan behavior, and duplicate unchanged file events.
- Batch processing now benefits from the shared atomic static renderer, which stages output before
  replacing the final rendered folder.

## Files Changed

- `src/brightlearn_site/batch/file_state.py`
- `src/brightlearn_site/batch/processor.py`
- `src/brightlearn_site/batch/watcher.py`
- `src/brightlearn_site/cli.py`
- `tests/test_batch_processor.py`
- `tests/test_cli.py`
- `docs/reports/003-batch-processing-implementation-report.md`

## Requirement Coverage

| Requirement | Status | Notes |
|---|---|---|
| Create and use `batch-process/` | Covered | Watch command ensures the input directory exists. |
| Watch compatible `.json` files | Covered | `watchdog` observes the configured input directory non-recursively. |
| Scan existing files at startup | Covered | `process_existing_files()` processes supported direct-child JSON files before watching. |
| Wait until file is stable | Covered | Stability checks compare file size and modified timestamp before processing. |
| Process new or changed JSON files | Covered | Created, modified, and moved-in files are handled. |
| Render into `rendered/<source-file-stem>/` | Covered | Processor uses the same `output_root_for_input()` planning logic as direct render. |
| Reuse validation, normalization, translation, and rendering | Covered | Processor calls existing loader, normalizer, render planner, and atomic renderer. |
| Log success and failure per file | Covered | Batch processor and watcher log detection, start, success, failure, ignored files, and shutdown. |
| Malformed file does not crash watcher | Covered | Processor returns a failure result and logs the error instead of raising to the watcher. |
| Avoid repeated processing while unchanged | Covered | Watch handler skips duplicate events for the same stable file snapshot. |
| Cross-platform paths | Covered | Batch code uses `pathlib.Path`; Windows behavior was not executed on Windows. |

## Tests Added or Updated

- Added `tests/test_batch_processor.py` coverage for:
  - supported JSON files
  - hidden and temporary files
  - unsupported extensions
  - non-recursive startup scan
  - stable and changing file snapshots
  - valid fixture rendering
  - malformed JSON failure
  - unsupported schema failure
  - ignored unsupported candidate files
  - unchanged snapshot event de-duplication
- Updated `tests/test_cli.py` to verify watcher CLI wiring with `--skip-translations`.

## Validation Commands

```bash
PYTHONPATH=src python3 -m pytest tests/test_batch_processor.py
PYTHONPATH=src python3 -m pytest tests/test_batch_processor.py tests/test_cli.py
PYTHONPATH=src python3 -m pytest
PYTHONPATH=src ruff check .
python3 -m compileall src tests
PYTHONPATH=src .venv/bin/python -m brightlearn_site watch --skip-translations --input-dir batch-process --output-dir rendered
cp data/samples/brightlearn_books.json batch-process/final_smoke_books.json
test -f rendered/final_smoke_books/index.html
```

## Validation Results

- Targeted batch tests: passed.
- Batch + CLI tests: passed.
- Full test suite: `64 passed`.
- Ruff: `All checks passed!`.
- Compileall: completed successfully for `src` and `tests`.
- Manual watcher smoke test:
  - Watcher started successfully.
  - Copying `data/samples/brightlearn_books.json` into `batch-process/final_smoke_books.json`
    created `rendered/final_smoke_books/index.html`.
  - Duplicate unchanged filesystem event was logged and ignored.
  - Watcher shut down cleanly with `Ctrl+C`.

## Known Limitations

- Windows was not available for runtime validation; path handling uses `pathlib` and existing
  slugification rules designed for Windows-safe names.
- No archive or quarantine folder is implemented.
- No sidecar status file is written for completed or failed files.
- Static output rebuilds now use a staging folder before replacing the final output folder.
- Watchdog event timing can vary by operating system and filesystem.

## Follow-up Tasks

- Clarify whether completed or failed batch files should remain in `batch-process/`.
- Clarify whether future specs should add sidecar status files.
- Run watcher smoke validation on Windows if cross-platform runtime proof is required.

## Out of Scope

- Hosted upload UI.
- Database-backed job queue.
- Archive or quarantine workflow.
- Sidecar status files.
- Processing schemas other than the BrightLearn book JSON schema.
- Fetching or translating full section content.
