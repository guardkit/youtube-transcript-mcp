"""Tests to verify youtube-transcript-api dependency is correctly installed."""

import importlib
import subprocess
import sys
from pathlib import Path


def test_youtube_transcript_api_importable():
    """AC-003: youtube_transcript_api can be imported."""
    mod = importlib.import_module("youtube_transcript_api")
    assert hasattr(mod, "YouTubeTranscriptApi")


def test_youtube_transcript_api_class_accessible():
    """Verify YouTubeTranscriptApi class is accessible and usable."""
    from youtube_transcript_api import YouTubeTranscriptApi

    assert YouTubeTranscriptApi is not None


def test_pyproject_contains_dependency():
    """AC-001: pyproject.toml contains youtube-transcript-api>=1.0.0."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    content = pyproject_path.read_text()
    assert "youtube-transcript-api>=1.0.0" in content


def test_youtube_transcript_api_version():
    """Verify installed version meets minimum requirement."""
    import importlib.metadata

    version = importlib.metadata.version("youtube-transcript-api")
    major, minor, *_ = version.split(".")
    assert int(major) >= 1, f"Expected version >= 1.0.0, got {version}"
