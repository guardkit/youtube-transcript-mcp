# FEAT-INT-001: Insight Extraction Tool

## Overview

Add a tool to extract actionable insights from transcripts using Claude-assisted analysis. This is the intelligence layer that transforms raw transcripts into structured, consumable knowledge nuggets.

**Complexity**: 6/10  
**Estimated Time**: 5-6 hours  
**Dependencies**: FEAT-SKEL-003 (Transcript Tool)

## Business Context

The core value proposition for the Brandon collaboration project. Transforms long-form video content into actionable insights focused on entrepreneurial strategies, investment trends, and key takeaways suitable for consumption during commutes, walks, or other activities.

## Acceptance Criteria

1. `extract_insights` tool accepts transcript text and focus area(s)
2. Supports focus presets: general, entrepreneurial, investment, technical
3. Returns structured insights with category, title, summary, optional quote, confidence
4. Handles long transcripts via chunking strategy
5. Returns both individual insights and overall summary
6. Provides actionability flag for each insight
7. Unit tests cover output structure validation

## Technical Specification

### Insight Models (`src/models/insight.py`)

```python
"""Pydantic models for insight extraction."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class FocusArea(str, Enum):
    """Available focus areas for insight extraction."""
    GENERAL = "general"
    ENTREPRENEURIAL = "entrepreneurial"
    INVESTMENT = "investment"
    TECHNICAL = "technical"


class InsightCategory(str, Enum):
    """Categories for extracted insights."""
    # General
    KEY_POINT = "key_point"
    ACTION_ITEM = "action_item"
    NOTABLE_QUOTE = "notable_quote"
    
    # Entrepreneurial
    BUSINESS_STRATEGY = "business_strategy"
    GROWTH_TACTIC = "growth_tactic"
    LESSON_LEARNED = "lesson_learned"
    MISTAKE_TO_AVOID = "mistake_to_avoid"
    
    # Investment
    MARKET_TREND = "market_trend"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    RECOMMENDATION = "recommendation"
    
    # Technical
    TECHNOLOGY = "technology"
    TOOL = "tool"
    BEST_PRACTICE = "best_practice"
    PITFALL = "pitfall"


class Insight(BaseModel):
    """A single extracted insight."""
    category: InsightCategory
    title: str = Field(..., max_length=100, description="Brief title (10-15 words)")
    summary: str = Field(..., max_length=500, description="2-3 sentence summary")
    quote: Optional[str] = Field(None, max_length=300, description="Verbatim quote if applicable")
    timestamp_hint: Optional[str] = Field(None, description="Approximate timestamp reference")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    actionable: bool = Field(..., description="Whether this insight is actionable")


class KeyQuote(BaseModel):
    """A notable quote from the transcript."""
    text: str = Field(..., max_length=300)
    context: str = Field(..., max_length=200)
    speaker: Optional[str] = None


class InsightExtractionResult(BaseModel):
    """Complete result of insight extraction."""
    video_id: Optional[str] = None
    focus_areas: list[str]
    insights: list[Insight]
    key_quotes: list[KeyQuote]
    summary: str = Field(..., description="Overall content summary")
    total_insights: int
    processing_note: Optional[str] = None


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
}


# Category definitions for prompts
CATEGORY_DEFINITIONS: dict[InsightCategory, str] = {
    InsightCategory.KEY_POINT: "Main takeaways and central ideas",
    InsightCategory.ACTION_ITEM: "Specific actions viewers can take",
    InsightCategory.NOTABLE_QUOTE: "Memorable or impactful statements",
    InsightCategory.BUSINESS_STRATEGY: "Core business approaches, models, and strategic decisions",
    InsightCategory.GROWTH_TACTIC: "Specific tactics for user/revenue/market growth",
    InsightCategory.LESSON_LEARNED: "Key learnings from experience, both positive and negative",
    InsightCategory.MISTAKE_TO_AVOID: "Common pitfalls, errors, and things that didn't work",
    InsightCategory.MARKET_TREND: "Industry trends, market movements, and predictions",
    InsightCategory.OPPORTUNITY: "Investment or business opportunities identified",
    InsightCategory.RISK: "Potential risks, downsides, or concerns mentioned",
    InsightCategory.RECOMMENDATION: "Specific recommendations or advice given",
    InsightCategory.TECHNOLOGY: "Technologies, platforms, or systems mentioned",
    InsightCategory.TOOL: "Tools, software, or resources recommended",
    InsightCategory.BEST_PRACTICE: "Recommended approaches and methodologies",
    InsightCategory.PITFALL: "Common problems and anti-patterns to avoid",
}
```

