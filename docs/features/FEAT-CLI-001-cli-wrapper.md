# FEAT-CLI-001: CLI Wrapper

## Overview

Wrap the core library functions in a CLI so the tools can be invoked directly from the command line, independent of the MCP transport layer. This enables use from deep agents, shell scripts, cron jobs, and direct terminal use without requiring a running MCP server.

**Complexity**: 3/10  
**Estimated Time**: 2-3 hours  
**Dependencies**: FEAT-SKEL-003 (Transcript Tool), FEAT-INT-001 (Insight Extraction)

## Business Context

The MCP server is the primary interface for Claude Desktop. However, the same tooling should be accessible in two additional ways:

1. **Deep agents** - An autonomous agent can shell out to `python -m src cli get-transcript <url>` and parse JSON output without needing MCP protocol overhead
2. **Direct/planning use** - Rich can call transcript and insight extraction directly from the terminal during planning sessions, without needing Claude Desktop open

This is a thin wrapper - the CLI calls the same service classes as the MCP tools. No business logic lives in the CLI layer itself.

## Acceptance Criteria

1. CLI is invocable via `python -m src cli <command> [args]`
2. All output is valid JSON (stdout) so agents can parse it
3. All logging remains on stderr (consistent with MCP server behaviour)
4. Commands mirror the MCP tools: `ping`, `video-info`, `get-transcript`, `extract-insights`, `list-focus-areas`
5. `--help` works on all commands with clear argument descriptions
6. Exit code 0 on success, non-zero on error
7. Unit tests cover CLI argument parsing and output format
8. Entry point does NOT interfere with MCP server (`__main__.py` still runs MCP when called without `cli` subcommand)

## Technical Specification

### Architecture: Single Entry Point, Two Modes

```
python -m src                    → runs MCP server (existing behaviour)
python -m src cli <command>      → runs CLI command
```

The `__main__.py` entry point switches modes based on whether the first argument is `cli`.

### CLI Module (`src/cli.py`)

```python
"""CLI wrapper for youtube-transcript-mcp.

Provides command-line access to all MCP tools, outputting JSON to stdout.
This enables use from deep agents, shell scripts, and direct terminal usage
without requiring the MCP transport layer.

CRITICAL: All logging goes to stderr. stdout is JSON only.
"""

import sys
import json
import asyncio
import argparse
import logging

logger = logging.getLogger(__name__)


def make_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI."""
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


def output_json(data: dict) -> None:
    """Write JSON to stdout. This is the ONLY thing that goes to stdout."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def exit_code_from_result(result: dict) -> int:
    """Determine exit code based on result dict."""
    if "error" in result:
        return 1
    return 0


async def run_command(args: argparse.Namespace) -> dict:
    """Dispatch to the appropriate service function."""

    if args.command == "ping":
        from datetime import datetime, timezone
        return {
            "status": "healthy",
            "server": "youtube-transcript-mcp",
            "version": "0.1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": "cli",
        }

    elif args.command == "video-info":
        from src.services.youtube_client import YouTubeClient, InvalidURLError, VideoNotFoundError
        client = YouTubeClient()
        try:
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
        except InvalidURLError as e:
            return {"error": {"category": "client_error", "code": "INVALID_URL", "message": str(e)}}
        except VideoNotFoundError as e:
            return {"error": {"category": "client_error", "code": "VIDEO_NOT_FOUND", "message": str(e)}}

    elif args.command == "get-transcript":
        from src.services.youtube_client import extract_video_id, InvalidURLError
        from src.services.transcript_client import (
            TranscriptClient, TranscriptsDisabledError,
            NoTranscriptFoundError, VideoUnavailableError,
        )
        try:
            video_id = extract_video_id(args.video_url)
        except InvalidURLError as e:
            return {"error": {"category": "client_error", "code": "INVALID_URL", "message": str(e)}}

        client = TranscriptClient()
        try:
            result = await client.get_transcript(video_id, args.language)
            output = {
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
            return {"error": {"category": "client_error", "code": "TRANSCRIPTS_DISABLED", "message": str(e)}}
        except NoTranscriptFoundError as e:
            return {"error": {"category": "client_error", "code": "NO_TRANSCRIPT_FOUND",
                               "message": str(e), "available_languages": e.available_languages}}
        except VideoUnavailableError as e:
            return {"error": {"category": "client_error", "code": "VIDEO_UNAVAILABLE", "message": str(e)}}

    elif args.command == "list-transcripts":
        from src.services.youtube_client import extract_video_id, InvalidURLError
        from src.services.transcript_client import TranscriptClient
        try:
            video_id = extract_video_id(args.video_url)
        except InvalidURLError as e:
            return {"error": {"category": "client_error", "code": "INVALID_URL", "message": str(e)}}
        client = TranscriptClient()
        transcripts = await client.list_transcripts(video_id)
        return {"video_id": video_id, "transcripts": transcripts, "count": len(transcripts)}

    elif args.command == "extract-insights":
        from src.services.insight_extractor import prepare_for_extraction

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
        from src.models.insight import FOCUS_PRESETS, CATEGORY_DEFINITIONS
        return {
            "focus_areas": {
                name: [cat.value for cat in categories]
                for name, categories in FOCUS_PRESETS.items()
            },
            "category_definitions": {
                cat.value: desc
                for cat, desc in CATEGORY_DEFINITIONS.items()
            },
            "usage_tip": (
                "Pass focus areas as comma-separated: "
                "'entrepreneurial,investment' or 'youtube-channel'"
            ),
        }

    else:
        return {"error": {"category": "client_error", "code": "UNKNOWN_COMMAND",
                          "message": f"Unknown command: {args.command}"}}


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns exit code."""
    parser = make_parser()
    args = parser.parse_args(argv)

    result = asyncio.run(run_command(args))
    output_json(result)
    return exit_code_from_result(result)
```

