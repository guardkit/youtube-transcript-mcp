"""Comprehensive unit tests for insight extraction models and service.

Tests for src/models/insight.py and src/services/insight_extractor.py covering:
- Focus preset definitions (all 6 presets, all 24 categories)
- get_focus_categories function (single, multiple, all, unknown, deduplication)
- Transcript chunking (short, long, overlap, paragraph boundaries)
- Prompt building (includes transcript, categories, max_insights)
- prepare_for_extraction (required fields, chunking detection, video_id)
- Insight Pydantic model validation (valid, with quote, confidence bounds)
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError
from src.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
    FocusArea,
    Insight,
    InsightCategory,
)
from src.services.insight_extractor import (
    build_extraction_prompt,
    chunk_transcript,
    get_focus_categories,
    prepare_for_extraction,
)

# ---------------------------------------------------------------------------
# TestFocusPresets
# ---------------------------------------------------------------------------


class TestFocusPresets:
    """Tests for focus area presets and category definitions."""

    def test_has_exactly_six_presets(self) -> None:
        """FOCUS_PRESETS should contain exactly 6 focus areas."""
        assert len(FOCUS_PRESETS) == 6

    def test_general_preset_has_correct_categories(self) -> None:
        """General preset should have KEY_POINT, ACTION_ITEM, NOTABLE_QUOTE, CONTEXT."""
        cats = FOCUS_PRESETS["general"]
        assert len(cats) == 4
        assert InsightCategory.KEY_POINT in cats
        assert InsightCategory.ACTION_ITEM in cats
        assert InsightCategory.NOTABLE_QUOTE in cats
        assert InsightCategory.CONTEXT in cats

    def test_entrepreneurial_preset_has_correct_categories(self) -> None:
        """Entrepreneurial preset: BUSINESS_STRATEGY, GROWTH_TACTIC, etc."""
        cats = FOCUS_PRESETS["entrepreneurial"]
        assert len(cats) == 4
        assert InsightCategory.BUSINESS_STRATEGY in cats
        assert InsightCategory.GROWTH_TACTIC in cats
        assert InsightCategory.LESSON_LEARNED in cats
        assert InsightCategory.MISTAKE_TO_AVOID in cats

    def test_investment_preset_has_correct_categories(self) -> None:
        """Investment preset should have MARKET_TREND, OPPORTUNITY, RISK, RECOMMENDATION."""
        cats = FOCUS_PRESETS["investment"]
        assert len(cats) == 4
        assert InsightCategory.MARKET_TREND in cats
        assert InsightCategory.OPPORTUNITY in cats
        assert InsightCategory.RISK in cats
        assert InsightCategory.RECOMMENDATION in cats

    def test_technical_preset_has_correct_categories(self) -> None:
        """Technical preset should have TECHNOLOGY, TOOL, BEST_PRACTICE, PITFALL."""
        cats = FOCUS_PRESETS["technical"]
        assert len(cats) == 4
        assert InsightCategory.TECHNOLOGY in cats
        assert InsightCategory.TOOL in cats
        assert InsightCategory.BEST_PRACTICE in cats
        assert InsightCategory.PITFALL in cats

    def test_youtube_channel_preset_has_correct_categories(self) -> None:
        """YouTube channel preset: CHANNEL_STRATEGY, CONTENT_IDEA, etc."""
        cats = FOCUS_PRESETS["youtube-channel"]
        assert len(cats) == 4
        assert InsightCategory.CHANNEL_STRATEGY in cats
        assert InsightCategory.CONTENT_IDEA in cats
        assert InsightCategory.AUDIENCE_GROWTH in cats
        assert InsightCategory.PRODUCTION_TIP in cats

    def test_ai_learning_preset_has_correct_categories(self) -> None:
        """AI learning preset: AI_CONCEPT, AI_TOOL, MENTAL_MODEL, etc."""
        cats = FOCUS_PRESETS["ai-learning"]
        assert len(cats) == 4
        assert InsightCategory.AI_CONCEPT in cats
        assert InsightCategory.AI_TOOL in cats
        assert InsightCategory.MENTAL_MODEL in cats
        assert InsightCategory.PRACTICAL_APPLICATION in cats

    def test_all_preset_keys_match_focus_area_values(self) -> None:
        """Each FocusArea enum value should have a corresponding FOCUS_PRESETS key."""
        for focus_area in FocusArea:
            assert focus_area.value in FOCUS_PRESETS, (
                f"FocusArea {focus_area.value} missing from FOCUS_PRESETS"
            )

    def test_all_categories_have_definitions(self) -> None:
        """Every InsightCategory must have a definition in CATEGORY_DEFINITIONS."""
        assert len(CATEGORY_DEFINITIONS) == 24
        for category in InsightCategory:
            assert category in CATEGORY_DEFINITIONS, (
                f"InsightCategory {category.value} missing from CATEGORY_DEFINITIONS"
            )
            assert len(CATEGORY_DEFINITIONS[category]) > 10, (
                f"Definition for {category.value} is too short"
            )

    def test_each_preset_has_four_categories(self) -> None:
        """Every preset should contain exactly 4 InsightCategory values."""
        for preset_name, categories in FOCUS_PRESETS.items():
            assert len(categories) == 4, (
                f"Preset '{preset_name}' has {len(categories)} categories, expected 4"
            )
            for cat in categories:
                assert isinstance(cat, InsightCategory), (
                    f"Invalid category {cat} in preset {preset_name}"
                )

    def test_total_unique_categories_across_presets_is_24(self) -> None:
        """All presets combined should cover all 24 categories with no overlaps."""
        all_cats: list[InsightCategory] = []
        for cats in FOCUS_PRESETS.values():
            all_cats.extend(cats)
        assert len(all_cats) == 24, f"Expected 24 total, got {len(all_cats)}"
        assert len(set(all_cats)) == 24, "Duplicate categories across presets"


# ---------------------------------------------------------------------------
# TestGetFocusCategories
# ---------------------------------------------------------------------------


class TestGetFocusCategories:
    """Tests for get_focus_categories function."""

    def test_single_known_focus_area(self) -> None:
        """Single known focus area returns its 4 categories."""
        result = get_focus_categories(["general"])
        assert len(result) == 4
        for cat in FOCUS_PRESETS["general"]:
            assert cat in result

    def test_multiple_focus_areas(self) -> None:
        """Multiple focus areas returns union of categories."""
        result = get_focus_categories(["entrepreneurial", "investment"])
        expected = set(FOCUS_PRESETS["entrepreneurial"]) | set(FOCUS_PRESETS["investment"])
        assert set(result) == expected
        assert len(result) == 8

    def test_all_keyword_returns_all_categories(self) -> None:
        """'all' keyword should return all 24 InsightCategory values."""
        result = get_focus_categories(["all"])
        assert len(result) == 24
        for cat in InsightCategory:
            assert cat in result

    def test_unknown_focus_area_falls_back_to_general(self) -> None:
        """Unknown focus areas should fall back to 'general' preset."""
        result = get_focus_categories(["nonexistent_area"])
        expected = FOCUS_PRESETS["general"]
        assert set(result) == set(expected)
        assert len(result) == 4

    def test_deduplication_when_same_area_specified_twice(self) -> None:
        """Same area twice should not produce duplicate categories."""
        result = get_focus_categories(["general", "general"])
        assert len(result) == len(set(result)), "Duplicate categories found"
        assert len(result) == 4

    def test_case_insensitive_matching(self) -> None:
        """Focus area matching should be case insensitive."""
        result = get_focus_categories(["General"])
        assert set(result) == set(FOCUS_PRESETS["general"])

    def test_all_with_other_areas(self) -> None:
        """'all' combined with other areas should still return all."""
        result = get_focus_categories(["all", "general"])
        assert len(result) == 24

    def test_returns_list_of_insight_category(self) -> None:
        """Return type should be list of InsightCategory."""
        result = get_focus_categories(["general"])
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, InsightCategory)

    def test_mixed_known_and_unknown_areas(self) -> None:
        """Known areas should be resolved, unknown silently skipped."""
        result = get_focus_categories(["technical", "bogus"])
        assert set(result) == set(FOCUS_PRESETS["technical"])


# ---------------------------------------------------------------------------
# TestChunkTranscript
# ---------------------------------------------------------------------------


class TestChunkTranscript:
    """Tests for chunk_transcript function."""

    def test_short_transcript_returns_single_chunk(self) -> None:
        """Transcripts under max_chars should return as single chunk."""
        transcript = "This is a short transcript."
        result = chunk_transcript(transcript, max_chars=30000)
        assert len(result) == 1
        assert result[0] == transcript

    def test_long_transcript_is_split(self) -> None:
        """Transcripts over max_chars should be split into multiple chunks."""
        paragraphs = ["Paragraph " + str(i) + ". " * 100 for i in range(50)]
        transcript = "\n\n".join(paragraphs)
        result = chunk_transcript(transcript, max_chars=500)
        assert len(result) > 1

    def test_splits_at_paragraph_boundaries(self) -> None:
        """Chunking should prefer splitting at paragraph boundaries."""
        para1 = "A" * 200
        para2 = "B" * 200
        para3 = "C" * 200
        transcript = f"{para1}\n\n{para2}\n\n{para3}"
        result = chunk_transcript(transcript, max_chars=450, overlap_chars=50)
        assert len(result) >= 2

    def test_overlap_between_chunks(self) -> None:
        """Chunks should have overlap for context continuity."""
        paragraphs = [f"Unique paragraph {i} content. " * 20 for i in range(20)]
        transcript = "\n\n".join(paragraphs)
        result = chunk_transcript(transcript, max_chars=500, overlap_chars=100)
        if len(result) >= 2:
            chunk1_end = result[0][-100:]
            assert chunk1_end in result[1], "No overlap found between consecutive chunks"

    def test_default_max_chars_is_30000(self) -> None:
        """Default max_chars should be 30000."""
        transcript = "A" * 29999
        result = chunk_transcript(transcript)
        assert len(result) == 1

    def test_handles_single_very_long_paragraph(self) -> None:
        """A single paragraph exceeding max_chars should be force-split."""
        transcript = "Word " * 10000  # ~50000 chars, no \n\n breaks
        result = chunk_transcript(transcript, max_chars=500, overlap_chars=50)
        assert len(result) > 1
        for chunk in result:
            assert len(chunk) <= 600, f"Chunk too large: {len(chunk)} chars"

    def test_returns_list_of_strings(self) -> None:
        """Return type should be list of strings."""
        result = chunk_transcript("Test")
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, str)

    def test_empty_string_returns_single_chunk(self) -> None:
        """Empty transcript should return a single (empty) chunk."""
        result = chunk_transcript("")
        assert len(result) == 1


# ---------------------------------------------------------------------------
# TestBuildExtractionPrompt
# ---------------------------------------------------------------------------


class TestBuildExtractionPrompt:
    """Tests for build_extraction_prompt function."""

    def test_includes_transcript_text(self) -> None:
        """Prompt should include the transcript text."""
        transcript = "This is my unique transcript text."
        result = build_extraction_prompt(transcript, ["general"])
        assert transcript in result

    def test_includes_category_descriptions(self) -> None:
        """Prompt should include category descriptions for the selected focus areas."""
        result = build_extraction_prompt("Some transcript", ["entrepreneurial"])
        assert "business_strategy" in result
        assert "growth_tactic" in result

    def test_includes_max_insights(self) -> None:
        """Prompt should include maximum insights count."""
        result = build_extraction_prompt("Transcript", ["general"], max_insights=5)
        assert "5" in result

    def test_default_max_insights_is_10(self) -> None:
        """Default max_insights should be 10."""
        result = build_extraction_prompt("Transcript", ["general"])
        assert "10" in result

    def test_returns_string(self) -> None:
        """build_extraction_prompt should return a string."""
        result = build_extraction_prompt("Sample transcript", ["general"])
        assert isinstance(result, str)
        assert len(result) > 0

    def test_includes_output_format_instructions(self) -> None:
        """Prompt should include output format instructions."""
        result = build_extraction_prompt("Transcript", ["general"])
        assert "category" in result.lower()
        assert "title" in result.lower()
        assert "summary" in result.lower()
        assert "confidence" in result.lower()

    def test_includes_json_response_format(self) -> None:
        """Prompt should instruct JSON response format."""
        result = build_extraction_prompt("Transcript", ["general"])
        assert "json" in result.lower()

    def test_general_focus_area_includes_all_general_categories(self) -> None:
        """General focus area should include all 4 general categories in prompt."""
        result = build_extraction_prompt("Transcript", ["general"])
        assert "key_point" in result
        assert "action_item" in result
        assert "notable_quote" in result
        assert "context" in result


# ---------------------------------------------------------------------------
# TestPrepareForExtraction
# ---------------------------------------------------------------------------


class TestPrepareForExtraction:
    """Tests for prepare_for_extraction function."""

    def test_returns_all_required_fields(self) -> None:
        """Result must contain all required keys."""
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
            "video_id",
        ]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_short_transcript_not_chunked(self) -> None:
        """Short transcripts should not be chunked."""
        result = prepare_for_extraction("Short text")
        assert result["needs_chunking"] is False
        assert result["chunk_count"] == 1
        assert result["chunks"] is None

    def test_long_transcript_is_chunked(self) -> None:
        """Long transcripts should be chunked."""
        long_text = "Paragraph. " * 5000  # ~55000 chars
        result = prepare_for_extraction(long_text)
        assert result["needs_chunking"] is True
        assert result["chunk_count"] > 1
        assert result["chunks"] is not None
        assert isinstance(result["chunks"], list)

    def test_video_id_passed_through(self) -> None:
        """video_id should be included in the result when provided."""
        result = prepare_for_extraction("Text", video_id="vid123")
        assert result["video_id"] == "vid123"

    def test_video_id_none_when_not_provided(self) -> None:
        """video_id should be None when not provided."""
        result = prepare_for_extraction("Text")
        assert result["video_id"] is None

    def test_default_focus_areas_is_general(self) -> None:
        """Default focus_areas should be ['general']."""
        result = prepare_for_extraction("Text")
        assert result["focus_areas"] == ["general"]

    def test_custom_focus_areas(self) -> None:
        """Custom focus areas should be reflected in result."""
        result = prepare_for_extraction("Text", focus_areas=["technical", "investment"])
        assert result["focus_areas"] == ["technical", "investment"]
        expected_cats = set(
            cat.value for cat in FOCUS_PRESETS["technical"]
        ) | set(
            cat.value for cat in FOCUS_PRESETS["investment"]
        )
        assert set(result["categories"]) == expected_cats

    def test_transcript_length_is_correct(self) -> None:
        """transcript_length should match actual length of input."""
        text = "Hello world"
        result = prepare_for_extraction(text)
        assert result["transcript_length"] == len(text)

    def test_max_insights_default_is_10(self) -> None:
        """Default max_insights should be 10."""
        result = prepare_for_extraction("Text")
        assert result["max_insights"] == 10

    def test_max_insights_custom(self) -> None:
        """Custom max_insights should be echoed in result."""
        result = prepare_for_extraction("Text", max_insights=5)
        assert result["max_insights"] == 5

    def test_categories_are_string_values(self) -> None:
        """Categories in result should be string values (not enum)."""
        result = prepare_for_extraction("Text")
        for cat in result["categories"]:
            assert isinstance(cat, str)

    def test_extraction_prompt_is_nonempty_string(self) -> None:
        """extraction_prompt should be a non-empty string."""
        result = prepare_for_extraction("Some transcript")
        assert isinstance(result["extraction_prompt"], str)
        assert len(result["extraction_prompt"]) > 0


# ---------------------------------------------------------------------------
# TestInsightModel
# ---------------------------------------------------------------------------


class TestInsightModel:
    """Tests for Insight Pydantic model validation."""

    def test_valid_insight(self) -> None:
        """A valid minimal Insight should be created successfully."""
        insight = Insight(
            category=InsightCategory.KEY_POINT,
            title="Important growth finding",
            summary="This insight covers important growth strategies.",
            confidence=0.85,
            actionable=True,
        )
        assert insight.category == InsightCategory.KEY_POINT
        assert insight.title == "Important growth finding"
        assert insight.confidence == 0.85
        assert insight.actionable is True
        assert insight.quote is None
        assert insight.timestamp_hint is None

    def test_insight_with_quote(self) -> None:
        """An Insight with optional quote and timestamp_hint should be valid."""
        insight = Insight(
            category=InsightCategory.NOTABLE_QUOTE,
            title="Memorable statement about AI",
            summary="Speaker shared a memorable point about AI development.",
            quote="AI will transform everything we know about work.",
            timestamp_hint="around 5:30",
            confidence=0.95,
            actionable=False,
        )
        assert insight.quote == "AI will transform everything we know about work."
        assert insight.timestamp_hint == "around 5:30"

    def test_confidence_below_zero_rejected(self) -> None:
        """Confidence must be >= 0.0."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Test",
                summary="Test summary",
                confidence=-0.1,
                actionable=True,
            )

    def test_confidence_above_one_rejected(self) -> None:
        """Confidence must be <= 1.0."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Test",
                summary="Test summary",
                confidence=1.5,
                actionable=True,
            )

    def test_confidence_at_bounds(self) -> None:
        """Confidence at exactly 0.0 and 1.0 should be valid."""
        insight_zero = Insight(
            category=InsightCategory.KEY_POINT,
            title="Test",
            summary="Test summary",
            confidence=0.0,
            actionable=True,
        )
        assert insight_zero.confidence == 0.0

        insight_one = Insight(
            category=InsightCategory.KEY_POINT,
            title="Test",
            summary="Test summary",
            confidence=1.0,
            actionable=True,
        )
        assert insight_one.confidence == 1.0

    def test_title_max_length_exceeded(self) -> None:
        """Title exceeding 100 characters should be rejected."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="x" * 101,
                summary="Valid summary",
                confidence=0.5,
                actionable=True,
            )

    def test_summary_max_length_exceeded(self) -> None:
        """Summary exceeding 500 characters should be rejected."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Valid title",
                summary="x" * 501,
                confidence=0.5,
                actionable=True,
            )

    def test_quote_max_length_exceeded(self) -> None:
        """Quote exceeding 300 characters should be rejected."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Valid title",
                summary="Valid summary",
                quote="x" * 301,
                confidence=0.5,
                actionable=True,
            )

    def test_missing_required_fields_rejected(self) -> None:
        """Insight without required fields should be rejected."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                # missing title, summary, confidence, actionable
            )
