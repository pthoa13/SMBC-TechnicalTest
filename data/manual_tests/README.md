# Manual Test Fixtures

This directory contains small fixtures for local manual QA.

## Batch: three files at once

Use the files in `batch-three-files/` to verify that watcher mode can process multiple JSON files
dropped into the batch directory at the same time.

Recommended test:

```bash
rm -f batch-process/manual_batch_*.json
rm -rf rendered/manual_batch_alpha rendered/manual_batch_beta rendered/manual_batch_gamma
PYTHONPATH=src python -m brightlearn_site watch --skip-translations
```

In a second terminal:

```bash
cp data/manual_tests/batch-three-files/*.json batch-process/
```

Expected output:

```text
rendered/manual_batch_alpha/index.html
rendered/manual_batch_beta/index.html
rendered/manual_batch_gamma/index.html
```

## LLM 429 retry without a real API call

Use the fixture in `rate-limit/` with `tools/mock_openai_rate_limit_server.py` to verify that the
HTTP client, retry policy, translation parser, cache, and renderer recover from a temporary `429`.

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

Expected output:

- First mock LLM request returns `429`.
- The renderer retries.
- The second mock LLM request returns valid translation JSON.
- `rendered/manual_rate_limit_books/index.html` is generated.
- `rendered/.cache/manual-rate-limit-translations.json` contains the accepted translations.
