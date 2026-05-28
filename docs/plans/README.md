# Plans Directory

This directory contains technical implementation plans derived from feature specs.

## Purpose

Plans translate feature specs into practical technical design. A plan should explain how a feature will be implemented, which files are affected, how errors and security concerns will be handled, and how the work will be validated.

Plans are not a substitute for specs. A spec says what should be built and why. A plan says how the project will implement it.

## Naming Convention

Use the matching spec number and kebab-case feature name:

```text
001-feature-name-plan.md
002-feature-name-plan.md
003-feature-name-plan.md
```

Examples:

```text
001-static-renderer-plan.md
002-llm-summary-translation-plan.md
003-batch-processing-plan.md
```

For this project, a plan should explicitly call out:

- Cross-platform `Path` handling when reading inputs or writing generated files.
- Whether the feature affects `rendered/<source-file-stem>/`.
- Whether translation failure should block rendering or fall back to English.
- Whether manual browser QA is required.

## Required Plan Format

```markdown
# Implementation Plan: Feature Name

## Related Spec

## Overview

## Files to Inspect

## Files to Create

## Files to Modify

## Data Model Changes

## API Changes

## Business Logic Flow

## Error Handling

## Security Considerations

## Test Strategy

## Step-by-step Implementation Plan

## Risks

## Open Questions
```

## Rules

- Do not implement before a plan exists.
- Plans must be reviewed before coding.
- Plans must keep changes small and incremental.
- Plans must include tests and validation strategy.
- Plans must identify source files and documentation files likely to change.
- Plans must mention cross-platform path handling when filesystem behavior is involved.
- Plans must document any new dependency before it is added.
- Plans should avoid unrelated refactors.
- Plans should not introduce a server runtime unless a future spec changes the static-output requirement.
