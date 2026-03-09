"""Tests for extract_insights and list_focus_areas MCP tools.

TDD RED phase: Tests define expected behavior for the two MCP tools
registered in src/__main__.py. Covers parameter handling, validation,
structured error responses, and successful extraction preparation.
"""

from __future__ import annotations

import pytest
from src.models.insight import FOCUS_PRESETS

# --- Seam Tests ---


@pytest.mark.seam
@pytest.mark.integration_contract("extraction_service")
def test_extraction_service_importable() -> None:
    """Verify extraction service functions are importable.

    Contract: prepare_for_extraction and get_focus_categories importable
    from src.services.insight_extractor
    Producer: TASK-INT-002
    """
    from src.services.insight_extractor import (
        get_focus_categories,
        prepare_for_extraction,
    )

    assert callable(prepare_for_extraction)
    assert callable(get_focus_categories)


@pytest.mark.seam
@pytest.mark.integration_contract("insight_models")
def test_focus_presets_importable() -> None:
    """Verify FOCUS_PRESETS importable for tool validation.

    Contract: FOCUS_PRESETS and CATEGORY_DEFINITIONS importable
    from src.models.insight
    Producer: TASK-INT-001
    """
    assert "general" in FOCUS_PRESETS
    assert "youtube-channel" in FOCUS_PRESETS
    assert "ai-learning" in FOCUS_PRESETS


# --- Tests for extract_insights tool ---


class TestExtractInsights:
    """Tests for the extract_insights MCP tool."""

    @pytest.mark.asyncio
    async def test_successful_extraction(self) -> None:
        """Successful call returns extraction metadata dict."""
        from src.__main__ import extract_insights

        transcript = "A" * 200  # Over 100 char minimum
        result = await extract_insights(transcript=transcript)
        assert isinstance(result, dict)
        assert "extraction_prompt" in result
        assert "focus_areas" in result
        assert "categories" in result
        assert "category_definitions" in result
        assert "transcript_length" in result
        assert "chunk_count" in result
        assert "needs_chunking" in result
        assert "max_insights" in result

    @pytest.mark.asyncio
    async def test_default_focus_area_is_general(self) -> None:
        """Default focus_areas parameter should resolve to general."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(transcript=transcript)
        assert "error" not in result
        assert result["focus_areas"] == ["general"]

    @pytest.mark.asyncio
    async def test_multiple_comma_separated_focus_areas(self) -> None:
        """Comma-separated focus areas should be parsed correctly."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            focus_areas="entrepreneurial,investment",
        )
        assert "error" not in result
        assert result["focus_areas"] == ["entrepreneurial", "investment"]
        # Should have categories from both areas
        expected_cats = set(
            cat.value for cat in FOCUS_PRESETS["entrepreneurial"]
        ) | set(cat.value for cat in FOCUS_PRESETS["investment"])
        assert set(result["categories"]) == expected_cats

    @pytest.mark.asyncio
    async def test_focus_areas_with_spaces_trimmed(self) -> None:
        """Focus areas with whitespace should be trimmed."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            focus_areas=" general , technical ",
        )
        assert "error" not in result
        assert result["focus_areas"] == ["general", "technical"]

    @pytest.mark.asyncio
    async def test_invalid_focus_area_returns_structured_error(self) -> None:
        """Invalid focus area should return INVALID_FOCUS_AREA error."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            focus_areas="nonexistent_area",
        )
        assert "error" in result
        assert result["error"]["code"] == "INVALID_FOCUS_AREA"
        assert result["error"]["category"] == "client_error"
        assert "nonexistent_area" in result["error"]["message"]

    @pytest.mark.asyncio
    async def test_transcript_too_short_returns_error(self) -> None:
        """Transcript under 100 chars returns TRANSCRIPT_TOO_SHORT error."""
        from src.__main__ import extract_insights

        result = await extract_insights(transcript="Too short")
        assert "error" in result
        assert result["error"]["code"] == "TRANSCRIPT_TOO_SHORT"
        assert result["error"]["category"] == "client_error"

    @pytest.mark.asyncio
    async def test_transcript_exactly_100_chars_passes(self) -> None:
        """Transcript of exactly 100 chars should pass validation."""
        from src.__main__ import extract_insights

        transcript = "A" * 100
        result = await extract_insights(transcript=transcript)
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_transcript_99_chars_fails(self) -> None:
        """Transcript of 99 chars should fail validation."""
        from src.__main__ import extract_insights

        transcript = "A" * 99
        result = await extract_insights(transcript=transcript)
        assert "error" in result
        assert result["error"]["code"] == "TRANSCRIPT_TOO_SHORT"

    @pytest.mark.asyncio
    async def test_max_insights_string_conversion(self) -> None:
        """max_insights arrives as string, must be converted to int."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            max_insights="5",
        )
        assert "error" not in result
        assert result["max_insights"] == 5

    @pytest.mark.asyncio
    async def test_default_max_insights_is_10(self) -> None:
        """Default max_insights should be 10."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(transcript=transcript)
        assert result["max_insights"] == 10

    @pytest.mark.asyncio
    async def test_video_id_passed_through(self) -> None:
        """video_id should be passed to extraction result."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            video_id="vid123",
        )
        assert "error" not in result
        assert result["video_id"] == "vid123"

    @pytest.mark.asyncio
    async def test_empty_video_id_becomes_none(self) -> None:
        """Empty string video_id should become None in result."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(transcript=transcript, video_id="")
        assert result["video_id"] is None

    @pytest.mark.asyncio
    async def test_all_focus_area(self) -> None:
        """'all' focus area should be accepted and return all categories."""
        from src.__main__ import extract_insights

        transcript = "A" * 200
        result = await extract_insights(
            transcript=transcript,
            focus_areas="all",
        )
        assert "error" not in result
        assert len(result["categories"]) == 24

    @pytest.mark.asyncio
    async def test_has_comprehensive_docstring(self) -> None:
        """Tool should have a comprehensive docstring for discovery."""
        from src.__main__ import extract_insights

        assert extract_insights.__doc__ is not None
        docstring = extract_insights.__doc__
        # Should mention key concepts
        assert "transcript" in docstring.lower()
        assert "focus" in docstring.lower()
        assert "insight" in docstring.lower()

    @pytest.mark.asyncio
    async def test_error_response_structure(self) -> None:
        """Error responses follow {error: {category, code, message}} pattern."""
        from src.__main__ import extract_insights

        result = await extract_insights(transcript="short")
        assert "error" in result
        error = result["error"]
        assert "category" in error
        assert "code" in error
        assert "message" in error


