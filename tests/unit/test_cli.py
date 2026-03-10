"""Unit tests for CLI parser and output format.

Covers argument parsing (TestCliParser) and JSON output/exit codes
(TestCliOutput) for the CLI wrapper module (src/cli.py).

AC-001: tests/unit/test_cli.py exists with TestCliParser and TestCliOutput classes
AC-002: Parser tests cover all 6 subcommands
AC-003: Parser tests verify default values
AC-004: Parser tests verify flag parsing
AC-005: Output tests verify ping returns valid JSON with status=healthy and mode=cli
AC-006: Output tests verify error results produce exit code 1
AC-007: Output tests verify list-focus-areas returns all presets
AC-008: All tests pass with pytest tests/unit/test_cli.py -v
"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import AsyncMock, patch

import pytest

from src.cli import main, make_parser


class TestCliParser:
    """Tests for CLI argument parsing.

    Covers all 6 subcommands, default values for optional arguments,
    and flag parsing for --language, --no-segments, --focus, --video-id,
    and --max-insights.
    """

    # ------------------------------------------------------------------
    # AC-002: Parser tests cover all 6 subcommands
    # ------------------------------------------------------------------

    def test_ping_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["ping"])
        assert args.command == "ping"

    def test_video_info_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["video-info", "https://youtu.be/dQw4w9WgXcQ"])
        assert args.command == "video-info"
        assert args.video_url == "https://youtu.be/dQw4w9WgXcQ"

    def test_get_transcript_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ"])
        assert args.command == "get-transcript"
        assert args.video_url == "dQw4w9WgXcQ"

    def test_list_transcripts_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["list-transcripts", "dQw4w9WgXcQ"])
        assert args.command == "list-transcripts"
        assert args.video_url == "dQw4w9WgXcQ"

    def test_extract_insights_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "some transcript text"])
        assert args.command == "extract-insights"
        assert args.transcript == "some transcript text"

    def test_list_focus_areas_subcommand(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["list-focus-areas"])
        assert args.command == "list-focus-areas"

    # ------------------------------------------------------------------
    # AC-003: Parser tests verify default values
    # ------------------------------------------------------------------

    def test_get_transcript_default_language(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ"])
        assert args.language == "en"

    def test_get_transcript_default_no_segments(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ"])
        assert args.no_segments is False

    def test_extract_insights_default_focus_areas(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text"])
        assert args.focus_areas == "general"

    def test_extract_insights_default_max_insights(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text"])
        assert args.max_insights == 10

    # ------------------------------------------------------------------
    # AC-004: Parser tests verify flag parsing
    # ------------------------------------------------------------------

    def test_language_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ", "--language", "fr"])
        assert args.language == "fr"

    def test_no_segments_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["get-transcript", "dQw4w9WgXcQ", "--no-segments"])
        assert args.no_segments is True

    def test_focus_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--focus", "youtube-channel"])
        assert args.focus_areas == "youtube-channel"

    def test_focus_flag_multiple_comma_separated(self) -> None:
        parser = make_parser()
        args = parser.parse_args(
            ["extract-insights", "text", "--focus", "entrepreneurial,investment"]
        )
        assert args.focus_areas == "entrepreneurial,investment"

    def test_video_id_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(
            ["extract-insights", "text", "--video-id", "dQw4w9WgXcQ"]
        )
        assert args.video_id == "dQw4w9WgXcQ"

    def test_video_id_flag_default_empty(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text"])
        assert args.video_id == ""

    def test_max_insights_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--max-insights", "5"])
        assert args.max_insights == 5

    def test_max_insights_flag_is_int(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--max-insights", "20"])
        assert isinstance(args.max_insights, int)
        assert args.max_insights == 20


class TestCliOutput:
    """Tests for CLI JSON output format and exit codes.

    Validates that commands produce valid JSON on stdout and return
    appropriate exit codes (0 for success, 1 for errors).
    """

    # ------------------------------------------------------------------
    # AC-005: Output tests verify ping returns valid JSON
    #         with status=healthy and mode=cli
    # ------------------------------------------------------------------

    def test_ping_returns_valid_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        exit_code = main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert isinstance(data, dict)

    def test_ping_status_healthy(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "healthy"

    def test_ping_mode_cli(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["mode"] == "cli"

    def test_ping_exit_code_zero(self) -> None:
        exit_code = main(["ping"])
        assert exit_code == 0

    def test_ping_includes_server_metadata(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["server"] == "youtube-transcript-mcp"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data

    # ------------------------------------------------------------------
    # AC-006: Output tests verify error results produce exit code 1
    # ------------------------------------------------------------------

    def test_error_result_produces_exit_code_1(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["video-info", "not-a-valid-url-at-all"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "error" in data
        assert exit_code == 1

    def test_error_result_has_error_structure(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["video-info", "not-a-valid-url-at-all"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "INVALID_URL"

    def test_get_transcript_invalid_url_exit_code_1(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["get-transcript", "not-a-valid-url-at-all"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 1
        assert "error" in data

    def test_list_transcripts_invalid_url_exit_code_1(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["list-transcripts", "not-valid"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 1
        assert data["error"]["code"] == "INVALID_URL"

    # ------------------------------------------------------------------
    # AC-007: Output tests verify list-focus-areas returns all presets
    # ------------------------------------------------------------------

    def test_list_focus_areas_returns_all_presets(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        expected_presets = [
            "general",
            "entrepreneurial",
            "investment",
            "technical",
            "youtube-channel",
            "ai-learning",
        ]
        for preset in expected_presets:
            assert preset in data["focus_areas"], f"Missing preset: {preset}"

    def test_list_focus_areas_returns_valid_json(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "focus_areas" in data
        assert "category_definitions" in data
        assert "usage_tip" in data

    def test_list_focus_areas_presets_contain_categories(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        # Each preset should have a non-empty list of categories
        for preset_name, categories in data["focus_areas"].items():
            assert isinstance(categories, list), f"{preset_name} is not a list"
            assert len(categories) > 0, f"{preset_name} has no categories"

    def test_list_focus_areas_exit_code_zero(self) -> None:
        exit_code = main(["list-focus-areas"])
        assert exit_code == 0

    # ------------------------------------------------------------------
    # Additional output format tests for completeness
    # ------------------------------------------------------------------

    def test_extract_insights_returns_valid_json(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        text = "A" * 200
        exit_code = main(["extract-insights", text, "--focus", "general"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        assert "extraction_prompt" in data
        assert data["focus_areas"] == ["general"]

    def test_get_transcript_success_with_mock(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify get-transcript outputs valid JSON via mocked TranscriptClient."""
        from src.services.transcript_client import TranscriptResult, TranscriptSegment

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=False,
            segments=[TranscriptSegment(start=0.0, duration=5.0, text="Hello world")],
            full_text="Hello world",
            total_segments=1,
            total_duration_seconds=5.0,
        )
        with patch("src.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(return_value=mock_result)
            exit_code = main(["get-transcript", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["full_text"] == "Hello world"
        assert "segments" in data

    def test_stdout_is_pure_json_no_extra_output(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verify stdout contains only JSON, no logging text."""
        main(["ping"])
        captured = capsys.readouterr()
        # The entire stdout should parse as a single JSON object
        stripped = captured.out.strip()
        assert stripped.startswith("{")
        assert stripped.endswith("}")
        json.loads(stripped)  # no ValueError means valid JSON
