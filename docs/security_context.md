# Security Context

## Security Principles

- Use least privilege for filesystem access, external API credentials, and runtime behavior.
- Be secure by default.
- Validate all external input before use.
- Protect sensitive data and secrets.
- Do not expose secrets in source code, generated output, logs, tests, or documentation examples.
- Treat LLM output as untrusted data.
- Fail safely and provide graceful degradation where possible.

## Sensitive Data

Known or possible sensitive data based on current specs:

- LLM API keys and provider credentials.
- Local `.env` values.
- Potentially unpublished future BrightLearn JSON files dropped into `batch-process/`.
- Logs that may include filenames, book titles, provider errors, or operational context.

TBD - confirm whether future datasets may contain personal, financial, health, authentication, or business-sensitive data. The current sample appears to be book metadata, but future inputs should still be handled cautiously.

## Secrets Management

- Never hardcode secrets.
- Never commit `.env` files.
- Never log secrets.
- Use environment variables or secret management for API credentials.
- Keep `.env.example` limited to placeholder values.
- Do not write secrets into generated HTML.
- Do not include secrets in test fixtures.
- Do not paste tokens into ADRs, reports, or implementation plans.

## Authentication and Authorization

Authentication and authorization are not required by the current specs. The current project requirements describe a local static site generator and batch processor, not a multi-user application.

Current assumptions:

- No user accounts are required.
- No roles or permissions are defined.
- No sessions, cookies, or access tokens are needed for generated static pages.
- LLM provider authentication is handled through server-side/local environment configuration, never browser-side JavaScript.

TBD only if future hosted or multi-user requirements are added:

- Identity model.
- User roles.
- Permission boundaries.
- Session or token handling.
- Access control for any hosted version of generated output.

## Data Access Rules

The current project processes local files rather than user-scoped database records.

Rules:

- Only process files intentionally provided through the configured input path or `batch-process/`.
- Do not recursively process unrelated directories.
- Do not read arbitrary files based on untrusted JSON content.
- Do not follow user-controlled paths from JSON fields when writing output.
- Generated output paths must come from safe slugs and configured output roots.
- Batch processing should ignore temporary, partial, hidden, or unsupported files where practical.
- If a future multi-user or hosted mode is added, data access must be scoped to the current user or tenant.

## Input Validation

### JSON Files

- Parse JSON using structured parsers, not ad hoc string manipulation.
- Validate top-level schema before rendering.
- Validate required fields such as `books`, `book_title`, `cover_image_url`, `author`, `description`, and `table_of_contents`.
- Validate nested chapter and section structures.
- Reject or safely handle unexpected data types.

### Uploaded or Dropped Files

- Only process `.json` files in the configured batch folder.
- Wait until file size is stable before processing.
- Do not execute file contents.
- Do not treat filenames as safe output paths without slugging and normalization.

### External API Payloads

- Validate remote LLM responses before accepting them.
- Do not trust HTTP success alone as proof of valid translation data.
- Treat malformed JSON as a recoverable external-data error, not as valid content.

### Generated HTML

- Escape user/content data through Jinja2 autoescaping.
- Be careful when embedding translation JSON in HTML or JavaScript.
- Avoid inserting untrusted content with raw HTML unless explicitly sanitized.

### Database Queries

- Not applicable. No database is currently defined.

## External API and LLM Safety

The project requires a remote LLM API for summary translation.

Rules:

- Do not send secrets to the LLM.
- Minimize data sent to the LLM. Send only the book summary and necessary translation instructions.
- Do not send full input JSON files unless a future spec explicitly requires it.
- Validate LLM outputs before using them.
- Do not treat LLM output as trusted code or trusted structured data.
- Do not execute LLM output.
- Require a strict JSON wrapper in prompts.
- Repair malformed JSON conservatively.
- Retry only within configured limits.
- Log external API failures safely without request secrets or raw credentials.
- Handle rate limits and transient failures without crashing the entire render.
- Do not expose LLM API keys to generated static JavaScript.

## Logging and Monitoring

- Logs must not contain secrets or sensitive user data.
- Logs should include enough context for debugging, such as filename, operation, book title, error category, and retry count.
- Logs should be sufficient for local debugging and failure review, including repeated LLM failures or suspicious invalid input.
- Avoid logging full LLM prompts or full responses if future data sensitivity is unclear.
- Avoid logging entire JSON input files.

## Common Security Mistakes to Avoid

- Committing `.env` or API keys.
- Putting LLM API keys in browser JavaScript.
- Trusting LLM output without JSON validation.
- Rendering unescaped user-controlled content as raw HTML.
- Building output paths directly from book titles without slugging.
- Using `../` or absolute paths from input data.
- Processing partially copied files in `batch-process/`.
- Logging full provider request/response bodies with secrets.
- Disabling validation to make malformed fixtures pass.
- Adding a local web server with broad file-serving behavior without a spec.

## Security Rules for AI Agents

- Do not add or disable auth checks unless a future spec introduces authentication.
- Do not bypass validation.
- Do not hardcode credentials.
- Do not expose secrets in logs or tests.
- Do not make data queries or filesystem reads broader than required.
- Do not add insecure shortcuts for development convenience.
- Do not place secrets in generated static output.
- Do not weaken escaping or mark content safe unless sanitization is documented.
- If a security requirement is unclear, document it as an open question.

## Open Security Questions

- Will future input JSON contain private or sensitive unpublished content?
- Which LLM provider will be used, and what data retention policy applies?
- Should translation requests redact or minimize any metadata beyond the summary text?
- Should batch processing archive or quarantine failed files?
- Should generated output include a content security policy if served through a static server?
- Is there any requirement to run the pipeline in CI, and how should secrets be provided there?
