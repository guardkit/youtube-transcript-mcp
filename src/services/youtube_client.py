"""YouTube client utilities — URL parsing and video ID extraction.

Provides extract_video_id() for parsing various YouTube URL formats into
11-character video IDs. Used by MCP tools for input normalisation.
"""

from __future__ import annotations

import re

# URL patterns for video ID extraction
VIDEO_ID_PATTERNS = [
    r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/"
    r"|m\.youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})",
    r"^([a-zA-Z0-9_-]{11})$",  # Just the video ID
]


class YouTubeClientError(Exception):
    """Base exception for YouTube client errors."""


class InvalidURLError(YouTubeClientError):
    """URL is not a valid YouTube URL."""


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from various YouTube URL formats.

    Supported formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://youtube.com/embed/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - VIDEO_ID (just the 11-character ID)

    Args:
        url_or_id: YouTube URL or video ID.

    Returns:
        11-character video ID.

    Raises:
        InvalidURLError: If URL format is not recognised.
    """
    url_or_id = url_or_id.strip()

    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

    raise InvalidURLError(f"Could not extract video ID from: {url_or_id}")
