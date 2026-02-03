# Feature-Plan Implementation Snippets

This document provides code snippets and implementation details to pass to GuardKit's `/feature-plan` and `/feature-build` commands for the youtube-mcp project.

---

## FEAT-SKEL-001: Walking Skeleton - Basic MCP Server

### Snippet for feature-plan

```
Feature: Walking Skeleton MCP Server
Goal: Create minimal FastMCP server that Claude can connect to and call a ping tool.

Implementation Details:
1. Use FastMCP 2.x: pip install 'fastmcp<3'
2. CRITICAL: All logging MUST go to stderr, NEVER stdout (corrupts JSON-RPC)
3. Use STDIO transport for Claude Desktop integration

Entry point (src/__main__.py):
```python
import sys
import logging
from datetime import datetime, timezone
from fastmcp import FastMCP

# CRITICAL: stderr only
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

mcp = FastMCP(name="youtube-mcp", version="0.1.0")

@mcp.tool()
async def ping() -> dict:
    """Health check - returns server status and version."""
    return {
        "status": "healthy",
        "server": "youtube-mcp",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Claude Desktop config (.mcp.json.template):
```json
{
  "mcpServers": {
    "youtube-mcp": {
      "command": "REPLACE_WITH_VENV_PYTHON_PATH",
      "args": ["-m", "src"],
      "cwd": "REPLACE_WITH_PROJECT_PATH",
      "env": {
        "PYTHONPATH": "REPLACE_WITH_PROJECT_PATH",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Testing:
- Test MCP initialize handshake
- Test tools/list returns ping
- Test tools/call with ping returns correct structure
- Use fastmcp dev for MCP Inspector testing
```

---

## FEAT-SKEL-002: Video Info Tool

### Snippet for feature-plan

```
Feature: Video Info Tool
Goal: Add get_video_info tool that fetches YouTube video metadata using yt-dlp.

Dependencies: pip install yt-dlp

Implementation Details:
1. yt-dlp is synchronous - wrap in asyncio.to_thread
2. Support multiple URL formats: youtube.com/watch, youtu.be, video ID only
3. Return structured metadata including caption availability

Service (src/services/youtube_client.py):
```python
import re
import asyncio
import yt_dlp
from typing import Optional

VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    r'^([a-zA-Z0-9_-]{11})$',
]

class YouTubeClient:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
    
    @staticmethod
    def extract_video_id(url: str) -> str:
        for pattern in VIDEO_ID_PATTERNS:
            match = re.search(pattern, url.strip())
            if match:
                return match.group(1)
        raise ValueError(f"Could not extract video ID from: {url}")
    
    async def get_video_info(self, video_url: str) -> dict:
        return await asyncio.to_thread(self._sync_get_info, video_url)
    
    def _sync_get_info(self, video_url: str) -> dict:
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return {
                'video_id': info.get('id'),
                'title': info.get('title'),
                'channel': info.get('uploader'),
                'channel_id': info.get('uploader_id'),
                'duration_seconds': info.get('duration'),
                'duration_formatted': self._format_duration(info.get('duration')),
                'description': info.get('description', '')[:500],  # Truncate
                'view_count': info.get('view_count'),
                'upload_date': info.get('upload_date'),
                'thumbnail_url': info.get('thumbnail'),
                'has_captions': bool(info.get('subtitles') or info.get('automatic_captions'))
            }
    
    @staticmethod
    def _format_duration(seconds: Optional[int]) -> str:
        if not seconds:
            return "0:00"
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"
```

Tool (src/tools/video_info.py):
```python
import logging
from src.services.youtube_client import YouTubeClient

logger = logging.getLogger(__name__)
client = YouTubeClient()

async def get_video_info(video_url: str) -> dict:
    """Get metadata for a YouTube video.
    
    Args:
        video_url: YouTube video URL or video ID
    
    Returns:
        Video metadata including title, channel, duration, and caption availability
    """
    try:
        video_id = client.extract_video_id(video_url)
        return await client.get_video_info(f"https://www.youtube.com/watch?v={video_id}")
    except ValueError as e:
        return {"error": {"category": "client_error", "code": "INVALID_URL", "message": str(e)}}
    except Exception as e:
        logger.error(f"Failed to get video info: {e}")
        return {"error": {"category": "external_error", "code": "YOUTUBE_UNAVAILABLE", "message": "Failed to fetch video info"}}
```

Register in __main__.py:
```python
from src.tools.video_info import get_video_info
mcp.tool()(get_video_info)
```
```

---

## FEAT-SKEL-003: Transcript Tool