### Insight Extraction Service (`src/services/insight_extractor.py`)

```python
"""Insight extraction service using Claude-assisted analysis.

This service structures the transcript for Claude analysis rather than
embedding an LLM directly. The MCP tool returns structured data that
Claude (the host) can then process conversationally.
"""

import logging
from typing import Optional

from src.models.insight import (
    FocusArea,
    InsightCategory,
    Insight,
    KeyQuote,
    InsightExtractionResult,
    FOCUS_PRESETS,
    CATEGORY_DEFINITIONS,
)

logger = logging.getLogger(__name__)


def get_focus_categories(focus_areas: list[str]) -> list[InsightCategory]:
    """Get insight categories for given focus areas.
    
    Args:
        focus_areas: List of focus area names or 'all'
        
    Returns:
        List of InsightCategory enum values to extract
    """
    if 'all' in focus_areas:
        return list(InsightCategory)
    
    categories = []
    for area in focus_areas:
        area_lower = area.lower()
        if area_lower in FOCUS_PRESETS:
            categories.extend(FOCUS_PRESETS[area_lower])
    
    return list(set(categories)) if categories else FOCUS_PRESETS['general']


def build_extraction_prompt(
    transcript: str,
    focus_areas: list[str],
    max_insights: int = 10
) -> str:
    """Build the prompt for insight extraction.
    
    This creates a structured prompt that can be used with Claude
    to extract insights from the transcript.
    
    Args:
        transcript: The full transcript text
        focus_areas: Focus areas to extract insights for
        max_insights: Maximum number of insights to extract
        
    Returns:
        Formatted prompt string
    """
    categories = get_focus_categories(focus_areas)
    
    category_descriptions = "\n".join([
        f"- **{cat.value}**: {CATEGORY_DEFINITIONS[cat]}"
        for cat in categories
    ])
    
    return f"""Analyze this transcript and extract actionable insights.

## Focus Areas
Extract insights in these categories:
{category_descriptions}

## Output Format
For each insight, provide:
1. **category**: One of the categories above
2. **title**: Brief title (10-15 words)
3. **summary**: 2-3 sentence explanation
4. **quote**: Verbatim quote from transcript (if applicable)
5. **confidence**: 0.0-1.0 how confident you are in this insight
6. **actionable**: true/false - can someone act on this?

Also provide:
- **key_quotes**: 2-3 most memorable quotes with context
- **summary**: Overall content summary (2-3 sentences)

## Guidelines
- Focus on ACTIONABLE insights the listener can use
- Prioritize specific advice over general observations
- Include context for why each insight matters
- Extract maximum {max_insights} insights
- For entrepreneurial/investment content, focus on concrete strategies

## Transcript
{transcript}

## Response
Respond with valid JSON matching this structure:
```json
{{
  "insights": [...],
  "key_quotes": [...],
  "summary": "..."
}}
```"""
```

### Example Output

Here's a concrete example of the expected JSON output when analyzing an entrepreneurial video:

```json
{
  "insights": [
    {
      "category": "business_strategy",
      "title": "Start with community building before product development",
      "summary": "The speaker emphasizes that successful startups build an engaged community first, then create products for that community. This reduces risk and ensures product-market fit from day one.",
      "quote": "Your community is your moat. Build the audience before you build the product.",
      "timestamp_hint": "around 5:30",
      "confidence": 0.92,
      "actionable": true
    },
    {
      "category": "mistake_to_avoid",
      "title": "Don't undercharge in early stages to win customers",
      "summary": "A key lesson learned: initially pricing too low attracted the wrong customers who churned quickly. Premium pricing filters for serious customers who value the offering.",
      "quote": null,
      "timestamp_hint": "around 12:45",
      "confidence": 0.88,
      "actionable": true
    },
    {
      "category": "growth_tactic",
      "title": "Use content marketing to build authority before selling",
      "summary": "The speaker grew from 0 to 10K subscribers by posting valuable content daily for 6 months before ever mentioning their product. Authority-first approach led to 40% conversion on launch.",
      "quote": "Give away your best stuff for free. The people who want more will pay.",
      "timestamp_hint": "around 18:20",
      "confidence": 0.85,
      "actionable": true
    }
  ],
  "key_quotes": [
    {
      "text": "Your community is your moat. Build the audience before you build the product.",
      "context": "Discussing why community-first approach reduces startup risk",
      "speaker": null
    },
    {
      "text": "Give away your best stuff for free. The people who want more will pay.",
      "context": "Explaining content marketing strategy that led to successful launch",
      "speaker": null
    }
  ],
  "summary": "This video covers community-driven product development, pricing strategies for early-stage startups, and content marketing as a growth lever. Key takeaway: build audience and authority before launching products."
}
```

