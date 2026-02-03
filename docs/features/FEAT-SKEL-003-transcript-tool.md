# FEAT-SKEL-003: Transcript Fetching Tool

## Overview

Add a tool to fetch YouTube video transcripts using youtube-transcript-api. This completes the walking skeleton's core data retrieval capabilities.

**Complexity**: 5/10  
**Estimated Time**: 4-5 hours  
**Dependencies**: FEAT-SKEL-001 (Basic MCP Server)

## Business Context

Transcript fetching is the core capability for the Brandon collaboration project. This enables extraction of spoken content from YouTube videos for subsequent insight analysis.

## Acceptance Criteria

1. `get_transcript` tool accepts video URL/ID and optional language parameter
2. Returns timestamped segments and full concatenated text
3. Implements intelligent language fallback (requested → auto-generated → English → first available)
4. Returns available languages when requested transcript not found
5. Handles edge cases: disabled transcripts, unavailable videos, no captions
6. Uses async wrapper around sync youtube-transcript-api
7. Unit tests cover happy path, language fallback, and error cases

## Technical Specification

### Transcript Client (`src/services/transcript_client.py`)

```python
"""Transcript client service using youtube-transcript-api."""

import asyncio
import logging
from typing import Optional
from dataclasses import dataclass, field

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NoTranscriptAvailable,
)

logger = logging.getLogger(__name__)


@dataclass
class TranscriptSegment:
    """A single segment of transcript with timing."""
    start: float
    duration: float
    text: str


@dataclass
class TranscriptResult:
    """Complete transcript result."""
    video_id: str
    language: str
    language_code: str
    is_auto_generated: bool
    segments: list[TranscriptSegment] = field(default_factory=list)
    full_text: str = ""
    total_segments: int = 0
    total_duration_seconds: float = 0.0


class TranscriptClientError(Exception):
    """Base exception for transcript client errors."""
    pass


class TranscriptsDisabledError(TranscriptClientError):
    """Transcripts are disabled for this video."""
    pass


class NoTranscriptFoundError(TranscriptClientError):
    """No transcript found for requested language."""
    def __init__(self, message: str, available_languages: list[str] = None):
        super().__init__(message)
        self.available_languages = available_languages or []


class VideoUnavailableError(TranscriptClientError):
    """Video is unavailable."""
    pass


class TranscriptClient:
    """Client for fetching YouTube video transcripts."""
    
    def __init__(self):
        self.api = YouTubeTranscriptApi()
    
    async def get_transcript(
        self, 
        video_id: str, 
        language: str = "en"
    ) -> TranscriptResult:
        """Fetch transcript for a video with language fallback.
        
        Fallback strategy:
        1. Try exact language requested
        2. Try auto-generated version of requested language
        3. Try any English variant
        4. Return first available transcript
        
        Args:
            video_id: YouTube video ID (11 characters)
            language: Preferred language code (default: "en")
            
        Returns:
            TranscriptResult with segments and full text
            
        Raises:
            TranscriptsDisabledError: Transcripts disabled for video
            NoTranscriptFoundError: No transcripts available (includes available languages)
            VideoUnavailableError: Video doesn't exist or is private
        """
        return await asyncio.to_thread(
            self._sync_get_transcript, video_id, language
        )
    
    async def list_transcripts(self, video_id: str) -> list[dict]:
        """List all available transcripts for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of transcript info dicts with language, language_code, is_generated
        """
        return await asyncio.to_thread(self._sync_list_transcripts, video_id)
    
    def _sync_get_transcript(
        self, 
        video_id: str, 
        language: str
    ) -> TranscriptResult:
        """Synchronous transcript fetching with fallback (runs in thread)."""
        try:
            # Try direct fetch first
            transcript = self.api.fetch(video_id, languages=[language])
            return self._build_result(video_id, transcript)
            
        except NoTranscriptFound:
            # Fallback strategy
            return self._fetch_with_fallback(video_id, language)
            
        except TranscriptsDisabled:
            raise TranscriptsDisabledError(
                f"Transcripts are disabled for video: {video_id}"
            )
            
        except VideoUnavailable:
            raise VideoUnavailableError(
                f"Video is unavailable: {video_id}"
            )
            
        except NoTranscriptAvailable:
            raise NoTranscriptFoundError(
                f"No transcripts available for video: {video_id}",
                available_languages=[]
            )
    
    def _fetch_with_fallback(
        self, 
        video_id: str, 
        preferred_language: str
    ) -> TranscriptResult:
        """Try fallback languages when preferred not found."""
        try:
            transcript_list = self.api.list(video_id)
            available = []
            
            # Collect available transcripts
            for t in transcript_list:
                available.append({
                    'language': t.language,
                    'language_code': t.language_code,
                    'is_generated': t.is_generated,
                })
            
            # Strategy 1: Auto-generated version of preferred language
            for t in transcript_list:
                if t.is_generated and t.language_code.startswith(preferred_language):
                    logger.info(f"Using auto-generated {t.language_code} transcript")
                    fetched = t.fetch()
                    return self._build_result(video_id, fetched)
            
            # Strategy 2: Any English variant
            for t in transcript_list:
                if t.language_code.startswith('en'):
                    logger.info(f"Falling back to {t.language_code} transcript")
                    fetched = t.fetch()
                    return self._build_result(video_id, fetched)
            
            # Strategy 3: First available
            for t in transcript_list:
                logger.info(f"Using first available transcript: {t.language_code}")
                fetched = t.fetch()
                return self._build_result(video_id, fetched)
            
            # No transcripts at all
            available_codes = [a['language_code'] for a in available]
            raise NoTranscriptFoundError(
                f"No transcript found for video: {video_id}",
                available_languages=available_codes
            )
            
        except (TranscriptsDisabled, VideoUnavailable, NoTranscriptAvailable):
            raise
    
    def _sync_list_transcripts(self, video_id: str) -> list[dict]:
        """Synchronous transcript listing (runs in thread)."""
        try:
            transcript_list = self.api.list(video_id)
            return [
                {
                    'language': t.language,
                    'language_code': t.language_code,
                    'is_generated': t.is_generated,
                }
                for t in transcript_list
            ]
        except (TranscriptsDisabled, VideoUnavailable, NoTranscriptAvailable):
            return []
    
    def _build_result(self, video_id: str, transcript) -> TranscriptResult:
        """Build TranscriptResult from fetched transcript."""
        segments = [
            TranscriptSegment(
                start=snippet.start,
                duration=snippet.duration,
                text=snippet.text
            )
            for snippet in transcript.snippets
        ]
        
        full_text = " ".join(snippet.text for snippet in transcript.snippets)
        total_duration = sum(s.duration for s in segments)
        
        return TranscriptResult(
            video_id=video_id,
            language=transcript.language,
            language_code=transcript.language_code,
            is_auto_generated=transcript.is_generated,
            segments=segments,
            full_text=full_text,
            total_segments=len(segments),
            total_duration_seconds=total_duration,
        )
```

