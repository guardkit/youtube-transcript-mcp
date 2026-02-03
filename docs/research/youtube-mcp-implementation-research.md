# YouTube MCP Implementation Research

## Overview

This document consolidates research for building a YouTube content digestion MCP server. The goal is to enable extraction of actionable insights (entrepreneurial strategies, investment trends) from YouTube videos for consumption during walks, drives, and bike rides.

---

## 1. MCP Server Framework: FastMCP

### Recommendation: FastMCP (Python)

FastMCP is the standard framework for building MCP servers in Python. FastMCP 1.0 was incorporated into the official MCP Python SDK in 2024, and FastMCP 2.0/3.0 are the actively maintained versions.

### Installation

```bash
# Stable (recommended for production)
pip install 'fastmcp<3'

# Beta with latest features
pip install fastmcp==3.0.0b1
```

### Basic Server Pattern

```python
from fastmcp import FastMCP

mcp = FastMCP(name="youtube-mcp", version="0.1.0")

@mcp.tool()
async def ping() -> dict:
    """Health check - returns server status."""
    return {"status": "healthy", "server": "youtube-mcp"}

@mcp.tool()
async def get_video_info(video_url: str) -> dict:
    """Get metadata for a YouTube video."""
    # Implementation
    pass

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Critical MCP Patterns

#### 1. NEVER Log to stdout (STDIO servers)

```python
import sys
import logging

# CRITICAL: Always log to stderr, NEVER stdout
logging.basicConfig(
    stream=sys.stderr,  # stdout corrupts JSON-RPC messages
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

#### 2. Tool Decorators with Type Hints

FastMCP automatically generates JSON schemas from function signatures:

```python
@mcp.tool()
async def get_transcript(
    video_url: str,
    language: str = "en"
) -> dict:
    """Fetch transcript for a YouTube video.
    
    Args:
        video_url: YouTube video URL or video ID
        language: ISO 639-1 language code (default: en)
    """
    # FastMCP uses docstring for tool description
    pass
```

#### 3. Error Handling Pattern

```python
from fastmcp import ToolError

@mcp.tool()
async def get_transcript(video_url: str) -> dict:
    try:
        # Implementation
        pass
    except VideoNotFound:
        raise ToolError("Video not found or unavailable")
    except Exception as e:
        # Log to stderr, return structured error
        logging.error(f"Unexpected error: {e}")
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
```

### Claude Desktop Configuration

For STDIO transport (recommended for local development):

```json
{
  "mcpServers": {
    "youtube-mcp": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/path/to/youtube-mcp",
      "env": {
        "PYTHONPATH": "/path/to/youtube-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Configuration file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Testing with MCP Inspector

FastMCP includes a debugging tool:

```bash
fastmcp dev src/__main__.py
# Opens Inspector at http://127.0.0.1:6274
```

---

## 2. YouTube Video Metadata: yt-dlp

### Recommendation: yt-dlp

yt-dlp is a feature-rich fork of youtube-dl with better maintenance and additional features. It's the preferred choice for metadata extraction.

### Installation

```bash
pip install yt-dlp
```

### Basic Usage for Metadata Extraction

```python
import yt_dlp
import asyncio

async def get_video_info(video_url: str) -> dict:
    """Extract video metadata using yt-dlp."""
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,  # Don't download video
    }
    
    def _sync_extract():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'channel': info.get('uploader'),
                'channel_id': info.get('uploader_id'),
                'duration_seconds': info.get('duration'),
                'description': info.get('description'),
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'thumbnail_url': info.get('thumbnail'),
                'has_captions': bool(info.get('subtitles') or info.get('automatic_captions'))
            }
    
    # yt-dlp is synchronous, wrap in thread
    return await asyncio.to_thread(_sync_extract)
```

### URL Parsing

yt-dlp handles various URL formats automatically, but for validation:

```python
import re

VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    r'^([a-zA-Z0-9_-]{11})$',  # Just the ID
]

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")
```

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://youtube.com/watch?v=VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID` (just the 11-character ID)

### Available Metadata Fields

Key fields from yt-dlp's `extract_info`:

| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Video ID |
| `title` | str | Video title |
| `uploader` | str | Channel name |
| `uploader_id` | str | Channel ID |
| `duration` | int | Duration in seconds |
| `description` | str | Video description |
| `view_count` | int | Number of views |
| `upload_date` | str | Upload date (YYYYMMDD) |
| `thumbnail` | str | Thumbnail URL |
| `subtitles` | dict | Manual subtitles |
| `automatic_captions` | dict | Auto-generated captions |
| `chapters` | list | Video chapters (if available) |

---

## 3. Transcript Extraction: youtube-transcript-api

### Recommendation: youtube-transcript-api

Purpose-built library for fetching YouTube transcripts. Handles both auto-generated and manual captions.

### Installation

```bash
pip install youtube-transcript-api
```

### Basic Usage

```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
import asyncio

async def get_transcript(video_id: str, language: str = "en") -> dict:
    """Fetch transcript for a YouTube video."""
    
    def _sync_fetch():
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id, languages=[language])
        
        segments = [
            {
                "start": snippet.start,
                "duration": snippet.duration,
                "text": snippet.text
            }
            for snippet in transcript.snippets
        ]
        
        full_text = " ".join(snippet.text for snippet in transcript.snippets)
        
        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_generated": transcript.is_generated,
            "segments": segments,
            "full_text": full_text,
            "total_segments": len(segments)
        }
    
    return await asyncio.to_thread(_sync_fetch)
```

### Language Fallback Strategy

```python
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound

def get_transcript_with_fallback(video_id: str, language: str = "en") -> dict:
    """Fetch transcript with intelligent language fallback."""
    
    ytt_api = YouTubeTranscriptApi()
    
    try:
        # Try requested language first
        return ytt_api.fetch(video_id, languages=[language])
    except NoTranscriptFound:
        pass
    
    # List all available transcripts
    transcript_list = ytt_api.list(video_id)
    
    # Try auto-generated in requested language
    for t in transcript_list:
        if t.is_generated and t.language_code.startswith(language):
            return t.fetch()
    
    # Fall back to any English variant
    for t in transcript_list:
        if t.language_code.startswith("en"):
            return t.fetch()
    
    # Return error with available languages
    available = [t.language_code for t in transcript_list]
    raise NoTranscriptFound(video_id, available)
```

### Transcript Object Structure (v1.2+)

```python
FetchedTranscript(
    snippets=[
        FetchedTranscriptSnippet(
            text="Hey there",
            start=0.0,
            duration=1.54,
        ),
        FetchedTranscriptSnippet(
            text="how are you",
            start=1.54,
            duration=4.16,
        ),
        # ...
    ],
    video_id="12345",
    language="English",
    language_code="en",
    is_generated=False,
)
```

### Error Handling

```python
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NoTranscriptAvailable
)

try:
    transcript = ytt_api.fetch(video_id)
except TranscriptsDisabled:
    return {"error": {"code": "TRANSCRIPTS_DISABLED", "message": "Transcripts are disabled for this video"}}
except NoTranscriptFound as e:
    return {"error": {"code": "NO_TRANSCRIPT", "message": "No transcript in requested language", "available": e.available_transcripts}}
except VideoUnavailable:
    return {"error": {"code": "VIDEO_UNAVAILABLE", "message": "Video is unavailable"}}
```

---

## 4. Insight Extraction Patterns

### LLM Prompt Patterns for Content Digestion

Based on research, effective insight extraction uses structured prompts with clear output schemas.

### Extraction Prompt Template

```python
INSIGHT_EXTRACTION_PROMPT = """
Analyze the following transcript and extract actionable insights.

## Focus Areas
{focus_areas}

## Instructions
For each insight, extract:
1. **Category**: Which focus area it belongs to
2. **Title**: Brief, actionable title (10-15 words)
3. **Summary**: 2-3 sentence explanation
4. **Quote**: Relevant verbatim quote from transcript (if available)
5. **Timestamp Hint**: Approximate location in video (e.g., "around 5:30")
6. **Confidence**: 0.0-1.0 scale
7. **Actionable**: true/false - can someone immediately act on this?

## Focus Area Definitions
- **business_strategies**: Core business approaches, models, and strategic decisions
- **growth_tactics**: Specific tactics for user/revenue/market growth
- **lessons_learned**: Key learnings from experience, both positive and negative
- **mistakes_to_avoid**: Common pitfalls, errors, and things that didn't work
- **market_trends**: Industry trends, market movements, and predictions
- **investment_signals**: Investment opportunities, risks, or recommendations

## Transcript
{transcript}

## Output Format
Return a JSON object with this structure:
{{
  "insights": [
    {{
      "category": "string",
      "title": "string",
      "summary": "string",
      "quote": "string or null",
      "timestamp_hint": "string or null",
      "confidence": 0.0-1.0,
      "actionable": boolean
    }}
  ],
  "key_quotes": [
    {{
      "text": "string",
      "context": "string"
    }}
  ],
  "summary": "Brief overall summary of the content"
}}
"""
```

