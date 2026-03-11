"""Unit tests for CLI parser, output format, and command dispatch.

Covers argument parsing (TestCliParser), JSON output/exit codes
(TestCliOutput), and command dispatch with mocking (TestCommandDispatch)
for the CLI wrapper module (youtube_insights_mcp/cli.py).

Consolidated from tests/test_cli.py and tests/unit/test_cli.py.
"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import AsyncMock, patch

import pytest

from youtube_insights_mcp.cli import (
    exit_code_from_result,
    main,
    make_parser,
    output_json,
    run_command,
)

# ---------------------------------------------------------------------------
# AC-001: Functions exist and are callable
# ---------------------------------------------------------------------------


class TestFunctionsExist:
    """Verify all required public functions are importable."""

    def test_make_parser_is_callable(self) -> None:
        assert callable(make_parser)

    def test_output_json_is_callable(self) -> None:
        assert callable(output_json)

    def test_exit_code_from_result_is_callable(self) -> None:
        assert callable(exit_code_from_result)

    def test_run_command_is_callable(self) -> None:
        assert callable(run_command)

    def test_main_is_callable(self) -> None:
        assert callable(main)


# ---------------------------------------------------------------------------
# AC-002/003/004: Parser tests cover all 6 subcommands, defaults, and flags
# ---------------------------------------------------------------------------


class TestCliParser:
    """Tests for CLI argument parsing.

    Covers all 6 subcommands, default values for optional arguments,
    and flag parsing for --language, --no-segments, --focus, --video-id,
    and --max-insights.
    """

    # Subcommand registration

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

    @pytest.mark.parametrize(
        "command",
        [
            "ping", "video-info", "get-transcript",
            "list-transcripts", "extract-insights", "list-focus-areas",
        ],
    )
    def test_subcommand_registered(self, command: str) -> None:
        """Each required subcommand should be parseable without error."""
        parser = make_parser()
        if command == "ping":
            args = parser.parse_args([command])
        elif command in ("video-info", "get-transcript", "list-transcripts"):
            args = parser.parse_args([command, "dQw4w9WgXcQ"])
        elif command == "extract-insights":
            args = parser.parse_args([command, "some text"])
        elif command == "list-focus-areas":
            args = parser.parse_args([command])
        else:
            pytest.fail(f"Unhandled command: {command}")
        assert args.command == command

    # Default values

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

    def test_extract_insights_default_video_id(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text"])
        assert args.video_id == ""

    # Flag parsing

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

    def test_max_insights_flag(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--max-insights", "5"])
        assert args.max_insights == 5

    def test_max_insights_flag_is_int(self) -> None:
        parser = make_parser()
        args = parser.parse_args(["extract-insights", "text", "--max-insights", "20"])
        assert isinstance(args.max_insights, int)
        assert args.max_insights == 20


# ---------------------------------------------------------------------------
# AC-003: output_json produces valid JSON
# ---------------------------------------------------------------------------


class TestOutputJson:
    """Test output_json writes valid JSON to stdout."""

    def test_output_json_produces_valid_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        data = {"status": "ok", "value": 42}
        output_json(data)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed == data

    def test_output_json_handles_unicode(self, capsys: pytest.CaptureFixture[str]) -> None:
        data = {"text": "Hello \u00e9\u00e8\u00ea"}
        output_json(data)
        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert parsed["text"] == "Hello \u00e9\u00e8\u00ea"


# ---------------------------------------------------------------------------
# AC-005/006/007: CLI output tests
# ---------------------------------------------------------------------------


class TestCliOutput:
    """Tests for CLI JSON output format and exit codes."""

    # Ping command

    def test_ping_returns_valid_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        main(["ping"])
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
        assert data["server"] == "youtube-insights-mcp"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data

    def test_ping_stdout_is_pure_json(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Ping command should produce only JSON on stdout, nothing else."""
        main(["ping"])
        captured = capsys.readouterr()
        stripped = captured.out.strip()
        assert stripped.startswith("{")
        assert stripped.endswith("}")
        json.loads(stripped)

    # Error exit codes

    def test_success_result_gives_zero(self) -> None:
        assert exit_code_from_result({"status": "ok"}) == 0

    def test_error_result_gives_one(self) -> None:
        assert exit_code_from_result({"error": {"message": "bad"}}) == 1

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
        main(["video-info", "not-a-valid-url-at-all"])
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

    # list-focus-areas

    def test_list_focus_areas_returns_all_presets(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        exit_code = main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert exit_code == 0
        expected_presets = [
            "general", "entrepreneurial", "investment",
            "technical", "youtube-channel", "ai-learning",
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
        for preset_name, categories in data["focus_areas"].items():
            assert isinstance(categories, list), f"{preset_name} is not a list"
            assert len(categories) > 0, f"{preset_name} has no categories"

    def test_list_focus_areas_exit_code_zero(self) -> None:
        exit_code = main(["list-focus-areas"])
        assert exit_code == 0

    # extract-insights output

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


# ---------------------------------------------------------------------------
# AC-005: --help works on all subcommands
# ---------------------------------------------------------------------------


class TestHelp:
    """Test --help works for main parser and all subcommands."""

    @pytest.mark.parametrize(
        "argv",
        [
            ["--help"],
            ["ping", "--help"],
            ["video-info", "--help"],
            ["get-transcript", "--help"],
            ["list-transcripts", "--help"],
            ["extract-insights", "--help"],
            ["list-focus-areas", "--help"],
        ],
    )
    def test_help_exits_cleanly(self, argv: list[str]) -> None:
        parser = make_parser()
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(argv)
        assert exc_info.value.code == 0


# ---------------------------------------------------------------------------
# AC-007: extract-insights supports `-` for stdin input
# ---------------------------------------------------------------------------


class TestStdinPipeSupport:
    """Test that extract-insights reads from stdin when `-` is passed."""

    def test_extract_insights_reads_stdin(
        self, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        fake_transcript = "A" * 200
        monkeypatch.setattr("sys.stdin", StringIO(fake_transcript))

        code = main(["extract-insights", "-", "--focus", "general"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert data.get("transcript_length") == 200


# ---------------------------------------------------------------------------
# AC-010: Async command dispatch via asyncio.run()
# ---------------------------------------------------------------------------


class TestAsyncDispatch:
    """Test that run_command is async and main uses asyncio.run()."""

    def test_run_command_is_coroutine_function(self) -> None:
        import inspect

        assert inspect.iscoroutinefunction(run_command)

    def test_main_dispatches_via_asyncio_run(self, capsys: pytest.CaptureFixture[str]) -> None:
        """main() should successfully execute async run_command via asyncio.run()."""
        code = main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "healthy"
        assert data["mode"] == "cli"
        assert code == 0


# ---------------------------------------------------------------------------
# Command dispatch tests (with mocking for service calls)
# ---------------------------------------------------------------------------


class TestCommandDispatch:
    """Test command dispatch with mocked services for full coverage."""

    def test_ping_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["ping"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert data["status"] == "healthy"
        assert data["server"] == "youtube-insights-mcp"
        assert data["version"] == "0.1.0"
        assert "timestamp" in data
        assert data["mode"] == "cli"
        assert code == 0

    def test_list_focus_areas_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["list-focus-areas"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "focus_areas" in data
        assert "category_definitions" in data
        assert "usage_tip" in data
        assert "youtube-channel" in data["focus_areas"]
        assert "ai-learning" in data["focus_areas"]
        assert "entrepreneurial" in data["focus_areas"]
        assert "general" in data["focus_areas"]
        assert "investment" in data["focus_areas"]
        assert "technical" in data["focus_areas"]
        assert code == 0

    def test_extract_insights_with_text(self, capsys: pytest.CaptureFixture[str]) -> None:
        text = "A" * 200
        code = main(["extract-insights", text, "--focus", "general", "--max-insights", "5"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert "extraction_prompt" in data
        assert data["max_insights"] == 5
        assert data["focus_areas"] == ["general"]

    def test_invalid_url_returns_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        code = main(["video-info", "not-a-valid-url-at-all"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 1
        assert "error" in data
        assert data["error"]["code"] == "INVALID_URL"

    def test_get_transcript_success_with_segments(self, capsys: pytest.CaptureFixture[str]) -> None:
        from youtube_insights_mcp.services.transcript_client import (
            TranscriptResult,
            TranscriptSegment,
        )

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
        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(return_value=mock_result)
            code = main(["get-transcript", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["full_text"] == "Hello world"
        assert "segments" in data
        assert len(data["segments"]) == 1

    def test_get_transcript_no_segments_flag(self, capsys: pytest.CaptureFixture[str]) -> None:
        from youtube_insights_mcp.services.transcript_client import (
            TranscriptResult,
            TranscriptSegment,
        )

        mock_result = TranscriptResult(
            video_id="dQw4w9WgXcQ",
            language="English",
            language_code="en",
            is_auto_generated=True,
            segments=[TranscriptSegment(start=0.0, duration=5.0, text="Hello")],
            full_text="Hello",
            total_segments=1,
            total_duration_seconds=5.0,
        )
        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(return_value=mock_result)
            code = main(["get-transcript", "dQw4w9WgXcQ", "--no-segments"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert "segments" not in data
        assert data["is_auto_generated"] is True

    def test_get_transcript_transcripts_disabled(self, capsys: pytest.CaptureFixture[str]) -> None:
        from youtube_insights_mcp.services.transcript_client import TranscriptsDisabledError

        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(
                side_effect=TranscriptsDisabledError("Transcripts disabled")
            )
            code = main(["get-transcript", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 1
        assert data["error"]["code"] == "TRANSCRIPTS_DISABLED"

    def test_get_transcript_no_transcript_found(self, capsys: pytest.CaptureFixture[str]) -> None:
        from youtube_insights_mcp.services.transcript_client import NoTranscriptFoundError

        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(
                side_effect=NoTranscriptFoundError("Not found", available_languages=["es", "fr"])
            )
            code = main(["get-transcript", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 1
        assert data["error"]["code"] == "NO_TRANSCRIPT_FOUND"
        assert data["error"]["available_languages"] == ["es", "fr"]

    def test_get_transcript_video_unavailable(self, capsys: pytest.CaptureFixture[str]) -> None:
        from youtube_insights_mcp.services.transcript_client import VideoUnavailableError

        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.get_transcript = AsyncMock(
                side_effect=VideoUnavailableError("Video unavailable")
            )
            code = main(["get-transcript", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 1
        assert data["error"]["code"] == "VIDEO_UNAVAILABLE"

    def test_list_transcripts_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        mock_transcripts = [
            {"language": "English", "language_code": "en", "is_generated": False},
            {"language": "Spanish", "language_code": "es", "is_generated": True},
        ]
        with patch("youtube_insights_mcp.services.transcript_client.TranscriptClient") as mock_cls:
            instance = mock_cls.return_value
            instance.list_transcripts = AsyncMock(return_value=mock_transcripts)
            code = main(["list-transcripts", "dQw4w9WgXcQ"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["count"] == 2
        assert len(data["transcripts"]) == 2

    def test_extract_insights_with_video_id(self, capsys: pytest.CaptureFixture[str]) -> None:
        text = "B" * 200
        code = main(["extract-insights", text, "--video-id", "dQw4w9WgXcQ"])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert data["video_id"] == "dQw4w9WgXcQ"

    def test_extract_insights_without_video_id(self, capsys: pytest.CaptureFixture[str]) -> None:
        text = "C" * 200
        code = main(["extract-insights", text])
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert code == 0
        assert data["video_id"] is None
