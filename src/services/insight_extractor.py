"""Insight extraction service using Claude-assisted analysis.

This service structures the transcript for Claude analysis rather than
embedding an LLM directly. The MCP tool returns structured data that
Claude (the host) can then process conversationally.

Functions:
    get_focus_categories: Resolve focus area names to InsightCategory lists.
    build_extraction_prompt: Generate a structured extraction prompt.
    chunk_transcript: Split long transcripts at paragraph boundaries.
    prepare_for_extraction: Return complete extraction metadata and prompt.
"""

from __future__ import annotations

import logging
from typing import Optional

from src.models.insight import (
    CATEGORY_DEFINITIONS,
    FOCUS_PRESETS,
    InsightCategory,
)

logger = logging.getLogger(__name__)


def get_focus_categories(focus_areas: list[str]) -> list[InsightCategory]:
    """Get insight categories for given focus areas.

    Resolves human-readable focus area names into their corresponding
    ``InsightCategory`` enum values using the ``FOCUS_PRESETS`` mapping.

    Special behaviours:
    - ``"all"`` returns every ``InsightCategory``.
    - Unknown area names are silently skipped; if *none* matched, the
      ``"general"`` preset is used as fallback.
    - Duplicate categories are removed.

    Args:
        focus_areas: List of focus area names (e.g. ``["general"]``)
            or ``["all"]``.

    Returns:
        De-duplicated list of ``InsightCategory`` values.
    """
    if "all" in [area.lower() for area in focus_areas]:
        return list(InsightCategory)

    categories: list[InsightCategory] = []
    for area in focus_areas:
        area_lower = area.lower()
        if area_lower in FOCUS_PRESETS:
            categories.extend(FOCUS_PRESETS[area_lower])

    if not categories:
        logger.info("No valid focus areas matched; falling back to 'general'")
        return list(FOCUS_PRESETS["general"])

    # De-duplicate while preserving insertion order
    seen: set[InsightCategory] = set()
    unique: list[InsightCategory] = []
    for cat in categories:
        if cat not in seen:
            seen.add(cat)
            unique.append(cat)
    return unique


def build_extraction_prompt(
    transcript: str,
    focus_areas: list[str],
    max_insights: int = 10,
) -> str:
    """Build the prompt for insight extraction.

    Creates a structured prompt that can be used with Claude to extract
    insights from the transcript.  The prompt includes category descriptions,
    output-format instructions, extraction guidelines, and the transcript text.

    Args:
        transcript: The full (or chunked) transcript text.
        focus_areas: Focus areas to extract insights for.
        max_insights: Maximum number of insights to extract.

    Returns:
        Formatted prompt string ready for LLM consumption.
    """
    categories = get_focus_categories(focus_areas)

    category_descriptions = "\n".join(
        f"- **{cat.value}**: {CATEGORY_DEFINITIONS[cat]}" for cat in categories
    )

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


def _force_split(text: str, max_chars: int, overlap_chars: int) -> list[str]:
    """Split text that has no paragraph boundaries into fixed-size chunks.

    Each chunk (except the last) is exactly *max_chars* long.  Consecutive
    chunks overlap by *overlap_chars* characters for context continuity.

    Args:
        text: The text to split.
        max_chars: Maximum characters per chunk.
        overlap_chars: Characters to overlap between chunks.

    Returns:
        List of text chunks.
    """
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        # Advance by (max_chars - overlap_chars) so the next chunk
        # starts with *overlap_chars* characters from the previous one.
        step = max_chars - overlap_chars
        if step <= 0:
            step = max_chars  # safety: avoid infinite loop
        start += step
    return chunks


def chunk_transcript(
    transcript: str,
    max_chars: int = 30000,
    overlap_chars: int = 500,
) -> list[str]:
    """Split long transcript into chunks for processing.

    Splits at paragraph boundaries (``\\n\\n``) when possible to maintain
    context.  Falls back to character-level splitting for paragraphs that
    individually exceed *max_chars*.  An *overlap_chars* tail from each
    chunk is prepended to the next chunk so that context is not lost at
    boundaries.

    Args:
        transcript: Full transcript text.
        max_chars: Maximum characters per chunk (default 30 000).
        overlap_chars: Characters to overlap between chunks (default 500).

    Returns:
        List of transcript chunks (at least one element).
    """
    if len(transcript) <= max_chars:
        return [transcript]

    paragraphs = transcript.split("\n\n")

    chunks: list[str] = []
    current_chunk = ""

    for para in paragraphs:
        # Would adding this paragraph exceed the limit?
        tentative_len = len(current_chunk) + len(para) + (2 if current_chunk else 0)

        if tentative_len > max_chars:
            if current_chunk:
                stored = current_chunk.strip()
                chunks.append(stored)
                # Start new chunk with overlap from end of stored chunk
                if len(stored) > overlap_chars:
                    overlap = stored[-overlap_chars:]
                else:
                    overlap = stored
                current_chunk = overlap + "\n\n" + para
            else:
                # Single paragraph exceeds limit — force-split by characters
                forced = _force_split(para, max_chars, overlap_chars)
                # All but the last forced chunk are final
                chunks.extend(forced[:-1])
                current_chunk = forced[-1] if forced else ""
        else:
            current_chunk = (current_chunk + "\n\n" + para) if current_chunk else para

    # The remaining current_chunk may still exceed max_chars (e.g. when
    # a large paragraph was appended after an overlap prefix).
    if current_chunk.strip():
        remaining = current_chunk.strip()
        if len(remaining) > max_chars:
            chunks.extend(_force_split(remaining, max_chars, overlap_chars))
        else:
            chunks.append(remaining)

    return chunks


def prepare_for_extraction(
    transcript: str,
    video_id: Optional[str] = None,
    focus_areas: Optional[list[str]] = None,
    max_insights: int = 10,
) -> dict:
    """Prepare transcript for Claude-assisted insight extraction.

    Structures the transcript and creates prompts / metadata that can be
    consumed by the Claude host for extraction.  The actual LLM call
    happens at the Claude host level, not within this function.

    Args:
        transcript: Full transcript text.
        video_id: Optional video ID for reference.
        focus_areas: Focus areas (default: ``["general"]``).
        max_insights: Maximum insights to request.

    Returns:
        Dictionary containing:
        - ``extraction_prompt`` – ready-to-use prompt string
        - ``focus_areas`` – list of resolved focus area names
        - ``categories`` – list of category value strings
        - ``category_definitions`` – mapping of category to description
        - ``transcript_length`` – character count of the transcript
        - ``chunk_count`` – number of chunks produced
        - ``needs_chunking`` – whether the transcript was split
        - ``max_insights`` – echo of the requested limit
        - ``chunks`` – list of chunk strings, or ``None`` if not chunked
    """
    focus_areas = focus_areas or ["general"]
    categories = get_focus_categories(focus_areas)

    chunks = chunk_transcript(transcript)
    needs_chunking = len(chunks) > 1

    return {
        "video_id": video_id,
        "focus_areas": focus_areas,
        "categories": [cat.value for cat in categories],
        "category_definitions": {
            cat.value: CATEGORY_DEFINITIONS[cat] for cat in categories
        },
        "transcript_length": len(transcript),
        "chunk_count": len(chunks),
        "needs_chunking": needs_chunking,
        "max_insights": max_insights,
        "extraction_prompt": build_extraction_prompt(
            chunks[0] if needs_chunking else transcript,
            focus_areas,
            max_insights,
        ),
        "chunks": chunks if needs_chunking else None,
    }
