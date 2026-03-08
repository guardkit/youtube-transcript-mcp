"""Tests for ping health check tool.

Verifies TASK-SKEL-002 acceptance criteria:
- FastMCP server with ping tool registered at module level
- Ping returns dict with status, server name, version, UTC ISO timestamp
- Logging configured to stderr only
- Timestamp uses datetime.now(timezone.utc)
"""

from __future__ import annotations

import ast
from datetime import datetime, timezone
from pathlib import Path

import pytest

# Resolve project root relative to this test file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestPingTool:
    """Verify ping tool functionality."""

    @pytest.mark.asyncio
    async def test_ping_returns_healthy_status(self) -> None:
        """AC: ping returns dict with status='healthy'."""
        from src.__main__ import ping

        result = await ping()

        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_ping_returns_server_name(self) -> None:
        """AC: ping returns server name 'youtube-transcript-mcp'."""
        from src.__main__ import ping

        result = await ping()

        assert result["server"] == "youtube-transcript-mcp"

    @pytest.mark.asyncio
    async def test_ping_returns_version(self) -> None:
        """AC: ping returns version '0.1.0'."""
        from src.__main__ import ping

        result = await ping()

        assert result["version"] == "0.1.0"

    @pytest.mark.asyncio
    async def test_ping_returns_timestamp(self) -> None:
        """AC: ping returns UTC ISO timestamp."""
        from src.__main__ import ping

        result = await ping()

        assert "timestamp" in result

    @pytest.mark.asyncio
    async def test_ping_timestamp_is_utc_iso_format(self) -> None:
        """AC: Timestamp uses datetime.now(timezone.utc), valid UTC ISO format."""
        from src.__main__ import ping

        result = await ping()

        # Should parse without error
        timestamp = datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))

        # Should be recent (within last minute)
        now = datetime.now(timezone.utc)
        delta = abs((now - timestamp).total_seconds())
        assert delta < 60, f"Timestamp {timestamp} is not recent"


class TestServerConfiguration:
    """Verify server module configuration meets MCP requirements."""

    def test_imports_fastmcp_from_mcp_package(self) -> None:
        """AC: src/__main__.py imports FastMCP from mcp.server.fastmcp."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        assert main_path.exists(), "src/__main__.py must exist"

        source = main_path.read_text()
        tree = ast.parse(source)

        fastmcp_import_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == "mcp.server.fastmcp" and any(
                    alias.name == "FastMCP" for alias in node.names
                ):
                    fastmcp_import_found = True
                    break

        assert fastmcp_import_found, (
            "Must import FastMCP from mcp.server.fastmcp"
        )

    def test_logging_configured_to_stderr(self) -> None:
        """AC: Logging configured to stderr only (stream=sys.stderr)."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        source = main_path.read_text()

        assert "sys.stderr" in source, (
            "Logging must be configured with stream=sys.stderr"
        )

    def test_fastmcp_instance_created_with_correct_name(self) -> None:
        """AC: FastMCP instance created with name='youtube-transcript-mcp'."""
        from src.__main__ import mcp as mcp_instance

        assert mcp_instance.name == "youtube-transcript-mcp"

    def test_server_version_defined(self) -> None:
        """AC: Server version '0.1.0' is defined and used."""
        from src.__main__ import SERVER_VERSION

        assert SERVER_VERSION == "0.1.0", (
            "SERVER_VERSION must be '0.1.0'"
        )

    def test_no_print_statements(self) -> None:
        """AC: No print statements to stdout (would break MCP protocol)."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        source = main_path.read_text()
        tree = ast.parse(source)

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "print":
                    # Check if print goes to stderr explicitly
                    stderr_kwarg = any(
                        kw.arg == "file"
                        and isinstance(kw.value, ast.Attribute)
                        and kw.value.attr == "stderr"
                        for kw in node.keywords
                    )
                    assert stderr_kwarg, (
                        "print() found without file=sys.stderr — "
                        "this breaks MCP protocol"
                    )

    def test_ping_tool_registered_at_module_level(self) -> None:
        """AC: ping tool registered at module level with @mcp.tool() decorator."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        source = main_path.read_text()
        tree = ast.parse(source)

        # Find async def ping at module level (not nested)
        ping_found_at_module_level = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "ping":
                # Check it has a decorator
                has_tool_decorator = any(
                    (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute)
                     and d.func.attr == "tool")
                    or (isinstance(d, ast.Attribute) and d.attr == "tool")
                    for d in node.decorator_list
                )
                if has_tool_decorator:
                    ping_found_at_module_level = True
                    break

        assert ping_found_at_module_level, (
            "ping must be an async function decorated with @mcp.tool() at module level"
        )

    def test_server_runs_with_stdio_transport(self) -> None:
        """AC: Server runs with mcp.run(transport='stdio') in __main__ block."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        source = main_path.read_text()

        assert 'transport="stdio"' in source or "transport='stdio'" in source, (
            "Server must use mcp.run(transport='stdio')"
        )

    def test_uses_timezone_aware_datetime(self) -> None:
        """AC: Timestamp uses datetime.now(timezone.utc), not utcnow()."""
        main_path = PROJECT_ROOT / "src" / "__main__.py"
        source = main_path.read_text()

        assert "utcnow()" not in source, (
            "Must not use deprecated utcnow() — use datetime.now(timezone.utc)"
        )
        assert "timezone.utc" in source, (
            "Must use timezone.utc for timezone-aware datetime"
        )
