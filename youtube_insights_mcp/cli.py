"""CLI wrapper for youtube-insights-mcp.

Provides command-line access to all MCP tools, outputting JSON to stdout.
This enables use from deep agents, shell scripts, and direct terminal usage
without requiring the MCP transport layer.

CRITICAL: All logging goes to stderr. stdout is JSON only.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


def make_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Registers all subcommands that mirror the MCP tools:
    ping, video-info, get-transcript, list-transcripts,
    extract-insights, and list-focus-areas.

    Returns:
        Configured ArgumentParser with all subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="youtube-mcp-cli",
        description="YouTube transcript and insight extraction CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ping
    subparsers.add_parser(
        "ping",
        help="Health check - verify server components are importable",
    )

    # video-info
    video_info_parser = subparsers.add_parser(
        "video-info",
        help="Fetch metadata for a YouTube video",
    )
    video_info_parser.add_argument(
        "video_url",
        help="YouTube URL or 11-character video ID",
    )

    # get-transcript
    transcript_parser = subparsers.add_parser(
        "get-transcript",
        help="Fetch the transcript for a YouTube video",
    )
    transcript_parser.add_argument(
        "video_url",
        help="YouTube URL or 11-character video ID",
    )
    transcript_parser.add_argument(
        "--language",
        default="en",
        help="Preferred language code (default: en). Falls back intelligently if unavailable.",
    )
    transcript_parser.add_argument(
        "--no-segments",
        action="store_true",
        help="Omit timestamped segments from output (smaller payload)",
    )

    # list-transcripts
    list_transcripts_parser = subparsers.add_parser(
        "list-transcripts",
        help="List all available transcript languages for a video",
    )
    list_transcripts_parser.add_argument(
        "video_url",
        help="YouTube URL or 11-character video ID",
    )

    # extract-insights
    insights_parser = subparsers.add_parser(
        "extract-insights",
        help="Prepare transcript for insight extraction (returns structured prompt + metadata)",
    )
    insights_parser.add_argument(
        "transcript",
        help="Full transcript text to analyse. Use '-' to read from stdin.",
    )
    insights_parser.add_argument(
        "--focus",
        default="general",
        dest="focus_areas",
        help=(
            "Focus areas for extraction. Options: general, entrepreneurial, investment, "
            "technical, youtube-channel, ai-learning. "
            "Comma-separated for multiple: 'entrepreneurial,investment'. "
            "Default: general"
        ),
    )
    insights_parser.add_argument(
        "--video-id",
        default="",
        help="Optional video ID to include in output for reference",
    )
    insights_parser.add_argument(
        "--max-insights",
        type=int,
        default=10,
        help="Maximum number of insights to extract (default: 10)",
    )

    # list-focus-areas
    subparsers.add_parser(
        "list-focus-areas",
        help="List all available focus area presets and their categories",
    )

    return parser


def output_json(data: dict[str, Any]) -> None:
    """Write JSON to stdout. This is the ONLY thing that goes to stdout.

    Args:
        data: Dictionary to serialise as JSON.
    """
    print(json.dumps(data, indent=2, ensure_ascii=False))


def exit_code_from_result(result: dict[str, Any]) -> int:
    """Determine exit code based on result dict.

    Args:
        result: The command result dictionary.

    Returns:
        0 on success, 1 if the result contains an ``"error"`` key.
    """
    if "error" in result:
        return 1
    return 0


async def run_command(args: argparse.Namespace) -> dict[str, Any]:
    """Dispatch to the appropriate service function.

    Imports services lazily inside the function to avoid import errors
    when services are not yet available or when only a subset of
    commands is needed.

    Args:
        args: Parsed argparse Namespace with command and flags.

    Returns:
        Result dictionary (may contain ``"error"`` key on failure).
    """
    if args.command == "ping":
        from datetime import datetime, timezone

        return {
            "status": "healthy",
            "server": "youtube-insights-mcp",
            "version": "0.1.4",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "cli",
        }

    elif args.command == "video-info":
        from youtube_insights_mcp.services.youtube_client import InvalidURLError, extract_video_id

        try:
            extract_video_id(args.video_url)
        except InvalidURLError as e:
            return {
                "error": {
                    "category": "client_error",
                    "code": "INVALID_URL",
                    "message": str(e),
                }
            }

        # Lazy import for full video info (requires network)
        try:
            from youtube_insights_mcp.services.youtube_client import (
                VideoNotFoundError,
                YouTubeClient,
            )

            client = YouTubeClient()
            info = await client.get_video_info(args.video_url)
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
        except ImportError:
            # YouTubeClient may not exist yet in all branches
            return {
                "error": {
                    "category": "server_error",
                    "code": "NOT_IMPLEMENTED",
                    "message": "YouTubeClient not available in this build",
                }
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
            logger.exception("Error fetching video info: %s", e)
            return {
                "error": {
                    "category": "server_error",
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                }
            }

    elif args.command == "get-transcript":
        from youtube_insights_mcp.services.transcript_client import (
            NoTranscriptFoundError,
            TranscriptClient,
            TranscriptsDisabledError,
            VideoUnavailableError,
            build_proxy_config,
        )
        from youtube_insights_mcp.services.youtube_client import InvalidURLError, extract_video_id

        try:
            video_id = extract_video_id(args.video_url)
        except InvalidURLError as e:
            return {
                "error": {
                    "category": "client_error",
                    "code": "INVALID_URL",
                    "message": str(e),
                }
            }

        client = TranscriptClient(proxy_config=build_proxy_config())
        try:
            result = await client.get_transcript(video_id, args.language)
            output: dict[str, Any] = {
                "video_id": result.video_id,
                "language": result.language,
                "language_code": result.language_code,
                "is_auto_generated": result.is_auto_generated,
                "full_text": result.full_text,
                "total_segments": result.total_segments,
                "total_duration_seconds": result.total_duration_seconds,
            }
            if not args.no_segments:
                output["segments"] = [
                    {"start": s.start, "duration": s.duration, "text": s.text}
                    for s in result.segments
                ]
            return output
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

    elif args.command == "list-transcripts":
        from youtube_insights_mcp.services.transcript_client import (
            TranscriptClient,
            build_proxy_config,
        )
        from youtube_insights_mcp.services.youtube_client import InvalidURLError, extract_video_id

        try:
            video_id = extract_video_id(args.video_url)
        except InvalidURLError as e:
            return {
                "error": {
                    "category": "client_error",
                    "code": "INVALID_URL",
                    "message": str(e),
                }
            }

        client = TranscriptClient(proxy_config=build_proxy_config())
        transcripts = await client.list_transcripts(video_id)
        return {
            "video_id": video_id,
            "transcripts": transcripts,
            "count": len(transcripts),
        }

    elif args.command == "extract-insights":
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        transcript_text = args.transcript
        if transcript_text == "-":
            transcript_text = sys.stdin.read()

        focus_list = [f.strip().lower() for f in args.focus_areas.split(",")]

        return prepare_for_extraction(
            transcript=transcript_text,
            video_id=args.video_id if args.video_id else None,
            focus_areas=focus_list,
            max_insights=args.max_insights,
        )

    elif args.command == "list-focus-areas":
        from youtube_insights_mcp.models.insight import CATEGORY_DEFINITIONS, FOCUS_PRESETS

        return {
            "focus_areas": {
                name: [cat.value for cat in categories]
                for name, categories in FOCUS_PRESETS.items()
            },
            "category_definitions": {
                cat.value: desc for cat, desc in CATEGORY_DEFINITIONS.items()
            },
            "usage_tip": (
                "Pass focus areas as comma-separated: "
                "'entrepreneurial,investment' or 'youtube-channel'"
            ),
        }

    else:
        return {
            "error": {
                "category": "client_error",
                "code": "UNKNOWN_COMMAND",
                "message": f"Unknown command: {args.command}",
            }
        }


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code.

    Parses arguments, dispatches to the async run_command() via
    asyncio.run(), outputs the result as JSON, and returns the
    appropriate exit code.

    Args:
        argv: Optional argument list (defaults to sys.argv[1:]).

    Returns:
        Exit code: 0 on success, 1 on error.
    """
    parser = make_parser()
    args = parser.parse_args(argv)

    result = asyncio.run(run_command(args))
    output_json(result)
    return exit_code_from_result(result)
