# Configuration

## Claude Desktop Configuration

The MCP server connects to Claude Desktop via the MCP configuration file (`claude_desktop_config.json`). Claude Desktop reads this file to discover and launch MCP servers.

### Using pip install (recommended)

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Using a local clone

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "youtube_insights_mcp"],
      "cwd": "/absolute/path/to/youtube-transcript-mcp",
      "env": {
        "PYTHONPATH": "/absolute/path/to/youtube-transcript-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

A template file is provided at `.mcp.json.template` in the repository root.

### Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `command` | Path to the installed entry point, or absolute path to Python in your venv | `youtube-insights-mcp` or `/Users/you/project/.venv/bin/python` |
| `args` | Arguments to start the MCP server (only needed for local clone) | `["-m", "youtube_insights_mcp"]` |
| `cwd` | Absolute path to the project root directory (local clone only) | `/Users/you/youtube-transcript-mcp` |
| `env.PYTHONPATH` | Must match `cwd` for correct module resolution (local clone only) | `/Users/you/youtube-transcript-mcp` |
| `env.LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

!!! danger "Absolute paths required"
    When using a local clone, all paths **must** be absolute. Relative paths like `./venv/bin/python` or `../project` will cause the server to fail silently on startup.

### Platform Examples (local clone)

=== "macOS"

    ```json
    {
      "mcpServers": {
        "youtube-insights-mcp": {
          "command": "/Users/yourname/Projects/youtube-transcript-mcp/.venv/bin/python",
          "args": ["-m", "youtube_insights_mcp"],
          "cwd": "/Users/yourname/Projects/youtube-transcript-mcp",
          "env": {
            "PYTHONPATH": "/Users/yourname/Projects/youtube-transcript-mcp",
            "LOG_LEVEL": "INFO"
          }
        }
      }
    }
    ```

=== "Linux"

    ```json
    {
      "mcpServers": {
        "youtube-insights-mcp": {
          "command": "/home/yourname/projects/youtube-transcript-mcp/.venv/bin/python",
          "args": ["-m", "youtube_insights_mcp"],
          "cwd": "/home/yourname/projects/youtube-transcript-mcp",
          "env": {
            "PYTHONPATH": "/home/yourname/projects/youtube-transcript-mcp",
            "LOG_LEVEL": "INFO"
          }
        }
      }
    }
    ```

=== "Windows"

    ```json
    {
      "mcpServers": {
        "youtube-insights-mcp": {
          "command": "C:\\Users\\yourname\\Projects\\youtube-transcript-mcp\\.venv\\Scripts\\python.exe",
          "args": ["-m", "youtube_insights_mcp"],
          "cwd": "C:\\Users\\yourname\\Projects\\youtube-transcript-mcp",
          "env": {
            "PYTHONPATH": "C:\\Users\\yourname\\Projects\\youtube-transcript-mcp",
            "LOG_LEVEL": "INFO"
          }
        }
      }
    }
    ```

### Configuration File Locations

| Location | Scope | Priority |
|----------|-------|----------|
| `<project>/.mcp.json` | Project-specific | Highest |
| `~/.claude/.mcp.json` | Global (all projects) | Lower |

Project-specific configuration takes precedence over global configuration.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level. Set to `DEBUG` for verbose output, `WARNING` for quiet operation. |
| `PYTHONPATH` | (none) | Must be set to project root for correct imports (local clone only). |

### Setting Log Level

For development and debugging, set `LOG_LEVEL=DEBUG`:

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

All log output goes to **stderr** (stdout is reserved for MCP protocol messages).

## Transport

The server uses **stdio** transport by default, which is the recommended transport for Claude Desktop integration. The server communicates via stdin/stdout using the MCP JSON-RPC protocol.

```bash
# Default: stdio transport (used by Claude Desktop)
youtube-insights-mcp
```

No additional transport configuration is needed for standard Claude Desktop usage.

## Verifying Configuration

After configuring, verify the server starts correctly:

1. **Restart Claude Desktop** to reload the configuration
2. **Check the server appears** in Claude's MCP server list
3. **Test with a prompt**: "Get the transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ"

If the server fails to start, check:

- All paths are absolute (when using local clone)
- The package is installed (`pip show youtube-insights-mcp`)
- Python version is >= 3.10

See [Troubleshooting](../troubleshooting.md) for common issues and solutions.
