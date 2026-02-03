# YouTube Transcript MCP - Implementation Research

## Overview

This document consolidates all research findings for building the youtube-transcript-mcp server. This MCP (Model Context Protocol) server fetches YouTube video transcripts and extracts actionable insights for content digestion.

**Part of the Brandon collaboration project** for automating content consumption from YouTube videos and podcasts.

---

## Problem Statement

Brandon wants to:
1. **Ingest** YouTube videos and podcasts
2. **Extract** actionable nuggets (entrepreneurial strategies, investment trends)
3. **Store** in Google Sheets for review
4. **Consume** distilled content during drives/walks/rides

This MCP addresses **Phase 1**: YouTube video transcript fetching and insight extraction.

---

## Architecture Decision: MCP vs LangChain Agent

**Decision**: Use MCP servers

**Rationale**:
- Claude orchestrates the workflow conversationally
- Tools are discrete: fetch video → get transcript → extract insights
- Building for personal workflow, not autonomous service
- Easier to iterate and debug
- Can wrap in agent later if needed

---

## 1. MCP Server Framework: FastMCP

### Recommendation: FastMCP (via mcp package)

FastMCP is the standard framework for building MCP servers in Python. It's included in the official `mcp` package.

### Installation

```bash
pip install mcp
```

### Basic Server Pattern

```python
import sys
import logging
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# CRITICAL: All logging MUST go to stderr
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

mcp = FastMCP(name="youtube-transcript-mcp", version="0.1.0")

@mcp.tool()
async def ping() -> dict:
    """Health check - returns server status."""
    return {
        "status": "healthy",
        "server": "youtube-transcript-mcp",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### Critical MCP Patterns

#### Pattern 1: NEVER Log to stdout (CRITICAL)

```python
import sys
import logging

# CORRECT - stderr only
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# WRONG - breaks MCP protocol
print("Processing request")  # stdout corrupts JSON-RPC
logging.basicConfig()  # Defaults to stdout!
```

**Why?**: stdout is reserved for MCP JSON-RPC protocol messages. Any stdout writes corrupt the protocol.

#### Pattern 2: Module-level Tool Registration

```python
# In __main__.py - CORRECT
@mcp.tool()
async def my_tool():
    pass

# WRONG - tools registered in functions won't be discovered
def setup_tools():
    @mcp.tool()  # This won't work!
    async def my_tool():
        pass
```

#### Pattern 3: String Parameter Conversion

```python
@mcp.tool()
async def process_items(
    count: str,      # MCP sends "10" not 10
    enabled: str     # MCP sends "true" not True
) -> dict:
    count_int = int(count)
    enabled_bool = enabled.lower() in ("true", "1", "yes")
    return {"count": count_int, "enabled": enabled_bool}
```

**Why?**: MCP protocol transmits all parameters as JSON strings.

#### Pattern 4: Async Wrappers for Sync Libraries

```python
import asyncio

async def get_transcript(video_id: str) -> dict:
    return await asyncio.to_thread(_sync_get_transcript, video_id)
```

**Why?**: FastMCP is async, but libraries like yt-dlp and youtube-transcript-api are synchronous.

#### Pattern 5: Structured Error Responses

```python
return {
    "error": {
        "category": "client_error",  # or server_error, external_error
        "code": "VIDEO_NOT_FOUND",
        "message": "Video does not exist"
    }
}
```

#### Pattern 6: Timezone-Aware DateTime

```python
from datetime import datetime, timezone

# CORRECT
timestamp = datetime.now(timezone.utc)