### Focus Area Presets

```python
FOCUS_PRESETS = {
    "general": ["key_points", "action_items", "notable_quotes"],
    "entrepreneurial": [
        "business_strategies",
        "growth_tactics", 
        "lessons_learned",
        "mistakes_to_avoid"
    ],
    "investment": [
        "market_trends",
        "opportunities",
        "risks",
        "recommendations"
    ],
    "technical": [
        "technologies_mentioned",
        "tools_recommended",
        "best_practices",
        "pitfalls_to_avoid"
    ]
}
```

### Chunking Strategy for Long Transcripts

For videos longer than ~45 minutes (token limits):

```python
def chunk_transcript(transcript: str, max_chars: int = 30000) -> list[str]:
    """Split transcript at natural boundaries."""
    if len(transcript) <= max_chars:
        return [transcript]
    
    # Split on paragraph boundaries (double newline)
    paragraphs = transcript.split("\n\n")
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = para
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

---

## 5. Project Structure Recommendation

```
youtube-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # FastMCP entry point
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── health.py            # ping tool
│   │   ├── video_info.py        # get_video_info tool
│   │   ├── transcript.py        # get_transcript tool
│   │   └── insights.py          # extract_insights tool
│   ├── services/
│   │   ├── __init__.py
│   │   ├── youtube_client.py    # yt-dlp wrapper
│   │   └── transcript_client.py # youtube-transcript-api wrapper
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py             # Pydantic models for video metadata
│   │   ├── transcript.py        # Pydantic models for transcript
│   │   └── insight.py           # Pydantic models for insights
│   └── prompts/
│       ├── __init__.py
│       └── templates.py         # LLM prompt templates
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_video_info.py
│   │   ├── test_transcript.py
│   │   └── test_insights.py
│   └── integration/
│       └── test_mcp_protocol.py
├── pyproject.toml
├── Dockerfile
├── .mcp.json.template           # Claude Desktop config template
└── README.md
```

---

## 6. Dependencies Summary

### pyproject.toml

```toml
[project]
name = "youtube-mcp"
version = "0.1.0"
description = "MCP server for YouTube content digestion"
requires-python = ">=3.10"

dependencies = [
    "fastmcp>=2.0,<3",    # MCP server framework
    "yt-dlp>=2024.1.0",   # Video metadata extraction
    "youtube-transcript-api>=1.0.0",  # Transcript fetching
    "pydantic>=2.0",      # Data validation
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]
```

---

## 7. Key Gotchas and Best Practices

### MCP-Specific

1. **NEVER print to stdout** - Use stderr for all logging
2. **MCP sends all parameters as strings** - Always validate and convert types
3. **Keep tools atomic** - One tool, one purpose
4. **Structured errors** - Return error objects, don't raise exceptions to MCP layer
5. **Async wrappers needed** - yt-dlp and youtube-transcript-api are sync

### YouTube API

1. **Rate limiting** - YouTube may block aggressive requests; add delays between bulk operations
2. **IP blocking** - yt-dlp can encounter blocks; consider cookies/auth for heavy use
3. **Transcript availability** - Not all videos have captions; handle gracefully
4. **URL formats vary** - Support multiple URL patterns

### Security

1. **Process isolation** - STDIO transport means only launching processes can connect
2. **No API keys in config** - Use environment variables
3. **Validate all inputs** - URLs, language codes, etc.

---

## References

- [FastMCP Documentation](https://gofastmcp.com/)
- [MCP Specification](https://modelcontextprotocol.io/specification)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [youtube-transcript-api PyPI](https://pypi.org/project/youtube-transcript-api/)
- [Claude Desktop MCP Guide](https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop)
