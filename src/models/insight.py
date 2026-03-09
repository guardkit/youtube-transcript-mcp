"""Pydantic models for insight extraction.

Defines enums, models, and mappings for the insight extraction feature.
Provides 6 focus area presets with 23 total insight categories.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class FocusArea(str, Enum):
    """Available focus areas for insight extraction."""

    GENERAL = "general"
    ENTREPRENEURIAL = "entrepreneurial"
    INVESTMENT = "investment"
    TECHNICAL = "technical"
    YOUTUBE_CHANNEL = "youtube-channel"
    AI_LEARNING = "ai-learning"


class InsightCategory(str, Enum):
    """Categories for extracted insights.

    24 categories across 6 focus areas (general has 3, others have 4 each).
    """

    # General (3 categories)
    KEY_POINT = "key_point"
    ACTION_ITEM = "action_item"
    NOTABLE_QUOTE = "notable_quote"

    # Entrepreneurial (4 categories)
    BUSINESS_STRATEGY = "business_strategy"
    GROWTH_TACTIC = "growth_tactic"
    LESSON_LEARNED = "lesson_learned"
    MISTAKE_TO_AVOID = "mistake_to_avoid"

    # Investment (4 categories)
    MARKET_TREND = "market_trend"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    RECOMMENDATION = "recommendation"

    # Technical (4 categories)
    TECHNOLOGY = "technology"
    TOOL = "tool"
    BEST_PRACTICE = "best_practice"
    PITFALL = "pitfall"

    # YouTube Channel (4 categories)
    CHANNEL_STRATEGY = "channel_strategy"
    CONTENT_IDEA = "content_idea"
    AUDIENCE_GROWTH = "audience_growth"
    PRODUCTION_TIP = "production_tip"

    # AI Learning (4 categories)
    AI_CONCEPT = "ai_concept"
    AI_TOOL = "ai_tool"
    MENTAL_MODEL = "mental_model"
    PRACTICAL_APPLICATION = "practical_application"


class Insight(BaseModel):
    """A single extracted insight."""

    category: InsightCategory
    title: str = Field(..., max_length=100, description="Brief title (10-15 words)")
    summary: str = Field(
        ..., max_length=500, description="2-3 sentence summary"
    )
    quote: str | None = Field(
        None, max_length=300, description="Verbatim quote if applicable"
    )
    timestamp_hint: str | None = Field(
        None, description="Approximate timestamp reference"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score 0-1"
    )
    actionable: bool = Field(
        ..., description="Whether this insight is actionable"
    )


class KeyQuote(BaseModel):
    """A notable quote from the transcript."""

    text: str = Field(..., max_length=300)
    context: str = Field(..., max_length=200)
    speaker: str | None = None


class InsightExtractionResult(BaseModel):
    """Complete result of insight extraction."""

    video_id: str | None = None
    focus_areas: list[str]
    insights: list[Insight]
    key_quotes: list[KeyQuote]
    summary: str = Field(..., description="Overall content summary")
    total_insights: int
    processing_note: str | None = None


# Focus area presets mapping
FOCUS_PRESETS: dict[str, list[InsightCategory]] = {
    "general": [
        InsightCategory.KEY_POINT,
        InsightCategory.ACTION_ITEM,
        InsightCategory.NOTABLE_QUOTE,
    ],
    "entrepreneurial": [
        InsightCategory.BUSINESS_STRATEGY,
        InsightCategory.GROWTH_TACTIC,
        InsightCategory.LESSON_LEARNED,
        InsightCategory.MISTAKE_TO_AVOID,
    ],
    "investment": [
        InsightCategory.MARKET_TREND,
        InsightCategory.OPPORTUNITY,
        InsightCategory.RISK,
        InsightCategory.RECOMMENDATION,
    ],
    "technical": [
        InsightCategory.TECHNOLOGY,
        InsightCategory.TOOL,
        InsightCategory.BEST_PRACTICE,
        InsightCategory.PITFALL,
    ],
    "youtube-channel": [
        InsightCategory.CHANNEL_STRATEGY,
        InsightCategory.CONTENT_IDEA,
        InsightCategory.AUDIENCE_GROWTH,
        InsightCategory.PRODUCTION_TIP,
    ],
    "ai-learning": [
        InsightCategory.AI_CONCEPT,
        InsightCategory.AI_TOOL,
        InsightCategory.MENTAL_MODEL,
        InsightCategory.PRACTICAL_APPLICATION,
    ],
}


# Category definitions for prompts
CATEGORY_DEFINITIONS: dict[InsightCategory, str] = {
    InsightCategory.KEY_POINT: "Main takeaways and central ideas",
    InsightCategory.ACTION_ITEM: "Specific actions viewers can take",
    InsightCategory.NOTABLE_QUOTE: "Memorable or impactful statements",
    InsightCategory.BUSINESS_STRATEGY: (
        "Core business approaches, models, and strategic decisions"
    ),
    InsightCategory.GROWTH_TACTIC: (
        "Specific tactics for user/revenue/market growth"
    ),
    InsightCategory.LESSON_LEARNED: (
        "Key learnings from experience, both positive and negative"
    ),
    InsightCategory.MISTAKE_TO_AVOID: (
        "Common pitfalls, errors, and things that didn't work"
    ),
    InsightCategory.MARKET_TREND: (
        "Industry trends, market movements, and predictions"
    ),
    InsightCategory.OPPORTUNITY: (
        "Investment or business opportunities identified"
    ),
    InsightCategory.RISK: "Potential risks, downsides, or concerns mentioned",
    InsightCategory.RECOMMENDATION: "Specific recommendations or advice given",
    InsightCategory.TECHNOLOGY: (
        "Technologies, platforms, or systems mentioned"
    ),
    InsightCategory.TOOL: "Tools, software, or resources recommended",
    InsightCategory.BEST_PRACTICE: (
        "Recommended approaches and methodologies"
    ),
    InsightCategory.PITFALL: "Common problems and anti-patterns to avoid",
    InsightCategory.CHANNEL_STRATEGY: (
        "High-level channel positioning, niche, and growth direction"
    ),
    InsightCategory.CONTENT_IDEA: (
        "Specific video ideas, formats, series concepts to steal or adapt"
    ),
    InsightCategory.AUDIENCE_GROWTH: (
        "Tactics for growing subscribers, views, and engagement"
    ),
    InsightCategory.PRODUCTION_TIP: (
        "Filming, editing, thumbnails, titles, SEO, workflow improvements"
    ),
    InsightCategory.AI_CONCEPT: (
        "Core AI/ML concepts, architectures, or techniques explained"
    ),
    InsightCategory.AI_TOOL: (
        "Specific AI tools, libraries, frameworks, or services discussed"
    ),
    InsightCategory.MENTAL_MODEL: (
        "Frameworks and mental models for thinking about AI systems"
    ),
    InsightCategory.PRACTICAL_APPLICATION: (
        "Concrete ways to apply AI concepts to real projects"
    ),
}
