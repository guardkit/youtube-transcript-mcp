"""Tests for video info tool and YouTube client.

Comprehensive unit tests for TASK-VID-004 covering:
- extract_video_id() — all URL formats + error cases
- YouTubeClient — mocked yt-dlp responses for happy path
- _format_duration() — edge cases (None, seconds, minutes, hours)

All tests use mocked yt-dlp to avoid network calls.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from src.services.youtube_client import (
    InvalidURLError,
    VideoInfo,
    YouTubeClient,
    extract_video_id,
)


# ---------------------------------------------------------------------------
# AC-001: TestExtractVideoId — standard URL, short URL, embed URL, mobile URL,
#         bare ID, URL with extra params
# ---------------------------------------------------------------------------
class TestExtractVideoId:
    """Tests for extract_video_id() URL parsing across all supported formats."""

    def test_standard_url(self) -> None:
        """Standard youtube.com/watch?v= URL extracts the video ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_short_url(self) -> None:
        """Short youtu.be/ URL extracts the video ID."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_embed_url(self) -> None:
        """Embed youtube.com/embed/ URL extracts the video ID."""
        url = "https://youtube.com/embed/dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_mobile_url(self) -> None:
        """Mobile m.youtube.com/watch?v= URL extracts the video ID."""
        url = "https://m.youtube.com/watch?v=dQw4w9WgXcQ"
        assert extract_video_id(url) == "dQw4w9WgXcQ"

    def test_bare_id(self) -> None:
        """Bare 11-character video ID is returned as-is."""
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_url_with_extra_params(self) -> None:
        """URL with extra query params (t, list) still extracts correct ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120&list=PLxyz"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


