# youtube-insights-mcp

[![PyPI version](https://img.shields.io/pypi/v/youtube-insights-mcp)](https://pypi.org/project/youtube-insights-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/youtube-insights-mcp)](https://pypi.org/project/youtube-insights-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An MCP server that fetches YouTube transcripts and extracts structured insights using Claude. Provides 4 MCP tools and a full CLI, with 6 focus area presets across 24 insight categories.

## Features

- **Transcript extraction** with intelligent language fallback
- **Structured insight analysis** across 24 categories (business, investment, technical, YouTube growth, AI learning)
- **6 focus area presets**: general, entrepreneurial, investment, technical, youtube-channel, ai-learning
- **Multiple URL formats**: youtube.com, youtu.be, embed links, or just a video ID
- **Dual mode**: MCP server for Claude Desktop + standalone CLI
- **Claude Code skill**: `/yt-insights` slash command for interactive insight extraction
- **Smart chunking** for long transcripts with overlap for context continuity
- **Proxy support** for environments with IP restrictions

## Prerequisites

You need Python 3.10 or later. Check if it's installed:

```bash
python3 --version
```

**If Python is not installed:**

- **macOS**: `brew install python` (requires [Homebrew](https://brew.sh)) or download from [python.org](https://www.python.org/downloads/)
- **Windows**: Download from [python.org](https://www.python.org/downloads/) (check "Add to PATH" during install)
- **Linux**: `sudo apt install python3 python3-pip` (Debian/Ubuntu) or `sudo dnf install python3 python3-pip` (Fedora)

## Installation

We recommend installing in a virtual environment to avoid conflicts with other Python packages:

```bash
# Create and activate a virtual environment
python3 -m venv youtube-mcp-env
source youtube-mcp-env/bin/activate  # On Windows: youtube-mcp-env\Scripts\activate

# Install the package
pip install youtube-insights-mcp
```

> **Troubleshooting:** If you see `ModuleNotFoundError: No module named 'pip'`, your system Python is misconfigured. Create a virtual environment first (as shown above) — this gives you a clean, working pip.

## Quick Start

### Claude Desktop Configuration

After installing, find the absolute path to the command:

```bash
which youtube-insights-mcp
```

Then add to your Claude Desktop MCP configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "/absolute/path/to/youtube-mcp-env/bin/youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Replace `/absolute/path/to/youtube-mcp-env/bin/youtube-insights-mcp` with the output from `which youtube-insights-mcp`.

> **Important:** Claude Desktop does not use your shell's PATH or virtual environment. You must provide the **full absolute path** to the command. Using just `"command": "youtube-insights-mcp"` will fail unless it's installed globally on your system PATH.

### Starting the Server

**With Claude Desktop** — no manual start needed. Claude Desktop automatically launches and manages the server process using the configuration above. Just restart Claude Desktop after adding the config.

**Manual start** (for testing or other MCP clients):

```bash
# Start the MCP server (stdio transport)
youtube-insights-mcp

# Or using Python module directly
python -m youtube_insights_mcp
```

The server communicates via stdin/stdout using the MCP JSON-RPC protocol. It is designed to be started by an MCP client (like Claude Desktop) rather than run interactively.

### CLI Usage

```bash
# Health check
youtube-insights-mcp cli ping

# Fetch a transcript
youtube-insights-mcp cli get-transcript "https://www.youtube.com/watch?v=VIDEO_ID"

# List available transcript languages
youtube-insights-mcp cli list-transcripts "https://www.youtube.com/watch?v=VIDEO_ID"

# Extract insights (pipe transcript from stdin)
youtube-insights-mcp cli get-transcript VIDEO_ID --no-segments | \
  jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - --focus "entrepreneurial,investment"

# List all focus areas and categories
youtube-insights-mcp cli list-focus-areas
```

## MCP Tools

### `get_transcript`

Fetch transcript for a YouTube video with intelligent language fallback.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_url` | string | required | YouTube URL or video ID |
| `language` | string | `"en"` | Preferred language code |

Fallback order: requested language > auto-generated version > any English variant > first available.

### `list_available_transcripts`

List all available transcript languages for a video. Useful for checking what's available before fetching.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `video_url` | string | required | YouTube URL or video ID |

### `extract_insights`

Prepare a transcript for structured insight extraction by Claude. Returns an extraction prompt, categories, and chunked transcript data.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `transcript` | string | required | Full transcript text (min 100 chars) |
| `focus_areas` | string | `"general"` | Comma-separated focus areas |
| `video_id` | string | `""` | Optional video ID for tracking |
| `max_insights` | string | `"10"` | Maximum insights to extract |

### `list_focus_areas`

List all available focus area presets and their category definitions.

## Focus Areas

| Preset | Categories |
|--------|-----------|
| **general** | Key points, action items, notable quotes, context |
| **entrepreneurial** | Business strategies, growth tactics, lessons learned, mistakes to avoid |
| **investment** | Market trends, opportunities, risks, recommendations |
| **technical** | Technologies, tools, best practices, pitfalls |
| **youtube-channel** | Channel strategy, content ideas, audience growth, production tips |
| **ai-learning** | AI concepts, AI tools, mental models, practical applications |

Use `"all"` to extract across every category, or combine presets: `"entrepreneurial,investment"`.

## Example Prompts for Claude Desktop

Once the MCP server is configured, you can use these prompts directly in Claude Desktop:

### Transcript & Summary

> Get the transcript for https://www.youtube.com/watch?v=VIDEO_ID and give me a concise summary

> Fetch the transcript for this video and list the 5 most important takeaways: https://youtu.be/VIDEO_ID

### Business & Entrepreneurship

> Get the transcript for https://www.youtube.com/watch?v=VIDEO_ID and extract entrepreneurial insights - focus on actionable business strategies and growth tactics

> Analyse this startup pitch and pull out the key business model, revenue strategy, and mistakes to avoid: https://www.youtube.com/watch?v=VIDEO_ID

### Investment Analysis

> Fetch the transcript for this market analysis video and extract investment insights including trends, opportunities, and risks: https://www.youtube.com/watch?v=VIDEO_ID

### Technical Learning

> Get the transcript for this tech talk and extract the key technologies mentioned, best practices, and common pitfalls: https://www.youtube.com/watch?v=VIDEO_ID

> Summarise this programming tutorial and list the tools and frameworks recommended: https://youtu.be/VIDEO_ID

### YouTube Channel Growth

> Analyse this video about growing a YouTube channel and extract content strategy tips, audience growth tactics, and production advice: https://www.youtube.com/watch?v=VIDEO_ID

### AI & Machine Learning

> Fetch the transcript for this AI talk and extract the key concepts, tools mentioned, and practical applications: https://www.youtube.com/watch?v=VIDEO_ID

### Multi-Focus Analysis

> Get the transcript for https://www.youtube.com/watch?v=VIDEO_ID and extract insights across both entrepreneurial and investment categories - I want business strategies AND market opportunities

### Comparing Videos

> Get the transcripts for these two videos and compare their advice on starting a business:
> - https://www.youtube.com/watch?v=VIDEO_ID_1
> - https://www.youtube.com/watch?v=VIDEO_ID_2

## Using with Claude Code & Cowork

The project includes a `/yt-insights` skill for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that provides an interactive workflow for extracting insights from YouTube videos. It works in both Claude Code (terminal) and Claude Cowork (collaborative mode).

### Setup

1. Clone the repository and add the MCP server to your Claude Code config (`.mcp.json`):

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "/absolute/path/to/youtube-mcp-env/bin/youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

2. The `/yt-insights` skill is automatically available from the project's `.claude/commands/` directory.

### Usage

Run the skill in Claude Code or Cowork:

```
/yt-insights https://www.youtube.com/watch?v=VIDEO_ID
```

Or just `/yt-insights` and it will prompt you for the URL.

The skill will:

1. Ask you to choose focus areas (general, entrepreneurial, investment, technical, youtube-channel, ai-learning, or all)
2. Fetch the video transcript
3. Extract structured insights using Claude
4. Save two markdown files:
   - **Insights** — structured analysis with key quotes, action items, and categorised insights
   - **Transcript** — full transcript text for future reference

### Cowork Mode

In Cowork, the skill is automatically converted to a Cowork skill. It uses the MCP tools directly (rather than CLI commands), which means it connects to the youtube-insights-mcp server through the MCP protocol for a seamless experience.

## Configuration

### Proxy Support

If YouTube blocks your IP, configure a proxy via environment variables:

```json
{
  "env": {
    "PROXY_URL": "http://user:pass@proxy:8080",
    "WEBSHARE_USERNAME": "",
    "WEBSHARE_PASSWORD": ""
  }
}
```

Priority: Webshare credentials > PROXY_URL > no proxy.

## Requirements

- Python >= 3.10
- Dependencies: `mcp`, `pydantic`, `youtube-transcript-api`, `yt-dlp`

## License

MIT
