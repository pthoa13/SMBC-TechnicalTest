# Specs Directory

This directory contains feature-level specifications.

## Purpose

Specs are the source of truth for what should be built. They describe the user-visible behavior, business rules, acceptance criteria, constraints, and open questions for a feature before implementation begins.

For this project, specs should stay grounded in the SMBC BrightLearn requirements:

- Static site generation from BrightLearn JSON.
- Summary translation into Spanish, French, and German.
- Batch processing from `batch-process/`.
- Cross-platform operation on macOS, Linux, and Windows.
- Brave browser compatibility on Windows.

## Naming Convention

Use a numeric prefix and a short kebab-case feature name:

```text
001-feature-name.md
002-feature-name.md
003-feature-name.md
```

Examples:

```text
001-static-renderer.md
002-llm-summary-translation.md
003-batch-processing.md
```

Example feature split for the current project:

- `001-static-renderer.md`: render dataset, book, and section pages from BrightLearn JSON.
- `002-llm-summary-translation.md`: translate book summaries and expose flag-based switching.
- `003-batch-processing.md`: watch `batch-process/` and render compatible JSON drops.

## Required Spec Format

```markdown
# Feature XXX: Feature Name

## Goal

## User Stories

## Functional Requirements

## Non-functional Requirements

## Acceptance Criteria

## Edge Cases

## Out of Scope

## Dependencies

## Open Questions
```

## Rules

- Every feature must have a spec before implementation.
- Specs should describe what and why, not low-level implementation details.
- Acceptance criteria must be testable.
- If requirements change, update the spec before changing code.
- Do not invent business requirements that are not present in the project specs.
- Mark unclear requirements as assumptions or open questions.
- Keep specs focused. Split large features into smaller specs when acceptance criteria become hard to validate.
- Project specs should explicitly state whether generated output must work from direct local file opening, because this project currently requires static output that does not depend on a running Python app.