# ---------------------------------------------------------------------------
# AC-002: TestExtractVideoId error cases — invalid URL raises InvalidURLError,
#         empty string raises InvalidURLError
# ---------------------------------------------------------------------------
class TestExtractVideoIdErrors:
    """Tests that invalid inputs to extract_video_id() raise InvalidURLError."""

    def test_invalid_url_raises(self) -> None:
        """Non-YouTube URL raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("https://example.com/video")

    def test_empty_string_raises(self) -> None:
        """Empty string raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("")

    def test_whitespace_only_raises(self) -> None:
        """Whitespace-only string raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("   ")

    def test_too_short_id_raises(self) -> None:
        """ID shorter than 11 characters raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("abc123")

    def test_too_long_id_raises(self) -> None:
        """ID longer than 11 characters (not a URL) raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("abcdefghijklm")

    def test_non_youtube_video_site_raises(self) -> None:
        """URL from another video site raises InvalidURLError."""
        with pytest.raises(InvalidURLError):
            extract_video_id("https://vimeo.com/12345")


# ---------------------------------------------------------------------------
# AC-003: TestYouTubeClient — get_video_info success path with mocked
#         _sync_get_info
# ---------------------------------------------------------------------------
class TestYouTubeClient:
    """Tests for YouTubeClient with mocked yt-dlp responses."""

    @pytest.fixture()
    def mock_yt_dlp_info(self) -> dict[str, object]:
        """Realistic yt-dlp response dict for mocking."""
        return {
            "id": "dQw4w9WgXcQ",
            "title": "Test Video",
            "uploader": "Test Channel",
            "uploader_id": "@testchannel",
            "duration": 212,
            "description": "This is a test video description.",
            "view_count": 1000000,
            "upload_date": "20240101",
            "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
            "subtitles": {"en": []},
            "automatic_captions": {"en": [], "es": []},
        }

    @pytest.fixture()
    def mock_video_info(self) -> VideoInfo:
        """Pre-built VideoInfo matching mock_yt_dlp_info for patching _sync_get_info."""
        return VideoInfo(
            video_id="dQw4w9WgXcQ",
            title="Test Video",
            channel="Test Channel",
            channel_id="@testchannel",
            duration_seconds=212,
            duration_formatted="3:32",
            description_snippet="This is a test video description.",
            view_count=1000000,
            upload_date="20240101",
            thumbnail_url="https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
            has_captions=True,
            has_auto_captions=True,
            available_languages=["en", "es"],
        )

    @pytest.mark.asyncio
    async def test_get_video_info_success(self, mock_video_info: VideoInfo) -> None:
        """get_video_info returns VideoInfo for a valid video with mocked _sync_get_info."""
        client = YouTubeClient()

        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")

        assert isinstance(result, VideoInfo)

    # -------------------------------------------------------------------
    # AC-004: Verifies video_id, title, has_captions, available_languages
    # -------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_video_id_from_mock(self, mock_video_info: VideoInfo) -> None:
        """Returned VideoInfo.video_id matches the mocked value."""
        client = YouTubeClient()
        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")
        assert result.video_id == "dQw4w9WgXcQ"

    @pytest.mark.asyncio
    async def test_title_from_mock(self, mock_video_info: VideoInfo) -> None:
        """Returned VideoInfo.title matches the mocked value."""
        client = YouTubeClient()
        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")
        assert result.title == "Test Video"

    @pytest.mark.asyncio
    async def test_has_captions_from_mock(self, mock_video_info: VideoInfo) -> None:
        """Returned VideoInfo.has_captions is True when subtitles exist."""
        client = YouTubeClient()
        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")
        assert result.has_captions is True

    @pytest.mark.asyncio
    async def test_available_languages_from_mock(
        self, mock_video_info: VideoInfo
    ) -> None:
        """Returned VideoInfo.available_languages includes expected languages."""
        client = YouTubeClient()
        with patch.object(client, "_sync_get_info", return_value=mock_video_info):
            result = await client.get_video_info("dQw4w9WgXcQ")
        assert "en" in result.available_languages
        assert "es" in result.available_languages

    @pytest.mark.asyncio
    async def test_get_video_info_invalid_url_raises(self) -> None:
        """get_video_info raises InvalidURLError for unrecognized URL."""
        client = YouTubeClient()
        with pytest.raises(InvalidURLError):
            await client.get_video_info("not-a-valid-url")

    @pytest.mark.asyncio
    async def test_cancelled_error_reraised(self) -> None:
        """CancelledError from asyncio.to_thread is re-raised, not swallowed."""
        client = YouTubeClient()
        with patch(
            "src.services.youtube_client.asyncio.to_thread",
            side_effect=asyncio.CancelledError(),
        ):
            with pytest.raises(asyncio.CancelledError):
                await client.get_video_info("dQw4w9WgXcQ")

    def test_sync_get_info_with_mocked_ytdlp(
        self, mock_yt_dlp_info: dict[str, object]
    ) -> None:
        """_sync_get_info builds VideoInfo from yt-dlp response dict (no network)."""
        client = YouTubeClient()
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info.return_value = mock_yt_dlp_info

        with patch("yt_dlp.YoutubeDL", return_value=mock_ydl):
            result = client._sync_get_info(
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "dQw4w9WgXcQ"
            )

        assert result.video_id == "dQw4w9WgXcQ"
        assert result.title == "Test Video"
        assert result.channel == "Test Channel"
        assert result.has_captions is True
        assert result.has_auto_captions is True
        assert "en" in result.available_languages
        assert "es" in result.available_languages


# ---------------------------------------------------------------------------
# AC-005: Duration formatting — None -> "0:00", 45 -> "0:45",
#         212 -> "3:32", 3661 -> "1:01:01"
# ---------------------------------------------------------------------------
class TestFormatDuration:
    """Tests for YouTubeClient._format_duration() edge cases."""

    def test_none_returns_zero(self) -> None:
        """None duration returns '0:00'."""
        assert YouTubeClient._format_duration(None) == "0:00"

    def test_zero_returns_zero(self) -> None:
        """Zero seconds returns '0:00'."""
        assert YouTubeClient._format_duration(0) == "0:00"

    def test_seconds_only(self) -> None:
        """45 seconds formats as '0:45'."""
        assert YouTubeClient._format_duration(45) == "0:45"

    def test_minutes_and_seconds(self) -> None:
        """212 seconds formats as '3:32'."""
        assert YouTubeClient._format_duration(212) == "3:32"

    def test_hours_minutes_seconds(self) -> None:
        """3661 seconds formats as '1:01:01'."""
        assert YouTubeClient._format_duration(3661) == "1:01:01"

    def test_exactly_one_hour(self) -> None:
        """3600 seconds formats as '1:00:00'."""
        assert YouTubeClient._format_duration(3600) == "1:00:00"

    def test_exactly_one_minute(self) -> None:
        """60 seconds formats as '1:00'."""
        assert YouTubeClient._format_duration(60) == "1:00"
