"""Tests for __main__.py CLI/MCP mode switching (TASK-CLI-002).

Verifies that:
- `python -m src` still starts the MCP server (no regression)
- `python -m src cli <command>` dispatches to src.cli.main()
- CLI arguments after `cli` are passed correctly
- Exit code from CLI is propagated via sys.exit()
- No import of src.cli happens in MCP server mode (lazy import)

Also includes regression tests for the MCP tool functions defined in
__main__.py to ensure mode switching didn't break them and to maintain
adequate test coverage of the module.
"""

from __future__ import annotations

import importlib
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.__main__ import (
    extract_insights,
    get_transcript,
    list_available_transcripts,
    list_focus_areas,
)


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
            # Re-execute the __main__ block by running the guarded code
            # We import and call the module's main guard logic
            import src.__main__ as main_mod

            # Simulate __name__ == "__main__" execution
            # The module should call mcp.run(transport="stdio") when no cli arg
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
        # Remove src.cli from modules if present
        saved = sys.modules.pop("src.cli", None)
        try:
            with (
                patch("sys.argv", ["src"]),
                patch("src.__main__.mcp") as mock_mcp,
            ):
                mock_mcp.run = MagicMock()
                import src.__main__ as main_mod

                _run_main_guard(main_mod, mock_mcp)

                # src.cli should NOT have been imported
                assert "src.cli" not in sys.modules
        finally:
            # Restore if it was there
            if saved is not None:
                sys.modules["src.cli"] = saved

    def test_cli_imported_only_in_cli_mode(self) -> None:
        """In CLI mode, src.cli should be imported (lazy)."""
        with (
            patch("sys.argv", ["src", "cli", "ping"]),
        ):
            # We need a real or mock src.cli available
            mock_cli_module = MagicMock()
            mock_cli_module.main = MagicMock(return_value=0)

            with patch.dict("sys.modules", {"src.cli": mock_cli_module}):
                import src.__main__ as main_mod

                _run_main_guard_cli(main_mod)

                # src.cli.main should have been called
                mock_cli_module.main.assert_called_once()


# ---------------------------------------------------------------------------
# Helpers to simulate __main__ guard execution
# ---------------------------------------------------------------------------


def _run_main_guard(main_mod: object, mock_mcp: MagicMock) -> None:
    """Simulate the `if __name__ == '__main__'` block for MCP server mode.

    Calls the module-level entry point logic. Since we can't re-trigger
    `if __name__ == '__main__'`, we call the function that encapsulates
    that logic.
    """
    # The implementation should expose a function or we invoke
    # the module entry point. After implementation, this will call
    # the entry_point() or the inline code.
    if hasattr(main_mod, "_entry_point"):
        main_mod._entry_point()
    else:
        pytest.fail(
            "__main__.py must expose _entry_point() function for testability. "
            "Wrap the 'if __name__ == \"__main__\"' body in a _entry_point() function."
        )


def _run_main_guard_cli(main_mod: object) -> int:
    """Simulate the `if __name__ == '__main__'` block for CLI mode.

    Returns the exit code that would be passed to sys.exit().
    """
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


# ===========================================================================
# MCP Tool Function Regression Tests
#
# These tests verify the MCP tool functions in __main__.py still work
# correctly after the mode-switching refactor. They call the async
# tool handlers directly with mocked service dependencies.
# ===========================================================================


