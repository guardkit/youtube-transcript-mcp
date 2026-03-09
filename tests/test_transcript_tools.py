"""Tests for get_transcript and list_available_transcripts MCP tool registration.

TDD RED phase: these tests define the expected behaviour of the MCP tools
registered in src/__main__.py. Covers all acceptance criteria for TASK-TRS-003.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Mock helpers (reused from test_transcript_client.py patterns)
# ---------------------------------------------------------------------------


@dataclass
class MockSnippet:
    """Mock FetchedTranscriptSnippet."""

    start: float
    duration: float
    text: str


@dataclass
class MockFetchedTranscript:
    """Mock FetchedTranscript returned by api.fetch()."""

    language: str
    language_code: str
    is_generated: bool
    snippets: list[MockSnippet]


def _make_mock_transcript(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    snippets: list[MockSnippet] | None = None,
) -> MockFetchedTranscript:
    if snippets is None:
        snippets = [
            MockSnippet(start=0.0, duration=2.5, text="Hello world"),
            MockSnippet(start=2.5, duration=3.0, text="This is a test"),
            MockSnippet(start=5.5, duration=2.0, text="Thank you"),
        ]
    return MockFetchedTranscript(
        language=language,
        language_code=language_code,
        is_generated=is_generated,
        snippets=snippets,
    )


# ---------------------------------------------------------------------------
# AC: Seam test — TranscriptClient contract from TASK-TRS-002
# ---------------------------------------------------------------------------


class TestTranscriptClientSeam:
    """Seam test: verify TranscriptClient contract from TASK-TRS-002."""

    def test_transcript_client_importable(self) -> None:
        """Verify TranscriptClient is importable and instantiable."""
        from src.services.transcript_client import TranscriptClient

        client = TranscriptClient()
        assert client is not None
        assert hasattr(client, "get_transcript")
        assert hasattr(client, "list_transcripts")


# ---------------------------------------------------------------------------
# AC: Tool registration at module level
# ---------------------------------------------------------------------------


class TestToolRegistration:
    """AC: get_transcript and list_available_transcripts registered at module level."""

    def test_mcp_server_exists(self) -> None:
        """FastMCP server instance exists in __main__."""
        from src.__main__ import mcp

        assert mcp is not None

    def test_transcript_client_at_module_level(self) -> None:
        """AC: TranscriptClient instantiated at module level (singleton)."""
        from src.__main__ import transcript_client
        from src.services.transcript_client import TranscriptClient

        assert isinstance(transcript_client, TranscriptClient)

    @pytest.mark.asyncio
    async def test_get_transcript_tool_registered(self) -> None:
        """AC: get_transcript tool registered with @mcp.tool()."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "get_transcript" in tool_names

    @pytest.mark.asyncio
    async def test_list_available_transcripts_tool_registered(self) -> None:
        """AC: list_available_transcripts tool registered with @mcp.tool()."""
        from src.__main__ import mcp

        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        assert "list_available_transcripts" in tool_names


# ---------------------------------------------------------------------------
# AC: get_transcript tool — parameters and success response
# ---------------------------------------------------------------------------


class TestGetTranscriptTool:
    """AC: get_transcript accepts video_url (required) and language (default 'en')."""

    @pytest.mark.asyncio
    async def test_get_transcript_success(self) -> None:
        """Happy path: returns structured transcript response."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import TranscriptResult, TranscriptSegment

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=False,
            segments=[
                TranscriptSegment(start=0.0, duration=2.5, text="Hello world"),
                TranscriptSegment(start=2.5, duration=3.0, text="This is a test"),
            ],
            full_text="Hello world This is a test",
            total_segments=2,
            total_duration_seconds=5.5,
        )

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            return_value=mock_result,
        ):
            result = await get_transcript(
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )

        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["language"] == "English"
        assert result["language_code"] == "en"
        assert result["is_auto_generated"] is False
        assert len(result["segments"]) == 2
        assert result["segments"][0]["start"] == 0.0
        assert result["segments"][0]["text"] == "Hello world"
        assert result["full_text"] == "Hello world This is a test"
        assert result["total_segments"] == 2
        assert result["total_duration_seconds"] == 5.5

    @pytest.mark.asyncio
    async def test_get_transcript_default_language(self) -> None:
        """AC: language parameter defaults to 'en'."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import TranscriptResult

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=False,
            full_text="Hello",
            total_segments=1,
            total_duration_seconds=1.0,
        )

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_get:
            await get_transcript(video_url="dQw4w9WgXcQ")
            mock_get.assert_awaited_once_with("dQw4w9WgXcQ", "en")

    @pytest.mark.asyncio
    async def test_get_transcript_custom_language(self) -> None:
        """get_transcript passes custom language to TranscriptClient."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import TranscriptResult

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="Spanish",
            language_code="es",
            is_auto_generated=False,
            full_text="Hola",
            total_segments=1,
            total_duration_seconds=1.0,
        )

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_get:
            result = await get_transcript(
                video_url="dQw4w9WgXcQ", language="es"
            )
            mock_get.assert_awaited_once_with("dQw4w9WgXcQ", "es")
            assert result["language_code"] == "es"

    @pytest.mark.asyncio
    async def test_get_transcript_uses_extract_video_id(self) -> None:
        """AC: Uses extract_video_id() for URL parsing."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import TranscriptResult

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=False,
            full_text="text",
            total_segments=1,
            total_duration_seconds=1.0,
        )

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            return_value=mock_result,
        ) as mock_get:
            # Full URL should be parsed to video ID
            await get_transcript(
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )
            mock_get.assert_awaited_once_with("dQw4w9WgXcQ", "en")