### Tool Registration (add to `src/__main__.py`)

```python
# Add imports at top
from src.services.transcript_client import (
    TranscriptClient,
    TranscriptsDisabledError,
    NoTranscriptFoundError,
    VideoUnavailableError,
)
from src.services.youtube_client import extract_video_id, InvalidURLError

# Initialize client
transcript_client = TranscriptClient()

@mcp.tool()
async def get_transcript(
    video_url: str,
    language: str = "en"
) -> dict:
    """Fetch transcript for a YouTube video.
    
    Retrieves the transcript/captions for a YouTube video with intelligent
    language fallback. If the requested language isn't available, it tries:
    1. Auto-generated version of requested language
    2. Any English variant
    3. First available transcript
    
    Args:
        video_url: YouTube URL or video ID
        language: Preferred language code (default: "en")
            Common codes: en, es, fr, de, ja, ko, zh-Hans, pt
    
    Returns:
        Dictionary containing:
        - video_id: The YouTube video ID
        - language: Human-readable language name
        - language_code: ISO language code
        - is_auto_generated: Whether this is auto-generated (vs manual)
        - segments: List of {start, duration, text} segments with timestamps
        - full_text: Complete transcript as single string
        - total_segments: Number of segments
        - total_duration_seconds: Total transcript duration
        
        Or error dict if transcript unavailable.
    """
    # Extract video ID from URL
    try:
        video_id = extract_video_id(video_url)
    except InvalidURLError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_URL",
                "message": str(e),
            }
        }
    
    # Fetch transcript
    try:
        result = await transcript_client.get_transcript(video_id, language)
        return {
            "video_id": result.video_id,
            "language": result.language,
            "language_code": result.language_code,
            "is_auto_generated": result.is_auto_generated,
            "segments": [
                {
                    "start": seg.start,
                    "duration": seg.duration,
                    "text": seg.text,
                }
                for seg in result.segments
            ],
            "full_text": result.full_text,
            "total_segments": result.total_segments,
            "total_duration_seconds": result.total_duration_seconds,
        }
        
    except TranscriptsDisabledError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "TRANSCRIPTS_DISABLED",
                "message": str(e),
            }
        }
        
    except NoTranscriptFoundError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "NO_TRANSCRIPT_FOUND",
                "message": str(e),
                "available_languages": e.available_languages,
            }
        }
        
    except VideoUnavailableError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "VIDEO_UNAVAILABLE",
                "message": str(e),
            }
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error fetching transcript: {e}")
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to fetch transcript",
            }
        }


@mcp.tool()
async def list_available_transcripts(video_url: str) -> dict:
    """List all available transcripts for a YouTube video.
    
    Returns information about all available transcripts including
    language codes and whether they are auto-generated or manual.
    Useful for checking what's available before fetching.
    
    Args:
        video_url: YouTube URL or video ID
    
    Returns:
        Dictionary containing:
        - video_id: The YouTube video ID
        - transcripts: List of available transcripts with:
            - language: Human-readable language name
            - language_code: ISO language code
            - is_generated: Whether auto-generated
    """
    try:
        video_id = extract_video_id(video_url)
    except InvalidURLError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_URL",
                "message": str(e),
            }
        }
    
    try:
        transcripts = await transcript_client.list_transcripts(video_id)
        return {
            "video_id": video_id,
            "transcripts": transcripts,
            "count": len(transcripts),
        }
    except Exception as e:
        logger.exception(f"Unexpected error listing transcripts: {e}")
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to list transcripts",
            }
        }
```