class TestGetTranscriptTool:
    """Regression tests for the get_transcript MCP tool function."""

    @pytest.mark.asyncio
    async def test_invalid_url_returns_error(self) -> None:
        """Invalid URL should return structured client error."""
        result = await get_transcript(video_url="not-a-valid-url")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_URL"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_successful_transcript_fetch(self) -> None:
        """Successful fetch returns transcript data with segments."""
        from src.services.transcript_client import TranscriptResult, TranscriptSegment

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=False,
            segments=[TranscriptSegment(start=0.0, duration=5.0, text="Hello")],
            full_text="Hello",
            total_segments=1,
            total_duration_seconds=5.0,
        )
        with patch.object(
            type(pytest.importorskip("src.__main__").transcript_client),
            "get_transcript",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            import src.__main__ as mod

            result = await mod.get_transcript(video_url="dQw4w9WgXcQ")

        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["full_text"] == "Hello"
        assert len(result["segments"]) == 1

    @pytest.mark.asyncio
    async def test_transcripts_disabled_error(self) -> None:
        """TranscriptsDisabledError should return structured error."""
        from src.services.transcript_client import TranscriptsDisabledError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=TranscriptsDisabledError("Disabled"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "TRANSCRIPTS_DISABLED"

    @pytest.mark.asyncio
    async def test_no_transcript_found_error(self) -> None:
        """NoTranscriptFoundError should return error with available languages."""
        from src.services.transcript_client import NoTranscriptFoundError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=NoTranscriptFoundError("Not found", available_languages=["es"]),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "NO_TRANSCRIPT_FOUND"
        assert result["error"]["available_languages"] == ["es"]

    @pytest.mark.asyncio
    async def test_video_unavailable_error(self) -> None:
        """VideoUnavailableError should return structured error."""
        from src.services.transcript_client import VideoUnavailableError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=VideoUnavailableError("Unavailable"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "VIDEO_UNAVAILABLE"

    @pytest.mark.asyncio
    async def test_unexpected_error_returns_internal_error(self) -> None:
        """Unexpected exceptions should return server_error."""
        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=RuntimeError("unexpected"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "INTERNAL_ERROR"
        assert result["error"]["category"] == "server_error"


class TestListAvailableTranscriptsTool:
    """Regression tests for the list_available_transcripts MCP tool function."""

    @pytest.mark.asyncio
    async def test_invalid_url_returns_error(self) -> None:
        """Invalid URL should return structured client error."""
        result = await list_available_transcripts(video_url="not-valid")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_URL"

    @pytest.mark.asyncio
    async def test_successful_list(self) -> None:
        """Successful listing returns transcripts with count."""
        mock_transcripts = [
            {"language": "English", "language_code": "en", "is_generated": False},
        ]
        with patch(
            "src.__main__.transcript_client.list_transcripts",
            new_callable=AsyncMock,
            return_value=mock_transcripts,
        ):
            result = await list_available_transcripts(video_url="dQw4w9WgXcQ")

        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["count"] == 1
        assert len(result["transcripts"]) == 1

    @pytest.mark.asyncio
    async def test_unexpected_error_returns_internal_error(self) -> None:
        """Unexpected exceptions should return server_error."""
        with patch(
            "src.__main__.transcript_client.list_transcripts",
            new_callable=AsyncMock,
            side_effect=RuntimeError("network failure"),
        ):
            result = await list_available_transcripts(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "INTERNAL_ERROR"
        assert result["error"]["category"] == "server_error"


class TestExtractInsightsTool:
    """Regression tests for the extract_insights MCP tool function."""

    @pytest.mark.asyncio
    async def test_invalid_max_insights_returns_error(self) -> None:
        """Non-integer max_insights should return client error."""
        result = await extract_insights(
            transcript="A" * 200,
            max_insights="not-a-number",
        )
        assert result["error"]["code"] == "INVALID_PARAMETER"

    @pytest.mark.asyncio
    async def test_invalid_focus_area_returns_error(self) -> None:
        """Invalid focus area should return client error."""
        result = await extract_insights(
            transcript="A" * 200,
            focus_areas="nonexistent-area",
        )
        assert result["error"]["code"] == "INVALID_FOCUS_AREA"

    @pytest.mark.asyncio
    async def test_short_transcript_returns_error(self) -> None:
        """Transcript shorter than 100 chars should return error."""
        result = await extract_insights(transcript="too short")
        assert result["error"]["code"] == "TRANSCRIPT_TOO_SHORT"

    @pytest.mark.asyncio
    async def test_successful_extraction(self) -> None:
        """Valid transcript produces extraction metadata."""
        result = await extract_insights(
            transcript="A" * 200,
            focus_areas="general",
            max_insights="5",
        )
        assert "extraction_prompt" in result
        assert result["max_insights"] == 5

    @pytest.mark.asyncio
    async def test_extraction_exception_returns_server_error(self) -> None:
        """Exception in prepare_for_extraction should return server error."""
        with patch(
            "src.__main__.prepare_for_extraction",
            side_effect=RuntimeError("extraction failed"),
        ):
            result = await extract_insights(
                transcript="A" * 200,
                focus_areas="general",
            )
        assert result["error"]["code"] == "EXTRACTION_PREP_ERROR"
        assert result["error"]["category"] == "server_error"


class TestListFocusAreasTool:
    """Regression tests for the list_focus_areas MCP tool function."""

    @pytest.mark.asyncio
    async def test_returns_focus_areas(self) -> None:
        """Should return focus areas, category definitions, and usage tip."""
        result = await list_focus_areas()
        assert "focus_areas" in result
        assert "category_definitions" in result
        assert "usage_tip" in result
        assert "general" in result["focus_areas"]
        assert "entrepreneurial" in result["focus_areas"]


# ===========================================================================
# Service-layer coverage tests
#
# These tests exercise uncovered paths in src/services/ to bring the
# overall src/ coverage above the 80% threshold. They cover the insight
# extractor functions that are called through the MCP tool.
# ===========================================================================


class TestInsightExtractorCoverage:
    """Additional tests for insight_extractor to boost overall coverage."""

    def test_get_focus_categories_all(self) -> None:
        """'all' focus area should return every InsightCategory."""
        from src.models.insight import InsightCategory
        from src.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["all"])
        assert len(result) == len(InsightCategory)
        assert set(result) == set(InsightCategory)

    def test_get_focus_categories_unknown_falls_back_to_general(self) -> None:
        """Unknown focus areas should fall back to 'general' preset."""
        from src.models.insight import FOCUS_PRESETS
        from src.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["nonexistent"])
        expected = list(FOCUS_PRESETS["general"])
        assert result == expected

    def test_chunk_transcript_no_split_needed(self) -> None:
        """Short transcript should return single chunk."""
        from src.services.insight_extractor import chunk_transcript

        text = "Short text"
        result = chunk_transcript(text, max_chars=1000)
        assert result == [text]

    def test_chunk_transcript_paragraph_split(self) -> None:
        """Long transcript should be split at paragraph boundaries."""
        from src.services.insight_extractor import chunk_transcript

        para1 = "A" * 100
        para2 = "B" * 100
        para3 = "C" * 100
        text = f"{para1}\n\n{para2}\n\n{para3}"
        result = chunk_transcript(text, max_chars=150, overlap_chars=10)
        assert len(result) >= 2

    def test_chunk_transcript_single_huge_paragraph(self) -> None:
        """Single paragraph exceeding max_chars triggers force split."""
        from src.services.insight_extractor import chunk_transcript

        text = "X" * 500
        result = chunk_transcript(text, max_chars=100, overlap_chars=20)
        assert len(result) >= 5
        for chunk in result:
            assert len(chunk) <= 100

    def test_force_split_basic(self) -> None:
        """Force split should produce overlapping chunks."""
        from src.services.insight_extractor import _force_split

        text = "A" * 200
        result = _force_split(text, max_chars=80, overlap_chars=10)
        assert len(result) >= 3
        for chunk in result:
            assert len(chunk) <= 80

    def test_force_split_zero_overlap(self) -> None:
        """Force split with zero overlap should still work."""
        from src.services.insight_extractor import _force_split

        text = "B" * 100
        result = _force_split(text, max_chars=30, overlap_chars=0)
        assert len(result) >= 3

    def test_prepare_for_extraction_with_chunking(self) -> None:
        """Long transcript should indicate chunking needed."""
        from src.services.insight_extractor import prepare_for_extraction

        long_text = "A" * 100000
        result = prepare_for_extraction(
            transcript=long_text,
            focus_areas=["general"],
            max_insights=5,
        )
        assert result["needs_chunking"] is True
        assert result["chunk_count"] > 1
        assert result["chunks"] is not None

    @pytest.mark.asyncio
    async def test_extract_insights_tool_with_all_focus(self) -> None:
        """extract_insights tool with 'all' focus should work."""
        result = await extract_insights(
            transcript="D" * 200,
            focus_areas="all",
            max_insights="3",
        )
        assert "extraction_prompt" in result
        assert result["max_insights"] == 3

    def test_chunk_with_large_remaining_after_accumulation(self) -> None:
        """Cover remaining chunk overflow branch after accumulation.

        When overlap + new paragraph exceeds max_chars, the remaining
        chunk is re-split via _force_split, producing more chunks.
        """
        from src.services.insight_extractor import chunk_transcript

        para1 = "A" * 80
        para2 = "B" * 80
        para3 = "C" * 80
        text = f"{para1}\n\n{para2}\n\n{para3}"
        result = chunk_transcript(text, max_chars=100, overlap_chars=50)
        # Should produce multiple chunks due to overlap accumulation
        assert len(result) >= 2
        # All text should be represented in the output
        combined = "".join(result)
        assert "A" in combined
        assert "B" in combined
        assert "C" in combined

    def test_chunk_with_short_stored_overlap(self) -> None:
        """Cover the branch where stored chunk is shorter than overlap_chars."""
        from src.services.insight_extractor import chunk_transcript

        # First para is short, second is big enough to trigger split
        para1 = "A" * 5
        para2 = "B" * 200
        text = f"{para1}\n\n{para2}"
        result = chunk_transcript(text, max_chars=100, overlap_chars=50)
        assert len(result) >= 2
