# Implementation Plan: LLM Summary Translation

## Related Spec

`docs/specs/002-llm-summary-translation.md`

## Overview

Implement a translation service that translates book summaries into Spanish, French, and German through a remote LLM API, validates strict JSON output, caches results, and integrates translated summaries into rendered book pages.

## Files to Inspect

- `src/brightlearn_site/settings.py`
- `src/brightlearn_site/translation/`
- `src/brightlearn_site/models.py`
- `src/brightlearn_site/templates/book_index.html`
- `src/brightlearn_site/templates/partials/language_flags.html`
- `src/brightlearn_site/static/js/app.js`
- `tests/test_translation_parser.py`

## Files to Create

- Translation service tests as needed.
- Translation cache tests as needed.
- Retry policy tests as needed.

## Files to Modify

- `src/brightlearn_site/translation/client.py`
- `src/brightlearn_site/translation/service.py`
- `src/brightlearn_site/translation/prompts.py`
- `src/brightlearn_site/translation/response_parser.py`
- `src/brightlearn_site/translation/json_repair.py`
- `src/brightlearn_site/translation/cache.py`
- `src/brightlearn_site/translation/retry.py`
- `src/brightlearn_site/translation/exceptions.py`
- Book template and static JS for language switching.

## Data Model Changes

- Confirm whether `TranslationBundle` is sufficient.
- Consider adding metadata for fallback status only if needed for rendering or reports.

## API Changes

- Add settings-driven translation behavior.
- Rendering should be able to use cached translations or English fallback.

## Business Logic Flow

1. Build cache key from provider, model, source language, target languages, book title, description hash, and prompt version.
2. Return cached translations when available.
3. Build strict JSON translation prompt.
4. Call remote LLM API with timeout.
5. Parse and validate JSON.
6. Attempt repair if parsing fails.
7. Retry if repair fails or transient API failure occurs.
8. Store valid translations in cache.
9. Return fallback English state if all translation attempts fail.

## Error Handling

- Missing credentials should not expose secrets.
- 429 should trigger backoff.
- Timeouts and disconnects should retry within configured limits.
- Invalid JSON should trigger repair, then retry if needed.
- Exhausted retries should log and fall back to English.

## Security Considerations

- Do not put LLM API keys in browser assets.
- Do not log secrets.
- Do not execute or trust LLM output beyond validated strings.
- Send only summaries and necessary instructions to the LLM.

## Test Strategy

- Mock LLM client responses.
- Test strict JSON parsing.
- Test repair behavior.
- Test retry decision behavior.
- Test cache key invalidation when description changes.
- Test rendering fallback when translations are unavailable.

## Step-by-step Implementation Plan

1. Finalize translation response schema.
2. Implement cache key and cache read/write.
3. Implement strict prompt.
4. Implement client and retry policy.
5. Implement parse/repair/validate flow.
6. Integrate translations into book rendering.
7. Implement flag switching behavior.
8. Add tests and run validation.

## Risks

- LLM provider API details may change.
- Real API calls may be slow or rate-limited.
- Browser embedding of translation data must avoid escaping issues.

## Open Questions

- Final production LLM provider and model.
- Exact behavior when credentials are absent.