### Unit Tests (`tests/unit/test_transcript.py`)

```python
"""Tests for transcript fetching tool and client."""

import pytest
from unittest.mock import patch, MagicMock
from dataclasses import dataclass

from src.services.transcript_client import (
    TranscriptClient,
    TranscriptResult,
    TranscriptSegment,
    TranscriptsDisabledError,
    NoTranscriptFoundError,
)


@dataclass
class MockSnippet:
    """Mock transcript snippet."""
    start: float
    duration: float
    text: str


@dataclass
class MockTranscript:
    """Mock fetched transcript."""
    language: str
    language_code: str
    is_generated: bool
    snippets: list


class TestTranscriptClient:
    """Tests for TranscriptClient."""
    
    @pytest.fixture
    def mock_transcript(self):
        """Create mock transcript response."""
        return MockTranscript(
            language='English',
            language_code='en',
            is_generated=False,
            snippets=[
                MockSnippet(start=0.0, duration=2.5, text="Hello world"),
                MockSnippet(start=2.5, duration=3.0, text="This is a test"),
                MockSnippet(start=5.5, duration=2.0, text="Thank you"),
            ]
        )
    
    @pytest.mark.asyncio
    async def test_get_transcript_success(self, mock_transcript):
        """Should return transcript for valid video."""
        client = TranscriptClient()
        
        with patch.object(client.api, 'fetch', return_value=mock_transcript):
            result = await client.get_transcript('dQw4w9WgXcQ', 'en')
            
            assert result.video_id == 'dQw4w9WgXcQ'
            assert result.language == 'English'
            assert result.language_code == 'en'
            assert result.is_auto_generated is False
            assert result.total_segments == 3
            assert "Hello world" in result.full_text
            assert "This is a test" in result.full_text
    
    @pytest.mark.asyncio
    async def test_get_transcript_fallback_to_auto_generated(self, mock_transcript):
        """Should fall back to auto-generated when manual not found."""
        from youtube_transcript_api._errors import NoTranscriptFound
        
        client = TranscriptClient()
        
        # Mock transcript in list
        mock_transcript_info = MagicMock()
        mock_transcript_info.language = 'English (auto-generated)'
        mock_transcript_info.language_code = 'en'
        mock_transcript_info.is_generated = True
        mock_transcript_info.fetch.return_value = mock_transcript
        
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([mock_transcript_info])
        
        with patch.object(client.api, 'fetch', side_effect=NoTranscriptFound('video_id', [], [])):
            with patch.object(client.api, 'list', return_value=mock_list):
                result = await client.get_transcript('dQw4w9WgXcQ', 'en')
                
                assert result.language_code == 'en'
    
    @pytest.mark.asyncio
    async def test_get_transcript_disabled_raises(self):
        """Should raise TranscriptsDisabledError when disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled
        
        client = TranscriptClient()
        
        with patch.object(client.api, 'fetch', side_effect=TranscriptsDisabled('video_id')):
            with pytest.raises(TranscriptsDisabledError):
                await client.get_transcript('dQw4w9WgXcQ', 'en')
    
    def test_build_result_calculates_totals(self, mock_transcript):
        """Should calculate total segments and duration."""
        client = TranscriptClient()
        
        result = client._build_result('test123', mock_transcript)
        
        assert result.total_segments == 3
        assert result.total_duration_seconds == 7.5  # 2.5 + 3.0 + 2.0
        assert result.full_text == "Hello world This is a test Thank you"


class TestTranscriptSegment:
    """Tests for TranscriptSegment dataclass."""
    
    def test_segment_creation(self):
        segment = TranscriptSegment(start=10.5, duration=3.2, text="Test")
        
        assert segment.start == 10.5
        assert segment.duration == 3.2
        assert segment.text == "Test"
```

