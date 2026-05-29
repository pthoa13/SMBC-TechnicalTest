# SMBC BrightLearn Static Site

Python 3.12 static site generator for the SMBC BrightLearn technical test.

The project reads BrightLearn book JSON, validates the expected schema, renders static HTML pages,
translates only book summary descriptions into Spanish, French, and German through a remote LLM API,
and watches `batch-process/` for future compatible JSON drops.

Public repository:

```text
https://github.com/pthoa13/SMBC-TechnicalTest
```

## Reviewer Quick Start

Use this path to evaluate the project from a fresh clone.

```bash
uv python install 3.12
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
PYTHONPATH=src python -m pytest
PYTHONPATH=src python -m brightlearn_site render data/samples/brightlearn_books.json --skip-translations
```

On Windows PowerShell, activate the virtual environment with `.\.venv\Scripts\Activate.ps1` instead
of `source .venv/bin/activate`.

Then open:

```text
rendered/brightlearn_books/index.html
```

This validates the static renderer, generated navigation, responsive HTML/CSS, and English fallback
behavior without requiring a real LLM API key.

To test real translation behavior, copy `.env.example` to `.env`, set `LLM_API_KEY`, and run:

```bash
PYTHONPATH=src python -m brightlearn_site render data/samples/brightlearn_books.json
```

Successful translations are cached, so rerunning the command should use cache hits for unchanged
book descriptions.

## Requirement Coverage

- Render individual static pages for each of the 5 sample books.
- Render section/subchapter pages from each book's table of contents.
- Generate static output that can be opened directly in a local browser.
- Use visually polished local CSS and static JavaScript navigation/summary switching.
- Reference remote book cover images from the source URLs.
- Translate only `Book.description`, not full book text, chapter titles, or section titles.
- Display small English, Spanish, French, and German flag controls near each book title.
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
data/manual_tests/  Small fixtures for manual batch and LLM retry testing
batch-process/    Runtime input folder for future JSON drops
rendered/         Runtime generated static websites and translation cache
logs/             Runtime logs
docs/             Specs, plans, tasks, reports, architecture, QA, and security context
tests/            Unit and integration tests
tools/            Local manual-test helper scripts
```

Runtime files under `batch-process/`, `rendered/`, and `logs/` are ignored by Git except
`.gitkeep` placeholders.

## Setup

This project is expected to run on Python 3.12. Use `uv` to provision Python and install
dependencies.

Install Python 3.12 with `uv`:

```bash
uv python install 3.12
```

Create a project virtual environment with Python 3.12:

```bash
uv venv --python 3.12 .venv
```

Activate the virtual environment on macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies from `requirements.txt` with `uv pip`:

```bash
uv pip install -r requirements.txt
```

Confirm the environment:

```bash
python --version
uv pip list
```

Expected Python version:

```text
Python 3.12.x
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
  The default is `4096` because the sample contains long summaries and the LLM must return three
  translated summaries in one strict JSON object.
- Secrets are read server-side only. They are not written into generated HTML or JavaScript.
- Successful translations are cached in `rendered/.cache/translations.json`. If a render is stopped
  after some books were translated, running the command again resumes from cache hits and only calls
  the LLM for missing cache entries.

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

The render command writes progress logs to both the terminal and `logs/app.log`. During real LLM
translation you should see cache hits/misses, per-book attempts, retries, fallbacks, and final render
completion.

Expected sample output:

