---
id: TASK-TRS-001
title: "Add youtube-transcript-api dependency to pyproject.toml"
task_type: scaffolding
parent_review: TASK-REV-9AD6
feature_id: FEAT-SKEL-003
status: pending
priority: high
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
tags: [dependency, scaffolding, transcript]
estimated_minutes: 10
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
