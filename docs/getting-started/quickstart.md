# Quick Start

Fetch your first YouTube transcript in 5 minutes.

## Step 1: Install

```bash
git clone https://github.com/appmilla/youtube-transcript-mcp.git
cd youtube-transcript-mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Step 2: Configure Claude Desktop

Create or edit `.mcp.json` in your project root (or `~/.claude/.mcp.json` for global config):

```json
{
  "mcpServers": {
    "youtube-transcript-mcp": {
      "command": "/absolute/path/to/youtube-transcript-mcp/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/absolute/path/to/youtube-transcript-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/youtube-transcript-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

!!! warning "Use absolute paths"
    All paths in `.mcp.json` **must** be absolute. Relative paths cause server startup failures. Replace `/absolute/path/to/youtube-transcript-mcp` with your actual project directory.

**Find your paths:**

```bash
# Get the project path
pwd

# Get the Python path
which python  # (with venv activated)
```

## Step 3: Use in Claude

Restart Claude Desktop to pick up the new configuration. Then try these prompts:

**Fetch a transcript:**

> Get the transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ

**List available languages:**

> What transcript languages are available for https://www.youtube.com/watch?v=dQw4w9WgXcQ

**Extract insights:**

> Extract technical insights from this YouTube video: https://www.youtube.com/watch?v=example

Claude will automatically use the MCP tools to fetch transcripts and extract insights.

## Step 4: Try the CLI

The CLI provides direct terminal access to the same tools without needing MCP:

```bash
# Fetch a transcript
python -m src cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# List available transcript languages
python -m src cli list-transcripts "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get transcript without timestamp segments (smaller output)
python -m src cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-segments

# List focus area presets
python -m src cli list-focus-areas

# Pipe transcript to jq for the full text only
python -m src cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" | jq '.full_text'
```

All CLI commands output JSON to stdout, making them easy to pipe and script.

## What's Next?

- [Configuration](configuration.md) - Environment variables, transport options
- [MCP Tools Reference](../tools/index.md) - Detailed documentation for all 4 tools
- [CLI Guide](../cli/index.md) - Full CLI command reference
- [Focus Areas](../focus-areas/index.md) - Insight extraction presets
