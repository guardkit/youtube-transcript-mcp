# FEAT-SKEL-002: Video Info Tool

## Overview

Add a tool to fetch YouTube video metadata using yt-dlp. This validates that the walking skeleton can integrate external libraries and provides essential video information before transcript fetching.

**Complexity**: 4/10  
**Estimated Time**: 3-4 hours  
**Dependencies**: FEAT-SKEL-001 (Basic MCP Server)

## Business Context

Before fetching transcripts, we need to verify video exists and check caption availability. This tool provides metadata that helps users understand what content they're about to process.

## Acceptance Criteria

1. `get_video_info` tool accepts YouTube URL or video ID
2. Returns: title, channel, duration, description snippet, caption availability
3. Handles various YouTube URL formats (watch, youtu.be, embed, mobile)
4. Returns structured error for invalid URLs or unavailable videos
5. Uses async wrapper around sync yt-dlp library
6. Unit tests cover happy path and error cases

## Technical Specification

### URL Parsing Utility (`src/services/youtube_client.py`)

```python
"""YouTube client service using yt-dlp for metadata extraction."""

import re
import asyncio
import logging
from typing import Optional
from dataclasses import dataclass

import yt_dlp

logger = logging.getLogger(__name__)

# URL patterns for video ID extraction
VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
    r'^([a-zA-Z0-9_-]{11})$',  # Just the video ID
]


@dataclass
class VideoInfo:
    """Video metadata from YouTube."""
    video_id: str
    title: str
    channel: str
    channel_id: Optional[str]
    duration_seconds: int
    duration_formatted: str
    description_snippet: str
    view_count: Optional[int]
    upload_date: Optional[str]
    thumbnail_url: Optional[str]
    has_captions: bool
    has_auto_captions: bool
    available_languages: list[str]


class YouTubeClientError(Exception):
    """Base exception for YouTube client errors."""
    pass


class VideoNotFoundError(YouTubeClientError):
    """Video does not exist or is unavailable."""
    pass


class InvalidURLError(YouTubeClientError):
    """URL is not a valid YouTube URL."""
    pass


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats.
    
    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - VIDEO_ID (just the 11-character ID)
    
    Args:
        url_or_id: YouTube URL or video ID
        
    Returns:
        11-character video ID
        
    Raises:
        InvalidURLError: If URL format is not recognized
    """
    url_or_id = url_or_id.strip()
    
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    raise InvalidURLError(f"Could not extract video ID from: {url_or_id}")


class YouTubeClient:
    """Client for fetching YouTube video metadata."""
    
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'extract_flat': False,
        }
    
    async def get_video_info(self, url_or_id: str) -> VideoInfo:
        """Fetch video metadata from YouTube.

        Args:
            url_or_id: YouTube URL or video ID

        Returns:
            VideoInfo with metadata

        Raises:
            InvalidURLError: If URL format is invalid
            VideoNotFoundError: If video doesn't exist
        """
        video_id = extract_video_id(url_or_id)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            return await asyncio.to_thread(self._sync_get_info, video_url, video_id)
        except asyncio.CancelledError:
            logger.info(f"Video info request cancelled for {video_id}")
            raise  # CRITICAL: Must re-raise CancelledError
    
    def _sync_get_info(self, video_url: str, video_id: str) -> VideoInfo:
        """Synchronous video info extraction (runs in thread)."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)
                
                if info is None:
                    raise VideoNotFoundError(f"Video not found: {video_id}")
                
                # Extract caption information
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                available_languages = list(set(
                    list(subtitles.keys()) + list(auto_captions.keys())
                ))
                
                return VideoInfo(
                    video_id=info.get('id', video_id),
                    title=info.get('title', 'Unknown'),
                    channel=info.get('uploader', 'Unknown'),
                    channel_id=info.get('uploader_id'),
                    duration_seconds=info.get('duration', 0),
                    duration_formatted=self._format_duration(info.get('duration')),
                    description_snippet=self._truncate(info.get('description', ''), 500),
                    view_count=info.get('view_count'),
                    upload_date=info.get('upload_date'),
                    thumbnail_url=info.get('thumbnail'),
                    has_captions=bool(subtitles),
                    has_auto_captions=bool(auto_captions),
                    available_languages=sorted(available_languages),
                )
                
        except yt_dlp.utils.DownloadError as e:
            logger.error(f"yt-dlp error for {video_id}: {e}")
            raise VideoNotFoundError(f"Video unavailable: {video_id}") from e
    
    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        """Format duration as HH:MM:SS or MM:SS."""
        if not seconds:
            return "0:00"
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"
    
    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        """Truncate text with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
```

