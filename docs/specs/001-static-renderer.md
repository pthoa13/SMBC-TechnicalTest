# Feature 001: Static Renderer

## Goal

Render BrightLearn JSON into a browsable static website under `rendered/<source-file-stem>/` without requiring the Python application or a running web server to view the generated pages.

## User Stories

- As an SMBC reviewer, I can run the renderer against the sample JSON and open the generated pages locally.
- As a local viewer, I can browse from the dataset index to each book and section page.
- As a future developer, I can trust generated paths and links to work across macOS, Linux, and Windows.

## Functional Requirements

- Load a BrightLearn JSON file from disk.
- Validate and normalize the expected dataset/book/chapter/section structure.
- Render one dataset index page.
- Render one book index page per book.
- Render one section page per section in each book's table of contents.
- Use remote cover image URLs directly.
- Copy bundled CSS, JavaScript, and local static assets into the output folder.
- Generate relative links that work from static files.
- Use safe deterministic slugs for output folders and pages.
- Render every input JSON into `rendered/<source-file-stem>/`.

## Non-functional Requirements

- Use Python 3.12.
- Use `pathlib.Path` for filesystem paths.
- Preserve compatibility with macOS, Linux, and Windows.
- Generated pages should be visually polished, readable, responsive, and navigable.
- Rendering should be deterministic for the same input.

## Acceptance Criteria

- `data/samples/brightlearn_books.json` renders into `rendered/brightlearn_books/`.
- The dataset index lists all 5 sample books.
- Each sample book has a book index page.
- Every section in the sample table of contents has a generated section page.
- Book pages show title, author, cover image, English summary, and table of contents.
- Section pages show book/chapter/section context and link to the original BrightLearn section URL.
- Generated links use browser-safe relative URLs.
- Generated files can be opened locally without running the Python app.

## Edge Cases

- Input filename contains spaces or parentheses.
- Book title contains punctuation or Windows reserved names.
- Two books or sections produce the same slug.
- Optional fields are missing.
- Remote image URL is unavailable at browser time.
- A section has a title and URL but no body text.

## Out of Scope

- LLM translation.
- Batch folder watching.
- Downloading remote images.
- Rendering full section body text not present in the JSON.
- Search functionality.

## Dependencies

- `jinja2`
- `pydantic`
- Existing package layout under `src/brightlearn_site`

## Open Questions

- What exact atomic-write strategy should be used when overwriting an existing output folder?
- Should a render manifest be written for debugging and tests?
