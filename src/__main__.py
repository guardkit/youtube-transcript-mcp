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

from src.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
)
from src.services.insight_extractor import prepare_for_extraction

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


if __name__ == "__main__":
    logger.info("Starting %s server...", SERVER_NAME)
    mcp.run(transport="stdio")