# WRONG - deprecated
timestamp = datetime.utcnow()  # Returns naive datetime
```

### Claude Desktop Configuration

For STDIO transport (recommended for local development):

```json
{
  "mcpServers": {
    "youtube-transcript-mcp": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/path/to/youtube-transcript-mcp",
      "env": {
        "PYTHONPATH": "/path/to/youtube-transcript-mcp",
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

```bash
# Use Anthropic's inspector
npx @anthropic-ai/mcp-inspector python -m src
```

---

## 2. YouTube Video Metadata: yt-dlp

### Recommendation: yt-dlp

yt-dlp is a feature-rich fork of youtube-dl with better maintenance. It's the preferred choice for metadata extraction - no API key needed.

### Installation

```bash
pip install yt-dlp
```

### Basic Usage for Metadata Extraction

```python
import yt_dlp
import asyncio

async def get_video_info(video_url: str) -> dict:
    def _sync():
        with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'channel': info.get('uploader'),
                'duration_seconds': info.get('duration'),
                'has_captions': bool(info.get('subtitles') or info.get('automatic_captions'))
            }
    return await asyncio.to_thread(_sync)
```

### URL Parsing

```python
import re

VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})',
    r'^([a-zA-Z0-9_-]{11})$',  # Just the ID
]

def extract_video_id(url: str) -> str:
    """Extract video ID from various YouTube URL formats."""
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url}")
```

### Supported URL Formats

| Format | Example |
|--------|---------|
| Standard | `https://www.youtube.com/watch?v=VIDEO_ID` |
| Short | `https://youtu.be/VIDEO_ID` |
| Embed | `https://youtube.com/embed/VIDEO_ID` |
| Mobile | `https://m.youtube.com/watch?v=VIDEO_ID` |
| Just ID | `VIDEO_ID` |

---

## 3. Transcript Extraction: youtube-transcript-api

### Recommendation: youtube-transcript-api

Purpose-built library for fetching YouTube transcripts. Handles both auto-generated and manual captions.

### Installation

```bash
pip install youtube-transcript-api
```

### Basic Usage (API v1.2+)

```python
from youtube_transcript_api import YouTubeTranscriptApi
import asyncio

async def get_transcript(video_id: str, language: str = "en") -> dict:
    def _sync():
        api = YouTubeTranscriptApi()
        transcript = api.fetch(video_id, languages=[language])
        
        segments = [
            {"start": s.start, "duration": s.duration, "text": s.text}
            for s in transcript.snippets
        ]
        full_text = " ".join(s.text for s in transcript.snippets)
        
        return {
            "video_id": video_id,
            "language": transcript.language,
            "language_code": transcript.language_code,
            "is_auto_generated": transcript.is_generated,
            "segments": segments,
            "full_text": full_text,
        }
    return await asyncio.to_thread(_sync)
```

### Language Fallback Strategy

```python
from youtube_transcript_api._errors import NoTranscriptFound

def get_transcript_with_fallback(video_id: str, language: str = "en"):
    api = YouTubeTranscriptApi()
    
    try:
        return api.fetch(video_id, languages=[language])
    except NoTranscriptFound:
        pass
    
    transcript_list = api.list(video_id)
    
    # Try auto-generated in requested language
    for t in transcript_list:
        if t.is_generated and t.language_code.startswith(language):
            return t.fetch()
    
    # Fall back to any English variant
    for t in transcript_list:
        if t.language_code.startswith("en"):
            return t.fetch()
    
    # Return first available
    for t in transcript_list:
        return t.fetch()
    
    raise NoTranscriptFound(video_id, [], [])
```

### Error Handling

| Exception | Meaning |
|-----------|---------|
| `TranscriptsDisabled` | Video owner disabled captions |
| `NoTranscriptFound` | Requested language not available |
| `VideoUnavailable` | Video doesn't exist/private |
| `NoTranscriptAvailable` | No captions at all |

---

## 4. Insight Extraction Patterns

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
        "pitfalls"
    ]
}
```

### Chunking Strategy for Long Transcripts

```python
def chunk_transcript(transcript: str, max_chars: int = 30000) -> list[str]:
    if len(transcript) <= max_chars:
        return [transcript]
    
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

## 5. Project Structure

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # FastMCP entry point + tool registration
│   ├── models/
│   │   ├── __init__.py
│   │   └── insight.py           # Pydantic models for insights
│   └── services/
│       ├── __init__.py
│       ├── youtube_client.py    # yt-dlp wrapper
│       ├── transcript_client.py # youtube-transcript-api wrapper
│       └── insight_extractor.py # Insight extraction service
├── tests/
│   ├── unit/
│   ├── integration/
│   └── protocol/
├── docs/
│   ├── features/
│   └── research/
├── pyproject.toml
└── README.md
```

---

## 6. Dependencies

```toml
[project]
name = "youtube-transcript-mcp"
version = "0.1.0"
requires-python = ">=3.10"

dependencies = [
    "mcp>=1.0.0",
    "yt-dlp>=2024.1.0",
    "youtube-transcript-api>=1.0.0",
    "pydantic>=2.0",
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

## 7. Implementation Phases

### Phase 1: Walking Skeleton

| Feature | Tool | Description |
|---------|------|-------------|
| FEAT-SKEL-001 | `ping()` | Basic MCP server with health check |
| FEAT-SKEL-002 | `get_video_info(url)` | Video metadata via yt-dlp |
| FEAT-SKEL-003 | `get_transcript(url, language)` | Transcript fetching |

### Phase 2: Intelligence Layer

| Feature | Tool | Description |
|---------|------|-------------|
| FEAT-INT-001 | `extract_insights(transcript, focus_areas)` | Claude-assisted insight extraction |

### Phase 3: Future Enhancements

- Google Sheets MCP (separate project)
- Podcast MCP (separate project)
- Caching layer
- Batch processing

---

## 8. Key Gotchas Summary

| ❌ Don't | ✅ Do |
|---------|-------|
| Print to stdout | Log to stderr only |
| Register tools in functions | Register at module level |
| Swallow CancelledError | Re-raise after logging |
| Use naive datetime | Use `datetime.now(timezone.utc)` |
| Assume parameter types | Convert strings explicitly |
| Use `logging.basicConfig()` | Use `logging.basicConfig(stream=sys.stderr)` |

---

## References

- [MCP Specification](https://modelcontextprotocol.io/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)
- [youtube-transcript-api PyPI](https://pypi.org/project/youtube-transcript-api/)
- [Claude Desktop MCP Guide](https://support.claude.com/en/articles/10949351)
