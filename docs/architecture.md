# Architecture

## Architecture Overview

The project is a local static site generator with a batch-processing mode. It is not a server-first web application. The core architecture is a pipeline:

1. Load JSON from disk.
2. Validate and normalize it into internal models.
3. Translate book summaries through a remote LLM service with cache and retry handling.
4. Plan static output paths.
5. Render Jinja2 templates into static HTML.
6. Copy static CSS, JavaScript, and bundled assets.
7. Provide a watcher mode for `batch-process/` and repeat the pipeline for future JSON files.

The generated output should be self-contained static HTML, CSS, and JavaScript under `rendered/<source-file-stem>/`, except for remote BrightLearn images referenced by URL. Generated pages should be directly viewable in a local browser without requiring the Python application or a running web server.

## Main Modules

### Repository Root

Responsibility:

- Hold project-level documentation, package configuration, sample inputs, runtime folders, and source package.

What belongs there:

- `README.md`, `AGENTS.md`, `pyproject.toml`, `requirements.txt`, `.env.example`, `.gitignore`.
- Original requirement files, including `Instructions.txt` and `Test_Project_scope.docx`.

What should not belong there:

- Application implementation files outside `src/brightlearn_site`.
- Generated logs or rendered output beyond `.gitkeep` placeholders.
- Real secrets or `.env` files.

### `data/samples/`

Responsibility:

- Store stable sample input files used by documentation, local testing, and development.

What belongs there:

- Cleanly named sample BrightLearn JSON files.

What should not belong there:

- Runtime batch drops.
- Generated output.
- Secret data.

### `batch-process/`

Responsibility:

- Runtime input folder watched for future compatible `.json` files.

What belongs there:

- User-dropped JSON files during local operation.
- `.gitkeep` as a version-control placeholder.

What should not belong there:

- Source code.
- Generated HTML.
- Long-lived secrets.

### `rendered/`

Responsibility:

- Runtime output folder for generated static websites and translation cache.

What belongs there:

- Generated static site folders.
- Generated static assets.
- Translation cache such as `rendered/.cache/translations.json`.
- `.gitkeep` as a version-control placeholder.

What should not belong there:

- Source templates.
- Canonical sample data.
- Files that must be reviewed as source artifacts.

### `logs/`

Responsibility:

- Runtime logging destination.

What belongs there:

- Local operational logs.
- `.gitkeep` as a version-control placeholder.

What should not belong there:

- Secrets.
- Sensitive input payload dumps.
- Committed log files.

### `src/brightlearn_site/cli.py`

Responsibility:

- Own command-line parsing and dispatch.

What belongs there:

- Subcommands such as `validate`, `render`, and `watch`.
- Argument parsing.
- Wiring from CLI inputs to service functions.

What should not belong there:

- Rendering logic.
- Translation logic.
- JSON schema rules beyond argument validation.
- Direct business logic that belongs in services.

### `src/brightlearn_site/settings.py`

Responsibility:

- Load configuration from environment variables with explicit defaults.

What belongs there:

- Dataclass or typed settings objects.
- Environment variable names.
- Non-secret defaults.

What should not belong there:

- Hardcoded API keys.
- Provider-specific request logic.
- Runtime mutation of global behavior.

### `src/brightlearn_site/logging_config.py`

Responsibility:

- Configure console and file logging consistently.

What belongs there:

- Logging format.
- Log file path setup.
- Log levels.

What should not belong there:

- Business event decisions that belong near the operation being logged.
- Secret filtering based on hardcoded token values.

### `src/brightlearn_site/paths.py`

Responsibility:

- Define package-relative paths and shared path helpers.

What belongs there:

- `PROJECT_ROOT`, `PACKAGE_ROOT`, `TEMPLATE_DIR`, `STATIC_DIR`.
- Reusable cross-platform path helpers if needed.

What should not belong there:

- Rendering decisions.
- Batch processing policy.

### `src/brightlearn_site/exceptions.py`

Responsibility:

- Define shared project exceptions.

What belongs there:

- Base project exception classes.
- Cross-module exception types.

What should not belong there:

- Provider-specific translation exceptions, which belong in `translation/exceptions.py`.

### `src/brightlearn_site/models.py`

Responsibility:

- Define typed internal data models for normalized BrightLearn data and translation bundles.

What belongs there:

- Pydantic models for dataset, book, author, chapter, section, and translations.

What should not belong there:

- File I/O.
- HTTP calls.
- Template rendering.
- CLI parsing.

### `src/brightlearn_site/loader.py`

Responsibility:

- Read JSON files from disk.

What belongs there:

- UTF-8 JSON loading.
- Basic file and JSON parsing errors.

What should not belong there:

- Business validation beyond confirming the top-level JSON shape.
- Rendering.
- Translation.