This example shows:
- 3 insights across different categories
- Mix of insights with and without direct quotes
- Confidence scores based on how explicitly stated the insight was
- Actionability flags for practical advice
- Overall summary capturing the video's main themes

```python
def chunk_transcript(
    transcript: str, 
    max_chars: int = 30000,
    overlap_chars: int = 500
) -> list[str]:
    """Split long transcript into chunks for processing.
    
    Splits at paragraph boundaries when possible to maintain context.
    
    Args:
        transcript: Full transcript text
        max_chars: Maximum characters per chunk
        overlap_chars: Characters to overlap between chunks
        
    Returns:
        List of transcript chunks
    """
    if len(transcript) <= max_chars:
        return [transcript]
    
    # Split on double newlines (paragraphs) first
    paragraphs = transcript.split("\n\n")
    
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        # If adding this paragraph exceeds limit, save current and start new
        if len(current_chunk) + len(para) + 2 > max_chars:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from end of previous
                overlap = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                current_chunk = overlap + "\n\n" + para
            else:
                # Single paragraph exceeds limit, split by sentences
                current_chunk = para[:max_chars]
                chunks.append(current_chunk.strip())
                current_chunk = para[max_chars - overlap_chars:]
        else:
            current_chunk = current_chunk + "\n\n" + para if current_chunk else para
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


def prepare_for_extraction(
    transcript: str,
    video_id: Optional[str] = None,
    focus_areas: Optional[list[str]] = None,
    max_insights: int = 10,
) -> dict:
    """Prepare transcript for Claude-assisted insight extraction.
    
    This function structures the transcript and creates prompts/metadata
    that can be used with Claude for extraction. The actual LLM call
    happens at the Claude host level, not embedded here.
    
    Args:
        transcript: Full transcript text
        video_id: Optional video ID for reference
        focus_areas: Focus areas (default: general)
        max_insights: Maximum insights to request
        
    Returns:
        Dictionary with extraction metadata and prompt
    """
    focus_areas = focus_areas or ['general']
    categories = get_focus_categories(focus_areas)
    
    # Check if chunking needed
    chunks = chunk_transcript(transcript)
    needs_chunking = len(chunks) > 1
    
    return {
        "video_id": video_id,
        "focus_areas": focus_areas,
        "categories": [cat.value for cat in categories],
        "category_definitions": {
            cat.value: CATEGORY_DEFINITIONS[cat] 
            for cat in categories
        },
        "transcript_length": len(transcript),
        "chunk_count": len(chunks),
        "needs_chunking": needs_chunking,
        "max_insights": max_insights,
        "extraction_prompt": build_extraction_prompt(
            chunks[0] if needs_chunking else transcript,
            focus_areas,
            max_insights
        ),
        "chunks": chunks if needs_chunking else None,
    }
```

### Tool Registration (add to `src/__main__.py`)

