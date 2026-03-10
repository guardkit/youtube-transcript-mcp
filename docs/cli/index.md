# CLI Guide

YouTube Transcript MCP includes a command-line interface that wraps the MCP tools for direct shell usage. All output is JSON on stdout, making the CLI composable with tools like `jq` and suitable for shell scripts, automation, and agent pipelines.

```bash
python -m src cli <command> [options]
```

## Key Features

- **JSON-only stdout** -- All output is valid JSON. Logs go to stderr, so stdout is always parseable.
- **Stdin support** -- The `extract-insights` command reads from stdin with `-`, enabling piped workflows.
- **Consistent error format** -- All errors return structured JSON with `category`, `code`, and `message` fields.
- **Exit codes** -- `0` on success, `1` on error.

## Available Commands

| Command | Description |
|---------|-------------|
| [`ping`](commands.md#ping) | Health check -- verifies server is importable |
| [`video-info`](commands.md#video-info) | Fetch metadata for a YouTube video |
| [`get-transcript`](commands.md#get-transcript) | Fetch transcript with language and format options |
| [`list-transcripts`](commands.md#list-transcripts) | List available transcript languages |
| [`extract-insights`](commands.md#extract-insights) | Prepare transcript for structured insight extraction |
| [`list-focus-areas`](commands.md#list-focus-areas) | List all focus area presets and categories |

## Quick Example

```bash
# Fetch a transcript and extract the plain text
python -m src cli get-transcript dQw4w9WgXcQ | jq -r '.full_text'

# Pipe into insight extraction
python -m src cli get-transcript dQw4w9WgXcQ | \
  jq -r '.full_text' | \
  python -m src cli extract-insights - --focus technical
```

See [Commands Reference](commands.md) for full details on each command and [Examples](examples.md) for practical usage patterns including piping, batch processing, and shell scripts.
