---
id: TASK-DOC-005
title: Write Focus Areas and Troubleshooting pages
status: completed
created: 2026-03-10T00:00:00Z
updated: 2026-03-10T00:00:00Z
completed: 2026-03-10T00:00:00Z
completed_location: tasks/completed/TASK-DOC-005/
priority: normal
tags: [documentation, mkdocs, focus-areas, troubleshooting]
task_type: implementation
complexity: 3
parent_review: TASK-DOC-FCD8
feature_id: FEAT-DOC-MKDOCS
wave: 3
implementation_mode: task-work
dependencies: [TASK-DOC-001]
---

# Task: Write Focus Areas and Troubleshooting Pages

## Description

Create documentation for the 6 focus area presets, the 24-category insight system, and a troubleshooting/FAQ page.

## Acceptance Criteria

- [x] `docs/focus-areas/presets.md` - All 6 presets (general, entrepreneurial, investment, technical, youtube-channel, ai-learning) with categories, descriptions, when to use
- [x] `docs/focus-areas/custom.md` - All 24 InsightCategory values, how the category system works, combining categories
- [x] `docs/troubleshooting.md` - Common errors (TranscriptsDisabled, VideoUnavailable, language not found, server connection issues), FAQ (URL formats, rate limiting, auto vs manual transcripts)
- [x] `docs/focus-areas/index.md` updated with overview

## Source Files to Reference

- `src/models/insight.py` - FocusArea enum (6), InsightCategory enum (24), FOCUS_PRESETS, CATEGORY_DEFINITIONS
- `src/services/transcript_client.py` - Exception types and error messages

## Content Outline

See `.claude/reviews/TASK-DOC-FCD8-review-report.md` for detailed content outlines.

## Test Execution Log

- MkDocs build: SUCCESS (no errors)
- All 4 files created/updated
- Navigation entries verified in mkdocs.yml

## Completion Summary

All documentation pages created with content sourced directly from source code:
- **presets.md**: 6 presets with category tables, descriptions, when-to-use guidance, combining presets
- **custom.md**: All 24 InsightCategory values in grouped tables, combining guide, insight structure schema, output control
- **troubleshooting.md**: 6 error types with JSON examples and solutions, 6 FAQ entries covering URL formats, rate limiting, language fallback, chunking, CLI usage
- **index.md**: Updated overview with preset summary table, usage examples, links to subpages
