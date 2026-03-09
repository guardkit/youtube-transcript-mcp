"""Tests for get_video_info MCP tool registration (TASK-VID-003).

TDD tests covering all acceptance criteria:
- AC-001: get_video_info registered at module level with @mcp.tool()
- AC-002: Tool accepts video_url: str parameter
- AC-003: Returns dict with all VideoInfo fields on success
- AC-004: Returns structured error on failure
- AC-005: InvalidURLError -> category: client_error, code: INVALID_URL
- AC-006: VideoNotFoundError -> category: client_error, code: VIDEO_NOT_FOUND
- AC-007: Unexpected exceptions -> category: server_error, code: INTERNAL_ERROR
- AC-008: Tool docstring describes accepted URL formats
- AC-009: YouTubeClient instantiated at module level
"""

from __future__ import annotations

import dataclasses
from unittest.mock import AsyncMock, patch

import pytest

from src.services.youtube_client import (
    InvalidURLError,
    VideoInfo,
    VideoNotFoundError,
    YouTubeClient,
)


def _make_video_info(**overrides: object) -> VideoInfo:
    """Create a VideoInfo with sensible defaults for testing."""
    defaults = {
        "video_id": "dQw4w9WgXcQ",
        "title": "Test Video",
        "channel": "Test Channel",
        "channel_id": "@testchannel",
        "duration_seconds": 212,
        "duration_formatted": "3:32",
        "description_snippet": "A test video.",
        "view_count": 1000000,
        "upload_date": "20240101",
        "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg",
        "has_captions": True,
        "has_auto_captions": True,
        "available_languages": ["en", "es"],
    }
    defaults.update(overrides)
    return VideoInfo(**defaults)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Seam Test: verify YouTubeClient contract from TASK-VID-002
# ---------------------------------------------------------------------------
class TestYouTubeClientSeam:
    """Seam test: verify YouTubeClient contract from TASK-VID-002."""

    @pytest.mark.seam
    def test_youtube_client_import(self) -> None:
        """Verify YouTubeClient can be imported from src.services.youtube_client."""
        from src.services.youtube_client import (
            InvalidURLError as InvalidUrlErr,
        )
        from src.services.youtube_client import (
            VideoNotFoundError as VideoNotFoundErr,
        )
        from src.services.youtube_client import (
            YouTubeClient as YtClient,
        )

        assert YtClient is not None, "YouTubeClient must be importable"
        assert issubclass(VideoNotFoundErr, Exception), "VideoNotFoundError must be an Exception"
        assert issubclass(InvalidUrlErr, Exception), "InvalidURLError must be an Exception"


# ---------------------------------------------------------------------------
# AC-001: get_video_info tool registered at module level with @mcp.tool()
# ---------------------------------------------------------------------------
class TestToolRegistration:
    """Verify the tool is registered at module level."""

    def test_main_module_has_get_video_info(self) -> None:
        """get_video_info must be a callable at module level in src.__main__."""
        import src.__main__ as main_mod

        assert hasattr(main_mod, "get_video_info"), (
            "get_video_info must be defined at module level in __main__.py"
        )
        assert callable(main_mod.get_video_info)

    def test_mcp_server_exists(self) -> None:
        """FastMCP instance must exist at module level."""
        import src.__main__ as main_mod

        assert hasattr(main_mod, "mcp"), "mcp FastMCP instance must exist at module level"

    def test_tool_is_registered_on_mcp(self) -> None:
        """get_video_info must be listed in the mcp server's tools."""
        import src.__main__ as main_mod

        # FastMCP stores tools in _tool_manager
        tool_names = list(main_mod.mcp._tool_manager._tools.keys())
        assert "get_video_info" in tool_names, (
            f"get_video_info not in registered tools: {tool_names}"
        )


# ---------------------------------------------------------------------------
# AC-002: Tool accepts video_url: str parameter
# ---------------------------------------------------------------------------
class TestToolSignature:
    """Verify tool accepts the correct parameter."""

    def test_accepts_video_url_param(self) -> None:
        """get_video_info must accept a video_url string parameter."""
        import inspect

        import src.__main__ as main_mod

        sig = inspect.signature(main_mod.get_video_info)
        assert "video_url" in sig.parameters, (
            f"Tool must accept 'video_url' param, got: {list(sig.parameters.keys())}"
        )
        param = sig.parameters["video_url"]
        assert param.annotation is str or param.annotation == "str", (
            f"video_url must be typed as str, got: {param.annotation}"
        )


