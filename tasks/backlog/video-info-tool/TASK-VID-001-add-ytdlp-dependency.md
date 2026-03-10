---
id: TASK-VID-001
title: Add yt-dlp dependency to pyproject.toml
status: in_review
created: 2026-03-06 00:00:00+00:00
updated: 2026-03-06 00:00:00+00:00
priority: high
tags:
- dependency
- configuration
- feat-skel-002
task_type: scaffolding
parent_review: TASK-REV-7005
feature_id: FEAT-SKEL-002
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-2AAA
  base_branch: main
  started_at: '2026-03-09T19:30:56.455153'
  last_updated: '2026-03-09T19:33:48.967568'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-09T19:30:56.455153'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 1173e6090 by <Task pending name=''Task-100'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
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
