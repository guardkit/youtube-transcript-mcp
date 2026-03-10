# Installation

## Prerequisites

- **Python >= 3.10** (check with `python3 --version`)
- **pip** (included with Python)
- **Git** (for installing from source)

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

## Install from PyPI

!!! note "Coming soon"
    PyPI publishing is planned. For now, install from source.

```bash
pip install youtube-transcript-mcp
```

## Verify Installation

Check that the server starts correctly:

```bash
# Run the MCP server (will wait for stdin - press Ctrl+C to exit)
python -m src
```

Test the CLI interface:

```bash
# Health check
python -m src cli ping
```

Expected output:

```json
{
  "status": "healthy",
  "server": "youtube-transcript-mcp",
  "version": "0.1.0",
  "mode": "cli"
}
```

## Next Steps

- [Quick Start](quickstart.md) - Fetch your first transcript in 5 minutes
- [Configuration](configuration.md) - Set up Claude Desktop integration
