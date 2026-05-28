# Reports Directory

This directory contains implementation reports after each feature or milestone.

## Purpose

Reports record what changed, why it changed, and how it was validated. They become durable context for future AI coding agents and reviewers.

Reports should be factual. They should not claim behavior that was not implemented or validation that was not run.

## Naming Convention

Use the matching feature number and kebab-case feature name:

```text
001-feature-name-implementation-report.md
002-feature-name-implementation-report.md
003-feature-name-implementation-report.md
```

Examples:

```text
001-static-renderer-implementation-report.md
002-llm-summary-translation-implementation-report.md
003-batch-processing-implementation-report.md
```

For this project, reports should always mention:

- Whether source code, docs, templates, static assets, or generated output changed.
- Whether generated output was inspected in a local browser when UI was affected.
- Whether validation was run on macOS/Linux only or also checked on Windows.
- Whether any LLM calls were made or skipped.

## Required Report Format

```markdown
# Implementation Report: Feature Name

## Related Spec

## Related Plan

## Related Tasks

## Summary

## What Changed

## Files Changed

## Requirement Coverage

| Requirement | Status | Notes |
|---|---|---|

## Tests Added or Updated

## Validation Commands

## Validation Results

## Known Limitations

## Follow-up Tasks

## Out of Scope
```

## Rules

- Every completed feature should have a report.
- Do not claim validation passed unless commands were actually run.
- Document any skipped validation.
- Reports should be factual and concise.
- Reports become context for future AI work.
- Include exact commands and summarized outcomes.
- Document known limitations instead of hiding them.
- Mention any requirement that remains partially covered or intentionally deferred.