# ---------------------------------------------------------------------------
# AC: get_transcript error responses
# ---------------------------------------------------------------------------


class TestGetTranscriptErrors:
    """AC: Structured error responses with category/code/message format."""

    @pytest.mark.asyncio
    async def test_invalid_url_error(self) -> None:
        """AC: INVALID_URL error for bad URLs."""
        from src.__main__ import get_transcript

        result = await get_transcript(video_url="not-a-valid-url")
        assert "error" in result
        assert result["error"]["code"] == "INVALID_URL"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_transcripts_disabled_error(self) -> None:
        """AC: TRANSCRIPTS_DISABLED error."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import TranscriptsDisabledError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=TranscriptsDisabledError("disabled"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "TRANSCRIPTS_DISABLED"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_no_transcript_found_error(self) -> None:
        """AC: NO_TRANSCRIPT_FOUND error includes available_languages."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import NoTranscriptFoundError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=NoTranscriptFoundError(
                "not found", available_languages=["en", "fr"]
            ),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "NO_TRANSCRIPT_FOUND"
        assert result["error"]["category"] == "client_error"
        assert result["error"]["available_languages"] == ["en", "fr"]

    @pytest.mark.asyncio
    async def test_video_unavailable_error(self) -> None:
        """AC: VIDEO_UNAVAILABLE error."""
        from src.__main__ import get_transcript
        from src.services.transcript_client import VideoUnavailableError

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=VideoUnavailableError("unavailable"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "VIDEO_UNAVAILABLE"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_internal_error(self) -> None:
        """AC: INTERNAL_ERROR for unexpected exceptions."""
        from src.__main__ import get_transcript

        with patch(
            "src.__main__.transcript_client.get_transcript",
            new_callable=AsyncMock,
            side_effect=RuntimeError("kaboom"),
        ):
            result = await get_transcript(video_url="dQw4w9WgXcQ")

        assert result["error"]["code"] == "INTERNAL_ERROR"
        assert result["error"]["category"] == "server_error"


# ---------------------------------------------------------------------------
# AC: list_available_transcripts tool — parameters and success
# ---------------------------------------------------------------------------


class TestListAvailableTranscriptsTool:
    """AC: list_available_transcripts accepts video_url parameter."""

    @pytest.mark.asyncio
    async def test_list_transcripts_success(self) -> None:
        """Happy path: returns transcripts list with count."""
        from src.__main__ import list_available_transcripts

        mock_transcripts = [
            {"language": "English", "language_code": "en", "is_generated": False},
            {"language": "Spanish", "language_code": "es", "is_generated": True},
        ]

        with patch(
            "src.__main__.transcript_client.list_transcripts",
            new_callable=AsyncMock,
            return_value=mock_transcripts,
        ):
            result = await list_available_transcripts(
                video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            )

        assert result["video_id"] == "dQw4w9WgXcQ"
        assert len(result["transcripts"]) == 2
        assert result["count"] == 2
        assert result["transcripts"][0]["language"] == "English"

    @pytest.mark.asyncio
    async def test_list_transcripts_uses_extract_video_id(self) -> None:
        """AC: Uses extract_video_id() for URL parsing."""
        from src.__main__ import list_available_transcripts

        with patch(
            "src.__main__.transcript_client.list_transcripts",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_list:
            await list_available_transcripts(
                video_url="https://youtu.be/dQw4w9WgXcQ"
            )
            mock_list.assert_awaited_once_with("dQw4w9WgXcQ")


# ---------------------------------------------------------------------------
# AC: list_available_transcripts error responses
# ---------------------------------------------------------------------------


class TestListAvailableTranscriptsErrors:
    """AC: Structured error responses for list_available_transcripts."""

    @pytest.mark.asyncio
    async def test_invalid_url_error(self) -> None:
        """AC: INVALID_URL error for bad URLs."""
        from src.__main__ import list_available_transcripts

        result = await list_available_transcripts(
            video_url="not-a-valid-url"
        )
        assert "error" in result
        assert result["error"]["code"] == "INVALID_URL"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_internal_error(self) -> None:
        """AC: INTERNAL_ERROR for unexpected exceptions."""
        from src.__main__ import list_available_transcripts

        with patch(
            "src.__main__.transcript_client.list_transcripts",
            new_callable=AsyncMock,
            side_effect=RuntimeError("kaboom"),
        ):
            result = await list_available_transcripts(
                video_url="dQw4w9WgXcQ"
            )

        assert result["error"]["code"] == "INTERNAL_ERROR"
        assert result["error"]["category"] == "server_error"


# ---------------------------------------------------------------------------
# AC: Logging to stderr only
# ---------------------------------------------------------------------------


class TestToolLogging:
    """AC: All logging to stderr via logger (never stdout)."""

    def test_module_logger_exists(self) -> None:
        """Module uses logging.getLogger(__name__)."""
        import logging

        import src.__main__ as mod

        assert hasattr(mod, "logger")
        assert isinstance(mod.logger, logging.Logger)

    def test_logging_configured_to_stderr(self) -> None:
        """Logging is configured to write to stderr (never stdout).

        Verifies that the __main__ module calls logging.basicConfig with
        stream=sys.stderr. We inspect the source code to confirm this
        critical MCP protocol requirement, since basicConfig is a no-op
        when called after the root logger already has handlers (e.g. in
        pytest's own logging setup).
        """
        import inspect

        import src.__main__ as mod

        source = inspect.getsource(mod)
        assert "stream=sys.stderr" in source, (
            "__main__.py must configure logging with stream=sys.stderr"
        )
        # Also verify stdout is never used for logging/print
        assert "print(" not in source, (
            "__main__.py must never print to stdout (breaks MCP protocol)"
        )
