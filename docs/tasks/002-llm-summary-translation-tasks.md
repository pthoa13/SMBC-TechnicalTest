# Tasks: LLM Summary Translation

## Related Spec

`docs/specs/002-llm-summary-translation.md`

## Related Plan

`docs/plans/002-llm-summary-translation-plan.md`

## Task List

### Task 1: Parser, Repair, and Cache

Goal:
Validate strict translation JSON and cache successful translation bundles.

Files to inspect:
`translation/response_parser.py`, `translation/json_repair.py`, `translation/cache.py`, `models.py`.

Files to modify:
Translation parser, repair, cache modules, tests.

Implementation details:
Cache key must include provider, model, source language, target languages, book title, and description hash.

Tests required:
Valid wrapped JSON, invalid JSON, repairable JSON, cache hit/miss.

Validation command:
`python -m pytest tests/test_translation_parser.py tests/test_translation_cache.py`

Acceptance criteria:
Invalid LLM JSON is never accepted silently.

Risk:
Over-permissive repair could accept wrong data.

### Task 2: LLM Client and Retry Policy

Goal:
Call the remote LLM API with timeout, 429 handling, transient retries, and clear errors.

Files to inspect:
`settings.py`, `translation/client.py`, `translation/retry.py`, `translation/exceptions.py`.

Files to modify:
LLM client, retry, exceptions, tests.

Implementation details:
Do not hardcode secrets and do not expose provider keys to browser code.

Tests required:
Mocked 429, timeout, disconnect, retryable 5xx, non-retryable failure.

Validation command:
`python -m pytest tests`

Acceptance criteria:
Retry policy is deterministic and bounded by settings.

Risk:
Provider-specific behavior may leak into higher layers.

### Task 3: Book Page Translation UI

Goal:
Embed validated translations in book pages and switch summaries with flag controls.

Files to inspect:
`templates/book_index.html`, `partials/language_flags.html`, `static/js/app.js`, renderer.

Files to modify:
Book templates, static JS, renderer integration, tests.

Implementation details:
English summary must remain visible when translations are missing or JavaScript is unavailable.

Tests required:
HTML structure tests for flags and translation data.

Validation command:
`python -m pytest tests`

Acceptance criteria:
Spain, France, and Germany controls reveal the correct translated summaries when available.

Risk:
Embedding JSON in HTML can break escaping if not handled carefully.
