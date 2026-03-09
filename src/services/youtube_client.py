"""YouTube client service using yt-dlp for metadata extraction.

Provides URL parsing, video metadata fetching, and structured error handling
for YouTube video information retrieval via yt-dlp.
"""

from __future__ import annotations

import asyncio
import logging
import re
import sys
from dataclasses import dataclass

import yt_dlp

logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

# URL patterns for extracting 11-character YouTube video IDs.
# Order matters: specific URL patterns first, bare ID last.
VIDEO_ID_PATTERNS: list[str] = [
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|m\.youtube\.com/watch\?v=)"
    r"([a-zA-Z0-9_-]{11})",
    r"^([a-zA-Z0-9_-]{11})$",  # Bare 11-character video ID
]


class YouTubeClientError(Exception):
    """Base exception for YouTube client errors."""


class VideoNotFoundError(YouTubeClientError):
    """Video does not exist or is unavailable."""


class InvalidURLError(YouTubeClientError):
    """URL is not a valid YouTube URL or video ID."""


@dataclass
class VideoInfo:
    """Structured video metadata container from YouTube."""

    video_id: str
    title: str
    channel: str
    channel_id: str | None
    duration_seconds: int
    duration_formatted: str
    description_snippet: str
    view_count: int | None
    upload_date: str | None
    thumbnail_url: str | None
    has_captions: bool
    has_auto_captions: bool
    available_languages: list[str]


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats.

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - VIDEO_ID (bare 11-character ID)

    Args:
        url_or_id: YouTube URL or video ID string.

    Returns:
        The 11-character video ID.

    Raises:
        InvalidURLError: If the URL format is not recognized.
    """
    url_or_id = url_or_id.strip()

    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise InvalidURLError(f"Could not extract video ID from: {url_or_id}")


class YouTubeClient:
    """Async client for fetching YouTube video metadata via yt-dlp.

    Wraps the synchronous yt-dlp library using asyncio.to_thread()
    to avoid blocking the event loop.
    """

    def __init__(self) -> None:
        self.ydl_opts: dict[str, object] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
        }

    async def get_video_info(self, url_or_id: str) -> VideoInfo:
        """Fetch video metadata from YouTube.

        Args:
            url_or_id: YouTube URL or video ID.

        Returns:
            VideoInfo populated with video metadata.

        Raises:
            InvalidURLError: If URL format is invalid.
            VideoNotFoundError: If video doesn't exist or is unavailable.
        """
        video_id = extract_video_id(url_or_id)
        video_url = f"https://www.youtube.com/watch?v={video_id}"

        try:
            return await asyncio.to_thread(self._sync_get_info, video_url, video_id)
        except asyncio.CancelledError:
            logger.info("Video info request cancelled for %s", video_id)
            raise

    def _sync_get_info(self, video_url: str, video_id: str) -> VideoInfo:
        """Synchronous video info extraction (runs in thread pool).

        Args:
            video_url: Full YouTube watch URL.
            video_id: The 11-character video ID.

        Returns:
            VideoInfo populated from yt-dlp response.

        Raises:
            VideoNotFoundError: If video is unavailable or yt-dlp returns None.
        """
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

                if info is None:
                    raise VideoNotFoundError(f"Video not found: {video_id}")

                subtitles: dict[str, list[object]] = info.get("subtitles", {})
                auto_captions: dict[str, list[object]] = info.get(
                    "automatic_captions", {}
                )

                available_languages = sorted(
                    set(list(subtitles.keys()) + list(auto_captions.keys()))
                )

                return VideoInfo(
                    video_id=info.get("id", video_id),
                    title=info.get("title", "Unknown"),
                    channel=info.get("uploader", "Unknown"),
                    channel_id=info.get("uploader_id"),
                    duration_seconds=info.get("duration", 0),
                    duration_formatted=self._format_duration(info.get("duration")),
                    description_snippet=self._truncate(
                        info.get("description", ""), 500
                    ),
                    view_count=info.get("view_count"),
                    upload_date=info.get("upload_date"),
                    thumbnail_url=info.get("thumbnail"),
                    has_captions=bool(subtitles),
                    has_auto_captions=bool(auto_captions),
                    available_languages=available_languages,
                )

        except yt_dlp.utils.DownloadError as e:
            logger.error("yt-dlp error for %s: %s", video_id, e)
            raise VideoNotFoundError(f"Video unavailable: {video_id}") from e

    @staticmethod
    def _format_duration(seconds: int | None) -> str:
        """Format duration as HH:MM:SS or MM:SS.

        Args:
            seconds: Duration in seconds, or None.

        Returns:
            Formatted duration string. Returns "0:00" for None or 0.
        """
        if not seconds:
            return "0:00"
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"

    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        """Truncate text with ellipsis if it exceeds max_length.

        Args:
            text: The text to truncate.
            max_length: Maximum allowed length.

        Returns:
            Original text if within limit, otherwise truncated with "..." suffix.
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."
