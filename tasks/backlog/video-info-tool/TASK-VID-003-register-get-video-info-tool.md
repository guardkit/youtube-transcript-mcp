---
id: TASK-VID-003
title: "Register get_video_info tool in __main__.py"
status: pending
created: 2026-03-06T00:00:00Z
updated: 2026-03-06T00:00:00Z
priority: high
tags: [mcp-tool, registration, feat-skel-002]
task_type: feature
parent_review: TASK-REV-7005
feature_id: FEAT-SKEL-002
wave: 2
implementation_mode: task-work
complexity: 2
dependencies:
  - TASK-VID-002
consumer_context:
  - task: TASK-VID-002
    consumes: YouTubeClient
    framework: "FastMCP tool registration"
    driver: "mcp.server.fastmcp"
    format_note: "Import YouTubeClient, VideoNotFoundError, InvalidURLError from src.services.youtube_client"
---

# Task: Register get_video_info tool in __main__.py

## Description

Add the `get_video_info` MCP tool to `src/__main__.py` at module level. The tool wraps `YouTubeClient.get_video_info()` with structured error handling, returning video metadata as a dict or structured error responses.

## Acceptance Criteria

- [ ] `get_video_info` tool registered at module level with `@mcp.tool()` decorator
- [ ] Tool accepts `video_url: str` parameter (YouTube URL or video ID)
- [ ] Returns dict with all VideoInfo fields on success
- [ ] Returns structured error `{"error": {"category": "...", "code": "...", "message": "..."}}` on failure
- [ ] `InvalidURLError` → `category: "client_error"`, `code: "INVALID_URL"`
- [ ] `VideoNotFoundError` → `category: "client_error"`, `code: "VIDEO_NOT_FOUND"`
- [ ] Unexpected exceptions → `category: "server_error"`, `code: "INTERNAL_ERROR"`, logged with `logger.exception()`
- [ ] Tool docstring describes accepted URL formats for LLM discovery
- [ ] `YouTubeClient` instantiated at module level (not inside tool function)

## Key Patterns

- **Module-level registration**: `@mcp.tool()` at top level, not inside functions
- **Structured errors**: Category/code/message pattern
- **No stdout**: All logging via logger (stderr)

## Seam Tests

The following seam test validates the integration contract with the producer task. Implement this test to verify the boundary before integration.

```python
"""Seam test: verify YouTubeClient contract from TASK-VID-002."""
import pytest


@pytest.mark.seam
@pytest.mark.integration_contract("YouTubeClient")
def test_youtube_client_import():
    """Verify YouTubeClient can be imported from src.services.youtube_client.

    Contract: Import YouTubeClient, VideoNotFoundError, InvalidURLError from src.services.youtube_client
    Producer: TASK-VID-002
    """
    from src.services.youtube_client import (
        YouTubeClient,
        VideoNotFoundError,
        InvalidURLError,
    )

    assert YouTubeClient is not None, "YouTubeClient must be importable"
    assert issubclass(VideoNotFoundError, Exception), "VideoNotFoundError must be an Exception"
    assert issubclass(InvalidURLError, Exception), "InvalidURLError must be an Exception"
```

## Implementation Notes

See feature spec: `docs/features/FEAT-SKEL-002-video-info-tool.md` for complete tool registration code.

File to modify: `src/__main__.py`
