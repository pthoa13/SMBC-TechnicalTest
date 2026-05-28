# ADR-001: Initial Architecture

## Status

Accepted

## Date

2026-05-28

## Context

This project starts from existing SMBC technical test specifications, an initial folder structure, and `AGENTS.md`. The implementation will be AI-assisted, so the project needs clear module boundaries, quality rules, and documentation governance before application code expands.

The core requirement is to transform BrightLearn book JSON into a browsable static website with LLM-powered summary translations. The project must also support future JSON drops through a local batch-processing folder. The output should be static HTML, not a server-dependent application.

## Decision

The project will use a modular Python 3.12 static site generator architecture under `src/brightlearn_site`.

Main structure:

- `cli.py` for command-line entry points.
- `settings.py` for environment-driven configuration.
- `logging_config.py` for logging setup.
- `models.py` for typed domain models.
- `loader.py`, `validator.py`, and `normalizer.py` for input handling.
- `slugify.py` for cross-platform safe output names.
- `site/` for render planning, Jinja2 rendering, static asset copying, and generated URL helpers.
- `translation/` for LLM prompt, client, response parsing, JSON repair, retry handling, cache, and translation service.
- `batch/` for folder watching, file stability checks, and batch orchestration.
- `templates/` and `static/` for generated site presentation.
- `tests/` for pytest-based validation.
- `docs/` for project context, architecture, conventions, QA, security, specs, plans, tasks, reports, and ADRs.

Initial static output decisions:

- Every input JSON renders into `rendered/<source-file-stem>/`.
- The sample dataset renders into `rendered/brightlearn_books/`.
- Generated pages should be directly viewable in a local browser without requiring the Python application or a running web server.
- Section pages are generated from table-of-contents entries. With the current JSON schema, they contain local navigation/context and links to original BrightLearn URLs rather than full local section body text.

Initial batch decisions:

- Watcher mode is a required capability invoked by a command such as `python -m brightlearn_site watch`.
- Watcher mode should scan existing compatible JSON files at startup and process new or changed compatible JSON files while running.
- Archive/quarantine behavior for processed or failed files remains TBD.

Initial translation decisions:

- Only book summaries/descriptions are translated.
- Required target keys are `es`, `fr`, and `de`.
- Cache keys should account for provider, model, source text, book title, and target languages.
- Translation failures should be logged and should fall back to English output after retries are exhausted.

Testing approach:

- Unit tests for isolated logic such as validation, slug generation, translation parsing, JSON repair, retry policy, and cache behavior.
- Integration tests for rendering fixtures into temporary output directories.
- HTML structure tests for generated pages and links.
- Manual browser QA for visual polish, responsive layout, and Brave on Windows.

Documentation and governance approach:

- Feature-level specs belong in `docs/specs/`.
- Implementation plans belong in `docs/plans/`.
- Small task breakdowns belong in `docs/tasks/`.
- Implementation reports belong in `docs/reports/`.
- Architecture changes require updated documentation and, where significant, a new ADR.

AI-assisted development rules:

- Implement from specs and plans rather than ad hoc changes.
- Keep changes small and reviewable.
- Do not modify unrelated modules during feature work.
- Do not add dependencies or architecture layers without documenting why.
- Keep validation, error handling, and security behavior intact.
- Use `pathlib.Path` for filesystem work and preserve cross-platform behavior.

## Consequences

Positive consequences:

- Clearer module boundaries.
- Easier AI-assisted implementation.
- Easier code review and validation.
- Better long-term maintainability.
- Static output remains aligned with the project requirement.
- Translation and rendering can be tested independently.
- Batch processing can reuse the same pipeline as explicit CLI rendering.

Trade-offs:

- More documentation overhead.
- Slower initial setup.
- Requires keeping docs updated as decisions change.
- More files than a single-script implementation.
- Some boundaries may feel formal for a small assessment project, but they reduce risk when using AI-assisted development.

## Alternatives Considered

### Ad-hoc vibe coding without documentation

This would be faster initially but increases the risk of inconsistent implementation, missing requirements, weak validation, and architecture drift. It was not chosen because the project is explicitly intended to guide future AI coding agents.

### Monolithic implementation without layers

A single script could load JSON, call the LLM, and write HTML. This was not chosen because translation retry logic, batch watching, rendering, validation, and path safety would become harder to test and maintain.

### Over-engineered multi-service architecture

A database-backed service, queue worker, and frontend app would be excessive. The requirement is local static generation with batch processing, not a hosted multi-service platform.

### Frontend build pipeline with React

React is allowed by the prompt, but not required. A static HTML, CSS, and minimal JavaScript approach better matches reviewer simplicity and the static-output requirement. This can be revisited only if future specs require richer client behavior.

## Follow-up Actions

- Split the known requirements into feature specs under `docs/specs/`.
- Create implementation plans under `docs/plans/`.
- Break plans into small tasks under `docs/tasks/`.
- Validate and finalize tooling commands after dependencies are installed.
- Implement the static renderer before LLM translation.
- Add translation cache, retry, validation, and fallback behavior.
- Add batch watcher and file stability behavior.
- Update ADRs when architecture changes materially.
