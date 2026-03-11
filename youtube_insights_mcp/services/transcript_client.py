"""Transcript client service using youtube-transcript-api.

Provides async transcript fetching with intelligent language fallback
and structured error handling. All sync youtube-transcript-api calls
are wrapped with asyncio.to_thread() to avoid blocking the event loop.
"""

from __future__ import annotations

import asyncio
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)
from youtube_transcript_api.proxies import (
    GenericProxyConfig,
    ProxyConfig,
    WebshareProxyConfig,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataclasses for structured responses
# ---------------------------------------------------------------------------


@dataclass
class TranscriptSegment:
    """A single segment of transcript with timing."""

    start: float
    duration: float
    text: str


@dataclass
class TranscriptResult:
    """Complete transcript result with segments, full text, and metadata."""

    video_id: str
    language: str
    language_code: str
    is_auto_generated: bool
    segments: list[TranscriptSegment] = field(default_factory=list)
    full_text: str = ""
    total_segments: int = 0
    total_duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TranscriptClientError(Exception):
    """Base exception for transcript client errors."""


class TranscriptsDisabledError(TranscriptClientError):
    """Transcripts are disabled for this video."""


class NoTranscriptFoundError(TranscriptClientError):
    """No transcript found for requested language.

    Attributes:
        available_languages: Language codes of transcripts that *are*
            available for the video, so the caller can suggest alternatives.
    """

    def __init__(
        self,
        message: str,
        available_languages: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.available_languages: list[str] = available_languages or []


class VideoUnavailableError(TranscriptClientError):
    """Video is unavailable (does not exist or is private)."""


class IpBlockedError(TranscriptClientError):
    """YouTube is blocking requests from this IP address."""


# ---------------------------------------------------------------------------
# Proxy configuration
# ---------------------------------------------------------------------------


def build_proxy_config() -> ProxyConfig | None:
    """Build proxy config from environment variables.

    Priority:
        1. WEBSHARE_USERNAME + WEBSHARE_PASSWORD → WebshareProxyConfig
        2. PROXY_URL → GenericProxyConfig (used for both http and https)
        3. None (no proxy)

    Returns:
        ProxyConfig instance or None if no proxy is configured.
    """
    webshare_username = os.getenv("WEBSHARE_USERNAME")
    webshare_password = os.getenv("WEBSHARE_PASSWORD")
    proxy_url = os.getenv("PROXY_URL")

    if webshare_username and webshare_password:
        if proxy_url:
            logger.warning(
                "Both WEBSHARE_USERNAME/PASSWORD and PROXY_URL are set; "
                "using Webshare proxy configuration"
            )
        logger.info("Using Webshare rotating proxy")
        return WebshareProxyConfig(
            proxy_username=webshare_username,
            proxy_password=webshare_password,
        )

    if proxy_url:
        logger.info("Using generic proxy: %s", proxy_url)
        return GenericProxyConfig(
            http_url=proxy_url,
            https_url=proxy_url,
        )

    return None


# ---------------------------------------------------------------------------
# TranscriptClient
# ---------------------------------------------------------------------------


class TranscriptClient:
    """Client for fetching YouTube video transcripts.

    Wraps the synchronous youtube-transcript-api with async helpers and
    implements a 4-step language fallback strategy.
    """

    def __init__(self, proxy_config: ProxyConfig | None = None) -> None:
        self.api = YouTubeTranscriptApi(proxy_config=proxy_config)

    # -- public async API --------------------------------------------------

    async def get_transcript(
        self,
        video_id: str,
        language: str = "en",
    ) -> TranscriptResult:
        """Fetch transcript for a video with language fallback.

        Fallback strategy:
            1. Try exact language requested
            2. Try auto-generated version of requested language
            3. Try any English variant
            4. Return first available transcript

        Args:
            video_id: YouTube video ID (11 characters).
            language: Preferred language code (default: ``"en"``).

        Returns:
            TranscriptResult with segments and full text.

        Raises:
            TranscriptsDisabledError: Transcripts disabled for video.
            NoTranscriptFoundError: No transcripts available (includes
                ``available_languages``).
            VideoUnavailableError: Video does not exist or is private.
        """
        try:
            return await asyncio.to_thread(
                self._sync_get_transcript, video_id, language
            )
        except asyncio.CancelledError:
            logger.info("Transcript request cancelled for %s", video_id)
            raise

    async def list_transcripts(self, video_id: str) -> list[dict[str, Any]]:
        """List all available transcripts for a video.

        Args:
            video_id: YouTube video ID.

        Returns:
            List of dicts with ``language``, ``language_code``, and
            ``is_generated`` keys.  Returns an empty list (not an
            exception) when transcripts are unavailable.
        """
        try:
            return await asyncio.to_thread(
                self._sync_list_transcripts, video_id
            )
        except asyncio.CancelledError:
            logger.info("List transcripts request cancelled for %s", video_id)
            raise

    # -- synchronous helpers (run inside asyncio.to_thread) ----------------

    def _sync_get_transcript(
        self,
        video_id: str,
        language: str,
    ) -> TranscriptResult:
        """Synchronous transcript fetching with fallback (runs in thread)."""
        try:
            transcript = self.api.fetch(video_id, languages=[language])
            return self._build_result(video_id, transcript)

        except NoTranscriptFound:
            return self._fetch_with_fallback(video_id, language)

        except TranscriptsDisabled:
            raise TranscriptsDisabledError(
                f"Transcripts are disabled for video: {video_id}"
            )

        except VideoUnavailable:
            raise VideoUnavailableError(
                f"Video is unavailable: {video_id}"
            )

        except (IpBlocked, RequestBlocked):
            raise IpBlockedError(
                "YouTube is blocking requests from this IP. "
                "Configure PROXY_URL or WEBSHARE_USERNAME/WEBSHARE_PASSWORD "
                "environment variables to use a proxy."
            )

    def _fetch_with_fallback(
        self,
        video_id: str,
        preferred_language: str,
    ) -> TranscriptResult:
        """Try fallback languages when preferred not found.

        Strategy order:
            1. Auto-generated version of preferred language
            2. Any English variant
            3. First available transcript
        """
        try:
            transcript_list = self.api.list(video_id)
            available: list[dict[str, Any]] = []

            for t in transcript_list:
                available.append(
                    {
                        "language": t.language,
                        "language_code": t.language_code,
                        "is_generated": t.is_generated,
                    }
                )

            # Strategy 1: Auto-generated version of preferred language
            for t in transcript_list:
                if (
                    t.is_generated
                    and t.language_code.startswith(preferred_language)
                ):
                    logger.info(
                        "Using auto-generated %s transcript",
                        t.language_code,
                    )
                    fetched = t.fetch()
                    return self._build_result(video_id, fetched)

            # Strategy 2: Any English variant
            for t in transcript_list:
                if t.language_code.startswith("en"):
                    logger.info(
                        "Falling back to %s transcript", t.language_code
                    )
                    fetched = t.fetch()
                    return self._build_result(video_id, fetched)

            # Strategy 3: First available
            for t in transcript_list:
                logger.info(
                    "Using first available transcript: %s", t.language_code
                )
                fetched = t.fetch()
                return self._build_result(video_id, fetched)

            # No transcripts at all
            available_codes = [a["language_code"] for a in available]
            raise NoTranscriptFoundError(
                f"No transcript found for video: {video_id}",
                available_languages=available_codes,
            )

        except (TranscriptsDisabled, VideoUnavailable):
            raise
        except (IpBlocked, RequestBlocked):
            raise IpBlockedError(
                "YouTube is blocking requests from this IP. "
                "Configure PROXY_URL or WEBSHARE_USERNAME/WEBSHARE_PASSWORD "
                "environment variables to use a proxy."
            )
        except TranscriptClientError:
            raise

    def _sync_list_transcripts(
        self, video_id: str
    ) -> list[dict[str, Any]]:
        """Synchronous transcript listing (runs in thread).

        Returns an empty list (not an exception) when transcripts are
        unavailable for the video.
        """
        try:
            transcript_list = self.api.list(video_id)
            return [
                {
                    "language": t.language,
                    "language_code": t.language_code,
                    "is_generated": t.is_generated,
                }
                for t in transcript_list
            ]
        except (TranscriptsDisabled, VideoUnavailable):
            return []

    # -- private helpers ---------------------------------------------------

    def _build_result(
        self,
        video_id: str,
        transcript: Any,
    ) -> TranscriptResult:
        """Build a TranscriptResult from a fetched transcript object.

        Calculates ``total_segments``, ``total_duration_seconds``, and
        ``full_text`` from the transcript snippets.
        """
        segments = [
            TranscriptSegment(
                start=snippet.start,
                duration=snippet.duration,
                text=snippet.text,
            )
            for snippet in transcript.snippets
        ]

        full_text = " ".join(snippet.text for snippet in transcript.snippets)
        total_duration = sum(s.duration for s in segments)

        return TranscriptResult(
            video_id=video_id,
            language=transcript.language,
            language_code=transcript.language_code,
            is_auto_generated=transcript.is_generated,
            segments=segments,
            full_text=full_text,
            total_segments=len(segments),
            total_duration_seconds=total_duration,
        )
