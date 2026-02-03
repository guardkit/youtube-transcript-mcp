# FEAT-SKEL-001: Basic MCP Server with Health Check

## Overview

Create the foundational MCP server using FastMCP with a health check (ping) tool. This establishes the walking skeleton that all subsequent features build upon.

**Complexity**: 2/10  
**Estimated Time**: 2-3 hours  
**Dependencies**: None (first feature)

## Business Context

Part of the Brandon collaboration project for YouTube content digestion. This feature establishes the MCP server foundation that will eventually fetch transcripts and extract entrepreneurial/investment insights.

## Acceptance Criteria

1. FastMCP server initializes and runs with STDIO transport
2. `ping` tool returns health status with version and timestamp
3. All logging goes to stderr (stdout reserved for MCP protocol)
4. Server can be tested with MCP Inspector
5. Claude Desktop configuration template is provided
6. Unit tests pass with >80% coverage

## Technical Specification

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install MCP SDK (includes FastMCP)
pip install mcp
```

### Package Choice: mcp vs fastmcp

FastMCP is available from two packages. Choose ONE:

#### Option A: mcp package (Recommended)
```bash
pip install mcp
```

```python
from mcp.server.fastmcp import FastMCP
```

**Pros**: Official Anthropic package, includes full MCP SDK, stable API
**Cons**: Slightly larger install

#### Option B: fastmcp standalone
```bash
pip install 'fastmcp<3'
```

```python
from fastmcp import FastMCP
```

**Pros**: Smaller install, latest features in 3.x beta
**Cons**: Separate from official SDK

#### Recommendation

For this project, use **Option A** (`mcp` package) because:
- Official support from Anthropic
- More likely to stay compatible with Claude Desktop
- Simpler dependency management

Update imports accordingly:
```python
# Use this import
from mcp.server.fastmcp import FastMCP

# NOT this
from fastmcp import FastMCP
```

### Server Entry Point (`src/__main__.py`)

```python
"""YouTube Transcript MCP Server Entry Point.

CRITICAL PATTERNS:
- FastMCP for automatic protocol handling
- Tool registration at module level
- All logging to stderr (stdout = MCP protocol)
- Use timezone-aware datetime (never utcnow())
"""

import sys
import logging
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# CRITICAL: stderr only - stdout breaks MCP protocol
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP(
    name="youtube-transcript-mcp",
    version="0.1.0"
)

