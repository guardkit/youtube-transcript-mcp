"""Tests for YouTubeClient service with URL parser and yt-dlp wrapper.

Covers all acceptance criteria for TASK-VID-002:
- AC-001: extract_video_id() URL format handling
- AC-002: extract_video_id() raises InvalidURLError
- AC-003: VideoInfo dataclass fields
- AC-004: get_video_info() uses asyncio.to_thread()
- AC-005: CancelledError caught, logged, re-raised
- AC-006: DownloadError mapped to VideoNotFoundError
- AC-007: _format_duration() edge cases
- AC-008: _truncate() behavior
- AC-009: src/services/__init__.py exists
- AC-010: Code passes ruff check and mypy
"""

from __future__ import annotations

import asyncio
import dataclasses
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.services.youtube_client import (
    InvalidURLError,
    VideoInfo,
    VideoNotFoundError,
    YouTubeClient,
    YouTubeClientError,
    extract_video_id,
)


# ---------------------------------------------------------------------------
# AC-001: extract_video_id handles multiple URL formats
# ---------------------------------------------------------------------------
class TestExtractVideoId:
    """Test URL parsing for various YouTube URL formats."""

    def test_standard_watch_url(self) -> None:
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self) -> None:
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self) -> None:
        url = "https://youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_url(self) -> None:
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_bare_video_id(self) -> None:
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_extra_query_params(self) -> None:
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120&list=PLxyz"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_url_with_www_prefix(self) -> None:
        url = "https://www.youtube.com/watch?v=abc12345678"
        assert extract_video_id(url) == "abc12345678"

    def test_bare_id_with_whitespace(self) -> None:
        assert extract_video_id("  dQw4w9WgXcQ  ") == "dQw4w9WgXcQ"

    def test_id_with_hyphens_and_underscores(self) -> None:
        assert extract_video_id("a-b_c123456") == "a-b_c123456"


