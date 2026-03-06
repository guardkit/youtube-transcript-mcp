# FEAT-CLI-001: CLI Wrapper

## Problem Statement

The MCP server is the primary interface for Claude Desktop, but the same tooling needs to be accessible from:
1. **Deep agents** that shell out and parse JSON output without MCP protocol overhead
2. **Direct terminal use** for planning sessions without Claude Desktop

## Solution

A thin CLI wrapper (`src/cli.py`) using argparse that delegates to the same service classes as MCP tools. JSON-only stdout output enables machine parsing. Mode switching in `__main__.py` keeps the MCP server as the default.

```
python -m src              → MCP server (default, unchanged)
python -m src cli <cmd>    → CLI with JSON output
```

## Subtasks

| Task | Description | Complexity | Status |
|------|-------------|-----------|--------|
| TASK-CLI-001 | Create `src/cli.py` with argparse + command dispatch | 3/10 | pending |
| TASK-CLI-002 | Update `__main__.py` with mode switching | 2/10 | pending |
| TASK-CLI-003 | Unit tests for parser + output format | 2/10 | pending |
| TASK-CLI-004 | Integration tests with real network calls | 2/10 | pending |

## Commands

| CLI Command | MCP Tool Equivalent | Description |
|-------------|-------------------|-------------|
| `ping` | `ping` | Health check |
| `video-info <url>` | `get_video_info` | Fetch video metadata |
| `get-transcript <url>` | `get_transcript` | Fetch transcript |
| `list-transcripts <url>` | `list_transcripts` | List available languages |
| `extract-insights <text>` | `extract_insights` | Prepare insight extraction |
| `list-focus-areas` | `list_focus_areas` | List focus area presets |

## Dependencies

- FEAT-SKEL-001 (Basic MCP Server)
- FEAT-SKEL-003 (Transcript Tool)
- FEAT-INT-001 (Insight Extraction)

## Reference

- Feature spec: `docs/features/FEAT-CLI-001-cli-wrapper.md`
- Review: `tasks/backlog/TASK-REV-E5FC-plan-feat-cli-001-cli-wrapper.md`
