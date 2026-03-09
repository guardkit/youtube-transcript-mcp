"""Tests for transcript fetching tool and client.

Comprehensive unit tests covering TranscriptClient service, tool registration,
and error handling. All youtube-transcript-api calls are mocked to avoid
external dependencies. Covers all acceptance criteria for TASK-TRS-004.
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
    TranscriptsDisabledError,
    TranscriptSegment,
    VideoUnavailableError,
)

# ---------------------------------------------------------------------------
# Mock helpers — match youtube-transcript-api v1.2+ response structure
# ---------------------------------------------------------------------------


@dataclass
class MockSnippet:
    """Mock FetchedTranscriptSnippet with .start, .duration, .text."""

    start: float
    duration: float
    text: str


@dataclass
class MockTranscript:
    """Mock FetchedTranscript returned by api.fetch().

    Attributes match youtube-transcript-api v1.2+: .snippets, .language,
    .language_code, .is_generated.
    """

    language: str
    language_code: str
    is_generated: bool
    snippets: list[MockSnippet]


def _make_mock_transcript(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    snippets: list[MockSnippet] | None = None,
) -> MockTranscript:
    """Create a mock transcript with sensible defaults."""
    if snippets is None:
        snippets = [
            MockSnippet(start=0.0, duration=2.5, text="Hello world"),
            MockSnippet(start=2.5, duration=3.0, text="This is a test"),
            MockSnippet(start=5.5, duration=2.0, text="Thank you"),
        ]
    return MockTranscript(
        language=language,
        language_code=language_code,
        is_generated=is_generated,
        snippets=snippets,
    )


def _make_transcript_info(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    fetched: MockTranscript | None = None,
) -> MagicMock:
    """Create a mock transcript-list entry (iterable item from api.list()).

    Uses MagicMock for transcript list iteration (__iter__).
    """
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
# AC: TranscriptSegment dataclass creation verified
# ---------------------------------------------------------------------------


class TestTranscriptSegment:
    """Tests for TranscriptSegment dataclass."""

    def test_segment_creation(self) -> None:
        """AC: TranscriptSegment dataclass creation verified."""
        segment = TranscriptSegment(start=10.5, duration=3.2, text="Test")

        assert segment.start == 10.5
        assert segment.duration == 3.2
        assert segment.text == "Test"

    def test_segment_equality(self) -> None:
        """Dataclass equality works for TranscriptSegment."""
        a = TranscriptSegment(start=1.0, duration=2.0, text="hi")
        b = TranscriptSegment(start=1.0, duration=2.0, text="hi")
        assert a == b

    def test_segment_inequality(self) -> None:
        """Different segments are not equal."""
        a = TranscriptSegment(start=1.0, duration=2.0, text="hi")
        b = TranscriptSegment(start=1.0, duration=2.0, text="bye")
        assert a != b


# ---------------------------------------------------------------------------
# AC: TranscriptResult dataclass
# ---------------------------------------------------------------------------


class TestTranscriptResult:
    """Tests for TranscriptResult dataclass defaults and fields."""

    def test_result_defaults(self) -> None:
        """TranscriptResult provides sensible defaults for optional fields."""
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

    def test_result_with_segments(self) -> None:
        """TranscriptResult stores segments and computed fields."""
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
        assert len(result.segments) == 1


# ---------------------------------------------------------------------------
# AC: TranscriptClient — happy path and _build_result
# ---------------------------------------------------------------------------


class TestTranscriptClient:
    """Tests for TranscriptClient service."""

    @pytest.fixture
    def mock_transcript(self) -> MockTranscript:
        """Create mock transcript response."""
        return _make_mock_transcript()

    @pytest.mark.asyncio
    async def test_get_transcript_success(
        self, mock_transcript: MockTranscript
    ) -> None:
        """AC: Happy path — successful transcript fetch with correct result structure."""
        client = TranscriptClient()

        with patch.object(client.api, "fetch", return_value=mock_transcript):
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
    async def test_get_transcript_fallback_to_auto_generated(
        self, mock_transcript: MockTranscript
    ) -> None:
        """AC: Language fallback — auto-generated fallback when manual not found."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()

        mock_transcript_info = MagicMock()
        mock_transcript_info.language = "English (auto-generated)"
        mock_transcript_info.language_code = "en"
        mock_transcript_info.is_generated = True
        mock_transcript_info.fetch.return_value = mock_transcript

        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([mock_transcript_info])

        with patch.object(
            client.api,
            "fetch",
            side_effect=NoTranscriptFound("vid", ["en"], mock_list),
        ):
            with patch.object(client.api, "list", return_value=mock_list):
                result = await client.get_transcript("dQw4w9WgXcQ", "en")

        assert result.language_code == "en"

    @pytest.mark.asyncio
    async def test_get_transcript_fallback_to_english(self) -> None:
        """Fallback strategy step 3: falls back to any English variant."""
        from youtube_transcript_api._errors import NoTranscriptFound

        client = TranscriptClient()
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
    async def test_get_transcript_fallback_to_first_available(self) -> None:
        """Fallback strategy step 4: falls back to first available transcript."""
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
    async def test_get_transcript_disabled_raises(self) -> None:
        """AC: Error case — TranscriptsDisabledError raised when disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled

        client = TranscriptClient()

        with patch.object(
            client.api, "fetch", side_effect=TranscriptsDisabled("vid")
        ):
            with pytest.raises(TranscriptsDisabledError, match="disabled"):
                await client.get_transcript("dQw4w9WgXcQ", "en")

    @pytest.mark.asyncio
    async def test_get_transcript_video_unavailable_raises(self) -> None:
        """AC: Error case — VideoUnavailableError raised when video unavailable."""
        from youtube_transcript_api._errors import VideoUnavailable

        client = TranscriptClient()

        with patch.object(
            client.api, "fetch", side_effect=VideoUnavailable("vid")
        ):
            with pytest.raises(VideoUnavailableError, match="unavailable"):
                await client.get_transcript("vid", "en")

    @pytest.mark.asyncio
    async def test_get_transcript_no_transcripts_raises(self) -> None:
        """AC: Error case — NoTranscriptFoundError when no transcripts at all."""
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

    def test_build_result_calculates_totals(
        self, mock_transcript: MockTranscript
    ) -> None:
        """AC: _build_result() correctly calculates totals (segments, duration, full_text)."""
        client = TranscriptClient()

        result = client._build_result("test123", mock_transcript)

        assert result.total_segments == 3
        assert result.total_duration_seconds == pytest.approx(7.5)  # 2.5 + 3.0 + 2.0
        assert result.full_text == "Hello world This is a test Thank you"

    def test_build_result_empty_snippets(self) -> None:
        """_build_result handles empty snippet list."""
        client = TranscriptClient()
        empty_transcript = _make_mock_transcript(snippets=[])

        result = client._build_result("vid", empty_transcript)

        assert result.total_segments == 0
        assert result.total_duration_seconds == 0.0
        assert result.full_text == ""

    def test_build_result_single_segment(self) -> None:
        """_build_result correctly handles a single segment."""
        client = TranscriptClient()
        transcript = _make_mock_transcript(
            snippets=[MockSnippet(start=0.0, duration=5.0, text="Only segment")]
        )

        result = client._build_result("vid", transcript)

        assert result.total_segments == 1
        assert result.total_duration_seconds == 5.0
        assert result.full_text == "Only segment"
        assert result.segments[0].start == 0.0
        assert result.segments[0].duration == 5.0
        assert result.segments[0].text == "Only segment"


# ---------------------------------------------------------------------------
# AC: list_transcripts() returns correct format
# ---------------------------------------------------------------------------


class TestListTranscripts:
    """Tests for TranscriptClient.list_transcripts()."""

    @pytest.mark.asyncio
    async def test_list_transcripts_success(self) -> None:
        """AC: list_transcripts() returns correct format with language info."""
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
        assert result[1]["language"] == "Spanish"
        assert result[1]["language_code"] == "es"
        assert result[1]["is_generated"] is True

    @pytest.mark.asyncio
    async def test_list_transcripts_disabled_returns_empty(self) -> None:
        """list_transcripts returns empty list when transcripts disabled."""
        from youtube_transcript_api._errors import TranscriptsDisabled

        client = TranscriptClient()
        with patch.object(
            client.api, "list", side_effect=TranscriptsDisabled("vid")
        ):
            result = await client.list_transcripts("vid")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_transcripts_video_unavailable_returns_empty(self) -> None:
        """list_transcripts returns empty list when video unavailable."""
        from youtube_transcript_api._errors import VideoUnavailable

        client = TranscriptClient()
        with patch.object(
            client.api, "list", side_effect=VideoUnavailable("vid")
        ):
            result = await client.list_transcripts("vid")

        assert result == []

    @pytest.mark.asyncio
    async def test_list_transcripts_empty_list(self) -> None:
        """list_transcripts returns empty list for video with no transcripts."""
        client = TranscriptClient()
        mock_list = MagicMock()
        mock_list.__iter__ = lambda self: iter([])

        with patch.object(client.api, "list", return_value=mock_list):
            result = await client.list_transcripts("vid")

        assert result == []


# ---------------------------------------------------------------------------
# AC: Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptionHierarchy:
    """Verify custom exception hierarchy and attributes."""

    def test_base_error_is_exception(self) -> None:
        assert issubclass(TranscriptClientError, Exception)

    def test_transcripts_disabled_inherits(self) -> None:
        assert issubclass(TranscriptsDisabledError, TranscriptClientError)

    def test_no_transcript_found_inherits(self) -> None:
        assert issubclass(NoTranscriptFoundError, TranscriptClientError)

    def test_video_unavailable_inherits(self) -> None:
        assert issubclass(VideoUnavailableError, TranscriptClientError)

    def test_no_transcript_found_has_available_languages(self) -> None:
        """NoTranscriptFoundError stores available_languages list."""
        err = NoTranscriptFoundError("no transcript", available_languages=["en", "fr"])
        assert err.available_languages == ["en", "fr"]

    def test_no_transcript_found_default_languages_empty(self) -> None:
        """NoTranscriptFoundError defaults to empty available_languages."""
        err = NoTranscriptFoundError("no transcript")
        assert err.available_languages == []


# ---------------------------------------------------------------------------
# AC: CancelledError handling
# ---------------------------------------------------------------------------


class TestCancelledErrorHandling:
    """CancelledError caught, logged, and re-raised (never swallowed)."""

    @pytest.mark.asyncio
    async def test_get_transcript_reraises_cancelled(self) -> None:
        """get_transcript re-raises CancelledError."""
        client = TranscriptClient()
        with patch(
            "src.services.transcript_client.asyncio.to_thread",
            side_effect=asyncio.CancelledError,
        ):
            with pytest.raises(asyncio.CancelledError):
                await client.get_transcript("vid", "en")

    @pytest.mark.asyncio
    async def test_list_transcripts_reraises_cancelled(self) -> None:
        """list_transcripts re-raises CancelledError."""
        client = TranscriptClient()
        with patch(
            "src.services.transcript_client.asyncio.to_thread",
            side_effect=asyncio.CancelledError,
        ):
            with pytest.raises(asyncio.CancelledError):
                await client.list_transcripts("vid")
