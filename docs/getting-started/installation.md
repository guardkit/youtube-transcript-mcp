# Installation

## Prerequisites

- **Python >= 3.10** (check with `python3 --version`)
- **pip** (included with Python)

## Install from PyPI

```bash
pip install youtube-insights-mcp
```

Or with development dependencies:

```bash
pip install youtube-insights-mcp[dev]
```

## Install from Source

Clone the repository and install in development mode:

```bash
git clone https://github.com/appmilla/youtube-transcript-mcp.git
cd youtube-transcript-mcp
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

This installs the server and all runtime dependencies:

| Package | Purpose |
|---------|---------|
| `mcp>=1.0.0` | MCP protocol framework (FastMCP) |
| `pydantic>=2.0` | Parameter validation |
| `yt-dlp>=2024.1.0` | YouTube video metadata extraction |
| `youtube-transcript-api>=1.0.0` | Transcript fetching |

### Development Dependencies

To also install testing and linting tools:

```bash
pip install -e ".[dev]"
```

This adds pytest, ruff, mypy, and related packages.

## Verify Installation

Check that the server starts correctly:

```bash
# Run the MCP server (will wait for stdin - press Ctrl+C to exit)
youtube-insights-mcp
```

Test the CLI interface:

```bash
# Health check
youtube-insights-mcp cli ping
```

Expected output:

```json
{
  "status": "healthy",
  "server": "youtube-insights-mcp",
  "version": "0.1.3",
  "mode": "cli"
}
```

## Next Steps

- [Quick Start](quickstart.md) - Fetch your first transcript in 5 minutes
- [Configuration](configuration.md) - Configure Claude Desktop integration