### Snippet for feature-plan

```
Feature: Transcript Fetching Tool
Goal: Add get_transcript tool that fetches YouTube video captions using youtube-transcript-api.

Dependencies: pip install youtube-transcript-api

Implementation Details:
1. youtube-transcript-api is synchronous - wrap in asyncio.to_thread
2. Support language selection with fallback to English
3. Return both timestamped segments and full concatenated text
4. Handle videos without captions gracefully

Service (src/services/transcript_client.py):
```python
import asyncio
import logging
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

logger = logging.getLogger(__name__)

class TranscriptClient:
    def __init__(self):
        self.api = YouTubeTranscriptApi()
    
    async def get_transcript(self, video_id: str, language: str = "en") -> dict:
        return await asyncio.to_thread(self._sync_get_transcript, video_id, language)
    
    def _sync_get_transcript(self, video_id: str, language: str) -> dict:
        try:
            # Try exact language first
            transcript = self.api.fetch(video_id, languages=[language])
        except NoTranscriptFound:
            # Try with fallback
            transcript = self._get_with_fallback(video_id, language)
        
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
            "is_auto_generated": transcript.is_generated,
            "segments": segments,
            "full_text": full_text,
            "total_segments": len(segments),
            "total_duration_seconds": sum(s["duration"] for s in segments)
        }
    
    def _get_with_fallback(self, video_id: str, language: str) -> dict:
        transcript_list = self.api.list(video_id)
        
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
        
        available = [t.language_code for t in transcript_list]
        raise NoTranscriptFound(video_id, available)
    
    async def list_languages(self, video_id: str) -> list:
        def _sync():
            transcript_list = self.api.list(video_id)
            return [{"code": t.language_code, "name": t.language, "is_generated": t.is_generated} 
                    for t in transcript_list]
        return await asyncio.to_thread(_sync)
```

Tool (src/tools/transcript.py):
```python
import logging
from src.services.youtube_client import YouTubeClient
from src.services.transcript_client import TranscriptClient
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

logger = logging.getLogger(__name__)
youtube_client = YouTubeClient()
transcript_client = TranscriptClient()

async def get_transcript(video_url: str, language: str = "en") -> dict:
    """Fetch transcript for a YouTube video.
    
    Args:
        video_url: YouTube video URL or video ID
        language: ISO 639-1 language code (default: en)
    
    Returns:
        Transcript with timestamped segments and full text
    """
    try:
        video_id = youtube_client.extract_video_id(video_url)
        return await transcript_client.get_transcript(video_id, language)
    except ValueError as e:
        return {"error": {"category": "client_error", "code": "INVALID_URL", "message": str(e)}}
    except TranscriptsDisabled:
        return {"error": {"category": "client_error", "code": "TRANSCRIPTS_DISABLED", "message": "Transcripts are disabled for this video"}}
    except NoTranscriptFound as e:
        available = getattr(e, 'available_transcripts', [])
        return {"error": {"category": "client_error", "code": "NO_TRANSCRIPT", "message": "No transcript in requested language", "available_languages": available}}
    except VideoUnavailable:
        return {"error": {"category": "client_error", "code": "VIDEO_NOT_FOUND", "message": "Video is unavailable"}}
    except Exception as e:
        logger.error(f"Failed to get transcript: {e}")
        return {"error": {"category": "external_error", "code": "TRANSCRIPT_FETCH_FAILED", "message": "Failed to fetch transcript"}}
```
```

---

## FEAT-INT-001: Insight Extraction Tool

### Snippet for feature-plan

```
Feature: Insight Extraction Tool
Goal: Add extract_insights tool that prepares transcript for Claude-assisted analysis.

Implementation Details:
1. This tool structures the analysis request - Claude does the actual extraction
2. Support focus area presets (entrepreneurial, investment, technical, general)
3. Support custom comma-separated focus areas
4. Return structured prompt framework for Claude

Focus Presets:
- general: key_points, action_items, notable_quotes
- entrepreneurial: business_strategies, growth_tactics, lessons_learned, mistakes_to_avoid
- investment: market_trends, opportunities, risks, recommendations
- technical: technologies_mentioned, tools_recommended, best_practices, pitfalls

Tool (src/tools/insights.py):
```python
import logging

logger = logging.getLogger(__name__)

FOCUS_PRESETS = {
    "general": ["key_points", "action_items", "notable_quotes"],
    "entrepreneurial": ["business_strategies", "growth_tactics", "lessons_learned", "mistakes_to_avoid"],
    "investment": ["market_trends", "opportunities", "risks", "recommendations"],
    "technical": ["technologies_mentioned", "tools_recommended", "best_practices", "pitfalls"],
}