```text
rendered/brightlearn_books/index.html
rendered/brightlearn_books/books/<book-slug>/index.html
rendered/brightlearn_books/books/<book-slug>/sections/<section-slug>.html
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

## Manual Evaluation Scenarios

### Batch: drop three files at once

Terminal 1:

```bash
rm -f batch-process/manual_batch_*.json
rm -rf rendered/manual_batch_alpha rendered/manual_batch_beta rendered/manual_batch_gamma
PYTHONPATH=src python -m brightlearn_site watch --skip-translations
```

Terminal 2:

```bash
cp data/manual_tests/batch-three-files/*.json batch-process/
```

Expected output:

```text
rendered/manual_batch_alpha/index.html
rendered/manual_batch_beta/index.html
rendered/manual_batch_gamma/index.html
```

The watcher processes files sequentially, waits for each file to become stable, logs success or
failure per file, and ignores duplicate unchanged filesystem events.

### LLM 429 retry without spending API credits

Terminal 1:

```bash
python tools/mock_openai_rate_limit_server.py --port 8765 --rate-limit-count 1
```

Terminal 2:

```bash
rm -f rendered/.cache/manual-rate-limit-translations.json
LLM_BASE_URL=http://127.0.0.1:8765/v1 \
LLM_API_KEY=test_mock_key \
TRANSLATION_CACHE_PATH=rendered/.cache/manual-rate-limit-translations.json \
TRANSLATION_MAX_RETRIES=2 \
PYTHONPATH=src \
python -m brightlearn_site render data/manual_tests/rate-limit/manual_rate_limit_books.json
```

Expected behavior:

- The mock server returns HTTP `429` for the first translation request.
- The renderer logs a retry.
- The second request succeeds with strict JSON translation content.
- `rendered/manual_rate_limit_books/index.html` is generated.

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

If the virtual environment is not activated, call the venv binaries directly:

```bash
PYTHONPATH=src .venv/bin/python -m pytest
PYTHONPATH=src .venv/bin/ruff check .
.venv/bin/python -m compileall src tests
```

Latest local validation result:

```text
environment: Python 3.12.13 provisioned by uv
pytest: 65 passed
ruff: All checks passed
compileall: passed
render smoke: rendered 5 books to rendered/brightlearn_books
real LLM render: cache contains 5 translated book summaries
generated output scan: 41,664 local links checked, 0 missing or unsafe
secret scan: 0 API key or sensitive marker hits in rendered output/logs
flag asset smoke: SVG flag assets copied into rendered output
watcher smoke: copied JSON into batch-process and rendered output successfully
manual 429 retry smoke: local mock server returned 429 then 200, render succeeded
manual three-file batch smoke: three simultaneous fixture drops generated three output folders
```

## Manual QA Checklist

- Render `data/samples/brightlearn_books.json`.
- Open `rendered/brightlearn_books/index.html`.
- Confirm the dataset page lists all 5 sample books.
- Open each book page and confirm title, author, cover image, English summary, language controls,
  and table of contents.
- Confirm the English summary button uses the English flag icon, not a text-only `EN` label.
- Click Spain, France, and Germany flag controls and confirm the summary switches when translations
  are available.
- Confirm English remains visible when translations are skipped or unavailable.
- Expand and collapse the sidebar book outlines and confirm sections are grouped under chapters
  without duplicate numbering such as `1. 1.`.
- Open several section pages and confirm breadcrumbs, book/chapter/section context, previous/next
  navigation, and original BrightLearn links.
- Start watcher mode with `--skip-translations`, copy a JSON file into `batch-process/`, and confirm
  output appears under `rendered/<source-file-stem>/`.
- Run the manual three-file batch fixture from `data/manual_tests/README.md` if multi-file batch
  behavior needs to be demonstrated.
- Run the mock 429 retry fixture from `data/manual_tests/README.md` if LLM retry behavior needs to be
  demonstrated without using real API credits.
- Check generated pages in Brave on Windows when available.

## Known Limitations

- The current JSON provides section titles and source URLs, not full section body text. Generated
  section pages therefore include local navigation and a link to the original BrightLearn section.
- Archive/quarantine handling for completed or failed batch files is not implemented because it is
  out of scope/TBD in the project specs.
- Sidecar job status files are not implemented because they are out of scope/TBD.
- Real LLM API behavior depends on the configured provider, model, quota, and API key.
- Batch files are processed sequentially. Parallel workers or a database-backed job queue are not
  required by the original test prompt and are listed as out of scope in Spec 003.
- Windows/Brave compatibility is designed through path-safe output and static relative links,
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
