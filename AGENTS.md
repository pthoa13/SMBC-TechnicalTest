# AGENTS.md

## Project Summary

This repository is for the SMBC BrightLearn technical test. The goal is to build a Python 3.12 static site generation pipeline that reads BrightLearn book JSON files and renders a polished, browsable static website.

The supplied sample input is:

- `data/samples/brightlearn_books.json`
- Original source file retained at repository root: `brightlearn_books (2).json`

The generated site must support:

- A dataset index page listing all books.
- A book index page for each book.
- Section/subchapter pages for every section in each book's table of contents.
- Clear navigation such as sidebar links, breadcrumbs, previous/next section links, or equivalent.
- Responsive layout and clean typography.
- Remote cover images loaded from BrightLearn URLs.
- Basic compatibility with Brave browser on Windows.

## Core Functional Requirements

1. Read structured BrightLearn JSON containing 5 books in the provided sample.
2. Validate and normalize book data before rendering.
3. Generate static HTML into the local `rendered/` directory.
4. Create and use a `batch-process/` directory for future JSON drops.
5. When a new compatible JSON file is placed in `batch-process/`, process it and render the output under `rendered/<source-file-stem>/`.
6. Do not treat this as a one-time conversion. The pipeline must be reusable for future JSON files with the same schema.
7. Keep generated runtime artifacts out of Git except `.gitkeep` placeholders.

## Translation Requirements

Only the book summary/description is translated. Do not translate full book text, chapter titles, or section content unless the user explicitly changes the requirement.

Required target languages:

- Spanish: `es`
- French: `fr`
- German: `de`

Each book index page must display small Spain, France, and Germany flag controls near the book title. Clicking a flag should reveal the corresponding translated summary.

The translation implementation must use a remote LLM API and include:

- A prompt that requires a strict JSON response.
- Response validation before accepting translations.
- JSON repair attempt if the LLM response is malformed.
- Retry if repair fails.
- HTTP 429 rate-limit detection.
- Exponential backoff for retryable failures.
- Timeout and disconnect handling.
- Sensible handling for modern LLM thinking/reasoning token behavior.
- Translation caching so rerendering does not repeatedly call the LLM for unchanged descriptions.
- Graceful fallback to the English summary if translation fails.

Expected translation response shape:

```json
{
  "translations": {
    "es": "Spanish summary here",
    "fr": "French summary here",
    "de": "German summary here"
  }
}
```

## Cross-Platform Path Requirement

All filesystem logic must work on macOS, Linux, and Windows.

Rules:

- Use `pathlib.Path` for filesystem paths.
- Do not manually concatenate paths with `/` or `\`.
- Do not assume POSIX-only paths.
- Do not assume Windows-only paths.
- For URLs written into generated HTML, convert paths with `.as_posix()` only at the final URL/link generation boundary.
- Keep filesystem paths and browser URLs conceptually separate.
- Avoid shell-specific assumptions in Python code.
- Avoid filenames that break on Windows.
- Handle spaces and parentheses in input filenames, such as `brightlearn_books (2).json`.
- Avoid Windows reserved filenames such as `CON`, `PRN`, `AUX`, `NUL`, `COM1`, and `LPT1`.
- Use deterministic slug generation for output folders and pages.
- Make duplicate titles safe by adding a stable suffix where needed.

When adding new code, prefer APIs like:

```python
from pathlib import Path

input_path = Path("data") / "samples" / "brightlearn_books.json"
output_dir = Path("rendered") / input_path.stem
```

Avoid code like:

```python
input_path = "data/samples/" + filename
output_dir = "rendered\\" + name
```

## Current Project Structure

```text
src/brightlearn_site/
├── cli.py
├── settings.py
├── logging_config.py
├── paths.py
├── exceptions.py
├── models.py
├── loader.py
├── validator.py
├── normalizer.py
├── slugify.py
├── site/
├── translation/
├── batch/
├── templates/
└── static/
```

Important runtime folders:

```text
batch-process/
rendered/
logs/
```

Important sample/test folders:

```text
data/samples/
tests/fixtures/
```

## Recommended Commands

After implementation, the expected command surface should be:

```bash
python -m brightlearn_site validate data/samples/brightlearn_books.json
python -m brightlearn_site render data/samples/brightlearn_books.json
python -m brightlearn_site watch
```

The package also exposes the planned console script:

```bash
brightlearn-site
```

## Development Principles

- Keep rendering separate from translation.
- Keep loading, validation, normalization, rendering, translation, and batch watching in separate modules.
- Static HTML generation is the core deliverable. A running server should not be required to view generated output.
- The site should still render if translation fails.
- Use logging for recoverable errors instead of silent failure.
- Keep templates readable and avoid embedding complex business logic in Jinja.
- Keep JavaScript minimal and focused on UI interactions such as language switching and mobile navigation.
- Prefer simple, reviewer-friendly dependencies.

## Review Expectations

SMBC is likely to evaluate:

- Whether the output is truly static HTML.
- Whether the generated pages are polished, navigable, and responsive.
- Whether batch processing works for future JSON drops.
- Whether LLM translation handling is robust rather than cosmetic.
- Whether the project handles broken data, failed translation, and reprocessing gracefully.
- Whether code is clean, testable, and easy to run on Windows with Python 3.12.

## Git Notes

The repository is public at:

```text
https://github.com/pthoa13/SMBC-TechnicalTest
```

Use this local Git identity unless the user requests otherwise:

```text
user.name = pthoa13
user.email = pt.hoaa13@gmail.com
```