@mcp.tool()
async def ping() -> dict:
    """Health check - returns server status.
    
    Use this to verify the MCP server is running and responsive.
    
    Returns:
        Dictionary with status, server name, version, and UTC timestamp.
    """
    return {
        "status": "healthy",
        "server": "youtube-transcript-mcp",
        "version": "0.1.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

if __name__ == "__main__":
    logger.info("Starting youtube-transcript-mcp server...")
    mcp.run(transport="stdio")
```

### Project Configuration (`pyproject.toml`)

```toml
[project]
name = "youtube-transcript-mcp"
version = "0.1.0"
description = "MCP server for YouTube transcript fetching and insight extraction"
requires-python = ">=3.10"
readme = "README.md"

dependencies = [
    "mcp>=1.0.0",        # MCP SDK - includes FastMCP via mcp.server.fastmcp
]

# Alternative: standalone fastmcp package (if not using MCP SDK)
# dependencies = ["fastmcp>=2.0,<3"]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-asyncio>=0.21",
    "pytest-cov>=4.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 100
target-version = "py310"

[tool.mypy]
python_version = "3.10"
strict = true
```

### Claude Desktop Configuration (`.mcp.json.template`)

```json
{
  "mcpServers": {
    "youtube-transcript-mcp": {
      "command": "${VENV_PATH}/bin/python",
      "args": ["-m", "src"],
      "cwd": "${PROJECT_PATH}",
      "env": {
        "PYTHONPATH": "${PROJECT_PATH}",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Note**: Replace `${VENV_PATH}` and `${PROJECT_PATH}` with **absolute paths**.

Config file locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Unit Test (`tests/unit/test_ping.py`)

```python
"""Tests for ping health check tool."""

import pytest
from datetime import datetime, timezone

# Import the tool function directly for unit testing
from src.__main__ import ping


@pytest.mark.asyncio
async def test_ping_returns_healthy_status():
    """Ping should return healthy status."""
    result = await ping()
    
    assert result["status"] == "healthy"
    assert result["server"] == "youtube-transcript-mcp"
    assert result["version"] == "0.1.0"
    assert "timestamp" in result


@pytest.mark.asyncio
async def test_ping_timestamp_is_utc_iso_format():
    """Ping timestamp should be valid UTC ISO format."""
    result = await ping()
    
    # Should parse without error
    timestamp = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
    
    # Should be recent (within last minute)
    now = datetime.now(timezone.utc)
    delta = abs((now - timestamp).total_seconds())
    assert delta < 60, f"Timestamp {timestamp} is not recent"
```

### Protocol Test (`tests/protocol/test_mcp_protocol.sh`)

```bash
#!/bin/bash
# MCP Protocol Test - verifies server responds to MCP initialize

set -e

echo "Testing MCP protocol initialization..."

# Send initialize request and check for valid JSON-RPC response
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | \
    python -m src 2>/dev/null | \
    head -1 | \
    python -c "import sys, json; d = json.load(sys.stdin); assert 'result' in d, 'No result in response'; print('✓ MCP protocol test passed')"
```

## File Structure After Implementation

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py              # Package marker
│   └── __main__.py              # Server entry + ping tool
├── tests/
│   ├── unit/
│   │   └── test_ping.py         # Unit tests
│   └── protocol/
│       └── test_mcp_protocol.sh # Protocol test
├── pyproject.toml               # Project config
├── .mcp.json.template           # Claude Desktop config
└── README.md                    # Updated with setup instructions
```

## Testing Strategy

1. **Unit Tests**: Test `ping()` function directly
2. **Protocol Tests**: Verify MCP JSON-RPC responses
3. **Manual Testing**: Use MCP Inspector (`fastmcp dev src/__main__.py`)

## Definition of Done

- [ ] `src/__main__.py` implements FastMCP server with ping tool
- [ ] `pyproject.toml` has correct dependencies
- [ ] `.mcp.json.template` provides Claude Desktop config
- [ ] Unit tests pass: `pytest tests/unit/test_ping.py -v`
- [ ] Protocol test passes: `./tests/protocol/test_mcp_protocol.sh`
- [ ] MCP Inspector shows ping tool
- [ ] No stdout logging (verified by protocol test)
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

### Critical MCP Patterns

These patterns are REQUIRED for correct MCP server behavior.

| # | Pattern | Why | Example |
|---|---------|-----|---------|
| 1 | **stderr logging** | stdout = MCP JSON-RPC protocol | `logging.basicConfig(stream=sys.stderr)` |
| 2 | **Module-level tools** | Required for Claude Code discovery | `@mcp.tool()` at module level in `__main__.py` |
| 3 | **String parameters** | MCP sends all params as strings | `count_int = int(count)` |
| 4 | **Timezone-aware datetime** | `utcnow()` is deprecated | `datetime.now(timezone.utc)` |
| 5 | **Async wrappers** | Don't block event loop | `await asyncio.to_thread(sync_fn)` |
| 6 | **CancelledError** | Must re-raise for cleanup | `except CancelledError: logger.info(...); raise` |
| 7 | **Structured errors** | Consistent error format | `{"error": {"category": "...", "code": "...", "message": "..."}}` |

#### Pattern Details

<details>
<summary>1. stderr logging (CRITICAL)</summary>

```python
import sys
import logging

# CORRECT
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# WRONG - breaks MCP protocol
print("Debug")  # stdout corrupts JSON-RPC
logging.basicConfig()  # Defaults to stdout!
```
</details>

<details>
<summary>2. Module-level tool registration</summary>

```python
# CORRECT - in __main__.py at module level
@mcp.tool()
async def my_tool():
    pass

# WRONG - tools registered in functions won't be discovered
def setup():
    @mcp.tool()
    async def my_tool():
        pass
```
</details>

<details>
<summary>3. String parameter conversion</summary>

```python
@mcp.tool()
async def process(count: str, enabled: str) -> dict:
    # MCP sends "10" not 10, "true" not True
    count_int = int(count)
    enabled_bool = enabled.lower() in ("true", "1", "yes")
    return {"count": count_int, "enabled": enabled_bool}
```
</details>

### Common Pitfalls to Avoid

- ❌ `print("debug")` - corrupts MCP protocol
- ❌ `logging.basicConfig()` without `stream=sys.stderr`
- ❌ Registering tools inside functions (won't be discovered)
- ❌ `datetime.utcnow()` (deprecated, use timezone-aware)
- ❌ Swallowing `asyncio.CancelledError`

### Testing with MCP Inspector

```bash
# Start the inspector (opens at http://127.0.0.1:6274)
fastmcp dev src/__main__.py

# Or use Anthropic's inspector
npx @anthropic-ai/mcp-inspector python -m src
```
