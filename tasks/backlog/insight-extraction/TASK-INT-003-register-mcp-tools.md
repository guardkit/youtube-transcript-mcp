---
id: TASK-INT-003
title: Register extract_insights and list_focus_areas MCP tools
task_type: feature
parent_review: TASK-REV-A880
feature_id: FEAT-INT-001
wave: 3
implementation_mode: task-work
complexity: 4
dependencies:
- TASK-INT-002
status: in_review
priority: high
tags:
- insight-extraction
- mcp-tools
- tool-registration
consumer_context:
- task: TASK-INT-001
  consumes: insight_models
  framework: Pydantic v2 (BaseModel, Field, Enum)
  driver: pydantic>=2.0
  format_note: FOCUS_PRESETS and CATEGORY_DEFINITIONS importable from src.models.insight
- task: TASK-INT-002
  consumes: extraction_service
  framework: Python module import
  driver: src.services.insight_extractor
  format_note: prepare_for_extraction and get_focus_categories importable from src.services.insight_extractor
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-87A6
  base_branch: main
  started_at: '2026-03-09T22:58:45.320036'
  last_updated: '2026-03-09T23:04:45.995994'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-09T22:58:45.320036'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Register extract_insights and list_focus_areas MCP Tools

## Description

Add two MCP tools to `src/__main__.py`:
1. `extract_insights` — accepts transcript text and focus areas, returns structured extraction metadata with prompt
2. `list_focus_areas` — returns all available focus presets with their category definitions

Both tools must follow MCP patterns: module-level registration, string parameters, structured error responses.

## Acceptance Criteria

- [ ] `extract_insights` tool registered at module level in `__main__.py`
- [ ] Accepts parameters: transcript (str), focus_areas (str, comma-separated), video_id (str), max_insights (str)
- [ ] Validates focus areas against known presets + 'all'
- [ ] Returns structured error for invalid focus areas (INVALID_FOCUS_AREA)
- [ ] Returns structured error for transcripts < 100 chars (TRANSCRIPT_TOO_SHORT)
- [ ] Converts max_insights from string to int (MCP string parameter pattern)
- [ ] Returns extraction metadata dict from `prepare_for_extraction`
- [ ] `list_focus_areas` tool registered at module level
- [ ] Returns all 6 presets with their categories and category definitions
- [ ] Both tools have comprehensive docstrings for Claude tool discovery
- [ ] Structured error responses follow `{"error": {"category", "code", "message"}}` pattern
- [ ] Code passes `ruff check` and `mypy`

## Seam Tests

The following seam tests validate the integration contracts with producer tasks.

```python
"""Seam test: verify extraction_service contract from TASK-INT-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("extraction_service")
def test_extraction_service_importable():
    """Verify extraction service functions are importable.

    Contract: prepare_for_extraction and get_focus_categories importable from src.services.insight_extractor
    Producer: TASK-INT-002
    """
    from src.services.insight_extractor import (
        prepare_for_extraction,
        get_focus_categories,
        chunk_transcript,
    )

    assert callable(prepare_for_extraction)
    assert callable(get_focus_categories)
    assert callable(chunk_transcript)


@pytest.mark.seam
@pytest.mark.integration_contract("insight_models")
def test_focus_presets_importable():
    """Verify FOCUS_PRESETS importable for tool validation.

    Contract: FOCUS_PRESETS and CATEGORY_DEFINITIONS importable from src.models.insight
    Producer: TASK-INT-001
    """
    from src.models.insight import FOCUS_PRESETS, CATEGORY_DEFINITIONS

    assert "general" in FOCUS_PRESETS
    assert "youtube-channel" in FOCUS_PRESETS
    assert "ai-learning" in FOCUS_PRESETS
```

## Implementation Notes

Reference the complete tool code in `docs/features/FEAT-INT-001-insight-extraction.md` lines 465-595.

Critical MCP patterns:
- **Module-level `@mcp.tool()` decorator** — tools registered at import time
- **String parameters** — `max_insights` arrives as `"10"` not `10`
- **stderr logging** — never `print()` to stdout
- **Structured errors** — consistent `{"error": {"category", "code", "message"}}` format
