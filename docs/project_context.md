# Project Context

## Product Overview

SMBC BrightLearn Static Site is a Python 3.12 project that converts BrightLearn book metadata JSON into a browsable static website. The generated website presents a dataset index, individual book pages, and section/subchapter pages derived from each book's table of contents.

The project also includes an LLM-assisted translation workflow for book summaries. Only each book's summary/description is translated into Spanish, French, and German. Full book text, chapter titles, and section titles are not translated under the current requirements.

## Product Goal

The main goal is to deliver a reusable static site generation pipeline that can process the provided BrightLearn JSON file and future JSON files with the same schema. The pipeline must generate polished static HTML output, support multilingual summary display, and handle future file drops through a local batch-processing workflow.

## Target Users

- SMBC technical reviewers who will clone the public repository and test it locally.
- Developers or AI coding agents extending the implementation.
- Local operators who drop compatible BrightLearn JSON files into `batch-process/`.
- End users viewing the generated static website in a local browser.

## Core Use Cases

- Validate a BrightLearn JSON input file before rendering.
- Render the sample `data/samples/brightlearn_books.json` into static HTML under `rendered/brightlearn_books/`.
- Generate one dataset index page listing all books.
- Generate one book index page per book with cover image, metadata, summary, language controls, and table of contents.
- Generate section/subchapter pages for every section in every chapter. The current JSON provides section titles and source URLs, not full section body text, so section pages should render local navigation/context plus a link to the original BrightLearn section URL.
- Fetch and display remote cover images from BrightLearn URLs.
- Translate each book summary into Spanish, French, and German through a remote LLM API.
- Click Spain, France, or Germany flag controls on a book page to reveal the corresponding translated summary.
- Watch `batch-process/` for compatible `.json` files and render each dataset into `rendered/<source-file-stem>/`.
- Re-run rendering without re-translating unchanged summaries by using a translation cache.

## Functional Scope

The system should:

- Load JSON files from disk using cross-platform path handling.
- Validate input data against the expected BrightLearn schema.
- Normalize raw input into internal data models.
- Create safe deterministic slugs for output folders and pages.
- Generate static HTML pages using templates.
- Copy bundled CSS, JavaScript, and local static assets into generated output.
- Use remote image URLs directly rather than downloading or processing images locally.
- Call a configurable remote LLM API for summary translations.
- Require strict JSON-wrapped LLM translation responses.
- Validate LLM responses before accepting them.
- Attempt conservative JSON repair when LLM output is malformed.
- Retry transient LLM failures, including 429 rate limits, timeouts, disconnects, and retryable 5xx responses.
- Log operational events and recoverable failures.
- Continue rendering with English summaries if translation fails.
- Process future dropped JSON files without code changes.

Canonical output layout:

- Every input JSON renders into `rendered/<source-file-stem>/`.
- The sample input `data/samples/brightlearn_books.json` renders into `rendered/brightlearn_books/`.
- This convention avoids collisions between the sample dataset and future batch files.

## Non-functional Requirements

### Performance

- Static rendering should be efficient enough for the provided 5-book dataset and future datasets with the same schema.
- Translation calls should be cached to avoid repeated API usage for unchanged descriptions.
- Batch processing should avoid repeatedly processing files that are still being copied or have not changed.

### Reliability

- Invalid input data should produce clear validation errors.
- Translation failures should not prevent static site generation.
- Batch processing should log failures per file and continue watching for future files where possible.
- Re-processing should produce clean, deterministic output.
- Initial batch behavior should scan existing compatible files at watcher startup and process new or changed files while running. If this proves too broad in implementation, document the limitation in the relevant report.

### Maintainability

- Loading, validation, normalization, rendering, translation, and batch watching should stay in separate modules.
- Templates should remain readable and should not contain complex business logic.
- AI-generated changes should be small, reviewable, and aligned with the documented architecture.

### Security

- LLM API credentials must come from environment variables or secret management.
- `.env` files must not be committed.
- LLM responses must be treated as untrusted external input and validated.
- Logs must not include secrets.

### Scalability

- The project is not a high-traffic service. Scalability mainly means the pipeline can process future JSON drops with the same schema.
- Output names and translation cache keys should remain stable as datasets grow.

### Usability

- Generated pages should be visually polished, readable, navigable, and responsive.
- Navigation should make it easy to move between dataset, book, chapter, and section context.
- Language controls should be obvious and should degrade gracefully if translations are missing by keeping the English summary available.

### Compatibility

- Python runtime target is Python 3.12.
- Filesystem logic must work on macOS, Linux, and Windows.
- Generated pages must work in a local browser and have basic compatibility with Brave browser on Windows.

## Tech Stack

- Language: Python 3.12.
- Packaging: `pyproject.toml` with setuptools.
- Static rendering: Jinja2.
- Data validation: Pydantic.
- HTTP client for LLM integration: httpx.
- Environment configuration: python-dotenv and environment variables.
- Batch folder watching: watchdog.
- Tests: pytest.
- HTML test utilities: Beautiful Soup, currently listed as a dev dependency.
- Linting: Ruff.
- Frontend runtime: static HTML, CSS, and minimal vanilla JavaScript.
- Translation LLM provider: configurable, currently represented by `LLM_PROVIDER=openai` in `.env.example`.
- Deployment/hosting: no hosted deployment is currently required. Current requirement is local static output plus public GitHub repository.
- Database: none defined.
- Authentication/authorization: not required by current specs; TBD only if future hosted or multi-user scope is added.

## Project Phase

The project is in the initial implementation phase. The repository currently contains the scaffold, package layout, requirements, AGENTS.md, and documentation governance. Full application behavior has not yet been implemented.

## Important Constraints

- Output must be static HTML files. Generated pages should be directly viewable in a local browser without requiring the Python application or a running web server.
- Python 3.12 is required.
- Filesystem path handling must be compatible with macOS, Linux, and Windows.
- Windows naming conventions must be respected for generated files and folders.
- Input filenames may include spaces and parentheses, for example `brightlearn_books (2).json`.
- Generated URLs should use POSIX-style separators only at the HTML URL boundary.
- Remote images can be loaded from BrightLearn URLs; no local image processing is required.
- Translation must use a remote LLM API.
- Translation prompt must require strict JSON output.
- LLM response JSON must be validated before use.
- Malformed LLM JSON should trigger repair and then retry if repair fails.
- Rate limit handling, retries, disconnect recovery, timeout handling, and reasoning-token awareness are required for translation calls.
- Generated runtime output under `rendered/`, logs under `logs/`, and dropped batch files under `batch-process/` should not be committed except `.gitkeep` placeholders.
- Final project should be available in a public GitHub repository.

## Out of Scope

- Translating full book text, chapter titles, or section titles.
- Downloading or transforming remote cover images locally.
- Building a production web service or requiring a running server to view output.
- Implementing authentication or user accounts. This is not required by current specs.
- Creating a database-backed content management system.
- Supporting unrelated JSON schemas.

## Open Questions

- Which remote LLM provider and model will be used for final translation calls?
- What exact command should be the default CLI behavior when no subcommand is provided?
- Should reprocessing clean and overwrite `rendered/<source-file-stem>/`, or should it preserve a previous run when render fails partway through?
- What exact manual browser matrix is expected beyond Brave on Windows?
- Should future data include section body text to render locally, or will section pages always be navigation/source-link pages?
- Should generated sites include a search feature, or is navigation-only sufficient?
- Should translation cache live only under `rendered/.cache/`, or should it be configurable per output dataset?
