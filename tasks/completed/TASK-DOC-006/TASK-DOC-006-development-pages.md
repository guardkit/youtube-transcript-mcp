---
id: TASK-DOC-006
title: Write Development pages
status: completed
created: 2026-03-10T00:00:00Z
updated: 2026-03-10T00:00:00Z
completed: 2026-03-10T00:00:00Z
priority: normal
tags: [documentation, mkdocs, development, contributing]
task_type: implementation
complexity: 3
parent_review: TASK-DOC-FCD8
feature_id: FEAT-DOC-MKDOCS
wave: 3
implementation_mode: task-work
dependencies: [TASK-DOC-001]
previous_state: in_review
completed_location: tasks/completed/TASK-DOC-006/
---

# Task: Write Development Pages

## Description

Create developer-facing documentation covering project architecture, key patterns, and contributing guidelines.

## Acceptance Criteria

- [x] `docs/development/architecture.md` - Project structure tree, component diagram (Mermaid), key patterns (FastMCP, stderr logging, async-first, Pydantic), service layer descriptions
- [x] `docs/development/contributing.md` - Dev setup, running tests (pytest), code quality (ruff, mypy), adding new tools pattern, PR guidelines
- [x] `docs/development/index.md` updated with overview

## Source Files to Reference

- `src/` - Full source directory structure
- `pyproject.toml` - Dev dependencies, ruff/mypy config, test config
- `.claude/CLAUDE.md` - Architectural patterns and anti-patterns

## Content Outline

See `.claude/reviews/TASK-DOC-FCD8-review-report.md` for detailed content outlines.

## Test Execution Log

[Automatically populated by /task-work]