### Tool Registration (add to `src/__main__.py`)

```python
# Add imports at top
from src.services.youtube_client import (
    YouTubeClient,
    VideoNotFoundError,
    InvalidURLError,
)

# Initialize client
youtube_client = YouTubeClient()

@mcp.tool()
async def get_video_info(video_url: str) -> dict:
    """Get metadata for a YouTube video.
    
    Fetches title, channel, duration, description, and caption availability
    for a YouTube video. Use this before fetching transcripts to verify
    the video exists and has captions available.
    
    Args:
        video_url: YouTube URL or video ID. Supports formats:
            - https://www.youtube.com/watch?v=VIDEO_ID
            - https://youtu.be/VIDEO_ID
            - VIDEO_ID (just the 11-character ID)
    
    Returns:
        Dictionary with video metadata including:
        - video_id: The YouTube video ID
        - title: Video title
        - channel: Channel name
        - duration_formatted: Duration as "MM:SS" or "HH:MM:SS"
        - description_snippet: First 500 chars of description
        - has_captions: Whether manual captions exist
        - has_auto_captions: Whether auto-generated captions exist
        - available_languages: List of available caption languages
    """
    try:
        info = await youtube_client.get_video_info(video_url)
        return {
            "video_id": info.video_id,
            "title": info.title,
            "channel": info.channel,
            "channel_id": info.channel_id,
            "duration_seconds": info.duration_seconds,
            "duration_formatted": info.duration_formatted,
            "description_snippet": info.description_snippet,
            "view_count": info.view_count,
            "upload_date": info.upload_date,
            "thumbnail_url": info.thumbnail_url,
            "has_captions": info.has_captions,
            "has_auto_captions": info.has_auto_captions,
            "available_languages": info.available_languages,
        }
    except InvalidURLError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_URL",
                "message": str(e),
            }
        }
    except VideoNotFoundError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "VIDEO_NOT_FOUND",
                "message": str(e),
            }
        }
    except Exception as e:
        logger.exception(f"Unexpected error fetching video info: {e}")
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to fetch video info",
            }
        }
```

### Unit Tests (`tests/unit/test_video_info.py`)

```python
"""Tests for video info tool and YouTube client."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.youtube_client import (
    extract_video_id,
    YouTubeClient,
    InvalidURLError,
    VideoNotFoundError,
)


class TestExtractVideoId:
    """Tests for URL parsing."""
    
    def test_standard_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_embed_url(self):
        url = "https://youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_mobile_url(self):
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_just_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    
    def test_url_with_extra_params(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120"
        assert extract_video_id(url) == "dQw4w9WgXcQ"
    
    def test_invalid_url_raises(self):
        with pytest.raises(InvalidURLError):
            extract_video_id("https://example.com/video")
    
    def test_empty_string_raises(self):
        with pytest.raises(InvalidURLError):
            extract_video_id("")


class TestYouTubeClient:
    """Tests for YouTubeClient."""
    
    @pytest.fixture
    def mock_yt_dlp_info(self):
        """Mock yt-dlp response."""
        return {
            'id': 'dQw4w9WgXcQ',
            'title': 'Test Video',
            'uploader': 'Test Channel',
            'uploader_id': '@testchannel',
            'duration': 212,
            'description': 'This is a test video description.',
            'view_count': 1000000,
            'upload_date': '20240101',
            'thumbnail': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg',
            'subtitles': {'en': []},
            'automatic_captions': {'en': [], 'es': []},
        }
    
    @pytest.mark.asyncio
    async def test_get_video_info_success(self, mock_yt_dlp_info):
        """Should return VideoInfo for valid video."""
        client = YouTubeClient()
        
        with patch.object(client, '_sync_get_info') as mock_sync:
            from src.services.youtube_client import VideoInfo
            mock_sync.return_value = VideoInfo(
                video_id='dQw4w9WgXcQ',
                title='Test Video',
                channel='Test Channel',
                channel_id='@testchannel',
                duration_seconds=212,
                duration_formatted='3:32',
                description_snippet='This is a test video description.',
                view_count=1000000,
                upload_date='20240101',
                thumbnail_url='https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg',
                has_captions=True,
                has_auto_captions=True,
                available_languages=['en', 'es'],
            )
            
            result = await client.get_video_info('dQw4w9WgXcQ')
            
            assert result.video_id == 'dQw4w9WgXcQ'
            assert result.title == 'Test Video'
            assert result.has_captions is True
            assert 'en' in result.available_languages
    
    def test_format_duration_seconds_only(self):
        assert YouTubeClient._format_duration(45) == "0:45"
    
    def test_format_duration_minutes(self):
        assert YouTubeClient._format_duration(212) == "3:32"
    
    def test_format_duration_hours(self):
        assert YouTubeClient._format_duration(3661) == "1:01:01"
    
    def test_format_duration_none(self):
        assert YouTubeClient._format_duration(None) == "0:00"
```

