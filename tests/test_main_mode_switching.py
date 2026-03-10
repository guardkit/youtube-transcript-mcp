"""Tests for __main__.py CLI/MCP mode switching (TASK-CLI-002).

Verifies that:
- `python -m src` still starts the MCP server (no regression)
- `python -m src cli <command>` dispatches to src.cli.main()
- CLI arguments after `cli` are passed correctly
- Exit code from CLI is propagated via sys.exit()
- No import of src.cli happens in MCP server mode (lazy import)

MCP tool regression tests and insight extractor coverage tests have been
moved to tests/unit/test_mcp_tools.py to eliminate duplication.
"""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# AC-001: `python -m src` still starts the MCP server (no regression)
# ---------------------------------------------------------------------------


class TestMCPServerModeNoRegression:
    """Verify MCP server mode still works when no 'cli' argument is given."""

    def test_no_args_starts_mcp_server(self) -> None:
        """When sys.argv has no extra args, mcp.run() should be called."""
        with (
            patch("sys.argv", ["src"]),
            patch("src.__main__.mcp") as mock_mcp,
        ):
            mock_mcp.run = MagicMock()
            import src.__main__ as main_mod

            _run_main_guard(main_mod, mock_mcp)
            mock_mcp.run.assert_called_once_with(transport="stdio")

    def test_random_args_starts_mcp_server(self) -> None:
        """When sys.argv[1] is NOT 'cli', MCP server should start normally."""
        with (
            patch("sys.argv", ["src", "--some-flag"]),
            patch("src.__main__.mcp") as mock_mcp,
        ):
            mock_mcp.run = MagicMock()
            import src.__main__ as main_mod

            _run_main_guard(main_mod, mock_mcp)
            mock_mcp.run.assert_called_once_with(transport="stdio")


# ---------------------------------------------------------------------------
# AC-002: `python -m src cli <command>` dispatches to src.cli.main()
# ---------------------------------------------------------------------------


class TestCLIDispatch:
    """Verify CLI mode dispatches to src.cli.main()."""

    def test_cli_arg_dispatches_to_cli_main(self) -> None:
        """When sys.argv[1] == 'cli', src.cli.main() should be called."""
        with (
            patch("sys.argv", ["src", "cli", "ping"]),
            patch.dict("sys.modules", {"src.cli": MagicMock()}),
        ):
            mock_cli = sys.modules["src.cli"]
            mock_cli.main = MagicMock(return_value=0)

            import src.__main__ as main_mod

            exit_code = _run_main_guard_cli(main_mod)

            mock_cli.main.assert_called_once()
            assert exit_code == 0


# ---------------------------------------------------------------------------
# AC-003: CLI arguments after `cli` are passed correctly
# ---------------------------------------------------------------------------


class TestCLIArgumentPassing:
    """Verify arguments after 'cli' are forwarded correctly."""

    def test_args_after_cli_stripped_and_passed(self) -> None:
        """sys.argv[2:] (everything after 'cli') should be passed to main()."""
        with (
            patch("sys.argv", ["src", "cli", "get-transcript", "URL", "--language", "fr"]),
            patch.dict("sys.modules", {"src.cli": MagicMock()}),
        ):
            mock_cli = sys.modules["src.cli"]
            mock_cli.main = MagicMock(return_value=0)

            import src.__main__ as main_mod

            _run_main_guard_cli(main_mod)

            mock_cli.main.assert_called_once_with(
                ["get-transcript", "URL", "--language", "fr"]
            )

    def test_cli_with_no_subcommand(self) -> None:
        """'python -m src cli' with no further args passes empty list."""
        with (
            patch("sys.argv", ["src", "cli"]),
            patch.dict("sys.modules", {"src.cli": MagicMock()}),
        ):
            mock_cli = sys.modules["src.cli"]
            mock_cli.main = MagicMock(return_value=0)

            import src.__main__ as main_mod

            _run_main_guard_cli(main_mod)

            mock_cli.main.assert_called_once_with([])


