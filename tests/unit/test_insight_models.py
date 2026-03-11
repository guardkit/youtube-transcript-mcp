"""Tests for insight extraction Pydantic models and constants.

TDD RED phase: These tests define the expected behavior for
youtube_insights_mcp/models/insight.py including enums, models, and mappings.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from youtube_insights_mcp.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
    FocusArea,
    Insight,
    InsightCategory,
    InsightExtractionResult,
    KeyQuote,
)


class TestFocusAreaEnum:
    """Tests for the FocusArea enum."""

    def test_has_exactly_six_values(self) -> None:
        assert len(FocusArea) == 6

    def test_general_value(self) -> None:
        assert FocusArea.GENERAL.value == "general"

    def test_entrepreneurial_value(self) -> None:
        assert FocusArea.ENTREPRENEURIAL.value == "entrepreneurial"

    def test_investment_value(self) -> None:
        assert FocusArea.INVESTMENT.value == "investment"

    def test_technical_value(self) -> None:
        assert FocusArea.TECHNICAL.value == "technical"

    def test_youtube_channel_value(self) -> None:
        assert FocusArea.YOUTUBE_CHANNEL.value == "youtube-channel"

    def test_ai_learning_value(self) -> None:
        assert FocusArea.AI_LEARNING.value == "ai-learning"

    def test_is_string_enum(self) -> None:
        """FocusArea should be a string enum for JSON serialization."""
        assert isinstance(FocusArea.GENERAL, str)
        assert FocusArea.GENERAL == "general"


class TestInsightCategoryEnum:
    """Tests for the InsightCategory enum."""

    def test_has_exactly_24_values(self) -> None:
        """4 general + 4 entrepreneurial + 4 investment + 4 technical + 4 youtube + 4 ai = 24."""
        assert len(InsightCategory) == 24

    def test_general_categories(self) -> None:
        assert InsightCategory.KEY_POINT.value == "key_point"
        assert InsightCategory.ACTION_ITEM.value == "action_item"
        assert InsightCategory.NOTABLE_QUOTE.value == "notable_quote"
        assert InsightCategory.CONTEXT.value == "context"

    def test_entrepreneurial_categories(self) -> None:
        assert InsightCategory.BUSINESS_STRATEGY.value == "business_strategy"
        assert InsightCategory.GROWTH_TACTIC.value == "growth_tactic"
        assert InsightCategory.LESSON_LEARNED.value == "lesson_learned"
        assert InsightCategory.MISTAKE_TO_AVOID.value == "mistake_to_avoid"

    def test_investment_categories(self) -> None:
        assert InsightCategory.MARKET_TREND.value == "market_trend"
        assert InsightCategory.OPPORTUNITY.value == "opportunity"
        assert InsightCategory.RISK.value == "risk"
        assert InsightCategory.RECOMMENDATION.value == "recommendation"

    def test_technical_categories(self) -> None:
        assert InsightCategory.TECHNOLOGY.value == "technology"
        assert InsightCategory.TOOL.value == "tool"
        assert InsightCategory.BEST_PRACTICE.value == "best_practice"
        assert InsightCategory.PITFALL.value == "pitfall"

    def test_youtube_channel_categories(self) -> None:
        assert InsightCategory.CHANNEL_STRATEGY.value == "channel_strategy"
        assert InsightCategory.CONTENT_IDEA.value == "content_idea"
        assert InsightCategory.AUDIENCE_GROWTH.value == "audience_growth"
        assert InsightCategory.PRODUCTION_TIP.value == "production_tip"

    def test_ai_learning_categories(self) -> None:
        assert InsightCategory.AI_CONCEPT.value == "ai_concept"
        assert InsightCategory.AI_TOOL.value == "ai_tool"
        assert InsightCategory.MENTAL_MODEL.value == "mental_model"
        assert InsightCategory.PRACTICAL_APPLICATION.value == "practical_application"

    def test_is_string_enum(self) -> None:
        """InsightCategory should be a string enum for JSON serialization."""
        assert isinstance(InsightCategory.KEY_POINT, str)
        assert InsightCategory.KEY_POINT == "key_point"


class TestInsightModel:
    """Tests for the Insight Pydantic model."""

    def test_valid_insight_minimal(self) -> None:
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

    def test_valid_insight_with_all_fields(self) -> None:
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

    def test_title_max_length_100(self) -> None:
        """Title must not exceed 100 characters."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="x" * 101,
                summary="Valid summary",
                confidence=0.5,
                actionable=True,
            )

    def test_title_at_max_length_100(self) -> None:
        """Title at exactly 100 characters should be valid."""
        insight = Insight(
            category=InsightCategory.KEY_POINT,
            title="x" * 100,
            summary="Valid summary",
            confidence=0.5,
            actionable=True,
        )
        assert len(insight.title) == 100

    def test_summary_max_length_500(self) -> None:
        """Summary must not exceed 500 characters."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Valid title",
                summary="x" * 501,
                confidence=0.5,
                actionable=True,
            )

    def test_quote_max_length_300(self) -> None:
        """Quote must not exceed 300 characters."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Valid title",
                summary="Valid summary",
                quote="x" * 301,
                confidence=0.5,
                actionable=True,
            )

    def test_confidence_minimum_zero(self) -> None:
        """Confidence must be >= 0."""
        with pytest.raises(ValidationError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Test",
                summary="Test summary",
                confidence=-0.1,
                actionable=True,
            )

    def test_confidence_maximum_one(self) -> None:
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