### Updated Entry Point (`src/__main__.py` addition)

Add mode-switching logic at the bottom of `__main__.py`:

```python
if __name__ == "__main__":
    # Switch between MCP server mode and CLI mode
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # CLI mode: python -m src cli <command> [args]
        from src.cli import main
        sys.exit(main(sys.argv[2:]))
    else:
        # MCP server mode (default): python -m src
        logger.info("Starting youtube-transcript-mcp server...")
        mcp.run(transport="stdio")
```

### Unit Tests (`tests/unit/test_cli.py`)

```python
"""Tests for CLI wrapper."""

import json
import pytest
from unittest.mock import patch, AsyncMock

from src.cli import main, make_parser


class TestCliParser:
    """Tests for argument parsing."""

    def test_ping_command(self):
        parser = make_parser()
        args = parser.parse_args(["ping"])
        assert args.command == "ping"

    def test_video_info_command(self):
        parser = make_parser()
        args = parser.parse_args(["video-info", "https://youtu.be/dQw4w9WgXcQ"])
        assert args.command == "video-info"
        assert args.video_url == "https://youtu.be/dQw4w9WgXcQ"

    def test_get_transcript_defaults(self):
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ"])
        assert args.language == "en"
        assert args.no_segments is False

    def test_get_transcript_with_language(self):
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ", "--language", "fr"])
        assert args.language == "fr"

    def test_get_transcript_no_segments_flag(self):
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ", "--no-segments"])
        assert args.no_segments is True

    def test_extract_insights_defaults(self):
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "some transcript text"])
        assert args.focus_areas == "general"
        assert args.max_insights == 10

    def test_extract_insights_youtube_channel_preset(self):
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--focus", "youtube-channel"])
        assert args.focus_areas == "youtube-channel"

    def test_extract_insights_multiple_focus(self):
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--focus", "entrepreneurial,investment"])
        assert args.focus_areas == "entrepreneurial,investment"


class TestCliOutput:
    """Tests for CLI JSON output."""

    def test_ping_returns_valid_json(self, capsys):
        exit_code = main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "healthy"
        assert data["mode"] == "cli"
        assert exit_code == 0

    def test_error_result_exits_nonzero(self, capsys):
        exit_code = main(["video-info", "not-a-valid-id-because-too-long"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "error" in data
        assert exit_code == 1

    def test_list_focus_areas_returns_all_presets(self, capsys):
        exit_code = main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "youtube-channel" in data["focus_areas"]
        assert "ai-learning" in data["focus_areas"]
        assert "entrepreneurial" in data["focus_areas"]
        assert exit_code == 0
```

### Integration Test (`tests/integration/test_cli_integration.py`)

