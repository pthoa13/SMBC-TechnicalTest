# Feature 002: LLM Summary Translation

## Goal

Translate each book's English summary/description into Spanish, French, and German using a remote LLM API, then expose translated summaries on book pages through flag controls.

## User Stories

- As a local viewer, I can click a Spain, France, or Germany flag near a book title and see the translated summary.
- As an SMBC reviewer, I can see robust LLM error handling instead of cosmetic translation code.
- As a developer, I can re-render without repeatedly paying for unchanged translations.

## Functional Requirements

- Translate only `Book.description`.
- Do not translate full book text, chapter titles, or section titles.
- Required target language keys are `es`, `fr`, and `de`.
- Use a remote LLM API configured through environment variables.
- Prompt the LLM to return strict JSON.
- The accepted response shape is:

```json
{
  "translations": {
    "es": "Spanish summary here",
    "fr": "French summary here",
    "de": "German summary here"
  }
}
```

- Validate LLM JSON before accepting it.
- Attempt conservative JSON repair when output is malformed.
- Retry the LLM call if repair fails.
- Handle HTTP 429, retryable 5xx responses, timeouts, and disconnects.
- Use exponential backoff within a configured retry budget.
- Account for modern LLM reasoning/thinking-token behavior by not assuming all provider output belongs in visible content and by validating only the final returned JSON content.
- Cache successful translations.
- Fall back to English summaries if translation fails after retries.
- Render flag controls on book pages near the title.

## Non-functional Requirements

- Do not hardcode secrets.
- Do not expose LLM API keys in generated static output.
- Do not log secrets.
- Keep translation independent from site rendering internals.
- Make cache keys deterministic.

## Acceptance Criteria

- For each book, the translation layer can produce or retrieve `es`, `fr`, and `de` summaries.
- Invalid LLM JSON is not accepted silently.
- Repair is attempted before retrying malformed LLM responses.
- 429 and transient failures trigger retry/backoff.
- Rendering continues with English summaries when translation ultimately fails.
- Book pages include Spain, France, and Germany flag controls.
- Clicking a flag switches to the matching translated summary when available.

## Edge Cases

- LLM returns extra prose around JSON.
- LLM omits one target language.
- LLM returns invalid JSON repeatedly.
- API key is missing.
- Provider times out or disconnects.
- Translation cache file is missing, empty, or malformed.
- Book description changes after a previous cache entry.

## Out of Scope

- Translating chapter or section titles.
- Translating full book content.
- Browser-side calls to the LLM API.
- Supporting multiple translation providers unless needed by the selected provider abstraction.

## Dependencies

- `httpx`
- `python-dotenv`
- Existing `translation/` package
- Static renderer from Feature 001

## Open Questions

- Which final production LLM provider and model will be used for translation? The implementation may use OpenAI-compatible configuration defaults while keeping provider/model configurable.
- Should cache entries include a prompt version in addition to provider/model/source hash?
- Should missing API credentials block translation only, or should they emit an explicit warning and render English-only output?
