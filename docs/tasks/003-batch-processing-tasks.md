# Tasks: Batch Processing

## Related Spec

`docs/specs/003-batch-processing.md`

## Related Plan

`docs/plans/003-batch-processing-plan.md`

## Task List

### Task 1: File Filtering and Stability

Goal:
Identify compatible JSON files and wait until they are stable before processing.

Files to inspect:
`batch/file_state.py`, `batch/watcher.py`, `.gitignore`.

Files to modify:
`batch/file_state.py`, tests.

Implementation details:
Ignore unsupported files and avoid recursive processing outside `batch-process/`.

Tests required:
Stable file, changing file size, unsupported extension.

Validation command:
`python -m pytest tests/test_batch_processor.py`

Acceptance criteria:
Partially copied files are not processed too early.

Risk:
Filesystem event timing differs across platforms.

### Task 2: Single-file Batch Processor

Goal:
Process one JSON file through the same pipeline as direct rendering.

Files to inspect:
`batch/processor.py`, `site/`, `translation/`, `cli.py`.

Files to modify:
`batch/processor.py`, tests.

Implementation details:
Output must be `rendered/<source-file-stem>/`.

Tests required:
Valid fixture renders; invalid fixture logs/fails without crashing caller.

Validation command:
`python -m pytest tests/test_batch_processor.py`

Acceptance criteria:
Batch processor reuses the shared renderer path and does not duplicate rendering internals.

Risk:
Processor may accidentally drift from CLI render behavior.

### Task 3: Watch Command

Goal:
Run startup scan and watch for new/changed JSON files.

Files to inspect:
`batch/watcher.py`, `cli.py`, `logging_config.py`.

Files to modify:
`batch/watcher.py`, `cli.py`, tests where practical.

Implementation details:
Watcher mode is a required capability, but it only runs when invoked.

Tests required:
Unit tests for event filtering; manual watcher smoke test.

Validation command:
`python -m brightlearn_site watch`

Acceptance criteria:
Dropping a compatible JSON file renders output and logs success.

Risk:
Long-running command needs careful manual verification and shutdown behavior.