```python
"""Integration tests for CLI - requires network access. Mark as slow."""

import json
import pytest
from src.cli import main


@pytest.mark.slow
@pytest.mark.integration
class TestCLIIntegration:
    """Real network calls - run with pytest -m integration."""

    def test_get_transcript_real_video(self, capsys):
        """Test full transcript fetch for a known public video."""
        exit_code = main(["get-transcript", "dQw4w9WgXcQ", "--no-segments"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        assert "full_text" in data
        assert len(data["full_text"]) > 100

    def test_video_info_real_video(self, capsys):
        """Test video metadata fetch for a known public video."""
        exit_code = main(["video-info", "dQw4w9WgXcQ"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert "title" in data
```

## File Structure After Implementation

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # Updated: mode-switching (MCP vs CLI)
│   └── cli.py                   # NEW: CLI entry point
├── tests/
│   ├── unit/
│   │   └── test_cli.py          # NEW: CLI unit tests
│   └── integration/
│       └── test_cli_integration.py  # NEW: CLI integration tests
└── (no pyproject.toml changes needed - no new dependencies)
```

## Example Usage

```bash
# Health check
python -m src cli ping

# Get video metadata
python -m src cli video-info https://youtu.be/dQw4w9WgXcQ

# Get transcript (full)
python -m src cli get-transcript https://youtu.be/dQw4w9WgXcQ

# Get transcript (text only, no segments - smaller payload for agents)
python -m src cli get-transcript https://youtu.be/dQw4w9WgXcQ --no-segments

# Get transcript in another language
python -m src cli get-transcript https://youtu.be/dQw4w9WgXcQ --language es

# List available transcript languages
python -m src cli list-transcripts https://youtu.be/dQw4w9WgXcQ

# Prepare insight extraction (entrepreneurial preset)
python -m src cli extract-insights "$(cat my_transcript.txt)" --focus entrepreneurial

# Prepare insight extraction (Rich's YouTube channel planning preset)
python -m src cli extract-insights "$(cat my_transcript.txt)" --focus youtube-channel

# Combined focus areas
python -m src cli extract-insights "$(cat my_transcript.txt)" --focus "youtube-channel,ai-learning"

# Pipe transcript from get-transcript into extract-insights
python -m src cli get-transcript https://youtu.be/dQw4w9WgXcQ --no-segments | \
  python -c "import json,sys; print(json.load(sys.stdin)['full_text'])" | \
  python -m src cli extract-insights - --focus entrepreneurial

# Deep agent usage pattern (JSON output, check exit code)
result=$(python -m src cli get-transcript "$VIDEO_URL" --no-segments)
if [ $? -eq 0 ]; then
  echo "$result" | python -c "import json,sys; d=json.load(sys.stdin); print(d['full_text'])"
fi

# List all available focus areas
python -m src cli list-focus-areas
```

## Definition of Done

- [ ] `src/cli.py` implements all commands with JSON output
- [ ] `__main__.py` switches between MCP and CLI mode correctly
- [ ] MCP server behaviour unchanged when no `cli` argument passed
- [ ] `--help` works on all subcommands
- [ ] All output to stdout is valid JSON
- [ ] All logging goes to stderr
- [ ] Exit code 0 on success, 1 on error
- [ ] Unit tests cover argument parsing and output format
- [ ] Integration tests cover real network calls (marked `slow`)
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

### Critical: stdout is JSON only

The CLI follows the same constraint as the MCP server - stdout is reserved for structured output. The reason is different (JSON for agents vs JSON-RPC for MCP) but the discipline is identical:

```python
# CORRECT - only in output_json()
print(json.dumps(data))

# WRONG - corrupts agent parsing
print("Fetching transcript...")
logging.basicConfig()  # defaults to stdout
```

### Agent Consumption Pattern

A deep agent calling this CLI should:
1. Capture stdout as the result payload
2. Check exit code: 0 = success, 1 = error
3. Parse stdout as JSON
4. Check for `"error"` key in result before using data

### Stdin Support for Transcript Text

The `extract-insights` command supports `-` as the transcript argument to read from stdin. This enables pipelines:

```bash
# Get transcript and pipe directly to insight extraction
python -m src cli get-transcript "$URL" --no-segments \
  | jq -r '.full_text' \
  | python -m src cli extract-insights - --focus youtube-channel
```
