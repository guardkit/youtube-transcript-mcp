---
id: TASK-TRS-003
title: "Register get_transcript and list_available_transcripts tools"
task_type: feature
parent_review: TASK-REV-9AD6
feature_id: FEAT-SKEL-003
status: pending
priority: high
wave: 3
implementation_mode: task-work
complexity: 4
dependencies:
  - TASK-TRS-002
tags: [mcp-tool, transcript, registration, feature]
estimated_minutes: 60
consumer_context:
  - task: TASK-TRS-002
    consumes: TranscriptClient
    framework: "FastMCP tool registration"
    driver: "mcp.server.fastmcp"
    format_note: "TranscriptClient must be importable from src.services.transcript_client and instantiable at module level"
---

# Task: Register get_transcript and list_available_transcripts Tools

## Objective

Register two new MCP tools in `src/__main__.py`: `get_transcript` and `list_available_transcripts`. These tools provide thin wrappers around the `TranscriptClient` service, following the same pattern as `get_video_info` from FEAT-SKEL-002.

## Acceptance Criteria

- [ ] `get_transcript` tool registered at module level with `@mcp.tool()`
- [ ] `list_available_transcripts` tool registered at module level with `@mcp.tool()`
- [ ] `get_transcript` accepts `video_url` (required) and `language` (default: "en") parameters
- [ ] `list_available_transcripts` accepts `video_url` parameter
- [ ] Both tools use `extract_video_id()` from YouTubeClient for URL parsing
- [ ] Structured error responses with category/code/message format
- [ ] Error codes: INVALID_URL, TRANSCRIPTS_DISABLED, NO_TRANSCRIPT_FOUND, VIDEO_UNAVAILABLE, INTERNAL_ERROR
- [ ] `TranscriptClient` instantiated at module level (singleton pattern)

## Implementation Details

### Add to `src/__main__.py`

Follow the code in the feature spec at `docs/features/FEAT-SKEL-003-transcript-tool.md` lines 266-428.

Key patterns:
1. **Module-level registration**: Both `@mcp.tool()` decorators at module level
2. **Thin wrappers**: Tools call TranscriptClient methods, handle exceptions, format responses
3. **URL extraction**: Reuse `extract_video_id()` from `src/services/youtube_client.py`
4. **Error mapping**: Each TranscriptClient exception maps to a structured error response

### Tool Response Formats

**get_transcript success:**
```python
{
    "video_id": "...",
    "language": "English",
    "language_code": "en",
    "is_auto_generated": False,
    "segments": [{"start": 0.0, "duration": 2.5, "text": "..."}],
    "full_text": "...",
    "total_segments": 42,
    "total_duration_seconds": 300.5,
}
```

**list_available_transcripts success:**
```python
{
    "video_id": "...",
    "transcripts": [{"language": "English", "language_code": "en", "is_generated": False}],
    "count": 3,
}
```

### Critical MCP Patterns

| Pattern | Application |
|---------|------------|
| Module-level tools | `@mcp.tool()` at module level only |
| String parameters | Parameters arrive as strings from MCP |
| Structured errors | `{"error": {"category": "...", "code": "...", "message": "..."}}` |
| stderr logging | Never print to stdout |

## Seam Tests

The following seam test validates the integration contract with the producer task. Implement this test to verify the boundary before integration.

```python
"""Seam test: verify TranscriptClient contract from TASK-TRS-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("TranscriptClient")
def test_transcript_client_importable():
    """Verify TranscriptClient is importable and instantiable.

    Contract: TranscriptClient must be importable from src.services.transcript_client
    and instantiable at module level.
    Producer: TASK-TRS-002
    """
    from src.services.transcript_client import TranscriptClient

    client = TranscriptClient()
    assert client is not None
    assert hasattr(client, 'get_transcript')
    assert hasattr(client, 'list_transcripts')
```

## Verification

```bash
python -c "from src.__main__ import mcp; print('Tools registered')"
ruff check src/__main__.py
mypy src/__main__.py
```

## Implementation Notes

- `transcript_client = TranscriptClient()` should be at module level alongside other client instantiations
- `logger.exception()` used for unexpected errors to capture stack traces
- `NO_TRANSCRIPT_FOUND` error includes `available_languages` field for caller guidance
