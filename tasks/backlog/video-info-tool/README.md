# FEAT-SKEL-002: Video Info Tool

## Problem

Before fetching transcripts, we need to verify a YouTube video exists and check caption availability. Currently there's no way to get video metadata through the MCP server.

## Solution

Add a `get_video_info` MCP tool that uses yt-dlp to fetch YouTube video metadata. The tool accepts various URL formats and returns structured metadata including title, channel, duration, and caption availability.

## Approach

**Option 1: Direct yt-dlp Integration** (selected)
- `YouTubeClient` service class wrapping yt-dlp with async
- `extract_video_id()` URL parser supporting 5+ formats
- Structured error responses for invalid URLs and unavailable videos
- `asyncio.to_thread()` for non-blocking execution

## Tasks

| # | Task | Complexity | Wave | Mode |
|---|------|-----------|------|------|
| 1 | [TASK-VID-001](TASK-VID-001-add-ytdlp-dependency.md) — Add yt-dlp dependency | 1 | 1 | direct |
| 2 | [TASK-VID-002](TASK-VID-002-create-youtube-client-service.md) — Create YouTubeClient service | 4 | 1 | task-work |
| 3 | [TASK-VID-003](TASK-VID-003-register-get-video-info-tool.md) — Register get_video_info tool | 2 | 2 | task-work |
| 4 | [TASK-VID-004](TASK-VID-004-create-unit-tests.md) — Create unit tests | 3 | 2 | task-work |
| 5 | [TASK-VID-005](TASK-VID-005-verify-mcp-inspector-linting.md) — Verify + linting | 1 | 3 | direct |

## Prerequisites

- FEAT-SKEL-001 (Basic MCP Server) must be implemented first

## Feature Spec

See [docs/features/FEAT-SKEL-002-video-info-tool.md](../../../docs/features/FEAT-SKEL-002-video-info-tool.md) for complete technical specification.
