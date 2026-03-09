---
complexity: 5
consumer_context:
- consumes: insight_models
  driver: pydantic>=2.0
  format_note: All models must be importable from src.models.insight
  framework: Pydantic v2 (BaseModel, Field, Enum)
  task: TASK-INT-001
dependencies:
- TASK-INT-001
feature_id: FEAT-INT-001
id: TASK-INT-002
implementation_mode: task-work
parent_review: TASK-REV-A880
priority: high
status: design_approved
tags:
- insight-extraction
- service
- chunking
- prompt-engineering
task_type: feature
title: Implement insight extraction service
wave: 2
---

# Task: Implement Insight Extraction Service

## Description

Create `src/services/insight_extractor.py` with the core extraction logic. This service structures transcripts for Claude-assisted analysis rather than embedding an LLM directly. It includes focus area resolution, prompt building, and transcript chunking for long content.

## Acceptance Criteria

- [ ] `src/services/__init__.py` exists (if not already)
- [ ] `src/services/insight_extractor.py` implements `get_focus_categories(focus_areas)` function
- [ ] `build_extraction_prompt(transcript, focus_areas, max_insights)` generates structured prompt
- [ ] `chunk_transcript(transcript, max_chars, overlap_chars)` splits long transcripts at paragraph boundaries
- [ ] `prepare_for_extraction(transcript, video_id, focus_areas, max_insights)` returns complete extraction metadata
- [ ] `get_focus_categories` handles 'all' keyword returning all categories
- [ ] `get_focus_categories` falls back to 'general' for unknown focus areas
- [ ] `get_focus_categories` deduplicates when same area specified twice
- [ ] `chunk_transcript` returns single chunk for short transcripts
- [ ] `chunk_transcript` maintains overlap between chunks for context continuity
- [ ] `prepare_for_extraction` returns: extraction_prompt, focus_areas, categories, category_definitions, transcript_length, chunk_count, needs_chunking, max_insights, chunks
- [ ] Prompt includes category descriptions, output format instructions, guidelines
- [ ] Code passes `ruff check` and `mypy`

## Seam Tests

The following seam test validates the integration contract with the producer task. Implement this test to verify the boundary before integration.

```python
"""Seam test: verify insight_models contract from TASK-INT-001."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("insight_models")
def test_insight_models_importable():
    """Verify insight models are importable from src.models.insight.

    Contract: All models must be importable from src.models.insight
    Producer: TASK-INT-001
    """
    from src.models.insight import (
        FocusArea,
        InsightCategory,
        Insight,
        KeyQuote,
        InsightExtractionResult,
        FOCUS_PRESETS,
        CATEGORY_DEFINITIONS,
    )

    assert len(FocusArea) == 6, f"Expected 6 FocusArea values, got {len(FocusArea)}"
    assert len(InsightCategory) == 24, f"Expected 24 InsightCategory values, got {len(InsightCategory)}"
    assert len(FOCUS_PRESETS) == 6, f"Expected 6 presets, got {len(FOCUS_PRESETS)}"
    assert len(CATEGORY_DEFINITIONS) == 24, f"Expected 24 definitions, got {len(CATEGORY_DEFINITIONS)}"
```

## Implementation Notes

Reference the complete service code in `docs/features/FEAT-INT-001-insight-extraction.md` lines 197-463.

Key design decisions:
- **Claude-assisted**: The service prepares prompts and metadata; actual LLM extraction happens at the host level
- **Chunking at paragraph boundaries**: Split on `\n\n` first, fall back to character split for very long paragraphs
- **Overlap**: 500 chars overlap between chunks to maintain context
- **Max chars per chunk**: 30,000 default (well within Claude's context window)