# Tasks Directory

This directory contains small implementation tasks derived from implementation plans.

## Purpose

Tasks break an implementation plan into small, safe, reviewable units of work. They help AI coding agents make focused changes without drifting into unrelated implementation.

Each task should be independently understandable and should include clear validation expectations.

## Naming Convention

Use the matching plan number and kebab-case feature name:

```text
001-feature-name-tasks.md
002-feature-name-tasks.md
003-feature-name-tasks.md
```

Examples:

```text
001-static-renderer-tasks.md
002-llm-summary-translation-tasks.md
003-batch-processing-tasks.md
```

For this project, task names should stay aligned to the implementation order:

1. Static rendering foundation.
2. LLM summary translation.
3. Batch processing and watcher behavior.
4. Polish, documentation, and final validation.

## Required Task Format

```markdown
# Tasks: Feature Name

## Related Spec

## Related Plan

## Task List

### Task 1: Task Name

Goal:

Files to inspect:

Files to modify:

Implementation details:

Tests required:

Validation command:

Acceptance criteria:

Risk:
```

## Rules

- Each task should be small enough to review independently.
- AI agents should implement only one task at a time.
- Do not combine unrelated tasks.
- Do not implement future tasks early.
- Each task should include validation.
- A task should name expected files to inspect and modify.
- A task should document whether docs or reports need updates.
- If a task uncovers missing requirements, pause and update the spec or open questions before expanding scope.
- Do not implement translation or batch behavior while working on a static-renderer-only task unless the task explicitly includes it.
