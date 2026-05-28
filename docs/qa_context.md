# QA Context

## Testing Philosophy

Tests are part of implementation, not a cleanup step. Every feature should be designed so its behavior can be validated automatically where practical and manually where browser behavior matters.

The tests should protect the project requirements:

- Correct BrightLearn JSON loading, validation, and normalization.
- Safe cross-platform output paths and slugs.
- Deterministic static HTML generation.
- Robust LLM translation parsing, repair, retry, fallback, and cache behavior.
- Reliable batch processing for future JSON drops.

Do not weaken tests to make them pass. If a test fails, first determine whether the production code or the test expectation is wrong.

## Test Types

### Unit Tests

Use unit tests for:

- `slugify.py` path and Windows reserved-name behavior.
- `loader.py` JSON loading.
- `validator.py` schema validation.
- `normalizer.py` default and compatibility behavior.
- `translation/response_parser.py` strict response validation.
- `translation/json_repair.py` conservative repair behavior.
- Translation cache key generation and read/write behavior.
- Retry policy decisions.

### Integration Tests

Use integration tests for:

- Full render pipeline from fixture JSON to a temporary output directory.
- Generated page count and expected file paths.
- Relative link correctness.
- Static asset copying.
- Batch processor behavior for one file.
- Translation fallback when the LLM client fails.

### HTML/Static UI Tests

Use HTML parsing tests for generated static output:

- Dataset index includes all books.
- Book pages include cover image, author, summary, language controls, and table of contents.
- Section pages include book/chapter/section context and original BrightLearn links.
- Breadcrumb and navigation links resolve to generated files.
- Language translation data is present in a safe and valid structure.

### Manual Browser QA

Manual QA is required for layout, responsiveness, and Brave-on-Windows compatibility. Automated tests can check structure, but they cannot fully judge visual polish.

### Security-Related Tests

Use focused tests for:

- `.env` values are not required for non-translation rendering.
- Translation code does not accept invalid LLM JSON silently.
- Logs and errors do not include configured secret values where testable.

Authentication and authorization tests are not currently applicable because no auth model is defined.

## What Must Be Tested

- Loading valid JSON.
- Handling malformed JSON.
- Rejecting invalid schema shapes.
- Handling missing required book fields.
- Handling empty or duplicate book titles.
- Handling Windows reserved filenames.
- Handling input filenames with spaces and parentheses.
- Creating deterministic output folders.
- Rendering dataset, book, and section pages.
- Rendering all chapters and sections from the sample dataset.
- Generating relative links that work from static files.
- Copying static assets.
- Preserving remote image URLs.
- Translation strict JSON parsing.
- JSON repair when the LLM response includes extra text or minor wrapper issues.
- Retry behavior for HTTP 429, timeouts, disconnects, and retryable server errors.
- Translation cache hit and miss behavior.
- English fallback when translation fails.
- Batch file stability detection.
- Batch processing idempotency and clean reprocessing.
- Direct local-browser viewing of generated static files without requiring the Python application to run.

## Test File Organization

- Tests live under `tests/`.
- Test fixtures live under `tests/fixtures/`.
- Test files should be named `test_<module_or_behavior>.py`.
- Use `tmp_path` for generated output in tests. Do not write test output into the committed `rendered/` folder.
- Keep fixtures small and purpose-specific.
- Add regression tests for every bug fix.

Existing examples:

- `tests/test_loader.py`
- `tests/test_validator.py`
- `tests/test_slugify.py`
- `tests/test_renderer.py`
- `tests/test_translation_parser.py`

## Validation Commands

Inferred from current project configuration:

```bash
python -m pytest
ruff check .
python -m compileall src tests
```

If the package is installed in editable mode, the CLI should also be validated with:

```bash
python -m brightlearn_site --help
brightlearn-site --help
```

Planned functional commands after implementation:

```bash
python -m brightlearn_site validate data/samples/brightlearn_books.json
python -m brightlearn_site render data/samples/brightlearn_books.json
python -m brightlearn_site watch
```

Note: validation commands should be reconfirmed once implementation and tooling are finalized.

## Definition of Done

A task is done only when:

- Implementation matches the relevant spec.
- Acceptance criteria are covered.
- Relevant tests are added or updated.
- Lint, tests, and compile checks pass where applicable.
- Static output is manually inspected when the task affects generated HTML or CSS.
- No unrelated files are modified.
- Implementation report is updated for completed features or milestones.
- Known limitations and skipped validations are documented.
- Cross-platform path behavior is considered and tested where relevant.

## Rules for Fixing Failing Tests

- Analyze the root cause first.
- Do not delete failing tests unless they are invalid or obsolete.
- Do not weaken assertions without documenting why.
- Prefer fixing production code over changing tests.
- Keep fixes minimal and scoped.
- Add regression coverage when a failure reveals an untested edge case.
- If a test relies on a wrong assumption, update the relevant spec or plan before changing the test.

## AI Validation Rules

- Always run or mention the relevant validation commands.
- If validation cannot be run, clearly explain why.
- Do not claim tests passed unless they were actually run.
- When reporting results, include exact commands and outcomes.
- If failures remain, document them clearly.
- Do not hide failures behind broad summaries like "minor test issues."
- For documentation-only changes, at minimum inspect the changed files and run `git diff --check` when practical.

## Manual QA Checklist

Use this checklist after the static renderer and translation UI are implemented:

- Open `rendered/<source-file-stem>/index.html` in a local browser.
- Confirm all 5 sample books appear on the dataset index.
- Confirm each book card/page shows the expected title, author, cover image, and English summary.
- Confirm remote cover images load from BrightLearn URLs.
- Confirm each book page includes Spain, France, and Germany flag controls near the title.
- Click each flag and confirm the corresponding translated summary appears.
- Confirm missing translation data falls back gracefully without breaking layout.
- Confirm table of contents lists chapters and sections.
- Open several section pages and confirm title, book context, chapter context, breadcrumbs, and original BrightLearn link.
- Confirm previous/next navigation where implemented.
- Resize to mobile width and confirm navigation and text remain usable.
- Check generated pages in Brave on Windows when available.
- Confirm generated links work from static files without a running app server.
- Drop a compatible JSON file into `batch-process/` and confirm output appears under `rendered/<source-file-stem>/`.
- Reprocess the same file and confirm output remains clean and deterministic.
- Simulate translation API failure and confirm English pages still render.
