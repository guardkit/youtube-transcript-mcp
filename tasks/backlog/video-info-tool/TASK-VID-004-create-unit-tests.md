---
id: TASK-VID-004
title: Create unit tests for video info tool and YouTube client
status: in_review
created: 2026-03-06 00:00:00+00:00
updated: 2026-03-06 00:00:00+00:00
priority: high
tags:
- testing
- unit-tests
- feat-skel-002
task_type: testing
parent_review: TASK-REV-7005
feature_id: FEAT-SKEL-002
wave: 2
implementation_mode: task-work
complexity: 3
dependencies:
- TASK-VID-002
- TASK-VID-003
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-2AAA
  base_branch: main
  started_at: '2026-03-09T20:03:14.855887'
  last_updated: '2026-03-09T20:06:12.175878'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-09T20:03:14.855887'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
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