# ---------------------------------------------------------------------------
# AC-004: Exit code from CLI is propagated via sys.exit()
# ---------------------------------------------------------------------------


class TestExitCodePropagation:
    """Verify CLI exit codes are propagated via sys.exit()."""

    def test_success_exit_code_propagated(self) -> None:
        """Exit code 0 from CLI should be passed to sys.exit()."""
        with (
            patch("sys.argv", ["src", "cli", "ping"]),
            patch.dict("sys.modules", {"src.cli": MagicMock()}),
        ):
            mock_cli = sys.modules["src.cli"]
            mock_cli.main = MagicMock(return_value=0)

            import src.__main__ as main_mod

            exit_code = _run_main_guard_cli(main_mod)
            assert exit_code == 0

    def test_error_exit_code_propagated(self) -> None:
        """Exit code 1 from CLI should be passed to sys.exit()."""
        with (
            patch("sys.argv", ["src", "cli", "get-transcript", "bad-url"]),
            patch.dict("sys.modules", {"src.cli": MagicMock()}),
        ):
            mock_cli = sys.modules["src.cli"]
            mock_cli.main = MagicMock(return_value=1)

            import src.__main__ as main_mod

            exit_code = _run_main_guard_cli(main_mod)
            assert exit_code == 1


# ---------------------------------------------------------------------------
# AC-005: No import of src.cli happens in MCP server mode (lazy import)
# ---------------------------------------------------------------------------


class TestLazyImport:
    """Verify src.cli is NOT imported during MCP server mode."""

    def test_cli_not_imported_in_mcp_mode(self) -> None:
        """In MCP server mode, src.cli should not appear in sys.modules."""
        saved = sys.modules.pop("src.cli", None)
        try:
            with (
                patch("sys.argv", ["src"]),
                patch("src.__main__.mcp") as mock_mcp,
            ):
                mock_mcp.run = MagicMock()
                import src.__main__ as main_mod

                _run_main_guard(main_mod, mock_mcp)

                assert "src.cli" not in sys.modules
        finally:
            if saved is not None:
                sys.modules["src.cli"] = saved

    def test_cli_imported_only_in_cli_mode(self) -> None:
        """In CLI mode, src.cli should be imported (lazy)."""
        with (
            patch("sys.argv", ["src", "cli", "ping"]),
        ):
            mock_cli_module = MagicMock()
            mock_cli_module.main = MagicMock(return_value=0)

            with patch.dict("sys.modules", {"src.cli": mock_cli_module}):
                import src.__main__ as main_mod

                _run_main_guard_cli(main_mod)

                mock_cli_module.main.assert_called_once()


# ---------------------------------------------------------------------------
# Helpers to simulate __main__ guard execution
# ---------------------------------------------------------------------------


def _run_main_guard(main_mod: object, mock_mcp: MagicMock) -> None:
    """Simulate the `if __name__ == '__main__'` block for MCP server mode."""
    if hasattr(main_mod, "_entry_point"):
        main_mod._entry_point()
    else:
        pytest.fail(
            "__main__.py must expose _entry_point() function for testability. "
            "Wrap the 'if __name__ == \"__main__\"' body in a _entry_point() function."
        )


def _run_main_guard_cli(main_mod: object) -> int:
    """Simulate the `if __name__ == '__main__'` block for CLI mode."""
    if hasattr(main_mod, "_entry_point"):
        with patch("sys.exit") as mock_exit:
            main_mod._entry_point()
            if mock_exit.called:
                return mock_exit.call_args[0][0]
            return 0
    else:
        pytest.fail(
            "__main__.py must expose _entry_point() function for testability. "
            "Wrap the 'if __name__ == \"__main__\"' body in a _entry_point() function."
        )
        return -1  # unreachable, but makes type checker happy
