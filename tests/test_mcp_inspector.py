"""Tests verifying MCP Inspector tool visibility.

MCP Inspector uses the tools/list JSON-RPC method to discover tools.
These tests simulate that process by calling mcp.list_tools() and
verifying both tools appear with correct names, descriptions, and
input schemas — exactly what MCP Inspector renders in its tool list.

Covers AC-001 and AC-002 for TASK-TRS-005.
"""

from __future__ import annotations

import pytest


class TestMCPInspectorToolDiscovery:
    """Simulate MCP Inspector's tool discovery via tools/list."""

    @pytest.mark.asyncio
    async def test_get_transcript_visible_in_tool_list(self) -> None:
        """AC-001: get_transcript tool visible in MCP Inspector tool list.

        MCP Inspector calls tools/list and renders every tool returned.
        Verify get_transcript is present with required metadata.
        """
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        assert "get_transcript" in tool_map, (
            "get_transcript not found in tools/list response — "
            "MCP Inspector would not show it"
        )

        tool = tool_map["get_transcript"]
        # MCP Inspector displays the tool description
        assert tool.description is not None
        assert len(tool.description) > 0
        # MCP Inspector renders the input schema
        assert tool.inputSchema is not None
        # Must declare video_url as required parameter
        assert "video_url" in tool.inputSchema.get("properties", {})
        assert "video_url" in tool.inputSchema.get("required", [])

    @pytest.mark.asyncio
    async def test_list_available_transcripts_visible_in_tool_list(self) -> None:
        """AC-002: list_available_transcripts tool visible in MCP Inspector tool list.

        MCP Inspector calls tools/list and renders every tool returned.
        Verify list_available_transcripts is present with required metadata.
        """
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}

        assert "list_available_transcripts" in tool_map, (
            "list_available_transcripts not found in tools/list response — "
            "MCP Inspector would not show it"
        )

        tool = tool_map["list_available_transcripts"]
        # MCP Inspector displays the tool description
        assert tool.description is not None
        assert len(tool.description) > 0
        # MCP Inspector renders the input schema
        assert tool.inputSchema is not None
        # Must declare video_url as required parameter
        assert "video_url" in tool.inputSchema.get("properties", {})
        assert "video_url" in tool.inputSchema.get("required", [])

    @pytest.mark.asyncio
    async def test_exactly_two_tools_registered(self) -> None:
        """Verify exactly the expected tools are registered (no extras, none missing)."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_names = sorted(t.name for t in tools)

        assert tool_names == [
            "extract_insights",
            "get_transcript",
            "list_available_transcripts",
            "list_focus_areas",
        ]

    @pytest.mark.asyncio
    async def test_get_transcript_has_language_parameter(self) -> None:
        """MCP Inspector shows the language parameter with default 'en'."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_map = {t.name: t for t in tools}
        schema = tool_map["get_transcript"].inputSchema

        props = schema.get("properties", {})
        assert "language" in props, "language parameter missing from schema"
        # language should NOT be required (it has a default)
        required = schema.get("required", [])
        assert "language" not in required, (
            "language should be optional with default 'en'"
        )