### Update `pyproject.toml` Dependencies

```toml
dependencies = [
    "mcp>=1.0.0",        # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",  # YouTube video metadata extraction
]
```

## File Structure After Implementation

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # + get_video_info tool
│   └── services/
│       ├── __init__.py
│       └── youtube_client.py    # NEW: yt-dlp wrapper
├── tests/
│   └── unit/
│       ├── test_ping.py
│       └── test_video_info.py   # NEW: video info tests
└── pyproject.toml               # + yt-dlp dependency
```

## Testing Strategy

1. **Unit Tests**: Test URL parsing and mock yt-dlp responses
2. **Integration Tests**: Test with real YouTube video (marked slow)
3. **Manual Testing**: Use MCP Inspector to call `get_video_info`

## Definition of Done

- [ ] `src/services/youtube_client.py` implements `YouTubeClient` class
- [ ] `get_video_info` tool registered in `__main__.py`
- [ ] URL parsing handles all common YouTube URL formats
- [ ] Structured errors returned for invalid URLs and missing videos
- [ ] Unit tests pass with mocked yt-dlp
- [ ] `pyproject.toml` includes yt-dlp dependency
- [ ] Tool visible in MCP Inspector
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

### Critical MCP Patterns

These patterns are REQUIRED for correct MCP server behavior.

| # | Pattern | Why | Example |
|---|---------|-----|---------|
| 1 | **stderr logging** | stdout = MCP JSON-RPC protocol | `logging.basicConfig(stream=sys.stderr)` |
| 2 | **Module-level tools** | Required for Claude Code discovery | `@mcp.tool()` at module level in `__main__.py` |
| 3 | **String parameters** | MCP sends all params as strings | `count_int = int(count)` |
| 4 | **Timezone-aware datetime** | `utcnow()` is deprecated | `datetime.now(timezone.utc)` |
| 5 | **Async wrappers** | Don't block event loop | `await asyncio.to_thread(sync_fn)` |
| 6 | **CancelledError** | Must re-raise for cleanup | `except CancelledError: logger.info(...); raise` |
| 7 | **Structured errors** | Consistent error format | `{"error": {"category": "...", "code": "...", "message": "..."}}` |

#### Pattern Details

<details>
<summary>1. stderr logging (CRITICAL)</summary>

```python
import sys
import logging

# CORRECT
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# WRONG - breaks MCP protocol
print("Debug")  # stdout corrupts JSON-RPC
logging.basicConfig()  # Defaults to stdout!
```
</details>

<details>
<summary>2. Module-level tool registration</summary>

```python
# CORRECT - in __main__.py at module level
@mcp.tool()
async def my_tool():
    pass

# WRONG - tools registered in functions won't be discovered
def setup():
    @mcp.tool()
    async def my_tool():
        pass
```
</details>

<details>
<summary>3. String parameter conversion</summary>

```python
@mcp.tool()
async def process(count: str, enabled: str) -> dict:
    # MCP sends "10" not 10, "true" not True
    count_int = int(count)
    enabled_bool = enabled.lower() in ("true", "1", "yes")
    return {"count": count_int, "enabled": enabled_bool}
```
</details>

### Async Pattern for Sync Libraries

yt-dlp is synchronous. Use `asyncio.to_thread()` to avoid blocking:

```python
# CORRECT - runs sync code in thread pool
result = await asyncio.to_thread(sync_function, arg1, arg2)

# WRONG - blocks the event loop
result = sync_function(arg1, arg2)
```

### Error Response Pattern

Follow structured error format from `.claude/rules/mcp-patterns.md`:

```python
return {
    "error": {
        "category": "client_error",  # or server_error, external_error
        "code": "SPECIFIC_ERROR_CODE",
        "message": "Human readable message",
    }
}
```

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
