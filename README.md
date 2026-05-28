# SMBC BrightLearn Static Site

Python 3.12 static site generator for the SMBC BrightLearn technical test.

The project reads BrightLearn book JSON, validates the expected schema, renders static HTML pages,
translates only book summary descriptions into Spanish, French, and German through a remote LLM API,
and watches `batch-process/` for future compatible JSON drops.

Public repository:

```text
https://github.com/pthoa13/SMBC-TechnicalTest
```

## Requirement Coverage

- Render individual static pages for each of the 5 sample books.
- Render section/subchapter pages from each book's table of contents.
- Generate static output that can be opened directly in a local browser.
- Use visually polished local CSS and static JavaScript navigation/summary switching.
- Reference remote book cover images from the source URLs.
- Translate only `Book.description`, not full book text, chapter titles, or section titles.
- Display small Spain, France, and Germany flag controls near each book title.
- Switch the displayed summary when a language flag is clicked.
- Provide a reusable batch workflow through `batch-process/`, not a one-time conversion.
- Process future compatible `.json` files into `rendered/<source-file-stem>/`.
- Use Windows-safe path handling and relative browser links.
- Detect LLM rate limits, retry transient failures, repair malformed JSON responses where possible,
  cache successful translations, and fall back to English when translation is unavailable.

## Tech Stack

- Python 3.12+
- Jinja2 for static HTML templates
- Pydantic for JSON schema validation
- httpx for OpenAI-compatible LLM API calls
- watchdog for local batch folder watching
- pytest and ruff for validation
- Vanilla JavaScript for client-side summary switching

Coding assistant used for this project: Codex.

Default translation provider configuration is OpenAI-compatible:

```text
LLM_PROVIDER=openai
LLM_MODEL=gpt-4.1-mini
LLM_BASE_URL=https://api.openai.com/v1
```

Any OpenAI-compatible chat completion endpoint can be used by changing `.env`.

## Project Layout

```text
src/brightlearn_site/
  batch/          Batch file filtering, single-file processing, and watcher mode
  site/           Render planning, URL helpers, asset copying, and Jinja rendering
  translation/    Prompting, LLM client, retry, repair, parser, cache, and fallback logic
  static/         CSS, JavaScript, favicon, and local flag SVG assets
  templates/      Jinja templates for dataset, book, and section pages

data/samples/     Sample BrightLearn JSON copied from the provided input
batch-process/    Runtime input folder for future JSON drops
rendered/         Runtime generated static websites and translation cache
logs/             Runtime logs
docs/             Specs, plans, tasks, reports, architecture, QA, and security context
tests/            Unit and integration tests
```

Runtime files under `batch-process/`, `rendered/`, and `logs/` are ignored by Git except
`.gitkeep` placeholders.

## Setup

Create and activate a virtual environment:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Environment Configuration

Remote translations require an API key. Copy the example file if you want to enable real LLM calls:

```bash
cp .env.example .env
```

Then set:

```text
LLM_API_KEY=<your real API key>
```

Important:

- Leave `LLM_API_KEY` empty to render English-only fallback output.
- `LLM_API_KEY=your_api_key_here` is treated as missing, so copying `.env.example` without edits will
  not accidentally call the LLM.
- `LLM_MAX_COMPLETION_TOKENS` controls the completion budget for the strict JSON translation
  response, including modern model reasoning/output token accounting where applicable.
- Secrets are read server-side only. They are not written into generated HTML or JavaScript.

## Commands

Validate the sample JSON:

```bash
PYTHONPATH=src python -m brightlearn_site validate data/samples/brightlearn_books.json
```

Render the sample with English-only summaries:

```bash
PYTHONPATH=src python -m brightlearn_site render data/samples/brightlearn_books.json --skip-translations
```

Render the sample with real translations if `.env` contains `LLM_API_KEY`:

```bash
PYTHONPATH=src python -m brightlearn_site render data/samples/brightlearn_books.json
```

Start batch watcher without real LLM calls:

```bash
PYTHONPATH=src python -m brightlearn_site watch --skip-translations
```

In another terminal, drop a compatible file:

```bash
cp data/samples/brightlearn_books.json batch-process/test_books.json
```

Expected output:

```text
rendered/test_books/index.html
```

The installed console script also works after package installation:

```bash
brightlearn-site validate data/samples/brightlearn_books.json
brightlearn-site render data/samples/brightlearn_books.json --skip-translations
brightlearn-site watch --skip-translations
```

## Opening the Static Site

After rendering the sample, open:

```text
rendered/brightlearn_books/index.html
```

On macOS:

```bash
open rendered/brightlearn_books/index.html
```

On Windows PowerShell:

```powershell
start .\rendered\brightlearn_books\index.html
```

The generated pages use relative links and can be opened directly from the filesystem without a
running Python server. Remote cover images still load from their original URLs.

## Validation

Run the full validation suite:

```bash
PYTHONPATH=src python -m pytest
PYTHONPATH=src ruff check .
python -m compileall src tests
```

Latest local validation result:

```text
pytest: 55 passed
ruff: All checks passed
compileall: passed
render smoke: rendered 5 books to rendered/brightlearn_books
flag asset smoke: SVG flag assets copied into rendered output
watcher smoke: copied JSON into batch-process and rendered output successfully
```

## Manual QA Checklist

- Render `data/samples/brightlearn_books.json`.
- Open `rendered/brightlearn_books/index.html`.
- Confirm the dataset page lists all 5 sample books.
- Open each book page and confirm title, author, cover image, English summary, language controls,
  and table of contents.
- Click Spain, France, and Germany flag controls and confirm the summary switches when translations
  are available.
- Confirm English remains visible when translations are skipped or unavailable.
- Open several section pages and confirm breadcrumbs, book/chapter/section context, previous/next
  navigation, and original BrightLearn links.
- Start watcher mode with `--skip-translations`, copy a JSON file into `batch-process/`, and confirm
  output appears under `rendered/<source-file-stem>/`.
- Check generated pages in Brave on Windows when available.

## Known Limitations

- The current JSON provides section titles and source URLs, not full section body text. Generated
  section pages therefore include local navigation and a link to the original BrightLearn section.
- Archive/quarantine handling for completed or failed batch files is not implemented because it is
  out of scope/TBD in the project specs.
- Sidecar job status files are not implemented because they are out of scope/TBD.
- Real LLM API behavior depends on the configured provider, model, quota, and API key.
- Windows/Brave compatibility is designed for through path-safe output and static relative links,
  but should be smoke-tested on an actual Windows machine before final delivery when possible.

## Documentation

Key project governance documents:

- `AGENTS.md`
- `docs/project_context.md`
- `docs/architecture.md`
- `docs/qa_context.md`
- `docs/security_context.md`
- `docs/specs/001-static-renderer.md`
- `docs/specs/002-llm-summary-translation.md`
- `docs/specs/003-batch-processing.md`
- `docs/reports/001-static-renderer-implementation-report.md`
- `docs/reports/002-llm-summary-translation-implementation-report.md`
- `docs/reports/003-batch-processing-implementation-report.md`