class TestKeyQuoteModel:
    """Tests for the KeyQuote Pydantic model."""

    def test_valid_key_quote_minimal(self) -> None:
        quote = KeyQuote(
            text="Build the audience before you build the product.",
            context="Discussing community-first approach",
        )
        assert quote.text == "Build the audience before you build the product."
        assert quote.context == "Discussing community-first approach"
        assert quote.speaker is None

    def test_valid_key_quote_with_speaker(self) -> None:
        quote = KeyQuote(
            text="Innovation is not about technology.",
            context="Opening keynote remarks",
            speaker="John Doe",
        )
        assert quote.speaker == "John Doe"

    def test_text_max_length_300(self) -> None:
        """Text must not exceed 300 characters."""
        with pytest.raises(ValidationError):
            KeyQuote(
                text="x" * 301,
                context="Valid context",
            )

    def test_context_max_length_200(self) -> None:
        """Context must not exceed 200 characters."""
        with pytest.raises(ValidationError):
            KeyQuote(
                text="Valid text",
                context="x" * 201,
            )


class TestInsightExtractionResultModel:
    """Tests for the InsightExtractionResult Pydantic model."""

    def test_valid_result_minimal(self) -> None:
        result = InsightExtractionResult(
            focus_areas=["general"],
            insights=[],
            key_quotes=[],
            summary="Overview of the video content.",
            total_insights=0,
        )
        assert result.video_id is None
        assert result.focus_areas == ["general"]
        assert result.insights == []
        assert result.key_quotes == []
        assert result.total_insights == 0
        assert result.processing_note is None

    def test_valid_result_with_all_fields(self) -> None:
        insight = Insight(
            category=InsightCategory.KEY_POINT,
            title="Key finding",
            summary="An important finding.",
            confidence=0.9,
            actionable=True,
        )
        quote = KeyQuote(
            text="A memorable quote.",
            context="During discussion",
        )
        result = InsightExtractionResult(
            video_id="abc123",
            focus_areas=["entrepreneurial", "investment"],
            insights=[insight],
            key_quotes=[quote],
            summary="Video covers business strategies.",
            total_insights=1,
            processing_note="Processed first chunk only.",
        )
        assert result.video_id == "abc123"
        assert len(result.insights) == 1
        assert len(result.key_quotes) == 1
        assert result.processing_note == "Processed first chunk only."


