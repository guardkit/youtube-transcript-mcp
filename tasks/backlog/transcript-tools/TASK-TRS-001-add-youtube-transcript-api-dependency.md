---
id: TASK-TRS-001
title: Add youtube-transcript-api dependency to pyproject.toml
task_type: scaffolding
parent_review: TASK-REV-9AD6
feature_id: FEAT-SKEL-003
status: in_review
priority: high
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
tags:
- dependency
- scaffolding
- transcript
estimated_minutes: 10
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6F80
  base_branch: main
  started_at: '2026-03-09T21:41:29.232597'
  last_updated: '2026-03-09T21:43:38.793812'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-09T21:41:29.232597'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 11adb9fd0 by <Task pending name=''Task-100'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
---

# Task: Add youtube-transcript-api Dependency

## Objective

Add `youtube-transcript-api>=1.0.0` to the project's `pyproject.toml` dependencies list. This library provides the core transcript fetching capability for FEAT-SKEL-003.

## Acceptance Criteria

- [ ] `youtube-transcript-api>=1.0.0` added to `[project.dependencies]` in pyproject.toml
- [ ] `pip install -e ".[dev]"` completes without errors
- [ ] `python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('OK')"` succeeds

## Implementation Details

Add the dependency to the existing dependencies list in `pyproject.toml`:

```toml
dependencies = [
    "mcp>=1.0.0",
    "yt-dlp>=2024.1.0",
    "youtube-transcript-api>=1.0.0",
]
```

## Verification

```bash
pip install -e ".[dev]"
python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('OK')"
python -c "from youtube_transcript_api._errors import TranscriptsDisabled; print('OK')"
```

## Implementation Notes

- The youtube-transcript-api v1.2+ uses instance methods (`api.fetch()`) not class methods
- Error types are in `youtube_transcript_api._errors` (private module but stable interface)
