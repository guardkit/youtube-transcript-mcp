"""YouTube Transcript MCP Server Entry Point.

CRITICAL PATTERNS:
- FastMCP for automatic protocol handling
- Tool registration at module level
- All logging to stderr (stdout = MCP protocol)
- Use timezone-aware datetime with timezone.utc
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

# Server metadata
SERVER_NAME = "youtube-transcript-mcp"
SERVER_VERSION = "0.1.0"

# CRITICAL: stderr only - stdout breaks MCP protocol
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
# Note: version="0.1.0" stored in SERVER_VERSION constant
mcp = FastMCP(
    name=SERVER_NAME,
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
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    logger.info("Starting %s server...", SERVER_NAME)
    mcp.run(transport="stdio")
