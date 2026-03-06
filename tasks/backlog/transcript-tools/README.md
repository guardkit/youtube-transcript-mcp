# FEAT-SKEL-003: Transcript Fetching Tools

## Problem Statement

The YouTube Transcript MCP server needs the ability to fetch video transcripts — the core data retrieval capability for the Brandon collaboration project. Users need to extract spoken content from YouTube videos for subsequent insight analysis, with intelligent handling of language availability.

## Solution Approach

Implement two MCP tools following the established service layer pattern:

1. **`get_transcript`** — Fetches transcript for a video with 4-step language fallback (requested → auto-generated → English → first available)
2. **`list_available_transcripts`** — Lists all available transcript languages for a video

Both tools use a `TranscriptClient` service that wraps the `youtube-transcript-api` library with async support, structured error handling, and MCP-compliant responses.

## Architecture

```
LLM Client → MCP Tool (thin wrapper) → TranscriptClient (service) → youtube-transcript-api (external)
```

- **Service layer**: `src/services/transcript_client.py` — async wrappers, language fallback, exception hierarchy
- **Tool layer**: `src/__main__.py` — MCP tool registration, URL parsing, error formatting
- **External dependency**: `youtube-transcript-api>=1.0.0`

## Subtask Summary

| # | Task | Type | Complexity | Wave |
|---|------|------|-----------|------|
| 1 | [TASK-TRS-001](TASK-TRS-001-add-youtube-transcript-api-dependency.md) — Add dependency | scaffolding | 1/10 | 1 |
| 2 | [TASK-TRS-002](TASK-TRS-002-create-transcript-client-service.md) — Create TranscriptClient | feature | 5/10 | 2 |
| 3 | [TASK-TRS-003](TASK-TRS-003-register-transcript-tools.md) — Register MCP tools | feature | 4/10 | 3 |
| 4 | [TASK-TRS-004](TASK-TRS-004-create-unit-tests.md) — Create unit tests | testing | 4/10 | 4 |
| 5 | [TASK-TRS-005](TASK-TRS-005-verify-quality-checks.md) — Verify quality checks | testing | 2/10 | 5 |

**Total estimated time**: 4-5 hours (sequential execution)

## Execution Order

All tasks execute sequentially — each depends on the previous:

```
Wave 1: Add dependency → Wave 2: Create service → Wave 3: Register tools → Wave 4: Tests → Wave 5: Verify
```

## Key Decisions

- **Approach**: Direct feature spec implementation (no caching, no tool merging)
- **Trade-off priority**: Quality/reliability over speed
- **Testing**: Standard quality gates (>80% coverage, ruff, mypy)
- **Parent review**: [TASK-REV-9AD6](../TASK-REV-9AD6-plan-feat-skel-003-transcript-tools.md)

## Getting Started

```bash
# Start with Wave 1
/task-work TASK-TRS-001
```

See [IMPLEMENTATION-GUIDE.md](IMPLEMENTATION-GUIDE.md) for detailed execution strategy and diagrams.