### `src/brightlearn_site/validator.py`

Responsibility:

- Validate raw input data against the expected BrightLearn schema.

What belongs there:

- Pydantic validation entry points.
- Clear validation errors for missing or invalid fields.

What should not belong there:

- Filesystem reading.
- Output path planning.
- LLM calls.

### `src/brightlearn_site/normalizer.py`

Responsibility:

- Convert validated raw data into the internal shape expected by renderer and services.

What belongs there:

- Normalization rules for optional values, defaults, and schema compatibility.

What should not belong there:

- Template logic.
- Remote API calls.
- Runtime folder watching.

### `src/brightlearn_site/slugify.py`

Responsibility:

- Generate filesystem-safe, deterministic slugs.

What belongs there:

- Slug normalization.
- Windows reserved-name handling.
- Length limits.
- Duplicate-safe helper functions when implemented.

What should not belong there:

- Rendering.
- HTML title formatting.
- Dataset validation.

### `src/brightlearn_site/site/`

Responsibility:

- Plan and render static website output.

What belongs there:

- Render planning.
- Jinja2 environment setup.
- Static asset copying.
- Relative URL helpers.
- HTML file writing.

What should not belong there:

- Remote LLM HTTP logic.
- File watching.
- Raw JSON parsing.
- Provider-specific configuration.

### `src/brightlearn_site/translation/`

Responsibility:

- Translate book summaries through a remote LLM API.

What belongs there:

- Provider client.
- Prompt templates.
- Strict JSON response parsing.
- JSON repair.
- Retry/backoff policies.
- Translation caching.
- Translation-specific exceptions.

What should not belong there:

- Full site rendering.
- Batch watcher file event handling.
- Template-specific UI behavior.

### `src/brightlearn_site/batch/`

Responsibility:

- Process future JSON drops from `batch-process/`.

What belongs there:

- Watchdog integration.
- File stability checks.
- Per-file processing orchestration.
- Duplicate-processing prevention.

What should not belong there:

- Low-level template rendering details.
- LLM provider-specific request bodies.
- Schema definitions.

### `src/brightlearn_site/templates/`

Responsibility:

- Define Jinja2 templates for generated HTML.

What belongs there:

- `base.html`, dataset index, book index, section page, partials, error templates.
- Presentation markup and simple template conditionals.

What should not belong there:

- Complex business logic.
- LLM prompt text.
- Filesystem path computation.

### `src/brightlearn_site/static/`

Responsibility:

- Store bundled static assets copied into generated output.

What belongs there:

- CSS, JavaScript, favicon, and other static assets.

What should not belong there:

- Generated output.
- Downloaded remote book covers.
- Python implementation code.

### `tests/`

Responsibility:

- Verify behavior through unit and integration tests.

What belongs there:

- Pytest test files.
- Small JSON fixtures.
- HTML output assertions.

What should not belong there:

- Large generated site outputs.
- Secrets.
- Production-only runtime logs.

## Data Flow

Expected render flow:

```text
CLI or batch watcher
  -> loader.load_json_file
  -> validator.validate_dataset
  -> normalizer.normalize_dataset
  -> translation.service translate descriptions, using cache/client/parser/retry
  -> site.planner create output targets and URLs
  -> site.renderer render Jinja templates
  -> site.asset_copier copy CSS/JS/favicon
  -> rendered/<source-file-stem> static output
```

Expected batch flow:

```text
watchdog file event
  -> batch.file_state wait until JSON file is stable
  -> batch.processor run validation, translation, and rendering pipeline
  -> logs/app.log record success or failure
```

Expected browser flow:

```text
User opens rendered/<source-file-stem>/index.html
  -> static HTML loads local CSS/JS
  -> remote cover images load from BrightLearn URLs
  -> flag controls switch between embedded summary translations
```

## Initial Output Decisions

- Every input JSON renders into `rendered/<source-file-stem>/`.
- The sample file `data/samples/brightlearn_books.json` renders into `rendered/brightlearn_books/`.
- A batch file such as `batch-process/new_books.json` renders into `rendered/new_books/`.
- Reprocessing should produce clean deterministic output. The renderer writes to a staging folder and replaces the final output folder only after rendering succeeds, so an interrupted or failed render leaves the previous output intact.
- Section pages should be generated for every section in the table of contents. Because the current JSON includes section titles and source URLs but not section body text, generated section pages should include book/chapter/section context, local navigation, and a link to the original BrightLearn URL.

## Initial Translation Decisions

- Translation is required only for `Book.description`.
- Required translation keys are `es`, `fr`, and `de`.
- LLM responses must validate to the strict translation shape before use.
- Extra LLM prose is not accepted unless the JSON repair step can extract and validate a correct JSON object.
- Translation cache keys should include at least provider, model, source language, target languages, book title, and a stable hash of the original description.
- If translation fails after configured retries and repair attempts, rendering should continue with the English summary and log the fallback.

