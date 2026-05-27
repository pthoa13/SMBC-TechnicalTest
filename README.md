# SMBC BrightLearn Static Site

Python 3.12 project for rendering BrightLearn book JSON into a browsable static website with batch processing and LLM-powered summary translations.

## Project Status

This repository currently contains the project scaffold:

- Static site generator package under `src/brightlearn_site`
- Jinja2 template locations
- Runtime folders for `batch-process`, `rendered`, and `logs`
- Sample input JSON under `data/samples`
- Test package placeholders

Implementation will be added incrementally in the next steps.

## Planned Commands

```bash
python -m brightlearn_site validate data/samples/brightlearn_books.json
python -m brightlearn_site render data/samples/brightlearn_books.json
python -m brightlearn_site watch
```

## Environment

Copy `.env.example` to `.env` and provide the translation LLM credentials before enabling remote translations.

## Coding Assistant

Coding assistant used for this project: Codex.