class TestFocusPresets:
    """Tests for the FOCUS_PRESETS mapping."""

    def test_has_exactly_six_presets(self) -> None:
        assert len(FOCUS_PRESETS) == 6

    def test_general_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["general"]
        assert len(cats) == 4
        assert InsightCategory.KEY_POINT in cats
        assert InsightCategory.ACTION_ITEM in cats
        assert InsightCategory.NOTABLE_QUOTE in cats
        assert InsightCategory.CONTEXT in cats

    def test_entrepreneurial_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["entrepreneurial"]
        assert len(cats) == 4
        assert InsightCategory.BUSINESS_STRATEGY in cats
        assert InsightCategory.GROWTH_TACTIC in cats
        assert InsightCategory.LESSON_LEARNED in cats
        assert InsightCategory.MISTAKE_TO_AVOID in cats

    def test_investment_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["investment"]
        assert len(cats) == 4
        assert InsightCategory.MARKET_TREND in cats
        assert InsightCategory.OPPORTUNITY in cats
        assert InsightCategory.RISK in cats
        assert InsightCategory.RECOMMENDATION in cats

    def test_technical_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["technical"]
        assert len(cats) == 4
        assert InsightCategory.TECHNOLOGY in cats
        assert InsightCategory.TOOL in cats
        assert InsightCategory.BEST_PRACTICE in cats
        assert InsightCategory.PITFALL in cats

    def test_youtube_channel_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["youtube-channel"]
        assert len(cats) == 4
        assert InsightCategory.CHANNEL_STRATEGY in cats
        assert InsightCategory.CONTENT_IDEA in cats
        assert InsightCategory.AUDIENCE_GROWTH in cats
        assert InsightCategory.PRODUCTION_TIP in cats

    def test_ai_learning_preset_has_four_categories(self) -> None:
        cats = FOCUS_PRESETS["ai-learning"]
        assert len(cats) == 4
        assert InsightCategory.AI_CONCEPT in cats
        assert InsightCategory.AI_TOOL in cats
        assert InsightCategory.MENTAL_MODEL in cats
        assert InsightCategory.PRACTICAL_APPLICATION in cats

    def test_all_preset_keys_match_focus_area_values(self) -> None:
        """Preset keys should match FocusArea enum values."""
        for focus_area in FocusArea:
            assert focus_area.value in FOCUS_PRESETS, (
                f"FocusArea {focus_area.value} missing from FOCUS_PRESETS"
            )

    def test_all_preset_values_are_insight_categories(self) -> None:
        """All categories in presets must be valid InsightCategory values."""
        for preset_name, categories in FOCUS_PRESETS.items():
            for cat in categories:
                assert isinstance(cat, InsightCategory), (
                    f"Invalid category {cat} in preset {preset_name}"
                )


class TestCategoryDefinitions:
    """Tests for the CATEGORY_DEFINITIONS mapping."""

    def test_all_categories_have_definitions(self) -> None:
        """Every InsightCategory must have a definition."""
        assert len(CATEGORY_DEFINITIONS) == len(InsightCategory)

    def test_every_insight_category_has_definition(self) -> None:
        for category in InsightCategory:
            assert category in CATEGORY_DEFINITIONS, (
                f"InsightCategory {category.value} missing from CATEGORY_DEFINITIONS"
            )

    def test_definitions_are_non_empty_strings(self) -> None:
        for category, definition in CATEGORY_DEFINITIONS.items():
            assert isinstance(definition, str)
            assert len(definition) > 10, (
                f"Definition for {category.value} is too short: '{definition}'"
            )

    def test_specific_definitions_content(self) -> None:
        """Spot check some definitions for correctness."""
        assert "takeaway" in CATEGORY_DEFINITIONS[InsightCategory.KEY_POINT].lower() or \
               "main" in CATEGORY_DEFINITIONS[InsightCategory.KEY_POINT].lower()
        assert "business" in CATEGORY_DEFINITIONS[InsightCategory.BUSINESS_STRATEGY].lower() or \
               "strateg" in CATEGORY_DEFINITIONS[InsightCategory.BUSINESS_STRATEGY].lower()


class TestImportability:
    """Tests that all models are importable from youtube_insights_mcp.models.insight."""

    def test_focus_area_importable(self) -> None:
        from youtube_insights_mcp.models.insight import FocusArea
        assert FocusArea is not None

    def test_insight_category_importable(self) -> None:
        from youtube_insights_mcp.models.insight import InsightCategory
        assert InsightCategory is not None

    def test_insight_importable(self) -> None:
        from youtube_insights_mcp.models.insight import Insight
        assert Insight is not None

    def test_key_quote_importable(self) -> None:
        from youtube_insights_mcp.models.insight import KeyQuote
        assert KeyQuote is not None

    def test_insight_extraction_result_importable(self) -> None:
        from youtube_insights_mcp.models.insight import InsightExtractionResult
        assert InsightExtractionResult is not None

    def test_focus_presets_importable(self) -> None:
        from youtube_insights_mcp.models.insight import FOCUS_PRESETS
        assert FOCUS_PRESETS is not None

    def test_category_definitions_importable(self) -> None:
        from youtube_insights_mcp.models.insight import CATEGORY_DEFINITIONS
        assert CATEGORY_DEFINITIONS is not None
