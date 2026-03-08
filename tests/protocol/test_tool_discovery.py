"""Protocol-level tests for MCP tool discovery.

Verifies TASK-SKEL-004 AC-006:
- MCP Inspector can discover the ping tool

These tests simulate what MCP Inspector does: connect to the server
and list available tools via the MCP protocol.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Resolve project root relative to this test file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestToolDiscoveryViaFastMCP:
    """Verify tool discovery via FastMCP server API (unit-level)."""

    @pytest.mark.asyncio
    async def test_ping_tool_discoverable_via_list_tools(self) -> None:
        """AC-006: ping tool is discoverable via mcp.list_tools()."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "ping" in tool_names, (
            f"ping tool must be discoverable. Found tools: {tool_names}"
        )

    @pytest.mark.asyncio
    async def test_ping_tool_has_description(self) -> None:
        """AC-006: ping tool has a non-empty description for discovery."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        ping_tools = [t for t in tools if t.name == "ping"]
        assert len(ping_tools) == 1, "Exactly one ping tool must exist"

        ping_tool = ping_tools[0]
        assert ping_tool.description is not None, "ping tool must have a description"
        assert len(ping_tool.description) > 0, "ping tool description must be non-empty"

    @pytest.mark.asyncio
    async def test_ping_tool_has_valid_input_schema(self) -> None:
        """AC-006: ping tool has a valid JSON Schema input schema."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        ping_tools = [t for t in tools if t.name == "ping"]
        assert len(ping_tools) == 1

        ping_tool = ping_tools[0]
        assert ping_tool.inputSchema is not None, "ping tool must have inputSchema"
        assert "type" in ping_tool.inputSchema, "inputSchema must have 'type' field"

    @pytest.mark.asyncio
    async def test_ping_tool_callable_via_mcp(self) -> None:
        """AC-006: ping tool can be called via mcp.call_tool()."""
        from src.__main__ import mcp

        result = await mcp.call_tool("ping", arguments={})
        assert result is not None, "call_tool('ping') must return a result"


class TestToolDiscoveryViaProtocol:
    """Verify tool discovery via MCP stdio protocol (integration-level).

    This simulates what MCP Inspector does: launches the server as a
    subprocess, connects via stdio, and discovers tools through the
    MCP JSON-RPC protocol.
    """

    @pytest.mark.asyncio
    async def test_ping_tool_discoverable_via_stdio_client(self) -> None:
        """AC-006: ping tool is discoverable via MCP stdio client protocol.

        This is the closest automated equivalent to 'MCP Inspector can
        discover the ping tool'.
        """
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src"],
            cwd=str(PROJECT_ROOT),
            env={
                "PYTHONPATH": str(PROJECT_ROOT),
                "PATH": str(Path(sys.executable).parent),
            },
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize the MCP session (required before any requests)
                await session.initialize()

                # List tools - this is what MCP Inspector does
                tools_result = await session.list_tools()

                tool_names = [t.name for t in tools_result.tools]
                assert "ping" in tool_names, (
                    f"ping tool must be discoverable via MCP protocol. "
                    f"Found tools: {tool_names}"
                )

    @pytest.mark.asyncio
    async def test_ping_tool_callable_via_stdio_client(self) -> None:
        """AC-006: ping tool can be called via MCP stdio client protocol."""
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "src"],
            cwd=str(PROJECT_ROOT),
            env={
                "PYTHONPATH": str(PROJECT_ROOT),
                "PATH": str(Path(sys.executable).parent),
            },
        )

        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()

                # Call the ping tool - simulates MCP Inspector tool invocation
                result = await session.call_tool("ping", arguments={})

                assert result is not None, "ping tool must return a result"
                assert len(result.content) > 0, "ping result must have content"
