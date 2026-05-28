# Implementation Plan: Static Renderer

## Related Spec

`docs/specs/001-static-renderer.md`

## Overview

Implement the core pipeline that loads a BrightLearn JSON file, validates and normalizes it, plans output paths, renders static HTML pages, and copies static assets into `rendered/<source-file-stem>/`.

## Files to Inspect

- `AGENTS.md`
- `Instructions.txt`
- `src/brightlearn_site/models.py`
- `src/brightlearn_site/loader.py`
- `src/brightlearn_site/validator.py`
- `src/brightlearn_site/normalizer.py`
- `src/brightlearn_site/slugify.py`
- `src/brightlearn_site/site/`
- `src/brightlearn_site/templates/`
- `src/brightlearn_site/static/`
- `tests/fixtures/`

## Files to Create

- Additional tests under `tests/` as needed.
- Optional render manifest only if decided during implementation.

## Files to Modify

- `src/brightlearn_site/cli.py`
- `src/brightlearn_site/site/planner.py`
- `src/brightlearn_site/site/renderer.py`
- `src/brightlearn_site/site/urls.py`
- `src/brightlearn_site/site/asset_copier.py`
- `src/brightlearn_site/templates/*.html`
- `src/brightlearn_site/templates/partials/*.html`
- `src/brightlearn_site/static/css/styles.css`
- `src/brightlearn_site/static/js/app.js` only if needed for navigation UI
- Relevant tests

## Data Model Changes

TBD during implementation. Prefer using existing Pydantic models unless the current schema misses required fields.

## API Changes

Add working CLI behavior for:

```bash
python -m brightlearn_site validate data/samples/brightlearn_books.json
python -m brightlearn_site render data/samples/brightlearn_books.json
```

## Business Logic Flow

1. Resolve input path using `Path`.
2. Load JSON.
3. Validate and normalize dataset.
4. Build deterministic slugs and output paths.
5. Render dataset index.
6. Render book index pages.
7. Render section pages from table-of-contents entries.
8. Copy static assets.
9. Report output path.

## Error Handling

- Invalid input path should fail clearly.
- Invalid JSON should fail clearly.
- Invalid schema should return validation details.
- Duplicate slugs should be resolved deterministically.
- Rendering errors should include template/output context.

## Security Considerations

- Use Jinja2 autoescaping.
- Do not render untrusted content as raw HTML.
- Do not use input data to construct output paths without slugging.
- Do not process paths outside the configured input/output roots.

## Test Strategy

- Unit tests for slug behavior and URL helpers.
- Validation tests for valid and invalid fixtures.
- Integration tests rendering fixture data into `tmp_path`.
- HTML parsing tests for expected links and content.

## Step-by-step Implementation Plan

1. Finalize output path helper for `rendered/<source-file-stem>/`.
2. Implement duplicate-safe slug planning.
3. Implement render plan generation.
4. Implement dataset/book/section rendering.
5. Polish templates and CSS enough for review.
6. Wire CLI validate/render commands.
7. Add automated tests.
8. Run validation commands and manually open generated output.

## Risks

- Relative links may break when opened from local files.
- Duplicate titles may produce collisions.
- Templates may accidentally become responsible for business logic.

## Open Questions

- Whether to generate a manifest file.
- Exact atomic overwrite strategy for existing output folders.
