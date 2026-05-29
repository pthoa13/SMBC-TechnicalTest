# Feature 003: Batch Processing

## Goal

Process compatible BrightLearn JSON files placed in `batch-process/` and render each dataset into `rendered/<source-file-stem>/` using the same output format as the sample renderer.

## User Stories

- As a local operator, I can drop a compatible JSON file into `batch-process/` and have it rendered automatically.
- As an SMBC reviewer, I can verify this is a reusable pipeline rather than a one-time conversion.
- As a developer, I can inspect logs to understand why a batch file succeeded or failed.

## Functional Requirements

- Create and use the local `batch-process/` folder.
- Watch for compatible `.json` files.
- Scan existing compatible files at watcher startup.
- Wait until a file is stable before processing it.
- Process new or changed compatible JSON files.
- Render each file into `rendered/<source-file-stem>/`.
- Reuse the same validation, normalization, translation, and rendering pipeline as direct rendering.
- Log success and failure per file.
- Do not crash the watcher because one file fails.

## Non-functional Requirements

- Batch paths must be cross-platform.
- Reprocessing should be deterministic.
- The watcher should avoid repeated processing while a file is still being copied.
- Runtime batch files and generated output should not be committed.

## Acceptance Criteria

- A compatible JSON file copied into `batch-process/` renders into `rendered/<source-file-stem>/`.
- Existing compatible files are detected when watcher mode starts.
- Malformed JSON produces a logged error without stopping the watcher.
- A partially copied file is not processed until stable.
- Reprocessing the same file does not create inconsistent duplicate output.

## Edge Cases

- File is copied slowly.
- File is modified after first processing.
- File has spaces or parentheses in the filename.
- File stem collides with a previous rendered output folder.
- File is not JSON.
- JSON schema does not match expected BrightLearn fields.

## Out of Scope

- Hosted upload UI.
- Database-backed job queue.
- Archiving or quarantining completed/failed files unless a future spec adds that behavior.
- Processing unrelated schemas.

## Dependencies

- `watchdog`
- Static renderer from Feature 001
- Translation workflow from Feature 002, with English fallback if translation is unavailable

## Open Questions

- Should completed files remain in `batch-process/` or be moved later?
- Should failed files get sidecar status files?
