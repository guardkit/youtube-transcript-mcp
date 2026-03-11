"""Tests for insight extraction service.

TDD RED phase: Tests define expected behavior for
youtube_insights_mcp/services/insight_extractor.py including focus area resolution,
prompt building, transcript chunking, and extraction preparation.
"""

from __future__ import annotations

import pytest

from youtube_insights_mcp.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
    InsightCategory,
)

# --- Seam Test: verify insight_models contract from TASK-INT-001 ---


@pytest.mark.seam
def test_insight_models_importable() -> None:
    """Verify insight models are importable from youtube_insights_mcp.models.insight.

    Contract: All models must be importable from youtube_insights_mcp.models.insight
    Producer: TASK-INT-001
    """
    from youtube_insights_mcp.models.insight import (
        FOCUS_PRESETS,
        FocusArea,
        InsightCategory,
    )

    assert len(FocusArea) == 6, f"Expected 6 FocusArea values, got {len(FocusArea)}"
    cat_count = len(InsightCategory)
    assert cat_count == 24, f"Expected 24 InsightCategory values, got {cat_count}"
    assert len(FOCUS_PRESETS) == 6, f"Expected 6 presets, got {len(FOCUS_PRESETS)}"
    def_count = len(CATEGORY_DEFINITIONS)
    assert def_count == 24, f"Expected 24 definitions, got {def_count}"


# --- Tests for get_focus_categories ---


class TestGetFocusCategories:
    """Tests for get_focus_categories function."""

    def test_all_keyword_returns_all_categories(self) -> None:
        """'all' keyword should return all 24 InsightCategory values."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["all"])
        assert len(result) == 24
        for cat in InsightCategory:
            assert cat in result

    def test_single_known_focus_area(self) -> None:
        """Single known focus area returns its 4 categories."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["general"])
        assert len(result) == 4
        for cat in FOCUS_PRESETS["general"]:
            assert cat in result

    def test_multiple_focus_areas(self) -> None:
        """Multiple focus areas returns union of categories."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["general", "technical"])
        expected = set(FOCUS_PRESETS["general"]) | set(FOCUS_PRESETS["technical"])
        assert set(result) == expected

    def test_unknown_focus_area_falls_back_to_general(self) -> None:
        """Unknown focus areas should fall back to 'general' preset."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["nonexistent_area"])
        expected = FOCUS_PRESETS["general"]
        assert set(result) == set(expected)

    def test_deduplication_when_same_area_specified_twice(self) -> None:
        """Same area twice should not produce duplicate categories."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["general", "general"])
        assert len(result) == len(set(result)), "Duplicate categories found"
        assert len(result) == 4

    def test_case_insensitive_matching(self) -> None:
        """Focus area matching should be case insensitive."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["General"])
        assert set(result) == set(FOCUS_PRESETS["general"])

    def test_all_with_other_areas(self) -> None:
        """'all' combined with other areas should still return all."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["all", "general"])
        assert len(result) == 24

    def test_returns_list_of_insight_category(self) -> None:
        """Return type should be list of InsightCategory."""
        from youtube_insights_mcp.services.insight_extractor import get_focus_categories

        result = get_focus_categories(["general"])
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, InsightCategory)


# --- Tests for build_extraction_prompt ---


class TestBuildExtractionPrompt:
    """Tests for build_extraction_prompt function."""

    def test_returns_string(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Sample transcript", ["general"])
        assert isinstance(result, str)

    def test_includes_transcript(self) -> None:
        """Prompt should include the transcript text."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        transcript = "This is my unique transcript text."
        result = build_extraction_prompt(transcript, ["general"])
        assert transcript in result

    def test_includes_category_descriptions(self) -> None:
        """Prompt should include category descriptions for focus areas."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Some transcript", ["general"])
        # Check that general category descriptions are present
        assert "key_point" in result
        assert "action_item" in result

    def test_includes_max_insights(self) -> None:
        """Prompt should include maximum insights count."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Transcript", ["general"], max_insights=5)
        assert "5" in result

    def test_default_max_insights_is_10(self) -> None:
        """Default max_insights should be 10."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Transcript", ["general"])
        assert "10" in result

    def test_includes_output_format_instructions(self) -> None:
        """Prompt should include output format instructions."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Transcript", ["general"])
        assert "category" in result.lower()
        assert "title" in result.lower()
        assert "summary" in result.lower()
        assert "confidence" in result.lower()

    def test_includes_guidelines(self) -> None:
        """Prompt should include extraction guidelines."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Transcript", ["general"])
        assert "actionable" in result.lower()

    def test_includes_json_response_format(self) -> None:
        """Prompt should instruct JSON response format."""
        from youtube_insights_mcp.services.insight_extractor import build_extraction_prompt

        result = build_extraction_prompt("Transcript", ["general"])
        assert "json" in result.lower()


# --- Tests for chunk_transcript ---


class TestChunkTranscript:
    """Tests for chunk_transcript function."""

    def test_short_transcript_returns_single_chunk(self) -> None:
        """Transcripts under max_chars should return as single chunk."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        transcript = "Short transcript."
        result = chunk_transcript(transcript, max_chars=30000)
        assert len(result) == 1
        assert result[0] == transcript

    def test_long_transcript_is_split(self) -> None:
        """Transcripts over max_chars should be split into multiple chunks."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        # Create a transcript that's clearly over the limit
        paragraphs = ["Paragraph " + str(i) + ". " * 100 for i in range(50)]
        transcript = "\n\n".join(paragraphs)
        result = chunk_transcript(transcript, max_chars=500)
        assert len(result) > 1

    def test_splits_at_paragraph_boundaries(self) -> None:
        """Chunking should prefer splitting at paragraph boundaries."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        para1 = "A" * 200
        para2 = "B" * 200
        para3 = "C" * 200
        transcript = f"{para1}\n\n{para2}\n\n{para3}"
        # max_chars just large enough for ~2 paragraphs
        result = chunk_transcript(transcript, max_chars=450, overlap_chars=50)
        assert len(result) >= 2

    def test_overlap_between_chunks(self) -> None:
        """Chunks should have overlap for context continuity."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        # Create paragraphs with distinct content
        paragraphs = [f"Unique paragraph {i} content. " * 20 for i in range(20)]
        transcript = "\n\n".join(paragraphs)
        result = chunk_transcript(transcript, max_chars=500, overlap_chars=100)
        if len(result) >= 2:
            # The beginning of chunk 2 should contain text from end of chunk 1
            chunk1_end = result[0][-100:]
            assert chunk1_end in result[1], "No overlap found between consecutive chunks"

    def test_default_max_chars_is_30000(self) -> None:
        """Default max_chars should be 30000."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        transcript = "A" * 29999
        result = chunk_transcript(transcript)
        assert len(result) == 1

    def test_default_overlap_is_500(self) -> None:
        """Default overlap_chars should be 500."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        # Create transcript just over 30000 chars with clear paragraph boundary
        para1 = "First " * 3000  # ~18000 chars
        para2 = "Second " * 3000  # ~21000 chars
        transcript = f"{para1}\n\n{para2}"
        result = chunk_transcript(transcript)
        if len(result) >= 2:
            # Overlap should be 500 chars from end of previous chunk
            chunk1_tail = result[0][-500:]
            assert chunk1_tail in result[1]

    def test_handles_single_very_long_paragraph(self) -> None:
        """Should handle a paragraph that exceeds max_chars by splitting it."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        # Single paragraph with no \n\n breaks
        transcript = "Word " * 10000  # ~50000 chars
        result = chunk_transcript(transcript, max_chars=500, overlap_chars=50)
        assert len(result) > 1
        for chunk in result:
            # Each chunk should not drastically exceed max_chars
            # (small tolerance for overlap additions)
            assert len(chunk) <= 600, f"Chunk too large: {len(chunk)} chars"

    def test_returns_list_of_strings(self) -> None:
        """Return type should be list of strings."""
        from youtube_insights_mcp.services.insight_extractor import chunk_transcript

        result = chunk_transcript("Test")
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)


