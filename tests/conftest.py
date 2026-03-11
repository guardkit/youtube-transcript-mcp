"""Shared test fixtures for youtube-insights-mcp test suite.

Provides common mock helpers for transcript API responses, eliminating
duplication across test modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

# ---------------------------------------------------------------------------
# Mock data classes matching youtube-transcript-api v1.2+ response structure
# ---------------------------------------------------------------------------


@dataclass
class MockSnippet:
    """Mock FetchedTranscriptSnippet with .start, .duration, .text."""

    start: float
    duration: float
    text: str


@dataclass
class MockTranscript:
    """Mock FetchedTranscript returned by api.fetch().

    Attributes match youtube-transcript-api v1.2+: .snippets, .language,
    .language_code, .is_generated.
    """

    language: str
    language_code: str
    is_generated: bool
    snippets: list[MockSnippet]


# ---------------------------------------------------------------------------
# Factory fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_transcript() -> MockTranscript:
    """Create a default mock transcript response with 3 segments."""
    return make_mock_transcript()


def make_mock_transcript(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    snippets: list[MockSnippet] | None = None,
) -> MockTranscript:
    """Create a mock transcript with sensible defaults."""
    if snippets is None:
        snippets = [
            MockSnippet(start=0.0, duration=2.5, text="Hello world"),
            MockSnippet(start=2.5, duration=3.0, text="This is a test"),
            MockSnippet(start=5.5, duration=2.0, text="Thank you"),
        ]
    return MockTranscript(
        language=language,
        language_code=language_code,
        is_generated=is_generated,
        snippets=snippets,
    )


def make_transcript_info(
    language: str = "English",
    language_code: str = "en",
    is_generated: bool = False,
    fetched: MockTranscript | None = None,
) -> MagicMock:
    """Create a mock transcript-list entry (iterable item from api.list()).

    Uses MagicMock for transcript list iteration (__iter__).
    """
    info = MagicMock()
    info.language = language
    info.language_code = language_code
    info.is_generated = is_generated
    info.fetch.return_value = fetched or make_mock_transcript(
        language=language,
        language_code=language_code,
        is_generated=is_generated,
    )
    return info
