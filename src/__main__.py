"""YouTube Transcript MCP Server — tool registration module.

All MCP tools are registered at module level using @mcp.tool() decorator.
stdout is reserved exclusively for MCP JSON-RPC messages; all logging
goes to stderr.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.services.transcript_client import (
    NoTranscriptFoundError,
    TranscriptClient,
    TranscriptsDisabledError,
    VideoUnavailableError,
)
from src.services.youtube_client import InvalidURLError, extract_video_id

# Server metadata
SERVER_NAME = "youtube-transcript-mcp"
SERVER_VERSION = "0.1.0"

# Configure logging to stderr only (stdout is reserved for MCP protocol)
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# FastMCP server instance
mcp = FastMCP(name=SERVER_NAME)

# Module-level client instances (singleton pattern)
transcript_client = TranscriptClient()


@mcp.tool()
async def get_transcript(
    video_url: str,
    language: str = "en",
) -> dict[str, Any]:
    """Fetch transcript for a YouTube video.

    Retrieves the transcript/captions for a YouTube video with intelligent
    language fallback. If the requested language isn't available, it tries:
    1. Auto-generated version of requested language
    2. Any English variant
    3. First available transcript

    Args:
        video_url: YouTube URL or video ID. Supports formats:
            - https://www.youtube.com/watch?v=VIDEO_ID
            - https://youtu.be/VIDEO_ID
            - https://youtube.com/embed/VIDEO_ID
            - https://m.youtube.com/watch?v=VIDEO_ID
            - VIDEO_ID (just the 11-character video ID)
        language: Preferred language code (default: "en").
            Common codes: en, es, fr, de, ja, ko, zh-Hans, pt

    Returns:
        Dictionary containing video_id, language, language_code,
        is_auto_generated, segments, full_text, total_segments, and
        total_duration_seconds. Or error dict if transcript unavailable.
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

    # Fetch transcript via TranscriptClient
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
        logger.exception("Unexpected error fetching transcript: %s", e)
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to fetch transcript",
            }
        }


@mcp.tool()
async def list_available_transcripts(video_url: str) -> dict[str, Any]:
    """List all available transcripts for a YouTube video.

    Returns information about all available transcripts including
    language codes and whether they are auto-generated or manual.
    Useful for checking what's available before fetching.

    Args:
        video_url: YouTube URL or video ID. Supports the same formats
            as get_transcript.

    Returns:
        Dictionary containing video_id, transcripts list, and count.
        Each transcript has language, language_code, and is_generated.
        Or error dict if request fails.
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
        logger.exception("Unexpected error listing transcripts: %s", e)
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to list transcripts",
            }
        }


if __name__ == "__main__":
    logger.info("Starting %s server...", SERVER_NAME)
    mcp.run(transport="stdio")