### Update `pyproject.toml` Dependencies

```toml
dependencies = [
    "mcp>=1.0.0",
    "yt-dlp>=2024.1.0",
    "youtube-transcript-api>=1.0.0",
]
```

## File Structure After Implementation

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # + get_transcript, list_available_transcripts
│   └── services/
│       ├── __init__.py
│       ├── youtube_client.py    # From FEAT-SKEL-002
│       └── transcript_client.py # NEW: transcript fetching
├── tests/
│   └── unit/
│       ├── test_ping.py
│       ├── test_video_info.py
│       └── test_transcript.py   # NEW: transcript tests
└── pyproject.toml               # + youtube-transcript-api dependency
```

## Testing Strategy

1. **Unit Tests**: Mock youtube-transcript-api responses
2. **Integration Tests**: Test with real video (marked slow)
3. **Manual Testing**: Use MCP Inspector with known video IDs

### Test Videos

| Video | Characteristics |
|-------|----------------|
| `dQw4w9WgXcQ` | Popular, has manual + auto captions |
| `jNQXAC9IVRw` | First YouTube video, simple captions |

## Definition of Done

- [ ] `src/services/transcript_client.py` implements `TranscriptClient`
- [ ] `get_transcript` tool registered in `__main__.py`
- [ ] `list_available_transcripts` tool registered
- [ ] Language fallback strategy works correctly
- [ ] Structured errors for disabled/unavailable transcripts
- [ ] Unit tests pass with mocked API
- [ ] `pyproject.toml` includes youtube-transcript-api
- [ ] Both tools visible in MCP Inspector
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

### youtube-transcript-api v1.2+ Syntax

The API changed in v1.2. Use the instance method pattern:

```python
# CORRECT - v1.2+
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en'])
transcript_list = api.list(video_id)

# OLD - pre-v1.2 (still works but deprecated)
transcript = YouTubeTranscriptApi.get_transcript(video_id)
```

### Transcript Object Structure

```python
# FetchedTranscript object
transcript.language        # "English"
transcript.language_code   # "en"
transcript.is_generated    # True/False
transcript.snippets        # List[FetchedTranscriptSnippet]

# FetchedTranscriptSnippet object
snippet.start     # float, seconds
snippet.duration  # float, seconds
snippet.text      # str, the text
```

### Error Types

| Exception | Meaning |
|-----------|---------|
| `TranscriptsDisabled` | Video owner disabled captions |
| `NoTranscriptFound` | Requested language not available |
| `VideoUnavailable` | Video doesn't exist/private |
| `NoTranscriptAvailable` | No captions at all |
