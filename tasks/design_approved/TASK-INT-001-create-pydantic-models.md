---
complexity: 3
dependencies: []
feature_id: FEAT-INT-001
id: TASK-INT-001
implementation_mode: task-work
parent_review: TASK-REV-A880
priority: high
status: design_approved
tags:
- insight-extraction
- models
- pydantic
task_type: scaffolding
title: Create Pydantic insight models
wave: 1
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