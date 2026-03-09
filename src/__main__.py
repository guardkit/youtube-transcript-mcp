"""YouTube Transcript MCP Server - tool registration module.

All MCP tools are registered at module level using @mcp.tool() decorator.
stdout is reserved exclusively for MCP JSON-RPC messages; all logging
goes to stderr.
"""

from __future__ import annotations

import dataclasses
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from mcp.server.fastmcp import FastMCP

from src.services.youtube_client import (
    InvalidURLError,
    VideoNotFoundError,
    YouTubeClient,
)

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

# Module-level client instance
youtube_client = YouTubeClient()


@mcp.tool()
async def ping() -> dict[str, str]:
    """Health check - returns server status.

    Use this to verify the MCP server is running and responsive.

    Returns:
        Dictionary with status, server name, version, and UTC timestamp.
    """
    return {
        "status": "healthy",
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.tool()
async def get_video_info(video_url: str) -> dict[str, Any]:
    """Get metadata for a YouTube video.

    Fetches title, channel, duration, description, and caption availability
    for a YouTube video. Use this before fetching transcripts to verify
    the video exists and has captions available.

    Args:
        video_url: YouTube URL or video ID. Supports formats:
            - https://www.youtube.com/watch?v=VIDEO_ID
            - https://youtu.be/VIDEO_ID
            - https://youtube.com/embed/VIDEO_ID
            - https://m.youtube.com/watch?v=VIDEO_ID
            - VIDEO_ID (just the 11-character video ID)

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
            field.name: getattr(info, field.name)
            for field in dataclasses.fields(info)
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
        logger.exception("Unexpected error fetching video info: %s", e)
        return {
            "error": {
                "category": "server_error",
                "code": "INTERNAL_ERROR",
                "message": "Failed to fetch video info",
            }
        }


if __name__ == "__main__":
    logger.info("Starting %s server...", SERVER_NAME)
    mcp.run(transport="stdio")
