---
id: TASK-INT-001
title: Create Pydantic insight models
task_type: scaffolding
parent_review: TASK-REV-A880
feature_id: FEAT-INT-001
wave: 1
implementation_mode: task-work
complexity: 3
dependencies: []
status: in_review
priority: high
tags:
- insight-extraction
- models
- pydantic
autobuild_state:
  current_turn: 2
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-87A6
  base_branch: main
  started_at: '2026-03-09T22:42:16.877473'
  last_updated: '2026-03-09T22:50:58.326500'
  turns:
  - turn: 1
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `InsightCategory` enum\
      \ defines 24 categories across all 6 focus areas (4 per focus area)"
    timestamp: '2026-03-09T22:42:16.877473'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
  - turn: 2
    decision: approve
    feedback: null
    timestamp: '2026-03-09T22:47:55.290359'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Create Pydantic Insight Models

## Description

Create `src/models/insight.py` with all Pydantic models and enums for the insight extraction feature. This includes the `FocusArea` enum (6 presets), `InsightCategory` enum (24 categories), `Insight` model, `KeyQuote` model, `InsightExtractionResult` model, and the `FOCUS_PRESETS` and `CATEGORY_DEFINITIONS` mappings.

## Acceptance Criteria

- [ ] `src/models/__init__.py` exists
- [ ] `src/models/insight.py` defines `FocusArea` enum with 6 values: general, entrepreneurial, investment, technical, youtube-channel, ai-learning
- [ ] `InsightCategory` enum defines 24 categories across all 6 focus areas (4 per focus area)
- [ ] `Insight` model has: category, title (max 100), summary (max 500), quote (optional, max 300), timestamp_hint, confidence (0-1), actionable
- [ ] `KeyQuote` model has: text (max 300), context (max 200), speaker (optional)
- [ ] `InsightExtractionResult` model has: video_id, focus_areas, insights, key_quotes, summary, total_insights, processing_note
- [ ] `FOCUS_PRESETS` dict maps each focus area name to its 4 InsightCategory values
- [ ] `CATEGORY_DEFINITIONS` dict provides description strings for all 24 categories
- [ ] All models importable from `src.models.insight`
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

Reference the complete model code in `docs/features/FEAT-INT-001-insight-extraction.md` lines 39-194. The spec provides the exact implementation.

Key patterns:
- Use `str, Enum` for string-based enums
- Use Pydantic `Field` with `max_length`, `ge`, `le` constraints
- Use `Optional[str]` for optional fields with `None` default