```python
# Add imports at top
from src.models.insight import (
    FocusArea,
    FOCUS_PRESETS,
    CATEGORY_DEFINITIONS,
)
from src.services.insight_extractor import (
    prepare_for_extraction,
    get_focus_categories,
    chunk_transcript,
)

@mcp.tool()
async def extract_insights(
    transcript: str,
    focus_areas: str = "general",
    video_id: str = "",
    max_insights: str = "10"
) -> dict:
    """Prepare transcript for insight extraction analysis.
    
    Structures the transcript and creates analysis metadata for Claude
    to extract actionable insights. Returns prompts and categories
    that guide the extraction process.
    
    This tool prepares the data - the actual insight extraction happens
    through Claude's analysis of the returned prompt and transcript.
    
    Args:
        transcript: Full transcript text to analyze
        focus_areas: Comma-separated focus areas. Options:
            - "general": Key points, action items, notable quotes
            - "entrepreneurial": Business strategies, growth tactics, lessons
            - "investment": Market trends, opportunities, risks
            - "technical": Technologies, tools, best practices
            - "all": All categories
            Example: "entrepreneurial,investment"
        video_id: Optional video ID for reference
        max_insights: Maximum insights to extract (default: 10)
    
    Returns:
        Dictionary with:
        - extraction_prompt: Ready-to-use prompt for Claude analysis
        - focus_areas: Parsed focus areas
        - categories: Insight categories to extract
        - category_definitions: What each category means
        - transcript_length: Character count
        - chunk_count: Number of chunks (if long transcript)
        - needs_chunking: Whether transcript was split
        
    Usage:
        1. Call this tool with transcript
        2. Use the returned extraction_prompt with Claude
        3. Parse Claude's JSON response as insights
    """
    # CRITICAL: Parameter type conversion (MCP sends strings)
    if isinstance(max_insights, str):
        max_insights = int(max_insights)
    
    # Parse focus areas
    focus_list = [f.strip().lower() for f in focus_areas.split(",")]
    
    # Validate focus areas
    valid_areas = list(FOCUS_PRESETS.keys()) + ['all']
    invalid = [f for f in focus_list if f not in valid_areas]
    if invalid:
        return {
            "error": {
                "category": "client_error",
                "code": "INVALID_FOCUS_AREA",
                "message": f"Invalid focus areas: {invalid}. Valid: {valid_areas}",
            }
        }
    
    # Check transcript length
    if len(transcript) < 100:
        return {
            "error": {
                "category": "client_error",
                "code": "TRANSCRIPT_TOO_SHORT",
                "message": "Transcript must be at least 100 characters",
            }
        }
    
    try:
        result = prepare_for_extraction(
            transcript=transcript,
            video_id=video_id if video_id else None,
            focus_areas=focus_list,
            max_insights=max_insights,
        )
        return result
        
    except Exception as e:
        logger.exception(f"Error preparing extraction: {e}")
        return {
            "error": {
                "category": "server_error",
                "code": "EXTRACTION_PREP_ERROR",
                "message": str(e),
            }
        }


@mcp.tool()
async def list_focus_areas() -> dict:
    """List available focus areas for insight extraction.
    
    Returns the available focus area presets and their categories,
    helping users understand what kinds of insights can be extracted.
    
    Returns:
        Dictionary with:
        - focus_areas: Available presets and their categories
        - all_categories: Complete list of insight categories
    """
    return {
        "focus_areas": {
            name: [cat.value for cat in categories]
            for name, categories in FOCUS_PRESETS.items()
        },
        "category_definitions": {
            cat.value: desc 
            for cat, desc in CATEGORY_DEFINITIONS.items()
        },
        "usage_tip": "Pass focus areas as comma-separated: 'entrepreneurial,investment'",
    }
```

### Unit Tests (`tests/unit/test_insights.py`)

