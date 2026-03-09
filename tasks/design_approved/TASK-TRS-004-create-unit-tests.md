---
complexity: 4
dependencies:
- TASK-TRS-002
- TASK-TRS-003
estimated_minutes: 60
feature_id: FEAT-SKEL-003
id: TASK-TRS-004
implementation_mode: task-work
parent_review: TASK-REV-9AD6
priority: high
status: design_approved
tags:
- testing
- transcript
- unit-tests
task_type: testing
title: Create unit tests for transcript tools
wave: 4
---

# Task: Create Unit Tests for Transcript Tools

## Objective

Create comprehensive unit tests in `tests/unit/test_transcript.py` covering TranscriptClient service, tool registration, and error handling. Tests must mock the youtube-transcript-api to avoid external dependencies.

## Acceptance Criteria

- [ ] `tests/unit/test_transcript.py` created with test classes
- [ ] Happy path: successful transcript fetch with correct result structure
- [ ] Language fallback: auto-generated fallback when manual not found
- [ ] Error cases: TranscriptsDisabledError, VideoUnavailableError, NoTranscriptFoundError
- [ ] `_build_result()` correctly calculates totals (segments, duration, full_text)
- [ ] `TranscriptSegment` dataclass creation verified
- [ ] `list_transcripts()` returns correct format
- [ ] All tests pass with `pytest tests/unit/test_transcript.py -v`
- [ ] Coverage >80% for `src/services/transcript_client.py`

## Implementation Details

### File: `tests/unit/test_transcript.py`

Follow the test code in the feature spec at `docs/features/FEAT-SKEL-003-transcript-tool.md` lines 431-553.

### Test Classes

**TestTranscriptClient**:
- `test_get_transcript_success` — Mock successful `api.fetch()`, verify TranscriptResult fields
- `test_get_transcript_fallback_to_auto_generated` — Mock `NoTranscriptFound` from fetch, then fallback via `api.list()`
- `test_get_transcript_disabled_raises` — Mock `TranscriptsDisabled`, verify `TranscriptsDisabledError` raised
- `test_build_result_calculates_totals` — Verify segment count, total duration, full text concatenation

**TestTranscriptSegment**:
- `test_segment_creation` — Verify dataclass fields

### Mock Strategy

```python
@dataclass
class MockSnippet:
    start: float
    duration: float
    text: str

@dataclass
class MockTranscript:
    language: str
    language_code: str
    is_generated: bool
    snippets: list
```

Use `unittest.mock.patch` to mock `client.api.fetch()` and `client.api.list()`.

### Critical Testing Patterns

| Pattern | Application |
|---------|------------|
| Async tests | `@pytest.mark.asyncio async def test_...()` |
| Mock external deps | `patch.object(client.api, 'fetch', ...)` |
| Fixtures | `@pytest.fixture def mock_transcript()` |
| Exception testing | `with pytest.raises(TranscriptsDisabledError)` |

## Verification

```bash
pytest tests/unit/test_transcript.py -v
pytest tests/unit/test_transcript.py --cov=src/services/transcript_client --cov-report=term
```

## Implementation Notes

- Mock objects must match youtube-transcript-api v1.2+ response structure (`.snippets`, `.language`, `.language_code`, `.is_generated`)
- `NoTranscriptFound` constructor takes `(video_id, requested_language_codes, transcript_data)` — check current API
- Use `MagicMock` for transcript list iteration (`__iter__`)