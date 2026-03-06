# FEAT-INT-001: Insight Extraction Implementation

## Problem Statement

Users (Brandon and Rich) need to extract actionable insights from YouTube video transcripts. Different users have different needs — entrepreneurial strategy, investment signals, YouTube channel growth tips, AI/ML learning — requiring a flexible preset system that structures extraction for each use case.

## Solution Approach

Implement a **Claude-assisted extraction** pattern where the MCP tool:
1. Accepts transcript text and focus area(s)
2. Resolves focus areas to specific insight categories
3. Builds a structured extraction prompt
4. Handles long transcripts via paragraph-boundary chunking
5. Returns metadata + prompt for Claude to analyze conversationally

This avoids embedding an LLM directly, keeping the server simple while enabling future automation via the `extraction_prompt` field.

## Focus Presets (6 total)

| Preset | Categories | Primary User |
|--------|-----------|-------------|
| `general` | key_point, action_item, notable_quote | Both |
| `entrepreneurial` | business_strategy, growth_tactic, lesson_learned, mistake_to_avoid | Brandon |
| `investment` | market_trend, opportunity, risk, recommendation | Brandon |
| `technical` | technology, tool, best_practice, pitfall | Both |
| `youtube-channel` | channel_strategy, content_idea, audience_growth, production_tip | Rich |
| `ai-learning` | ai_concept, ai_tool, mental_model, practical_application | Rich |

## Subtask Summary

| Task | Title | Type | Complexity | Wave |
|------|-------|------|-----------|------|
| TASK-INT-001 | Create Pydantic insight models | scaffolding | 3/10 | 1 |
| TASK-INT-002 | Implement extraction service | feature | 5/10 | 2 |
| TASK-INT-003 | Register MCP tools | feature | 4/10 | 3 |
| TASK-INT-004 | Create unit tests | testing | 4/10 | 4 |
| TASK-INT-005 | Verify quality gates | testing | 2/10 | 5 |

**Execution**: Sequential (5 waves)
**Approach**: Direct spec implementation
**Testing**: Standard (>80% coverage, ruff, mypy)
**Total estimated effort**: 4-5 hours

## Dependencies

- **FEAT-SKEL-003** (Transcript Tool) — provides transcript text input
- **pydantic>=2.0** — model validation (add to pyproject.toml if not present)

## Files Created/Modified

```
src/
├── models/
│   ├── __init__.py           # NEW
│   └── insight.py            # NEW: Pydantic models + presets
├── services/
│   └── insight_extractor.py  # NEW: extraction service
└── __main__.py               # MODIFIED: + extract_insights, list_focus_areas

tests/
└── unit/
    └── test_insights.py      # NEW: comprehensive unit tests
```

## Review Origin

- **Review task**: TASK-REV-A880
- **Feature spec**: docs/features/FEAT-INT-001-insight-extraction.md
- **Approach selected**: Option 1 — Direct Spec Implementation
