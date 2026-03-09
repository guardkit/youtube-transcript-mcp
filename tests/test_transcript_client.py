"""Tests for TranscriptClient service.

TDD RED phase: these tests define the expected behavior of TranscriptClient.
Covers all acceptance criteria for TASK-TRS-002.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from src.services.transcript_client import (
    NoTranscriptFoundError,
    TranscriptClient,
    TranscriptClientError,
    TranscriptResult,
    TranscriptSegment,
    TranscriptsDisabledError,
    VideoUnavailableError,
)


# ---------------------------------------------------------------------------
# Mock helpers
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


def _make_transcript_info(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    fetched: MockFetchedTranscript | None = None,
) -> MagicMock:
    """Create a mock transcript-list entry (iterable item from api.list())."""
    info = MagicMock()
    info.language = language
    info.language_code = language_code
    info.is_generated = is_generated
    info.fetch.return_value = fetched or _make_mock_transcript(
        language=language,
        language_code=language_code,
        is_generated=is_generated,
    )
    return info


# ---------------------------------------------------------------------------
# AC: TranscriptSegment and TranscriptResult dataclasses
# ---------------------------------------------------------------------------

class TestTranscriptSegment:
    """AC: TranscriptResult and TranscriptSegment dataclasses for structured responses."""

    def test_segment_creation(self) -> None:
        seg = TranscriptSegment(start=10.5, duration=3.2, text="Test")
        assert seg.start == 10.5
        assert seg.duration == 3.2
        assert seg.text == "Test"

    def test_segment_equality(self) -> None:
        a = TranscriptSegment(start=1.0, duration=2.0, text="hi")
        b = TranscriptSegment(start=1.0, duration=2.0, text="hi")
        assert a == b


class TestTranscriptResult:
    """AC: TranscriptResult and TranscriptSegment dataclasses for structured responses."""

    def test_result_creation(self) -> None:
        result = TranscriptResult(
            video_id="abc123",
            language="English",
            language_code="en",
            is_auto_generated=False,
            segments=[TranscriptSegment(start=0.0, duration=1.0, text="hi")],
            full_text="hi",
            total_segments=1,
            total_duration_seconds=1.0,
        )
        assert result.video_id == "abc123"
        assert result.language_code == "en"
        assert result.total_segments == 1

    def test_result_defaults(self) -> None:
        result = TranscriptResult(
            video_id="x",
            language="X",
            language_code="x",
            is_auto_generated=False,
        )
        assert result.segments == []
        assert result.full_text == ""
        assert result.total_segments == 0
        assert result.total_duration_seconds == 0.0


# ---------------------------------------------------------------------------
# AC: Custom exceptions hierarchy
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    """AC: Custom exceptions: TranscriptClientError, TranscriptsDisabledError, ..."""

    def test_base_error_is_exception(self) -> None:
        assert issubclass(TranscriptClientError, Exception)

    def test_transcripts_disabled_inherits(self) -> None:
        assert issubclass(TranscriptsDisabledError, TranscriptClientError)

    def test_no_transcript_found_inherits(self) -> None:
        assert issubclass(NoTranscriptFoundError, TranscriptClientError)

    def test_video_unavailable_inherits(self) -> None:
        assert issubclass(VideoUnavailableError, TranscriptClientError)

    def test_no_transcript_found_has_available_languages(self) -> None:
        err = NoTranscriptFoundError("no transcript", available_languages=["en", "fr"])
        assert err.available_languages == ["en", "fr"]

    def test_no_transcript_found_default_languages(self) -> None:
        err = NoTranscriptFoundError("no transcript")
        assert err.available_languages == []


# ---------------------------------------------------------------------------
# AC: get_transcript() async method with language fallback
# ---------------------------------------------------------------------------

class TestGetTranscript:
    """AC: get_transcript() async method fetches transcript with language fallback."""

    @pytest.mark.asyncio
    async def test_get_transcript_success(self) -> None:
        """Happy path: exact language found via api.fetch()."""
        client = TranscriptClient()
        mock_t = _make_mock_transcript()

        with patch.object(client.api, "fetch", return_value=mock_t):
            result = await client.get_transcript("dQw4w9WgXcQ", "en")

        assert result.video_id == "dQw4w9WgXcQ"
        assert result.language == "English"
        assert result.language_code == "en"
        assert result.is_auto_generated is False
        assert result.total_segments == 3
        assert "Hello world" in result.full_text
        assert "This is a test" in result.full_text
        assert "Thank you" in result.full_text

    @pytest.mark.asyncio
    async def test_get_transcript_calculates_totals(self) -> None:
        """_build_result calculates total_segments, total_duration_seconds, full_text."""
        client = TranscriptClient()
        mock_t = _make_mock_transcript()

        with patch.object(client.api, "fetch", return_value=mock_t):
            result = await client.get_transcript("vid123", "en")

        assert result.total_segments == 3
        assert result.total_duration_seconds == pytest.approx(7.5)
        assert result.full_text == "Hello world This is a test Thank you"

    @pytest.mark.asyncio
    async def test_get_transcript_disabled_raises(self) -> None:
        """AC: TranscriptsDisabledError raised when transcripts disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled

        client = TranscriptClient()
        with patch.object(
            client.api, "fetch", side_effect=TranscriptsDisabled("vid")
        ):
            with pytest.raises(TranscriptsDisabledError, match="disabled"):
                await client.get_transcript("vid", "en")

    @pytest.mark.asyncio
    async def test_get_transcript_video_unavailable_raises(self) -> None:
        """AC: VideoUnavailableError raised when video unavailable."""
        from youtube_transcript_api._errors import VideoUnavailable

        client = TranscriptClient()
        with patch.object(
            client.api, "fetch", side_effect=VideoUnavailable("vid")
        ):
            with pytest.raises(VideoUnavailableError, match="unavailable"):
                await client.get_transcript("vid", "en")

    @pytest.mark.asyncio
    async def test_get_transcript_uses_asyncio_to_thread(self) -> None:
        """AC: Async wrappers use asyncio.to_thread() for sync calls."""
        client = TranscriptClient()
        mock_t = _make_mock_transcript()

        with patch.object(client.api, "fetch", return_value=mock_t):
            with patch("src.services.transcript_client.asyncio.to_thread", wraps=asyncio.to_thread) as mock_thread:
                await client.get_transcript("vid", "en")
                mock_thread.assert_called_once()