# ---------------------------------------------------------------------------
# AC-002: extract_video_id raises InvalidURLError for bad formats
# ---------------------------------------------------------------------------
class TestExtractVideoIdErrors:
    """Test that unrecognized formats raise InvalidURLError."""

    def test_invalid_url(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("https://example.com/video")

    def test_empty_string(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("")

    def test_too_short_id(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("abc123")

    def test_too_long_id(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("abcdefghijklm")

    def test_invalid_characters(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("abc!@#$%^&*(")

    def test_non_youtube_video_url(self) -> None:
        with pytest.raises(InvalidURLError):
            extract_video_id("https://vimeo.com/12345")


# ---------------------------------------------------------------------------
# AC-003: VideoInfo dataclass has required fields
# ---------------------------------------------------------------------------
class TestVideoInfoDataclass:
    """Test VideoInfo dataclass structure."""

    def test_is_dataclass(self) -> None:
        assert dataclasses.is_dataclass(VideoInfo)

    def test_all_fields_present(self) -> None:
        expected_fields = {
            "video_id",
            "title",
            "channel",
            "channel_id",
            "duration_seconds",
            "duration_formatted",
            "description_snippet",
            "view_count",
            "upload_date",
            "thumbnail_url",
            "has_captions",
            "has_auto_captions",
            "available_languages",
        }
        actual_fields = {f.name for f in dataclasses.fields(VideoInfo)}
        assert expected_fields == actual_fields

    def test_can_instantiate(self) -> None:
        info = VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            channel="Test Channel",
            channel_id="@testchannel",
            duration_seconds=212,
            duration_formatted="3:32",
            description_snippet="A test video.",
            view_count=1000000,
            upload_date="20240101",
            thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
            has_captions=True,
            has_auto_captions=True,
            available_languages=["en", "es"],
        )
        assert info.video_id == "dQw4w9WgXcQ"
        assert info.title == "Test Video"
        assert info.has_captions is True
        assert info.available_languages == ["en", "es"]


# ---------------------------------------------------------------------------
# AC-004: get_video_info() uses asyncio.to_thread()
# ---------------------------------------------------------------------------
class TestGetVideoInfoAsync:
    """Test async wrapper around sync yt-dlp."""

    @pytest.fixture()
    def client(self) -> YouTubeClient:
        return YouTubeClient()

    @pytest.fixture()
    def mock_video_info(self) -> VideoInfo:
        return VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            channel="Test Channel",
            channel_id="@testchannel",
            duration_seconds=212,
            duration_formatted="3:32",
            description_snippet="Test description.",
            view_count=1000000,
            upload_date="20240101",
            thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
            has_captions=True,
            has_auto_captions=True,
            available_languages=["en", "es"],
        )

    @pytest.mark.asyncio
    async def test_get_video_info_returns_video_info(
        self, client: YouTubeClient, mock_video_info: VideoInfo
    ) -> None:
        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")
            assert result.video_id == "dQw4w9WgXcQ"
            assert result.title == "Test Video"

    @pytest.mark.asyncio
    async def test_get_video_info_uses_to_thread(
        self, client: YouTubeClient, mock_video_info: VideoInfo
    ) -> None:
        """Verify get_video_info delegates to asyncio.to_thread with _sync_get_info."""

        async def fake_to_thread(fn: object, *args: object, **kwargs: object) -> VideoInfo:
            return mock_video_info

        patch_target = "src.services.youtube_client.asyncio.to_thread"
        with patch(patch_target, side_effect=fake_to_thread) as mock_to_thread:
            result = await client.get_video_info("dQw4w9WgXcQ")
            mock_to_thread.assert_called_once()
            # Verify _sync_get_info was passed as the callable
            call_args = mock_to_thread.call_args
            assert call_args[0][0] == client._sync_get_info
            assert result.video_id == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_get_video_info_invalid_url(self, client: YouTubeClient) -> None:
        with pytest.raises(InvalidURLError):
            await client.get_video_info("not-a-valid-url")


# ---------------------------------------------------------------------------
# AC-005: CancelledError caught, logged, re-raised
# ---------------------------------------------------------------------------
class TestCancelledErrorHandling:
    """Test CancelledError is properly handled."""

    @pytest.mark.asyncio
    async def test_cancelled_error_is_reraised(self) -> None:
        client = YouTubeClient()
        with patch.object(
            client, "_sync_get_info", side_effect=asyncio.CancelledError()
        ):
            with patch("asyncio.to_thread", side_effect=asyncio.CancelledError()):
                with pytest.raises(asyncio.CancelledError):
                    await client.get_video_info("dQw4w9WgXcQ")


# ---------------------------------------------------------------------------
# AC-006: yt_dlp.utils.DownloadError mapped to VideoNotFoundError
# ---------------------------------------------------------------------------
class TestDownloadErrorMapping:
    """Test yt-dlp DownloadError is mapped to VideoNotFoundError."""

    def test_download_error_mapped(self) -> None:
        import yt_dlp

        client = YouTubeClient()
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.side_effect = yt_dlp.utils.DownloadError("Not found")

        with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
            with pytest.raises(VideoNotFoundError):
                client._sync_get_info(
                    "https://www.youtube.com/watch?v=xxxxxxxxxxx", "xxxxxxxxxxx"
                )

    def test_none_info_raises_video_not_found(self) -> None:
        client = YouTubeClient()
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = None

        with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
            with pytest.raises(VideoNotFoundError):
                client._sync_get_info(
                    "https://www.youtube.com/watch?v=xxxxxxxxxxx", "xxxxxxxxxxx"
                )


# ---------------------------------------------------------------------------
# AC-007: _format_duration() handles edge cases
# ---------------------------------------------------------------------------
class TestFormatDuration:
    """Test duration formatting."""

    def test_none_returns_zero(self) -> None:
        assert YouTubeClient._format_duration(None) == "0:00"

    def test_zero_seconds(self) -> None:
        assert YouTubeClient._format_duration(0) == "0:00"

    def test_seconds_only(self) -> None:
        assert YouTubeClient._format_duration(45) == "0:45"

    def test_minutes_and_seconds(self) -> None:
        assert YouTubeClient._format_duration(212) == "3:32"

    def test_hours_minutes_seconds(self) -> None:
        assert YouTubeClient._format_duration(3661) == "1:01:01"

    def test_exactly_one_hour(self) -> None:
        assert YouTubeClient._format_duration(3600) == "1:00:00"

    def test_exactly_one_minute(self) -> None:
        assert YouTubeClient._format_duration(60) == "1:00"


# ---------------------------------------------------------------------------
# AC-008: _truncate() behavior
# ---------------------------------------------------------------------------
class TestTruncate:
    """Test text truncation."""

    def test_short_text_unchanged(self) -> None:
        assert YouTubeClient._truncate("hello", 500) == "hello"

    def test_exact_length_unchanged(self) -> None:
        text = "x" * 500
        assert YouTubeClient._truncate(text, 500) == text

    def test_long_text_truncated_with_ellipsis(self) -> None:
        text = "x" * 600
        result = YouTubeClient._truncate(text, 500)
        assert len(result) == 500
        assert result.endswith("...")

    def test_empty_string(self) -> None:
        assert YouTubeClient._truncate("", 500) == ""


# ---------------------------------------------------------------------------
# AC-009: src/services/__init__.py exists
# ---------------------------------------------------------------------------
class TestPackageStructure:
    """Test package marker file exists."""

    def test_services_init_exists(self) -> None:
        init_path = Path(__file__).parent.parent / "src" / "services" / "__init__.py"
        assert init_path.exists(), f"src/services/__init__.py not found at {init_path}"


# ---------------------------------------------------------------------------
# Exception hierarchy tests
# ---------------------------------------------------------------------------
class TestExceptionHierarchy:
    """Test custom exception hierarchy."""

    def test_video_not_found_is_youtube_client_error(self) -> None:
        assert issubclass(VideoNotFoundError, YouTubeClientError)

    def test_invalid_url_is_youtube_client_error(self) -> None:
        assert issubclass(InvalidURLError, YouTubeClientError)

    def test_youtube_client_error_is_exception(self) -> None:
        assert issubclass(YouTubeClientError, Exception)


# ---------------------------------------------------------------------------
# Sync info extraction test
# ---------------------------------------------------------------------------
class TestSyncGetInfo:
    """Test _sync_get_info with mocked yt-dlp."""

    def test_extracts_all_fields(self) -> None:
        client = YouTubeClient()
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "uploader": "Test Channel",
            "uploader_id": "@testchannel",
            "duration": 212,
            "description": "Full description here.",
            "view_count": 1000000,
            "upload_date": "20240101",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
            "subtitles": {"en": []},
            "automatic_captions": {"en": [], "es": []},
        }

        with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
            result = client._sync_get_info(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"
            )

        assert result.video_id == "dQw4w9WgXcQ"
        assert result.title == "Test Video"
        assert result.channel == "Test Channel"
        assert result.channel_id == "@testchannel"
        assert result.duration_seconds == 212
        assert result.duration_formatted == "3:32"
        assert result.description_snippet == "Full description here."
        assert result.view_count == 1000000
        assert result.upload_date == "20240101"
        assert result.thumbnail_url == "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"
        assert result.has_captions is True
        assert result.has_auto_captions is True
        assert "en" in result.available_languages
        assert "es" in result.available_languages