# --- Tests for prepare_for_extraction ---


class TestPrepareForExtraction:
    """Tests for prepare_for_extraction function."""

    def test_returns_dict(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Transcript text")
        assert isinstance(result, dict)

    def test_contains_all_required_keys(self) -> None:
        """Result must contain all required keys."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Transcript text", video_id="abc123")
        required_keys = [
            "extraction_prompt",
            "focus_areas",
            "categories",
            "category_definitions",
            "transcript_length",
            "chunk_count",
            "needs_chunking",
            "max_insights",
            "chunks",
        ]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_video_id_passed_through(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text", video_id="vid123")
        assert result["video_id"] == "vid123"

    def test_default_focus_areas_is_general(self) -> None:
        """Default focus_areas should be ['general']."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text")
        assert result["focus_areas"] == ["general"]

    def test_categories_are_string_values(self) -> None:
        """Categories in result should be string values (not enum)."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text")
        for cat in result["categories"]:
            assert isinstance(cat, str)

    def test_category_definitions_are_strings(self) -> None:
        """Category definitions should map string keys to string descriptions."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text")
        for key, value in result["category_definitions"].items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_transcript_length_is_correct(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        text = "Hello world"
        result = prepare_for_extraction(text)
        assert result["transcript_length"] == len(text)

    def test_short_transcript_not_chunked(self) -> None:
        """Short transcripts should not be chunked."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Short text")
        assert result["needs_chunking"] is False
        assert result["chunk_count"] == 1
        assert result["chunks"] is None

    def test_long_transcript_is_chunked(self) -> None:
        """Long transcripts should be chunked."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        long_text = "Paragraph. " * 5000  # ~55000 chars
        result = prepare_for_extraction(long_text)
        assert result["needs_chunking"] is True
        assert result["chunk_count"] > 1
        assert result["chunks"] is not None
        assert isinstance(result["chunks"], list)

    def test_extraction_prompt_is_string(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Some transcript")
        assert isinstance(result["extraction_prompt"], str)
        assert len(result["extraction_prompt"]) > 0

    def test_max_insights_default_is_10(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text")
        assert result["max_insights"] == 10

    def test_max_insights_custom(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text", max_insights=5)
        assert result["max_insights"] == 5

    def test_custom_focus_areas(self) -> None:
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        result = prepare_for_extraction("Text", focus_areas=["technical", "investment"])
        assert result["focus_areas"] == ["technical", "investment"]
        # Should have categories from both areas
        expected_cats = set(
            cat.value for cat in FOCUS_PRESETS["technical"]
        ) | set(
            cat.value for cat in FOCUS_PRESETS["investment"]
        )
        assert set(result["categories"]) == expected_cats

    def test_chunked_prompt_uses_first_chunk(self) -> None:
        """When chunking is needed, extraction_prompt should use the first chunk."""
        from youtube_insights_mcp.services.insight_extractor import prepare_for_extraction

        # Build a long transcript with identifiable first paragraph
        first_para = "FIRST_PARAGRAPH_MARKER " * 100
        rest = ("Other content. " * 300 + "\n\n") * 10
        long_text = first_para + "\n\n" + rest
        result = prepare_for_extraction(long_text)
        if result["needs_chunking"]:
            assert "FIRST_PARAGRAPH_MARKER" in result["extraction_prompt"]