# ---------------------------------------------------------------------------
# AC: Language fallback strategy
# ---------------------------------------------------------------------------

class TestLanguageFallback:
    """AC: Language fallback strategy: requested -> auto-generated -> English -> first available."""

    @pytest.mark.asyncio
    async def test_fallback_to_auto_generated(self) -> None:
        """Step 2: Falls back to auto-generated version of requested language."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()
        auto_gen = _make_transcript_info(
            language="English (auto-generated)",
            language_code="en",
            is_generated=True,
        )
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([auto_gen])

        with patch.object(
            client.api,
            "fetch",
            side_effect=NoTranscriptFound("vid", ["en"], mock_list),
        ):
            with patch.object(client.api, "list", return_value=mock_list):
                result = await client.get_transcript("vid", "en")

        assert result.language_code == "en"

    @pytest.mark.asyncio
    async def test_fallback_to_english(self) -> None:
        """Step 3: Falls back to any English variant when preferred not found."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()
        # Only a non-generated English transcript available (no auto-gen for 'fr')
        en_info = _make_transcript_info(
            language="English",
            language_code="en",
            is_generated=False,
        )
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([en_info])

        with patch.object(
            client.api,
            "fetch",
            side_effect=NoTranscriptFound("vid", ["fr"], mock_list),
        ):
            with patch.object(client.api, "list", return_value=mock_list):
                result = await client.get_transcript("vid", "fr")

        assert result.language_code == "en"

    @pytest.mark.asyncio
    async def test_fallback_to_first_available(self) -> None:
        """Step 4: Falls back to first available when no English."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()
        es_info = _make_transcript_info(
            language="Spanish",
            language_code="es",
            is_generated=False,
        )
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([es_info])

        with patch.object(
            client.api,
            "fetch",
            side_effect=NoTranscriptFound("vid", ["en"], mock_list),
        ):
            with patch.object(client.api, "list", return_value=mock_list):
                result = await client.get_transcript("vid", "en")

        assert result.language_code == "es"

    @pytest.mark.asyncio
    async def test_fallback_no_transcripts_raises(self) -> None:
        """Raises NoTranscriptFoundError when no transcripts at all."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([])

        with patch.object(
            client.api,
            "fetch",
            side_effect=NoTranscriptFound("vid", ["en"], mock_list),
        ):
            with patch.object(client.api, "list", return_value=mock_list):
                with pytest.raises(NoTranscriptFoundError):
                    await client.get_transcript("vid", "en")


