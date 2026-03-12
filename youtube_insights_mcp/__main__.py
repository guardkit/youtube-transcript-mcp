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

from youtube_insights_mcp.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
)
from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction
from youtube_insights_mcp.services.transcript_client import (
    IpBlockedError,
    NoTranscriptFoundError,
    TranscriptClient,
    TranscriptsDisabledError,
    VideoUnavailableError,
    build_proxy_config,
)
from youtube_insights_mcp.services.youtube_client import InvalidURLError, extract_video_id

# Server metadata
SERVER_NAME = "youtube-insights-mcp"
SERVER_VERSION = "0.1.6"

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
transcript_client = TranscriptClient(proxy_config=build_proxy_config())


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

    except IpBlockedError as e:
        return {
            "error": {
                "category": "client_error",
                "code": "IP_BLOCKED",
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


@mcp.tool()
async def extract_insights(
    transcript: str,
    focus_areas: str = "general",
    video_id: str = "",
    max_insights: str = "10",
) -> dict[str, Any]:
    """Prepare transcript for insight extraction analysis.

    Structures the transcript and creates analysis metadata for Claude
    to extract actionable insights. Returns prompts and categories
    that guide the extraction process.

    This tool prepares the data — the actual insight extraction happens
    through Claude's analysis of the returned prompt and transcript.

    Args:
        transcript: Full transcript text to analyze. Must be at least
            100 characters long.
        focus_areas: Comma-separated focus areas. Options:
            - "general": Key points, action items, notable quotes, context
            - "entrepreneurial": Business strategies, growth tactics, lessons
            - "investment": Market trends, opportunities, risks, recommendations
            - "technical": Technologies, tools, best practices, pitfalls
            - "youtube-channel": Channel strategy, content ideas, audience growth
            - "ai-learning": AI concepts, AI tools, mental models, applications
            - "all": All categories from every focus area
            Example: "entrepreneurial,investment"
        video_id: Optional YouTube video ID for reference tracking.
        max_insights: Maximum number of insights to extract (default: "10").
            Arrives as a string per MCP convention.

    Returns:
        Dictionary with extraction metadata including:
        - extraction_prompt: Ready-to-use prompt for Claude analysis
        - focus_areas: Parsed focus area names
        - categories: Insight categories to extract
        - category_definitions: What each category means
        - transcript_length: Character count of the transcript
        - chunk_count: Number of chunks (if long transcript)
        - needs_chunking: Whether the transcript was split
        - max_insights: The requested insight limit (as int)
        - chunks: List of chunk strings if chunked, else None

    Usage:
        1. Call this tool with a transcript
        2. Use the returned extraction_prompt with Claude
        3. Parse Claude's JSON response as structured insights
    """
    # CRITICAL: Parameter type conversion (MCP sends strings)
    try:
        max_insights_int = int(max_insights)
    except (ValueError, TypeError) as exc:
        logger.warning("Invalid max_insights value %r: %s", max_insights, exc)
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_PARAMETER",
                "message": f"max_insights must be a valid integer, got: {max_insights!r}",
            }
        }

    # Parse comma-separated focus areas
    focus_list = [f.strip().lower() for f in focus_areas.split(",")]

    # Validate focus areas against known presets + 'all'
    valid_areas = list(FOCUS_PRESETS.keys()) + ["all"]
    invalid = [f for f in focus_list if f not in valid_areas]
    if invalid:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_FOCUS_AREA",
                "message": (
                    f"Invalid focus areas: {invalid}. "
                    f"Valid options: {valid_areas}"
                ),
            }
        }

    # Check transcript length
    if len(transcript) < 100:
        return {
            "error": {
                "category": "client_error",
                "code": "TRANSCRIPT_TOO_SHORT",
                "message": "Transcript must be at least 100 characters",
            }
        }

    try:
        result = prepare_for_extraction(
            transcript=transcript,
            video_id=video_id if video_id else None,
            focus_areas=focus_list,
            max_insights=max_insights_int,
        )
        return result

    except Exception as exc:
        logger.exception("Error preparing extraction: %s", exc)
        return {
            "error": {
                "category": "server_error",
                "code": "EXTRACTION_PREP_ERROR",
                "message": str(exc),
            }
        }


@mcp.tool()
async def list_focus_areas() -> dict[str, Any]:
    """List available focus areas for insight extraction.

    Returns the available focus area presets and their insight categories,
    along with detailed definitions for each category. Use this to
    understand what kinds of insights can be extracted from transcripts.

    Each focus area contains 4 specialised categories. Pass focus area
    names as comma-separated values to the extract_insights tool.

    Returns:
        Dictionary with:
        - focus_areas: Mapping of preset names to their category lists
        - category_definitions: Mapping of every category to its description
        - usage_tip: Quick-start instructions for using focus areas
    """
    return {
        "focus_areas": {
            name: [cat.value for cat in categories]
            for name, categories in FOCUS_PRESETS.items()
        },
        "category_definitions": {
            cat.value: desc
            for cat, desc in CATEGORY_DEFINITIONS.items()
        },
        "usage_tip": "Pass focus areas as comma-separated: 'entrepreneurial,investment'",
    }


def _entry_point() -> None:
    """Entry point with CLI/MCP mode switching.

    Checks ``sys.argv`` to decide which mode to run:

    * ``python -m src cli <command> [args...]`` — dispatches to the CLI
      wrapper (``src.cli.main``), passing ``sys.argv[2:]`` as arguments
      and propagating the exit code via ``sys.exit()``.
    * ``python -m src`` (or any other invocation) — starts the MCP
      server over stdio transport (existing behaviour).

    The ``src.cli`` module is imported lazily so that MCP server mode
    never pays the cost of loading CLI dependencies.
    """
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # Lazy import: src.cli is only loaded when CLI mode is requested
        from youtube_insights_mcp.cli import main as cli_main

        exit_code = cli_main(sys.argv[2:])
        sys.exit(exit_code)
    else:
        logger.info("Starting %s server...", SERVER_NAME)
        mcp.run(transport="stdio")


if __name__ == "__main__":
    _entry_point()
