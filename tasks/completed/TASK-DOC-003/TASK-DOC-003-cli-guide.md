---
id: TASK-DOC-003
title: Write CLI guide pages
status: completed
created: 2026-03-10T00:00:00Z
completed: 2026-03-10T12:00:00Z
completed_location: tasks/completed/TASK-DOC-003/
priority: normal
tags: [documentation, mkdocs, cli]
task_type: implementation
complexity: 3
parent_review: TASK-DOC-FCD8
feature_id: FEAT-DOC-MKDOCS
wave: 2
implementation_mode: task-work
dependencies: [TASK-DOC-001]
---

# Task: Write CLI Guide Pages

## Description

Create CLI documentation covering all subcommands, flags, output formats, and practical usage examples including piping and scripting.

## Acceptance Criteria

- [x] `docs/cli/commands.md` - Complete command reference for all 6 subcommands (ping, video-info, get-transcript, list-transcripts, extract-insights, list-focus-areas)
- [x] `docs/cli/examples.md` - Practical examples: basic usage, piping to jq, stdin input, batch processing, shell script integration
- [x] `docs/cli/index.md` updated with CLI overview
- [x] All flags and options match actual CLI implementation in `src/cli.py`

## Source Files to Reference

- `src/cli.py` - CLI implementation (392 lines), all subcommands and flags

## Content Outline

See `.claude/reviews/TASK-DOC-FCD8-review-report.md` for detailed content outlines.

## Test Execution Log

- mkdocs build: SUCCESS (zero warnings for cli/ pages)
- All 6 subcommands documented: ping, video-info, get-transcript, list-transcripts, extract-insights, list-focus-areas
- All flags verified against `src/cli.py` via `make_parser()` introspection
- Acceptance criteria: all met
