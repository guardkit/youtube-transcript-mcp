---
id: TASK-VID-001
title: "Add yt-dlp dependency to pyproject.toml"
status: pending
created: 2026-03-06T00:00:00Z
updated: 2026-03-06T00:00:00Z
priority: high
tags: [dependency, configuration, feat-skel-002]
task_type: scaffolding
parent_review: TASK-REV-7005
feature_id: FEAT-SKEL-002
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
---

# Task: Add yt-dlp dependency to pyproject.toml

## Description

Add `yt-dlp>=2024.1.0` to the project dependencies in `pyproject.toml`. This is the YouTube metadata extraction library used by the `get_video_info` tool.

## Acceptance Criteria

- [ ] `yt-dlp>=2024.1.0` added to `dependencies` list in `pyproject.toml`
- [ ] `pip install -e ".[dev]"` succeeds without errors
- [ ] `python -c "import yt_dlp; print(yt_dlp.version.__version__)"` runs successfully

## Implementation Notes

Update the dependencies section:

```toml
dependencies = [
    "mcp>=1.0.0",        # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",  # YouTube video metadata extraction
]
```