# --- Tests for list_focus_areas tool ---


class TestListFocusAreas:
    """Tests for the list_focus_areas MCP tool."""

    @pytest.mark.asyncio
    async def test_returns_dict(self) -> None:
        """list_focus_areas should return a dict."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_contains_all_six_presets(self) -> None:
        """Result should contain all 6 focus area presets."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        assert "focus_areas" in result
        expected = {"general", "entrepreneurial", "investment",
                    "technical", "youtube-channel", "ai-learning"}
        assert set(result["focus_areas"].keys()) == expected

    @pytest.mark.asyncio
    async def test_each_preset_has_categories(self) -> None:
        """Each preset should have a list of category strings."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        for name, categories in result["focus_areas"].items():
            assert isinstance(categories, list), f"{name} categories not a list"
            assert len(categories) == 4, f"{name} should have 4 categories, got {len(categories)}"
            for cat in categories:
                assert isinstance(cat, str), f"Category in {name} not a string"

    @pytest.mark.asyncio
    async def test_contains_category_definitions(self) -> None:
        """Result should contain category definitions."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        assert "category_definitions" in result
        # Should have all 24 definitions
        assert len(result["category_definitions"]) == 24

    @pytest.mark.asyncio
    async def test_category_definitions_are_descriptive(self) -> None:
        """Category definitions should be non-empty strings."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        for cat, desc in result["category_definitions"].items():
            assert isinstance(cat, str)
            assert isinstance(desc, str)
            assert len(desc) > 10, f"Definition for {cat} too short: {desc}"

    @pytest.mark.asyncio
    async def test_has_comprehensive_docstring(self) -> None:
        """Tool should have a comprehensive docstring for discovery."""
        from src.__main__ import list_focus_areas

        assert list_focus_areas.__doc__ is not None
        docstring = list_focus_areas.__doc__
        assert "focus" in docstring.lower()

    @pytest.mark.asyncio
    async def test_contains_usage_tip(self) -> None:
        """Result should contain a usage tip."""
        from src.__main__ import list_focus_areas

        result = await list_focus_areas()
        assert "usage_tip" in result
        assert isinstance(result["usage_tip"], str)


# --- Tests for tool registration ---


class TestToolRegistration:
    """Tests verifying tools are properly registered at module level."""

    def test_extract_insights_is_registered(self) -> None:
        """extract_insights should be importable from __main__."""
        from src.__main__ import extract_insights

        assert callable(extract_insights)

    def test_list_focus_areas_is_registered(self) -> None:
        """list_focus_areas should be importable from __main__."""
        from src.__main__ import list_focus_areas

        assert callable(list_focus_areas)

    def test_mcp_server_exists(self) -> None:
        """FastMCP server instance should exist."""
        from src.__main__ import mcp

        assert mcp is not None
