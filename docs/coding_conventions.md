# Coding Conventions

## General Principles

- Prefer readability over cleverness.
- Keep functions small and focused.
- Use explicit names that match the BrightLearn domain.
- Minimize side effects and keep I/O at module boundaries.
- Keep structure predictable and consistent with the existing `src/brightlearn_site` layout.
- Keep rendering, translation, validation, and batch processing concerns separate.
- Make changes incrementally so AI-assisted diffs stay reviewable.
- Preserve cross-platform behavior for macOS, Linux, and Windows.

## Naming Conventions

### Files and Folders

- Python modules use `snake_case.py`.
- Python packages use lowercase folder names with underscores where needed.
- Documentation files use lowercase descriptive names, except ADR files which use the ADR naming convention.
- Template files use descriptive lowercase names, for example `book_index.html`.
- Static asset folders remain grouped by type: `css/`, `js/`, `img/`.
- Runtime folders keep the existing names: `batch-process/`, `rendered/`, and `logs/`.

### Classes

- Classes use `PascalCase`.
- Pydantic models should be named as domain nouns, for example `BookDataset`, `Book`, `Chapter`, and `TranslationBundle`.
- Exception classes should end with `Error` unless a more specific convention is already established.

### Functions and Variables

- Functions use `snake_case`.
- Variables use `snake_case`.
- Boolean variables should read clearly, for example `is_stable`, `has_translation`, or `should_retry`.
- Avoid vague names such as `data2`, `obj`, or `thing` outside very small local contexts.

### Constants

- Constants use `UPPER_SNAKE_CASE`.
- Keep constants near the module that owns them unless shared broadly.

### CLI Commands

- CLI subcommands should be short lowercase verbs, for example `validate`, `render`, and `watch`.
- CLI arguments should use kebab-case, for example `--output-dir`.

### Test Files

- Test files use `test_<module_or_behavior>.py`.
- Test functions use `test_<expected_behavior>()`.
- Fixtures should be small and named for the behavior they exercise, for example `minimal_books.json` or `duplicate_titles.json`.

## File Organization

- `src/brightlearn_site/models.py`: typed domain models.
- `src/brightlearn_site/loader.py`: disk JSON loading.
- `src/brightlearn_site/validator.py`: schema validation.
- `src/brightlearn_site/normalizer.py`: conversion into internal models.
- `src/brightlearn_site/slugify.py`: safe slug and filename helpers.
- `src/brightlearn_site/site/`: static output planning, rendering, assets, and generated URLs.
- `src/brightlearn_site/translation/`: LLM client, prompt, parser, repair, retry, cache, and translation service.
- `src/brightlearn_site/batch/`: folder watcher, file stability checks, and batch orchestration.
- `src/brightlearn_site/templates/`: Jinja2 templates and partials.
- `src/brightlearn_site/static/`: CSS, JavaScript, and local image assets.
- `tests/`: pytest tests and small fixtures.
- `docs/`: project context, architecture, QA, security, specs, plans, tasks, reports, and ADRs.

Example:

```python
from pathlib import Path

input_path = Path("data") / "samples" / "brightlearn_books.json"
output_dir = Path("rendered") / input_path.stem
```

Discouraged:

```python
input_path = "data/samples/" + filename
output_dir = "rendered\\" + name
```

Project-specific organization rules:

- Keep all filesystem path construction in Python code using `Path`.
- Convert filesystem paths to browser links only at the URL-generation boundary.
- Prepare template context data before calling Jinja. Do not make templates compute slugs, cache keys, filesystem paths, or retry decisions.
- Keep LLM prompt text in `translation/prompts.py`, response validation in `translation/response_parser.py`, and retry mechanics in `translation/retry.py`.
- Keep batch file stability and duplicate-processing rules in `batch/`, not in CLI command handlers.

## Function and Class Design

- A function should do one clear thing.
- Avoid large god classes or orchestration objects that own unrelated responsibilities.
- Keep public interfaces stable once tests and docs depend on them.
- Separate business logic from infrastructure concerns.
- Avoid hidden global state, especially for settings, translation cache, or output paths.
- Pass dependencies explicitly when doing so improves testability.
- Keep provider-specific LLM request details inside the translation client.
- Keep Jinja2 template setup inside the site rendering layer.

