"""Tests to verify project dependencies are correctly installed."""

import importlib
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib  # type: ignore[import]
    except ImportError:
        import tomli as tomllib  # type: ignore[import,no-redef]

from pathlib import Path


def test_ytdlp_importable():
    """AC-003: yt-dlp can be imported successfully."""
    import yt_dlp

    assert yt_dlp is not None


def test_ytdlp_version_accessible():
    """AC-003: yt-dlp version is accessible."""
    import yt_dlp

    version = yt_dlp.version.__version__
    assert version is not None
    assert isinstance(version, str)
    assert len(version) > 0


def test_ytdlp_in_pyproject_dependencies():
    """AC-001: yt-dlp>=2024.1.0 is listed in pyproject.toml dependencies."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
    assert pyproject_path.exists(), f"pyproject.toml not found at {pyproject_path}"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dependencies = data.get("project", {}).get("dependencies", [])
    ytdlp_deps = [dep for dep in dependencies if dep.startswith("yt-dlp")]
    assert len(ytdlp_deps) == 1, f"Expected exactly one yt-dlp dependency, found: {ytdlp_deps}"
    assert ytdlp_deps[0] == "yt-dlp>=2024.1.0", f"Unexpected yt-dlp spec: {ytdlp_deps[0]}"


def test_ytdlp_has_youtube_dl_class():
    """Verify yt-dlp provides the core YoutubeDL class needed for video info extraction."""
    from yt_dlp import YoutubeDL

    assert YoutubeDL is not None
    assert callable(YoutubeDL)


def test_mcp_dependency_still_present():
    """Verify the existing mcp dependency was not removed when adding yt-dlp."""
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    dependencies = data.get("project", {}).get("dependencies", [])
    mcp_deps = [dep for dep in dependencies if dep.startswith("mcp")]
    assert len(mcp_deps) >= 1, "mcp dependency should still be present in pyproject.toml"
