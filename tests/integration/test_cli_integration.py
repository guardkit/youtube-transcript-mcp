"""Integration tests for CLI - requires network access.

Exercises the CLI with real YouTube API calls to verify end-to-end
functionality including transcript fetching and video metadata retrieval.

Run selectively with:
    pytest -m integration
    pytest -m slow

AC-001: tests/integration/test_cli_integration.py exists with TestCLIIntegration class
AC-002: Tests marked with @pytest.mark.slow and @pytest.mark.integration
AC-003: test_get_transcript_real_video verifies full transcript fetch (dQw4w9WgXcQ)
AC-004: test_video_info_real_video verifies video metadata fetch
AC-005: All results are valid JSON with expected fields
AC-006: Exit codes are correct (0 for success)
AC-007: Tests can be run selectively: pytest -m integration
"""

from __future__ import annotations

import json

import pytest

from src.cli import main

# Known stable video: Rick Astley - Never Gonna Give You Up
KNOWN_VIDEO_ID = "dQw4w9WgXcQ"


def _has_youtube_client() -> bool:
    """Check whether YouTubeClient is available for video-info tests."""
    try:
        from src.services.youtube_client import YouTubeClient  # noqa: F401

        return True
    except ImportError:
        return False


@pytest.mark.slow
@pytest.mark.integration
class TestCLIIntegration:
    """Real network calls - run with ``pytest -m integration``.

    These tests require network access and may be slow. They exercise
    the full CLI pipeline: argument parsing, service invocation over
    the network, JSON serialisation, and exit code handling.
    """

    # ------------------------------------------------------------------
    # AC-003: test_get_transcript_real_video
    # ------------------------------------------------------------------

    def test_get_transcript_real_video(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify full transcript fetch for a known public video.

        Uses --no-segments to keep the payload small while still verifying
        that a real transcript is returned with expected fields.
        """
        exit_code = main(["get-transcript", KNOWN_VIDEO_ID, "--no-segments"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        # AC-006: Exit code 0 for success
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}: {data}"

        # AC-005: Valid JSON with expected fields
        assert "video_id" in data
        assert data["video_id"] == KNOWN_VIDEO_ID
        assert "full_text" in data
        assert len(data["full_text"]) > 100, "Transcript text too short"
        assert "language" in data
        assert "language_code" in data
        assert "is_auto_generated" in data
        assert "total_segments" in data
        assert isinstance(data["total_segments"], int)
        assert data["total_segments"] > 0
        assert "total_duration_seconds" in data
        assert isinstance(data["total_duration_seconds"], (int, float))
        assert data["total_duration_seconds"] > 0

        # --no-segments flag: segments should NOT be in output
        assert "segments" not in data

    def test_get_transcript_real_video_with_segments(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify transcript fetch includes segments when flag is not set."""
        exit_code = main(["get-transcript", KNOWN_VIDEO_ID])
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert exit_code == 0
        assert "segments" in data
        assert isinstance(data["segments"], list)
        assert len(data["segments"]) > 0

        # Verify segment structure
        segment = data["segments"][0]
        assert "start" in segment
        assert "duration" in segment
        assert "text" in segment
        assert isinstance(segment["start"], (int, float))
        assert isinstance(segment["duration"], (int, float))
        assert isinstance(segment["text"], str)

    # ------------------------------------------------------------------
    # AC-004: test_video_info_real_video
    # ------------------------------------------------------------------

    @pytest.mark.skipif(
        not _has_youtube_client(),
        reason="YouTubeClient not yet implemented (FEAT-SKEL-002 dependency)",
    )
    def test_video_info_real_video(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify video metadata fetch for a known public video.

        Skipped until YouTubeClient (FEAT-SKEL-002) is implemented.
        When available, validates that video-info returns correct
        metadata fields for Rick Astley's Never Gonna Give You Up.
        """
        exit_code = main(["video-info", KNOWN_VIDEO_ID])
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        # AC-006: Exit code 0 for success
        assert exit_code == 0, f"Expected exit code 0, got {exit_code}: {data}"

        # AC-005: Valid JSON with expected fields
        assert data["video_id"] == KNOWN_VIDEO_ID
        assert "title" in data
        assert isinstance(data["title"], str)
        assert len(data["title"]) > 0
        assert "channel" in data
        assert isinstance(data["channel"], str)
        assert "duration_seconds" in data
        assert isinstance(data["duration_seconds"], (int, float))
        assert data["duration_seconds"] > 0
        assert "has_captions" in data
        assert isinstance(data["has_captions"], bool)

    # ------------------------------------------------------------------
    # Additional integration coverage
    # ------------------------------------------------------------------

    def test_get_transcript_output_is_pure_json(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify stdout contains only valid JSON, no logging text."""
        main(["get-transcript", KNOWN_VIDEO_ID, "--no-segments"])
        captured = capsys.readouterr()

        # Entire stdout should be a single JSON object
        stripped = captured.out.strip()
        assert stripped.startswith("{"), "stdout does not start with '{'"
        assert stripped.endswith("}"), "stdout does not end with '}'"
        json.loads(stripped)  # raises ValueError if not valid JSON

    def test_get_transcript_invalid_video_returns_error(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify that an invalid video ID returns an error with exit code 1."""
        exit_code = main(["get-transcript", "xxxxxxxxxxx"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert exit_code == 1
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