# ---------------------------------------------------------------------------
# AC-003: Returns dict with all VideoInfo fields on success
# ---------------------------------------------------------------------------
class TestSuccessResponse:
    """Verify tool returns all VideoInfo fields on success."""

    @pytest.mark.asyncio
    async def test_returns_all_video_info_fields(self) -> None:
        """On success, the dict must contain all VideoInfo dataclass fields."""
        import src.__main__ as main_mod

        mock_info = _make_video_info()

        with patch.object(
            main_mod.youtube_client, "get_video_info", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_info
            result = await main_mod.get_video_info("dQw4w9WgXcQ")

        assert isinstance(result, dict)

        # All VideoInfo fields must be present
        for field in dataclasses.fields(VideoInfo):
            assert field.name in result, f"Missing field in response: {field.name}"

        assert result["video_id"] == "dQw4w9WgXcQ"
        assert result["title"] == "Test Video"
        assert result["channel"] == "Test Channel"
        assert result["has_captions"] is True
        assert result["available_languages"] == ["en", "es"]

    @pytest.mark.asyncio
    async def test_success_no_error_key(self) -> None:
        """On success, response must not contain 'error' key."""
        import src.__main__ as main_mod

        mock_info = _make_video_info()

        with patch.object(
            main_mod.youtube_client, "get_video_info", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_info
            result = await main_mod.get_video_info("dQw4w9WgXcQ")

        assert "error" not in result


# ---------------------------------------------------------------------------
# AC-004 + AC-005: InvalidURLError -> client_error / INVALID_URL
# ---------------------------------------------------------------------------
class TestInvalidURLErrorHandling:
    """Verify InvalidURLError is mapped to structured client_error."""

    @pytest.mark.asyncio
    async def test_invalid_url_returns_structured_error(self) -> None:
        """InvalidURLError must produce category=client_error, code=INVALID_URL."""
        import src.__main__ as main_mod

        with patch.object(
            main_mod.youtube_client,
            "get_video_info",
            new_callable=AsyncMock,
            side_effect=InvalidURLError("Bad URL"),
        ):
            result = await main_mod.get_video_info("not-valid")

        assert "error" in result
        err = result["error"]
        assert err["category"] == "client_error"
        assert err["code"] == "INVALID_URL"
        assert "Bad URL" in err["message"]


# ---------------------------------------------------------------------------
# AC-006: VideoNotFoundError -> client_error / VIDEO_NOT_FOUND
# ---------------------------------------------------------------------------
class TestVideoNotFoundErrorHandling:
    """Verify VideoNotFoundError is mapped to structured client_error."""

    @pytest.mark.asyncio
    async def test_video_not_found_returns_structured_error(self) -> None:
        """VideoNotFoundError must produce category=client_error, code=VIDEO_NOT_FOUND."""
        import src.__main__ as main_mod

        with patch.object(
            main_mod.youtube_client,
            "get_video_info",
            new_callable=AsyncMock,
            side_effect=VideoNotFoundError("Video unavailable: xxxxxxxxxxx"),
        ):
            result = await main_mod.get_video_info("xxxxxxxxxxx")

        assert "error" in result
        err = result["error"]
        assert err["category"] == "client_error"
        assert err["code"] == "VIDEO_NOT_FOUND"
        assert "Video unavailable" in err["message"]


# ---------------------------------------------------------------------------
# AC-007: Unexpected exceptions -> server_error / INTERNAL_ERROR
# ---------------------------------------------------------------------------
class TestUnexpectedExceptionHandling:
    """Verify unexpected exceptions are mapped to server_error."""

    @pytest.mark.asyncio
    async def test_unexpected_error_returns_server_error(self) -> None:
        """Generic exceptions must produce category=server_error, code=INTERNAL_ERROR."""
        import src.__main__ as main_mod

        with patch.object(
            main_mod.youtube_client,
            "get_video_info",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Something broke"),
        ):
            result = await main_mod.get_video_info("dQw4w9WgXcQ")

        assert "error" in result
        err = result["error"]
        assert err["category"] == "server_error"
        assert err["code"] == "INTERNAL_ERROR"
        assert isinstance(err["message"], str)

    @pytest.mark.asyncio
    async def test_unexpected_error_logs_exception(self) -> None:
        """Unexpected exceptions must be logged with logger.exception()."""
        import src.__main__ as main_mod

        with patch.object(
            main_mod.youtube_client,
            "get_video_info",
            new_callable=AsyncMock,
            side_effect=RuntimeError("Something broke"),
        ):
            with patch.object(main_mod.logger, "exception") as mock_log:
                await main_mod.get_video_info("dQw4w9WgXcQ")
                mock_log.assert_called_once()


# ---------------------------------------------------------------------------
# AC-008: Tool docstring describes accepted URL formats
# ---------------------------------------------------------------------------
class TestToolDocstring:
    """Verify tool has a descriptive docstring for LLM discovery."""

    def test_has_docstring(self) -> None:
        """get_video_info must have a non-empty docstring."""
        import src.__main__ as main_mod

        doc = main_mod.get_video_info.__doc__
        assert doc is not None, "Tool must have a docstring"
        assert len(doc.strip()) > 0

    def test_docstring_mentions_url_formats(self) -> None:
        """Docstring must describe accepted URL formats."""
        import src.__main__ as main_mod

        doc = main_mod.get_video_info.__doc__
        assert doc is not None
        doc_lower = doc.lower()
        # Must mention at least the key URL patterns
        assert "youtube" in doc_lower
        assert "video_id" in doc_lower or "video id" in doc_lower
        assert "youtu.be" in doc_lower or "youtu.be" in doc


# ---------------------------------------------------------------------------
# AC-009: YouTubeClient instantiated at module level
# ---------------------------------------------------------------------------
class TestModuleLevelClient:
    """Verify YouTubeClient is instantiated at module level."""

    def test_youtube_client_at_module_level(self) -> None:
        """youtube_client must be a YouTubeClient instance at module level."""
        import src.__main__ as main_mod

        assert hasattr(main_mod, "youtube_client"), (
            "youtube_client must be defined at module level"
        )
        assert isinstance(main_mod.youtube_client, YouTubeClient), (
            f"youtube_client must be a YouTubeClient instance, got: {type(main_mod.youtube_client)}"
        )