```python
"""Tests for insight extraction models and service."""

import pytest

from src.models.insight import (
    FocusArea,
    InsightCategory,
    Insight,
    InsightExtractionResult,
    FOCUS_PRESETS,
    CATEGORY_DEFINITIONS,
)
from src.services.insight_extractor import (
    get_focus_categories,
    build_extraction_prompt,
    chunk_transcript,
    prepare_for_extraction,
)


class TestFocusPresets:
    """Tests for focus area presets."""
    
    def test_general_preset_has_basic_categories(self):
        categories = FOCUS_PRESETS['general']
        assert InsightCategory.KEY_POINT in categories
        assert InsightCategory.ACTION_ITEM in categories
    
    def test_entrepreneurial_preset_has_business_categories(self):
        categories = FOCUS_PRESETS['entrepreneurial']
        assert InsightCategory.BUSINESS_STRATEGY in categories
        assert InsightCategory.GROWTH_TACTIC in categories
        assert InsightCategory.LESSON_LEARNED in categories
    
    def test_all_categories_have_definitions(self):
        for category in InsightCategory:
            assert category in CATEGORY_DEFINITIONS
            assert len(CATEGORY_DEFINITIONS[category]) > 10


class TestGetFocusCategories:
    """Tests for get_focus_categories function."""
    
    def test_single_focus_area(self):
        categories = get_focus_categories(['general'])
        assert InsightCategory.KEY_POINT in categories
    
    def test_multiple_focus_areas(self):
        categories = get_focus_categories(['entrepreneurial', 'investment'])
        assert InsightCategory.BUSINESS_STRATEGY in categories
        assert InsightCategory.MARKET_TREND in categories
    
    def test_all_returns_all_categories(self):
        categories = get_focus_categories(['all'])
        assert len(categories) == len(InsightCategory)
    
    def test_unknown_area_falls_back_to_general(self):
        categories = get_focus_categories(['unknown_area'])
        assert categories == FOCUS_PRESETS['general']
    
    def test_deduplicates_categories(self):
        # If same area specified twice, should not duplicate
        categories = get_focus_categories(['general', 'general'])
        assert len(categories) == len(set(categories))


class TestChunkTranscript:
    """Tests for transcript chunking."""
    
    def test_short_transcript_single_chunk(self):
        transcript = "This is a short transcript."
        chunks = chunk_transcript(transcript, max_chars=1000)
        assert len(chunks) == 1
        assert chunks[0] == transcript
    
    def test_long_transcript_multiple_chunks(self):
        # Create transcript longer than max_chars
        transcript = "Paragraph one.\n\n" * 100
        chunks = chunk_transcript(transcript, max_chars=500)
        assert len(chunks) > 1
    
    def test_chunks_have_overlap(self):
        transcript = "A" * 1000 + "\n\n" + "B" * 1000
        chunks = chunk_transcript(transcript, max_chars=1200, overlap_chars=100)
        
        # Second chunk should start with end of first
        if len(chunks) > 1:
            # There should be some overlap
            assert len(chunks[1]) > 900  # Should have content plus overlap
    
    def test_respects_paragraph_boundaries(self):
        transcript = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        chunks = chunk_transcript(transcript, max_chars=40)
        
        # Should split at paragraph boundaries
        for chunk in chunks:
            # Chunks shouldn't have partial paragraphs (no hanging text)
            assert chunk.strip().endswith('.')


class TestBuildExtractionPrompt:
    """Tests for prompt building."""
    
    def test_includes_transcript(self):
        prompt = build_extraction_prompt("Test transcript", ['general'])
        assert "Test transcript" in prompt
    
    def test_includes_category_descriptions(self):
        prompt = build_extraction_prompt("Test", ['entrepreneurial'])
        assert "business_strategy" in prompt
        assert "growth_tactic" in prompt
    
    def test_includes_max_insights(self):
        prompt = build_extraction_prompt("Test", ['general'], max_insights=5)
        assert "5" in prompt


class TestPrepareForExtraction:
    """Tests for prepare_for_extraction function."""
    
    def test_returns_required_fields(self):
        result = prepare_for_extraction("Test transcript content here", focus_areas=['general'])
        
        assert 'extraction_prompt' in result
        assert 'focus_areas' in result
        assert 'categories' in result
        assert 'transcript_length' in result
        assert 'chunk_count' in result
    
    def test_detects_chunking_needed(self):
        short_result = prepare_for_extraction("Short", focus_areas=['general'])
        assert short_result['needs_chunking'] is False
        assert short_result['chunk_count'] == 1
        
        long_transcript = "Long content " * 5000
        long_result = prepare_for_extraction(long_transcript, focus_areas=['general'])
        assert long_result['needs_chunking'] is True
        assert long_result['chunk_count'] > 1
    
    def test_includes_video_id_when_provided(self):
        result = prepare_for_extraction("Test", video_id='abc123', focus_areas=['general'])
        assert result['video_id'] == 'abc123'


class TestInsightModel:
    """Tests for Insight Pydantic model."""
    
    def test_valid_insight(self):
        insight = Insight(
            category=InsightCategory.KEY_POINT,
            title="Important finding about growth",
            summary="This is a key insight that was discovered during the analysis.",
            confidence=0.85,
            actionable=True,
        )
        assert insight.category == InsightCategory.KEY_POINT
        assert insight.confidence == 0.85
    
    def test_insight_with_quote(self):
        insight = Insight(
            category=InsightCategory.NOTABLE_QUOTE,
            title="Memorable statement",
            summary="Speaker made this memorable point.",
            quote="The exact words they said.",
            confidence=0.95,
            actionable=False,
        )
        assert insight.quote == "The exact words they said."
    
    def test_confidence_bounds(self):
        with pytest.raises(ValueError):
            Insight(
                category=InsightCategory.KEY_POINT,
                title="Test",
                summary="Test summary",
                confidence=1.5,  # Invalid - over 1.0
                actionable=True,
            )
```

### Update `pyproject.toml` Dependencies

```toml
dependencies = [
    "mcp>=1.0.0",                    # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",              # YouTube video metadata extraction
    "youtube-transcript-api>=1.0.0", # Transcript fetching
    "pydantic>=2.0",                 # Data validation (v2 features: Field, BaseModel)
]
```

