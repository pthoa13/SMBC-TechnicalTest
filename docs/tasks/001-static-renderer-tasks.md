# Tasks: Static Renderer

## Related Spec

`docs/specs/001-static-renderer.md`

## Related Plan

`docs/plans/001-static-renderer-plan.md`

## Task List

### Task 1: Render Planning and Slugs

Goal:
Create deterministic output planning for dataset, book, and section pages.

Files to inspect:
`slugify.py`, `site/planner.py`, `site/urls.py`, sample JSON.

Files to modify:
`slugify.py`, `site/planner.py`, `site/urls.py`, tests.

Implementation details:
Use `Path` for filesystem paths and POSIX strings only for generated browser links.

Tests required:
Slug collisions, Windows reserved names, output path expectations.

Validation command:
`python -m pytest tests/test_slugify.py`

Acceptance criteria:
Sample input maps to `rendered/brightlearn_books/` and duplicate names are safe.

Risk:
Broken links if filesystem paths and browser URLs are mixed.

### Task 2: Static HTML Rendering

Goal:
Render dataset, book, and section pages from normalized data.

Files to inspect:
`site/renderer.py`, templates, `models.py`, fixtures.

Files to modify:
`site/renderer.py`, templates, CSS, tests.

Implementation details:
Prepare template context outside Jinja and keep templates presentation-focused.

Tests required:
Integration render into `tmp_path`, HTML structure assertions.

Validation command:
`python -m pytest tests/test_renderer.py`

Acceptance criteria:
All sample books and sections produce pages with expected navigation/context.

Risk:
Templates may accidentally encode business logic.

### Task 3: CLI Validate and Render

Goal:
Wire CLI commands for validation and rendering.

Files to inspect:
`cli.py`, `loader.py`, `validator.py`, `normalizer.py`, `site/`.

Files to modify:
`cli.py`, tests, README only if command usage changes.

Implementation details:
Keep CLI as orchestration only.

Tests required:
CLI behavior tests or direct command smoke tests.

Validation command:
`python -m brightlearn_site validate data/samples/brightlearn_books.json`

Acceptance criteria:
Commands run without `NotImplementedError`.

Risk:
CLI may duplicate pipeline logic that belongs in reusable services.
