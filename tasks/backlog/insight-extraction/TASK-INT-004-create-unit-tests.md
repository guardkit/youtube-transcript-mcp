---
id: TASK-INT-004
title: "Create unit tests for insight extraction"
task_type: testing
parent_review: TASK-REV-A880
feature_id: FEAT-INT-001
wave: 4
implementation_mode: task-work
complexity: 4
dependencies:
  - TASK-INT-003
status: pending
priority: high
tags: [insight-extraction, testing, unit-tests]
---

# Task: Create Unit Tests for Insight Extraction

## Description

Create `tests/unit/test_insights.py` with comprehensive unit tests covering:
- Focus preset definitions (all 6 presets, all 24 categories)
- `get_focus_categories` function (single, multiple, all, unknown, deduplication)
- Transcript chunking (short, long, overlap, paragraph boundaries)
- Prompt building (includes transcript, categories, max_insights)
- `prepare_for_extraction` (required fields, chunking detection, video_id)
- Insight Pydantic model validation (valid, with quote, confidence bounds)

## Acceptance Criteria

- [ ] `tests/unit/test_insights.py` created
- [ ] `TestFocusPresets` class: tests general preset, entrepreneurial preset, all categories have definitions
- [ ] `TestGetFocusCategories` class: tests single area, multiple areas, 'all', unknown fallback, deduplication
- [ ] `TestChunkTranscript` class: tests short transcript (single chunk), long transcript (multiple chunks), overlap, paragraph boundaries
- [ ] `TestBuildExtractionPrompt` class: tests transcript inclusion, category descriptions, max_insights
- [ ] `TestPrepareForExtraction` class: tests required fields, chunking detection, video_id inclusion
- [ ] `TestInsightModel` class: tests valid insight, insight with quote, confidence bounds validation
- [ ] Tests cover all 6 focus presets: general, entrepreneurial, investment, technical, youtube-channel, ai-learning
- [ ] All tests pass with `pytest tests/unit/test_insights.py -v`
- [ ] Coverage >80% on `src/models/insight.py` and `src/services/insight_extractor.py`

## Implementation Notes

Reference the complete test code in `docs/features/FEAT-INT-001-insight-extraction.md` lines 597-778.

The spec provides a comprehensive test suite. Additional tests to consider:
- Test `youtube-channel` preset has CHANNEL_STRATEGY, CONTENT_IDEA, AUDIENCE_GROWTH, PRODUCTION_TIP
- Test `ai-learning` preset has AI_CONCEPT, AI_TOOL, MENTAL_MODEL, PRACTICAL_APPLICATION
- Test edge case: empty transcript list for chunking
- Test edge case: very long single paragraph exceeding max_chars
