# Quick Start

Fetch your first YouTube transcript in 5 minutes.

## Step 1: Install

```bash
pip install youtube-insights-mcp
```

Or install from source:

```bash
git clone https://github.com/appmilla/youtube-transcript-mcp.git
cd youtube-transcript-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Step 2: Configure Claude Desktop

Add to your Claude Desktop MCP configuration (`claude_desktop_config.json`):

First, find the absolute path to the installed command (with your venv activated):

```bash
which youtube-insights-mcp
```

This will output something like `/Users/yourname/youtube-mcp-env/bin/youtube-insights-mcp`.

Then add to your Claude Desktop config using that full path:

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

!!! warning "Use the full absolute path"
    Claude Desktop does **not** use your shell's PATH or virtual environment. You must provide the full absolute path from `which youtube-insights-mcp`. Using just `"command": "youtube-insights-mcp"` will fail.

## Step 3: Start the Server

**With Claude Desktop** — no manual start needed. Claude Desktop automatically launches and manages the server process using the configuration above. Just restart Claude Desktop after adding the config.

**Manual start** (for testing or other MCP clients):

```bash
# Start the MCP server (stdio transport)
youtube-insights-mcp

# Or using Python module directly
python -m youtube_insights_mcp
```

## Step 4: Use in Claude

Restart Claude Desktop to pick up the new configuration. Then try these prompts:

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

Claude will automatically use the MCP tools to fetch transcripts and extract insights.

## Step 5: Try the CLI

The CLI provides direct terminal access to the same tools without needing MCP:

```bash
# Health check
youtube-insights-mcp cli ping

# Fetch a transcript
youtube-insights-mcp cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# List available transcript languages
youtube-insights-mcp cli list-transcripts "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get transcript without timestamp segments (smaller output)
youtube-insights-mcp cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-segments

# List focus area presets
youtube-insights-mcp cli list-focus-areas

# Pipe transcript to jq for the full text only
youtube-insights-mcp cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" | jq '.full_text'
```

All CLI commands output JSON to stdout, making them easy to pipe and script.

## What's Next?

- [Configuration](configuration.md) - Environment variables, transport options
- [MCP Tools Reference](../tools/index.md) - Detailed documentation for all 4 tools
- [CLI Guide](../cli/index.md) - Full CLI command reference
- [Focus Areas](../focus-areas/index.md) - Insight extraction presets
