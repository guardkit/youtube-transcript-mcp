---
autobuild_state:
  base_branch: main
  current_turn: 1
  last_updated: '2026-03-09T14:44:42.403462'
  max_turns: 25
  started_at: '2026-03-09T14:41:12.559858'
  turns:
  - coach_success: true
    decision: approve
    feedback: null
    player_success: true
    player_summary: Implementation via task-work delegation
    timestamp: '2026-03-09T14:41:12.559858'
    turn: 1
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-2AAA
complexity: 3
created: 2026-03-06 00:00:00+00:00
dependencies:
- TASK-VID-002
- TASK-VID-003
feature_id: FEAT-SKEL-002
id: TASK-VID-004
implementation_mode: task-work
parent_review: TASK-REV-7005
priority: high
status: design_approved
tags:
- testing
- unit-tests
- feat-skel-002
task_type: testing
title: Create unit tests for video info tool and YouTube client
updated: 2026-03-06 00:00:00+00:00
wave: 2
---

# Task: Create unit tests for video info tool and YouTube client

## Description

Create `tests/unit/test_video_info.py` with comprehensive unit tests for:
- `extract_video_id()` — all URL formats + error cases
- `YouTubeClient` — mocked yt-dlp responses for happy path
- `_format_duration()` — edge cases (None, seconds, minutes, hours)

All tests use mocked yt-dlp to avoid network calls.

## Acceptance Criteria

- [ ] `TestExtractVideoId`: standard URL, short URL, embed URL, mobile URL, bare ID, URL with extra params
- [ ] `TestExtractVideoId`: invalid URL raises `InvalidURLError`, empty string raises `InvalidURLError`
- [ ] `TestYouTubeClient`: `get_video_info` success path with mocked `_sync_get_info`
- [ ] `TestYouTubeClient`: verifies `video_id`, `title`, `has_captions`, `available_languages` from mock
- [ ] Duration formatting: `None → "0:00"`, `45 → "0:45"`, `212 → "3:32"`, `3661 → "1:01:01"`
- [ ] All tests pass: `pytest tests/unit/test_video_info.py -v`
- [ ] No network calls in unit tests (all yt-dlp mocked)

## Testing Strategy

- **Mocking**: Use `unittest.mock.patch` on `_sync_get_info` to avoid yt-dlp network calls
- **Fixtures**: `mock_yt_dlp_info` fixture provides realistic yt-dlp response dict
- **Async tests**: Use `@pytest.mark.asyncio` for async client methods

## Implementation Notes

See feature spec: `docs/features/FEAT-SKEL-002-video-info-tool.md` for complete test code.

File location: `tests/unit/test_video_info.py`