---
complexity: 5
dependencies:
- TASK-TRS-001
estimated_minutes: 90
feature_id: FEAT-SKEL-003
id: TASK-TRS-002
implementation_mode: task-work
parent_review: TASK-REV-9AD6
priority: high
status: design_approved
tags:
- service
- transcript
- async
- feature
task_type: feature
title: Create TranscriptClient service
wave: 2
---

# Task: Create TranscriptClient Service

## Objective

Create `src/services/transcript_client.py` implementing the `TranscriptClient` class with async transcript fetching, intelligent language fallback, and structured error handling. This follows the established service layer pattern from FEAT-SKEL-002 (YouTubeClient).

## Acceptance Criteria

- [ ] `TranscriptClient` class created in `src/services/transcript_client.py`
- [ ] `get_transcript()` async method fetches transcript with language fallback
- [ ] `list_transcripts()` async method lists available transcripts
- [ ] Language fallback strategy: requested -> auto-generated -> English -> first available
- [ ] Custom exceptions: `TranscriptClientError`, `TranscriptsDisabledError`, `NoTranscriptFoundError`, `VideoUnavailableError`
- [ ] `TranscriptResult` and `TranscriptSegment` dataclasses for structured responses
- [ ] Async wrappers use `asyncio.to_thread()` for sync youtube-transcript-api calls
- [ ] CancelledError caught, logged, and re-raised (never swallowed)
- [ ] All logging to stderr via `logging.getLogger(__name__)`

## Implementation Details

### File: `src/services/transcript_client.py`

Follow the code in the feature spec at `docs/features/FEAT-SKEL-003-transcript-tool.md` lines 29-262.

Key patterns to apply:
1. **Async wrapper**: `asyncio.to_thread(self._sync_get_transcript, video_id, language)`
2. **CancelledError**: Catch, log, re-raise in both async methods
3. **Language fallback**: 4-step strategy in `_fetch_with_fallback()`
4. **Structured results**: `TranscriptResult` dataclass with segments and full_text
5. **Exception hierarchy**: Base `TranscriptClientError` with specific subclasses

### Critical MCP Patterns

| Pattern | Application |
|---------|------------|
| stderr logging | `logger = logging.getLogger(__name__)` |
| Async wrappers | `asyncio.to_thread()` for all sync API calls |
| CancelledError | Catch, log, re-raise in `get_transcript()` and `list_transcripts()` |
| Error boundaries | Custom exception hierarchy maps to structured error responses |

### youtube-transcript-api v1.2+ API

```python
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en'])  # FetchedTranscript
transcript_list = api.list(video_id)                 # TranscriptList (iterable)
```

## Verification

```bash
python -c "from src.services.transcript_client import TranscriptClient, TranscriptResult; print('OK')"
ruff check src/services/transcript_client.py
mypy src/services/transcript_client.py
```

## Implementation Notes

- `NoTranscriptFoundError` includes `available_languages` list for caller context
- `_build_result()` calculates `total_segments`, `total_duration_seconds`, and `full_text` from transcript snippets
- `_sync_list_transcripts()` returns empty list (not exception) when transcripts unavailable