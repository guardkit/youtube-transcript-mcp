---
id: TASK-FSE-005
title: Add internal import path warning
status: backlog
created: 2026-02-03T22:30:00Z
priority: low
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 3
implementation_mode: direct
tags: [documentation, warnings, youtube-transcript-api]
target_files:
  - docs/features/FEAT-SKEL-003-transcript-tool.md
---

# Task: Add Internal Import Path Warning

## Problem

The spec shows importing errors from `youtube_transcript_api._errors`, which is an internal/private module path (indicated by the underscore prefix). While this currently works, internal APIs can change without notice.

## Solution

Add a warning note about the import path stability in FEAT-SKEL-003.

## Content to Add

Add this note after the error import example:

```markdown
### Error Handling Imports

```python
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NoTranscriptAvailable,
)
```

> **Note**: These imports use an internal module path (`_errors`). The underscore
> prefix typically indicates a private API that could change. However, the
> youtube-transcript-api library has kept this interface stable across versions.
> If a future version changes the import path, update accordingly.
>
> Alternative: Wrap imports in try/except for version compatibility:
> ```python
> try:
>     from youtube_transcript_api._errors import TranscriptsDisabled
> except ImportError:
>     from youtube_transcript_api.errors import TranscriptsDisabled  # Future?
> ```
```

## Where to Add

In FEAT-SKEL-003, locate the "Error Types" table (around line 632-639) and add this note directly after the table.

## Acceptance Criteria

- [ ] Warning note added about internal import path
- [ ] Alternative import pattern shown for future-proofing
- [ ] Note explains why this is currently acceptable