## Initial Batch Decisions

- Watcher mode is a required capability, though it only runs when the user invokes the watch command.
- On startup, watcher mode should scan existing compatible `.json` files in `batch-process/` and process files that have not already been processed for their current content.
- While running, watcher mode should process new or changed compatible `.json` files after file stability checks pass.
- Failed files should be logged clearly. Quarantine/archive behavior is TBD and should not be invented without a spec update.

## Layering Rules

- CLI code should parse arguments and call orchestration functions. It should not contain rendering, validation, translation, or batch business logic.
- Loader code should only read input data. It should not validate domain rules or mutate output folders.
- Validator and normalizer code should prepare trusted internal models. They should not perform I/O other than what is explicitly required by validation.
- Translation code should only translate summaries and return validated translation bundles. It should not render templates or write HTML pages.
- Site rendering code should consume normalized data and translation results. It should not call the LLM directly.
- Batch code should orchestrate the same pipeline used by CLI rendering. It should not duplicate renderer or translator internals.
- Templates should receive already-prepared data. Avoid complex data transformations in Jinja.
- Static JavaScript should handle browser interactions only. It should not be required for core page generation.
- Static JavaScript may be used for summary language switching, but the page must still show a readable English summary without JavaScript.

## Dependency Rules

- `cli.py` may depend on settings, logging, loader, validator, normalizer, site, translation, and batch orchestration.
- `loader.py` should depend only on the standard library and shared exceptions where needed.
- `validator.py` and `normalizer.py` may depend on `models.py`.
- `models.py` should not depend on CLI, site rendering, translation clients, or batch watchers.
- `site/` may depend on models, paths, slug helpers, and Jinja2.
- `translation/` may depend on settings, models, httpx, and translation-specific utilities.
- `batch/` may depend on loader, validator, normalizer, translation service, site renderer, logging, and watchdog.
- Shared utilities must remain generic. If a helper becomes domain-specific, place it in the owning module.

## Configuration Strategy

- Runtime configuration must come from environment variables, `.env` loaded locally, or explicit CLI arguments.
- `.env.example` may contain placeholder values only.
- `.env` must not be committed.
- No API keys, tokens, or secrets may be hardcoded.
- Defaults should be explicit and safe for local development.
- Provider-specific LLM settings should be isolated behind translation configuration.
- Output paths should be configurable where useful, but defaults should remain `batch-process/`, `rendered/`, and `logs/`.
- Use `pathlib.Path` for filesystem config values.

## Error Handling Strategy

### Validation Errors

- Invalid JSON or schema errors should produce actionable messages.
- Validation failures for one batch file should not stop the watcher.
- Tests should cover required fields and malformed structures.

### Business Errors

- Duplicate titles, unsafe filenames, missing optional fields, and empty values should be handled deterministically where possible.
- If rendering cannot continue safely, fail with a clear project exception.

### External API Errors

- LLM errors should distinguish rate limits, retryable transient errors, invalid responses, and non-retryable failures.
- HTTP 429 must trigger backoff.
- Timeouts and disconnects should be retried within the configured retry budget.
- If translation ultimately fails, render English summaries and log the failure.

### Unexpected System Errors

- Unexpected exceptions should be logged with context.
- Do not swallow exceptions silently.
- Avoid dumping full input files or secrets into logs.

## External Integrations

- BrightLearn remote image URLs: generated pages load cover images directly from URLs in the JSON.
- Remote LLM API: required for summary translations. Provider and final model are TBD, though `.env.example` currently uses OpenAI-oriented placeholders.
- GitHub public repository: required for final submission and review.
- Database: none defined.
- Payment provider: not applicable.
- Authentication provider: not required by current specs.

## Architecture Rules for AI Agents

- Do not change architecture without updating this document.
- Do not introduce new layers without justification.
- Do not move files across modules without explaining why.
- Do not introduce new dependencies without documenting the reason.
- Do not refactor unrelated modules during feature work.
- Prefer small, incremental changes.
- Keep implementation aligned with the feature spec and implementation plan.
- Keep filesystem paths cross-platform with `pathlib.Path`.
- Keep generated output out of Git unless a future spec explicitly says otherwise.
- Do not weaken validation or translation safety to make implementation faster.

## Open Architecture Questions

- Should translation cache be global under `rendered/.cache/` or scoped per input dataset?
- Should render planning produce a complete manifest file for testability and debugging?
- Should watcher processing move completed files to an archive folder, or leave them in `batch-process/`?
- Should failed batch files be marked with sidecar status files?
- Which LLM provider abstraction is sufficient without overengineering multiple providers?
