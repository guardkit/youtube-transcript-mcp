---
id: TASK-FSE-002
title: Add CancelledError handling pattern to specs
status: completed
created: 2026-02-03T22:30:00Z
updated: 2026-02-03T23:00:00Z
completed: 2026-02-03T23:05:00Z
priority: medium
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 2
implementation_mode: direct
tags: [documentation, async, error-handling]
target_files:
  - docs/features/FEAT-SKEL-002-video-info-tool.md
  - docs/features/FEAT-SKEL-003-transcript-tool.md
completed_location: tasks/completed/TASK-FSE-002/
---

# Task: Add CancelledError Handling Pattern

## Problem

The feature specs show async wrappers using `asyncio.to_thread()` but don't document the critical CancelledError handling pattern. MCP clients may cancel requests, and swallowing CancelledError breaks proper async cancellation.

## Solution

Add CancelledError handling to async methods in FEAT-SKEL-002 and FEAT-SKEL-003.

## Pattern to Add

```python
import asyncio

async def get_video_info(self, url_or_id: str) -> VideoInfo:
    """Fetch video metadata from YouTube."""
    video_id = extract_video_id(url_or_id)
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        return await asyncio.to_thread(self._sync_get_info, video_url, video_id)
    except asyncio.CancelledError:
        logger.info(f"Video info request cancelled for {video_id}")
        raise  # CRITICAL: Must re-raise CancelledError
```

## Changes Required

### FEAT-SKEL-002 (youtube_client.py)

Add to `YouTubeClient.get_video_info()` method:

```python
async def get_video_info(self, url_or_id: str) -> VideoInfo:
    video_id = extract_video_id(url_or_id)
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    try:
        return await asyncio.to_thread(self._sync_get_info, video_url, video_id)
    except asyncio.CancelledError:
        logger.info(f"Video info request cancelled for {video_id}")
        raise  # CRITICAL: Must re-raise
```

### FEAT-SKEL-003 (transcript_client.py)

Add to `TranscriptClient.get_transcript()` method:

```python
async def get_transcript(self, video_id: str, language: str = "en") -> TranscriptResult:
    try:
        return await asyncio.to_thread(self._sync_get_transcript, video_id, language)
    except asyncio.CancelledError:
        logger.info(f"Transcript request cancelled for {video_id}")
        raise  # CRITICAL: Must re-raise
```

Also add to `list_transcripts()` method.

## Implementation Notes Section

Add to both specs under "Implementation Notes":

```markdown
### CancelledError Handling

CRITICAL: Never swallow `asyncio.CancelledError`. When using `asyncio.to_thread()`,
wrap the call to log cancellation but always re-raise:

```python
try:
    result = await asyncio.to_thread(sync_fn, args)
except asyncio.CancelledError:
    logger.info("Request cancelled")
    raise  # Must re-raise!
```

MCP clients may cancel requests at any time. Swallowing CancelledError prevents
proper cleanup and can cause resource leaks.
```

## Acceptance Criteria

- [x] FEAT-SKEL-002 shows CancelledError handling in YouTubeClient
- [x] FEAT-SKEL-003 shows CancelledError handling in TranscriptClient
- [x] Both specs have Implementation Notes explaining why this matters
- [x] Pattern shows logging before re-raise

## Implementation Summary

**Completed 2026-02-03**

### Changes Made

1. **FEAT-SKEL-002-video-info-tool.md**:
   - Updated `get_video_info()` method with try/except for CancelledError
   - Added "CancelledError Handling" section under Implementation Notes

2. **FEAT-SKEL-003-transcript-tool.md**:
   - Updated `get_transcript()` method with try/except for CancelledError
   - Updated `list_transcripts()` method with try/except for CancelledError
   - Added "CancelledError Handling" section under Implementation Notes

All async methods using `asyncio.to_thread()` now demonstrate proper cancellation handling.