# ---------------------------------------------------------------------------
# AC: list_transcripts() async method
# ---------------------------------------------------------------------------

class TestListTranscripts:
    """AC: list_transcripts() async method lists available transcripts."""

    @pytest.mark.asyncio
    async def test_list_transcripts_success(self) -> None:
        client = TranscriptClient()
        en_info = _make_transcript_info("English", "en", False)
        es_info = _make_transcript_info("Spanish", "es", True)
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([en_info, es_info])

        with patch.object(client.api, "list", return_value=mock_list):
            result = await client.list_transcripts("vid")

        assert len(result) == 2
        assert result[0]["language"] == "English"
        assert result[0]["language_code"] == "en"
        assert result[0]["is_generated"] is False
        assert result[1]["language_code"] == "es"
        assert result[1]["is_generated"] is True

    @pytest.mark.asyncio
    async def test_list_transcripts_disabled_returns_empty(self) -> None:
        """Returns empty list (not exception) when transcripts unavailable."""
        from youtube_transcript_api._errors import TranscriptsDisabled

        client = TranscriptClient()
        with patch.object(
            client.api, "list", side_effect=TranscriptsDisabled("vid")
        ):
            result = await client.list_transcripts("vid")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_transcripts_video_unavailable_returns_empty(self) -> None:
        """Returns empty list when video unavailable."""
        from youtube_transcript_api._errors import VideoUnavailable

        client = TranscriptClient()
        with patch.object(
            client.api, "list", side_effect=VideoUnavailable("vid")
        ):
            result = await client.list_transcripts("vid")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_transcripts_uses_asyncio_to_thread(self) -> None:
        """AC: Async wrappers use asyncio.to_thread()."""
        client = TranscriptClient()
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([])

        with patch.object(client.api, "list", return_value=mock_list):
            with patch("src.services.transcript_client.asyncio.to_thread", wraps=asyncio.to_thread) as mock_thread:
                await client.list_transcripts("vid")
                mock_thread.assert_called_once()


# ---------------------------------------------------------------------------
# AC: CancelledError handling
# ---------------------------------------------------------------------------

class TestCancelledErrorHandling:
    """AC: CancelledError caught, logged, and re-raised (never swallowed)."""

    @pytest.mark.asyncio
    async def test_get_transcript_reraises_cancelled(self) -> None:
        client = TranscriptClient()
        with patch(
            "src.services.transcript_client.asyncio.to_thread",
            side_effect=asyncio.CancelledError,
        ):
            with pytest.raises(asyncio.CancelledError):
                await client.get_transcript("vid", "en")

    @pytest.mark.asyncio
    async def test_list_transcripts_reraises_cancelled(self) -> None:
        client = TranscriptClient()
        with patch(
            "src.services.transcript_client.asyncio.to_thread",
            side_effect=asyncio.CancelledError,
        ):
            with pytest.raises(asyncio.CancelledError):
                await client.list_transcripts("vid")


# ---------------------------------------------------------------------------
# AC: All logging to stderr via logging.getLogger(__name__)
# ---------------------------------------------------------------------------

class TestLogging:
    """AC: All logging to stderr via logging.getLogger(__name__)."""

    def test_module_logger_exists(self) -> None:
        """Module uses logging.getLogger(__name__)."""
        import src.services.transcript_client as mod
        import logging

        assert hasattr(mod, "logger")
        assert isinstance(mod.logger, logging.Logger)
        assert mod.logger.name == "src.services.transcript_client"
