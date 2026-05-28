# Implementation Plan: Batch Processing

## Related Spec

`docs/specs/003-batch-processing.md`

## Overview

Implement watcher mode for `batch-process/` so compatible JSON files are processed through the same validation, translation, and rendering pipeline used by direct CLI rendering.

## Files to Inspect

- `src/brightlearn_site/cli.py`
- `src/brightlearn_site/batch/`
- `src/brightlearn_site/site/`
- `src/brightlearn_site/translation/`
- `src/brightlearn_site/logging_config.py`
- `.gitignore`

## Files to Create

- Batch tests as needed.
- Small watcher fixtures if useful.

## Files to Modify

- `src/brightlearn_site/batch/file_state.py`
- `src/brightlearn_site/batch/processor.py`
- `src/brightlearn_site/batch/watcher.py`
- `src/brightlearn_site/cli.py`
- Relevant tests.

## Data Model Changes

No domain model changes expected.

## API Changes

Add working CLI behavior for:

```bash
python -m brightlearn_site watch
```

Optional CLI arguments may include:

- `--input-dir`
- `--output-dir`

## Business Logic Flow

1. Configure logging.
2. Ensure `batch-process/` and `rendered/` exist.
3. Scan existing compatible JSON files.
4. For each candidate file, wait for file stability.
5. Process the file through the render pipeline.
6. Watch for create/modify events.
7. Reprocess changed compatible JSON files after stability checks.
8. Log success or failure per file.

## Error Handling

- Malformed JSON should log a validation failure.
- One failed file should not stop the watcher.
- Partial copy should not start processing until stable.
- Unsupported files should be ignored.

## Security Considerations

- Do not recursively process unrelated directories.
- Do not use filenames directly as output paths without safe stem handling.
- Do not log secrets or full input payloads.

## Test Strategy

- Unit tests for file stability checks.
- Processor tests with valid and invalid JSON fixtures.
- Tests for ignored unsupported files.
- Tests that output goes to `rendered/<source-file-stem>/`.

## Step-by-step Implementation Plan

1. Implement file filtering and stability checks.
2. Implement single-file batch processor.
3. Wire processor to existing render pipeline.
4. Implement startup scan.
5. Implement watchdog event handling.
6. Wire CLI watch command.
7. Add tests and manual batch checklist.

## Risks

- Watchdog behavior may differ across operating systems.
- Slow file copies can trigger premature processing.
- Reprocessing strategy may need atomic output handling.

## Open Questions

- Whether to archive completed files.
- Whether to create sidecar status files for failures.
- Exact atomic rebuild behavior.
