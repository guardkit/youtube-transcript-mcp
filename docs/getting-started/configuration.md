# Configuration

## Claude Desktop Configuration

The MCP server connects to Claude Desktop via the `.mcp.json` configuration file. Claude Desktop reads this file to discover and launch MCP servers.

### Configuration Template

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

A template file is provided at `.mcp.json.template` in the repository root.

### Configuration Fields

| Field | Description | Example |
|-------|-------------|---------|
| `command` | Absolute path to the Python interpreter in your virtual environment | `/Users/you/youtube-transcript-mcp/.venv/bin/python` |
| `args` | Arguments to start the MCP server | `["-m", "src"]` |
| `cwd` | Absolute path to the project root directory | `/Users/you/youtube-transcript-mcp` |
| `env.PYTHONPATH` | Must match `cwd` for correct module resolution | `/Users/you/youtube-transcript-mcp` |
| `env.LOG_LEVEL` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) | `INFO` |

!!! danger "Absolute paths required"
    All paths **must** be absolute. Relative paths like `./venv/bin/python` or `../project` will cause the server to fail silently on startup.

### Platform Examples

=== "macOS"

    ```json
    {
      "mcpServers": {
        "youtube-transcript-mcp": {
          "command": "/Users/yourname/Projects/youtube-transcript-mcp/.venv/bin/python",
          "args": ["-m", "src"],
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
        "youtube-transcript-mcp": {
          "command": "/home/yourname/projects/youtube-transcript-mcp/.venv/bin/python",
          "args": ["-m", "src"],
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
        "youtube-transcript-mcp": {
          "command": "C:\\Users\\yourname\\Projects\\youtube-transcript-mcp\\.venv\\Scripts\\python.exe",
          "args": ["-m", "src"],
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
| `PYTHONPATH` | (none) | Must be set to project root for correct imports. |

### Setting Log Level

For development and debugging, set `LOG_LEVEL=DEBUG` in your `.mcp.json`:

```json
{
  "mcpServers": {
    "youtube-transcript-mcp": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/absolute/path/to/project",
      "env": {
        "PYTHONPATH": "/absolute/path/to/project",
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
python -m src
```

No additional transport configuration is needed for standard Claude Desktop usage.

## Verifying Configuration

After configuring, verify the server starts correctly:

1. **Restart Claude Desktop** to reload the configuration
2. **Check the server appears** in Claude's MCP server list
3. **Test with a prompt**: "Get the transcript for https://www.youtube.com/watch?v=dQw4w9WgXcQ"

If the server fails to start, check:

- All paths in `.mcp.json` are absolute
- The virtual environment exists and has dependencies installed
- `PYTHONPATH` matches the `cwd` value
- Python version is >= 3.10

See [Troubleshooting](../troubleshooting.md) for common issues and solutions.