## File Structure After Implementation

```
youtube-transcript-mcp/
├── src/
│   ├── __init__.py
│   ├── __main__.py              # + extract_insights, list_focus_areas
│   ├── models/
│   │   ├── __init__.py
│   │   └── insight.py           # NEW: Pydantic models
│   └── services/
│       ├── __init__.py
│       ├── youtube_client.py
│       ├── transcript_client.py
│       └── insight_extractor.py # NEW: extraction service
├── tests/
│   └── unit/
│       ├── test_ping.py
│       ├── test_video_info.py
│       ├── test_transcript.py
│       └── test_insights.py     # NEW: insight tests
└── pyproject.toml               # Updated with pydantic dependency
```

## Testing Strategy

1. **Unit Tests**: Test models, chunking, prompt building
2. **Integration Tests**: Test with sample transcripts
3. **Manual Testing**: Full flow with MCP Inspector + Claude

## Definition of Done

- [ ] `src/models/insight.py` defines Pydantic models
- [ ] `src/services/insight_extractor.py` implements extraction prep
- [ ] `extract_insights` tool registered in `__main__.py`
- [ ] `list_focus_areas` tool provides discovery
- [ ] Chunking works for long transcripts
- [ ] Focus area validation with helpful errors
- [ ] Unit tests pass
- [ ] Code passes `ruff check` and `mypy`

## Implementation Notes

### Critical MCP Patterns

These patterns are REQUIRED for correct MCP server behavior.

| # | Pattern | Why | Example |
|---|---------|-----|---------|
| 1 | **stderr logging** | stdout = MCP JSON-RPC protocol | `logging.basicConfig(stream=sys.stderr)` |
| 2 | **Module-level tools** | Required for Claude Code discovery | `@mcp.tool()` at module level in `__main__.py` |
| 3 | **String parameters** | MCP sends all params as strings | `count_int = int(count)` |
| 4 | **Timezone-aware datetime** | `utcnow()` is deprecated | `datetime.now(timezone.utc)` |
| 5 | **Async wrappers** | Don't block event loop | `await asyncio.to_thread(sync_fn)` |
| 6 | **CancelledError** | Must re-raise for cleanup | `except CancelledError: logger.info(...); raise` |
| 7 | **Structured errors** | Consistent error format | `{"error": {"category": "...", "code": "...", "message": "..."}}` |

#### Pattern Details

<details>
<summary>1. stderr logging (CRITICAL)</summary>

```python
import sys
import logging

# CORRECT
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# WRONG - breaks MCP protocol
print("Debug")  # stdout corrupts JSON-RPC
logging.basicConfig()  # Defaults to stdout!
```
</details>

<details>
<summary>2. Module-level tool registration</summary>

```python
# CORRECT - in __main__.py at module level
@mcp.tool()
async def my_tool():
    pass

# WRONG - tools registered in functions won't be discovered
def setup():
    @mcp.tool()
    async def my_tool():
        pass
```
</details>

<details>
<summary>3. String parameter conversion</summary>

```python
@mcp.tool()
async def process(count: str, enabled: str) -> dict:
    # MCP sends "10" not 10, "true" not True
    count_int = int(count)
    enabled_bool = enabled.lower() in ("true", "1", "yes")
    return {"count": count_int, "enabled": enabled_bool}
```
</details>

## Usage Example

```
User: Extract entrepreneurial insights from this video
Claude: [calls get_transcript]
Claude: [calls extract_insights with transcript and focus_areas="entrepreneurial"]
Claude: [uses returned extraction_prompt to analyze]
Claude: Here are the key entrepreneurial insights from the video:

1. **Growth through community** (confidence: 0.92)
   The speaker emphasizes building community before product...

2. **Pricing strategy mistake** (confidence: 0.88)
   A key lesson learned: they initially priced too low...
```

## Design Decision: Claude-Assisted vs Embedded LLM

This implementation uses **Claude-assisted** extraction rather than embedding an LLM:

**Pros of Claude-assisted:**
- No additional API keys or costs
- Claude already has context from conversation
- Simpler implementation
- Better user experience (conversational)

**Cons:**
- Requires user interaction to complete extraction
- Can't be fully automated

For Brandon's use case (interactive consumption), Claude-assisted is ideal. If autonomous processing is needed later, the `extraction_prompt` can be sent to any LLM API.