## Type Safety

- Use Python type annotations for public functions and non-trivial internal helpers.
- Prefer Pydantic models for external JSON validation and normalized domain models.
- Validate external input before passing it into rendering or translation.
- Avoid `Any` unless the value is genuinely unknown at the boundary. Narrow it as soon as practical.
- Do not weaken model types to avoid fixing validation problems.
- Use `pathlib.Path` for filesystem paths, not raw strings.

## Error Handling

- Raise project-specific exceptions for expected project failures where useful.
- Preserve useful context when wrapping exceptions.
- Do not catch broad exceptions unless adding context, logging, or preserving batch processing.
- Do not silently ignore validation, rendering, or translation failures.
- Translation failure should degrade gracefully to English summaries after retry budget is exhausted.
- Batch processing should isolate failures to the current file where possible.

## Logging

- Log meaningful operational events such as start/end of render, batch file detection, validation failure, retry attempts, and translation fallback.
- Do not log API keys, tokens, `.env` values, or full authorization headers.
- Do not log sensitive user data. The current dataset is public-like book metadata, but future inputs should still be treated carefully.
- Avoid noisy logs inside tight loops unless using debug level.
- Include enough context for debugging, such as input filename, book title, retry attempt, and provider error category.
- Logs should be helpful without requiring the user to inspect stack traces for normal recoverable errors.

## Comments and Documentation

- Comment why code exists, not what obvious code does.
- Document non-obvious decisions, edge-case handling, and provider limitations.
- Keep comments updated when behavior changes.
- Prefer clear function names and tests over explanatory comments for straightforward behavior.
- Update relevant docs when requirements, architecture, validation commands, or operational behavior change.

## Dependency Usage

- Prefer the Python standard library or existing project dependencies.
- Add a new dependency only when it materially improves correctness, robustness, or simplicity.
- Document the reason for new dependencies in the relevant plan or implementation report.
- Avoid duplicate libraries that solve the same problem.
- Keep dependencies reviewer-friendly and compatible with Python 3.12.
- Do not add heavy frontend build tooling unless a future spec justifies it.

Current dependencies:

- `jinja2`
- `httpx`
- `pydantic`
- `python-dotenv`
- `watchdog`
- `pytest`
- `beautifulsoup4`
- `ruff`

## AI Coding Rules

- Follow existing style before introducing new patterns.
- Do not rewrite working code unless required by the current task.
- Do not introduce abstractions before they are needed.
- Do not remove validation for convenience.
- Do not weaken types to make errors disappear.
- Do not ignore lint, type, or test failures.
- Keep diffs small and reviewable.
- Do not implement application code when the task asks for documentation only.
- Do not modify generated runtime folders unless the task is specifically about generated output.
- If a requirement is unclear, document the assumption or open question instead of inventing behavior.

## Examples

### Preferred: Boundary Validation

```python
from pathlib import Path

from brightlearn_site.loader import load_json_file
from brightlearn_site.validator import validate_dataset


def load_valid_dataset(path: Path):
    raw_data = load_json_file(path)
    return validate_dataset(raw_data)
```

### Preferred: Template Context Prepared Outside Jinja

```python
context = {
    "book": book,
    "book_url": urls.book_index_url(book_slug),
    "sections": section_links,
}
```

Discouraged:

```jinja2
{# Do not create slugs or filesystem paths inside templates. #}
<a href="{{ book.book_title.lower().replace(' ', '-') }}/index.html">
```

### Preferred: Strict Translation Shape

```python
translations = parse_translation_json(raw_response)
summary_by_language = {
    "en": original_description,
    "es": translations.es,
    "fr": translations.fr,
    "de": translations.de,
}
```

### Discouraged: Mixed Responsibilities

```python
def render_file(path):
    # Reads JSON, mutates globals, calls LLM, creates HTML, and catches every error.
    ...
```

### Preferred: Final URL Conversion Only

```python
relative_href = output_path.relative_to(site_root).as_posix()
```

### Discouraged: Using URL Separators for Filesystem Logic

```python
output_path = "rendered/" + book_title + "/index.html"
```
