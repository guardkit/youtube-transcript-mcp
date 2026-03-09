---
autobuild_state:
  base_branch: main
  current_turn: 1
  last_updated: '2026-03-09T14:37:01.528450'
  max_turns: 25
  started_at: '2026-03-09T14:31:41.937874'
  turns:
  - coach_success: true
    decision: approve
    feedback: null
    player_success: true
    player_summary: Implementation via task-work delegation
    timestamp: '2026-03-09T14:31:41.937874'
    turn: 1
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-2AAA
complexity: 4
created: 2026-03-06 00:00:00+00:00
dependencies:
- TASK-VID-001
feature_id: FEAT-SKEL-002
id: TASK-VID-002
implementation_mode: task-work
parent_review: TASK-REV-7005
priority: high
status: design_approved
tags:
- service
- yt-dlp
- async
- feat-skel-002
task_type: feature
title: Create YouTubeClient service with URL parser and yt-dlp wrapper
updated: 2026-03-06 00:00:00+00:00
wave: 1
---

# Task: Create YouTubeClient service with URL parser and yt-dlp wrapper

## Description

Create `src/services/youtube_client.py` implementing:
- `extract_video_id()` — URL parsing utility supporting 5+ YouTube URL formats
- `VideoInfo` dataclass — structured video metadata container
- `YouTubeClient` class — async wrapper around sync yt-dlp `extract_info`
- Custom exceptions: `YouTubeClientError`, `VideoNotFoundError`, `InvalidURLError`

## Acceptance Criteria

- [ ] `extract_video_id()` handles: standard watch URLs, youtu.be short URLs, embed URLs, mobile URLs, bare 11-char video IDs
- [ ] `extract_video_id()` raises `InvalidURLError` for unrecognized formats
- [ ] `VideoInfo` dataclass contains: video_id, title, channel, channel_id, duration_seconds, duration_formatted, description_snippet, view_count, upload_date, thumbnail_url, has_captions, has_auto_captions, available_languages
- [ ] `YouTubeClient.get_video_info()` uses `asyncio.to_thread()` for non-blocking execution
- [ ] `CancelledError` is caught, logged, and re-raised (never swallowed)
- [ ] `yt_dlp.utils.DownloadError` mapped to `VideoNotFoundError`
- [ ] `_format_duration()` handles None, seconds-only, minutes, and hours
- [ ] `_truncate()` truncates description to 500 chars with ellipsis
- [ ] `src/services/__init__.py` exists as package marker
- [ ] Code passes `ruff check` and `mypy`

## Key Patterns

- **Async wrapper**: `await asyncio.to_thread(self._sync_get_info, video_url, video_id)`
- **CancelledError**: Catch, log to stderr, re-raise
- **Structured exceptions**: Custom hierarchy for error categorization
- **yt-dlp options**: `quiet=True, no_warnings=True, skip_download=True`

## Implementation Notes

See feature spec: `docs/features/FEAT-SKEL-002-video-info-tool.md` for complete implementation code.

File location: `src/services/youtube_client.py`
Also create: `src/services/__init__.py`