"""Tests verifying MCP Inspector visibility criteria (TASK-VID-005).

These tests validate that the get_video_info tool is properly registered
and discoverable via the MCP protocol, as would be seen in MCP Inspector.

- AC-003: get_video_info tool visible (registered on FastMCP server)
- AC-004: Tool shows correct parameter schema (video_url: string)
- AC-005: Tool docstring visible for LLM discovery
"""

from __future__ import annotations


class TestMCPInspectorVisibility:
    """Verify tool would be visible in MCP Inspector."""

    def test_get_video_info_registered_on_mcp_server(self) -> None:
        """AC-003: get_video_info tool must be registered and discoverable."""
        import src.__main__ as main_mod

        tool_names = list(main_mod.mcp._tool_manager._tools.keys())
        assert "get_video_info" in tool_names, (
            f"get_video_info not in registered tools: {tool_names}"
        )


class TestParameterSchema:
    """Verify tool parameter schema matches AC-004."""

    def test_schema_has_video_url_property(self) -> None:
        """AC-004: Schema must include video_url property."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        schema = tool.parameters
        assert "video_url" in schema.get("properties", {}), (
            f"video_url not in schema properties: {schema}"
        )

    def test_video_url_is_string_type(self) -> None:
        """AC-004: video_url must be typed as string in the schema."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        schema = tool.parameters
        video_url_prop = schema["properties"]["video_url"]
        assert video_url_prop["type"] == "string", (
            f"video_url type must be 'string', got: {video_url_prop.get('type')}"
        )

    def test_video_url_is_required(self) -> None:
        """AC-004: video_url must be a required parameter."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        schema = tool.parameters
        assert "video_url" in schema.get("required", []), (
            f"video_url must be required, required list: {schema.get('required', [])}"
        )

    def test_schema_has_no_extra_required_params(self) -> None:
        """AC-004: Only video_url should be required (no unexpected params)."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        schema = tool.parameters
        required = schema.get("required", [])
        assert required == ["video_url"], (
            f"Expected only ['video_url'] as required, got: {required}"
        )


class TestToolDocstringDiscovery:
    """Verify tool docstring is visible for LLM discovery (AC-005)."""

    def test_tool_has_nonempty_description(self) -> None:
        """AC-005: Tool must have a non-empty description for LLM discovery."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        assert tool.description is not None, "Tool description must not be None"
        assert len(tool.description.strip()) > 0, "Tool description must not be empty"

    def test_description_mentions_youtube(self) -> None:
        """AC-005: Description must mention YouTube for discoverability."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        desc_lower = tool.description.lower()
        assert "youtube" in desc_lower, (
            "Tool description must mention 'YouTube' for LLM discovery"
        )

    def test_description_mentions_url_formats(self) -> None:
        """AC-005: Description must describe accepted URL formats."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        desc = tool.description
        assert "youtu.be" in desc, "Description must mention youtu.be format"
        assert "video_url" in desc, "Description must mention video_url parameter"

    def test_description_mentions_metadata_fields(self) -> None:
        """AC-005: Description must describe returned metadata fields."""
        import src.__main__ as main_mod

        tool = main_mod.mcp._tool_manager._tools["get_video_info"]
        desc_lower = tool.description.lower()
        assert "title" in desc_lower, "Description must mention title field"
        assert "channel" in desc_lower, "Description must mention channel field"
        assert "duration" in desc_lower, "Description must mention duration field"
        assert "captions" in desc_lower, "Description must mention captions"

    def test_get_video_info_function_has_docstring(self) -> None:
        """AC-005: The Python function itself must have a docstring."""
        import src.__main__ as main_mod

        doc = main_mod.get_video_info.__doc__
        assert doc is not None, "get_video_info must have a docstring"
        assert len(doc.strip()) > 50, (
            "Docstring must be substantial for LLM discovery"
        )