FOCUS_DEFINITIONS = {
    "business_strategies": "Core business approaches, models, and strategic decisions",
    "growth_tactics": "Specific tactics for user/revenue/market growth",
    "lessons_learned": "Key learnings from experience, both positive and negative",
    "mistakes_to_avoid": "Common pitfalls, errors, and things that didn't work",
    "market_trends": "Industry trends, market movements, and predictions",
    "opportunities": "Investment or business opportunities identified",
    "risks": "Potential risks, downsides, or concerns mentioned",
    "recommendations": "Specific recommendations or advice given",
    "key_points": "Main ideas and important takeaways",
    "action_items": "Specific actions someone could take",
    "notable_quotes": "Memorable or impactful statements",
    "technologies_mentioned": "Specific technologies, platforms, or tools discussed",
    "tools_recommended": "Tools or services recommended by the speaker",
    "best_practices": "Recommended approaches or patterns",
    "pitfalls": "Common mistakes or anti-patterns to avoid",
}

INSIGHT_OUTPUT_SCHEMA = {
    "insights": [
        {
            "category": "string (focus area)",
            "title": "string (10-15 words)",
            "summary": "string (2-3 sentences)",
            "quote": "string or null (verbatim from transcript)",
            "timestamp_hint": "string or null (e.g. 'around 5:30')",
            "confidence": "float 0.0-1.0",
            "actionable": "boolean"
        }
    ],
    "key_quotes": [
        {"text": "string", "context": "string"}
    ],
    "summary": "string (overall content summary)"
}

def parse_focus_areas(focus_areas: str) -> list:
    focus_areas = focus_areas.strip().lower()
    if focus_areas in FOCUS_PRESETS:
        return FOCUS_PRESETS[focus_areas]
    return [area.strip() for area in focus_areas.split(",") if area.strip()]

async def extract_insights(transcript: str, focus_areas: str = "general") -> dict:
    """Prepare transcript for insight extraction.
    
    Args:
        transcript: Full transcript text to analyze
        focus_areas: Preset name (general, entrepreneurial, investment, technical) 
                    or comma-separated custom areas
    
    Returns:
        Analysis framework with focus areas and output schema for Claude to process
    """
    if not transcript or len(transcript.strip()) < 100:
        return {
            "error": {
                "category": "client_error",
                "code": "TRANSCRIPT_TOO_SHORT",
                "message": "Transcript must be at least 100 characters",
                "transcript_length": len(transcript) if transcript else 0
            }
        }
    
    areas = parse_focus_areas(focus_areas)
    if not areas:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_FOCUS_AREAS",
                "message": f"No valid focus areas found. Use preset ({list(FOCUS_PRESETS.keys())}) or comma-separated custom areas"
            }
        }
    
    definitions = {area: FOCUS_DEFINITIONS.get(area, f"Insights related to {area}") for area in areas}
    
    return {
        "analysis_ready": True,
        "transcript_length": len(transcript),
        "focus_areas": areas,
        "focus_definitions": definitions,
        "output_schema": INSIGHT_OUTPUT_SCHEMA,
        "transcript": transcript,
        "instructions": f"""Analyze this transcript and extract actionable insights.

Focus on these areas: {', '.join(areas)}

For each insight found:
1. Categorize it into one of the focus areas
2. Create a brief, actionable title (10-15 words)
3. Write a 2-3 sentence summary
4. Include a relevant quote if available
5. Estimate timestamp location if possible
6. Rate confidence (0.0-1.0)
7. Mark if actionable (true/false)

Also extract 3-5 key memorable quotes and provide an overall content summary.

Return your analysis in the JSON schema provided in output_schema."""
    }
```

Register in __main__.py:
```python
from src.tools.insights import extract_insights
mcp.tool()(extract_insights)
```
```

---

## Usage with GuardKit

### Running feature-plan

```bash
# Navigate to youtube-mcp project
cd /path/to/youtube-mcp

# Run feature-plan with snippet
guardkit feature-plan --feature FEAT-SKEL-001 --snippet "$(cat docs/research/snippets/FEAT-SKEL-001.md)"
```

### Running feature-build

```bash
# After plan is approved
guardkit feature-build --feature FEAT-SKEL-001
```

---

## Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Test MCP protocol manually
fastmcp dev src/__main__.py

# Test with Claude Desktop
# Add config to ~/Library/Application Support/Claude/claude_desktop_config.json
# Restart Claude Desktop
# Ask Claude to "ping the youtube-mcp server"
```
