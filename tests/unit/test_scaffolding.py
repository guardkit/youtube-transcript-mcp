"""Tests to verify project scaffolding meets acceptance criteria."""

from pathlib import Path

import tomllib

# Resolve project root relative to this test file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestPyprojectToml:
    """Verify pyproject.toml exists and has correct configuration."""

    def setup_method(self) -> None:
        self.pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert self.pyproject_path.exists(), "pyproject.toml must exist"
        with open(self.pyproject_path, "rb") as f:
            self.config = tomllib.load(f)

    def test_pyproject_exists(self) -> None:
        """AC-001: pyproject.toml exists with correct project metadata."""
        assert self.pyproject_path.exists()
        project = self.config["project"]
        assert "name" in project
        assert "version" in project
        assert "description" in project
        assert "requires-python" in project

    def test_mcp_dependency(self) -> None:
        """AC-002: pyproject.toml declares mcp>=1.0.0 as dependency."""
        deps = self.config["project"]["dependencies"]
        mcp_deps = [d for d in deps if d.startswith("mcp")]
        assert len(mcp_deps) == 1, "Must have exactly one mcp dependency"
        assert "mcp>=1.0.0" in deps

    def test_dev_dependencies(self) -> None:
        """AC-003: pyproject.toml declares dev dependencies."""
        dev_deps = self.config["project"]["optional-dependencies"]["dev"]
        dep_names = [d.split(">=")[0].split(">")[0].split("==")[0].strip() for d in dev_deps]
        assert "pytest" in dep_names
        assert "pytest-asyncio" in dep_names
        assert "pytest-cov" in dep_names
        assert "ruff" in dep_names
        assert "mypy" in dep_names

    def test_pytest_asyncio_mode(self) -> None:
        """AC-004: pyproject.toml configures asyncio_mode = 'auto' for pytest."""
        pytest_config = self.config["tool"]["pytest"]["ini_options"]
        assert pytest_config["asyncio_mode"] == "auto"

    def test_ruff_config(self) -> None:
        """AC-005: pyproject.toml configures ruff with line-length=100, target-version='py310'."""
        ruff_config = self.config["tool"]["ruff"]
        assert ruff_config["line-length"] == 100
        assert ruff_config["target-version"] == "py310"

    def test_mypy_config(self) -> None:
        """AC-006: pyproject.toml configures mypy with python_version='3.10', strict=true."""
        mypy_config = self.config["tool"]["mypy"]
        assert mypy_config["python_version"] == "3.10"
        assert mypy_config["strict"] is True


class TestDirectoryStructure:
    """Verify required directory structure exists."""

    def test_src_init_exists(self) -> None:
        """AC-007: src/__init__.py exists (empty package marker)."""
        init_path = PROJECT_ROOT / "src" / "__init__.py"
        assert init_path.exists(), "src/__init__.py must exist"
        # Verify it's empty (or effectively empty)
        content = init_path.read_text().strip()
        assert content == "", "src/__init__.py should be empty"

    def test_tests_unit_dir_exists(self) -> None:
        """AC-008: tests/unit/ directory exists."""
        unit_dir = PROJECT_ROOT / "tests" / "unit"
        assert unit_dir.exists(), "tests/unit/ directory must exist"
        assert unit_dir.is_dir(), "tests/unit/ must be a directory"

    def test_tests_protocol_dir_exists(self) -> None:
        """AC-009: tests/protocol/ directory exists."""
        protocol_dir = PROJECT_ROOT / "tests" / "protocol"
        assert protocol_dir.exists(), "tests/protocol/ directory must exist"
        assert protocol_dir.is_dir(), "tests/protocol/ must be a directory"


class TestInstallability:
    """Verify project can be installed."""

    def test_build_system_configured(self) -> None:
        """AC-010 prerequisite: build-system is configured in pyproject.toml."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            config = tomllib.load(f)
        assert "build-system" in config
        assert "requires" in config["build-system"]
        assert "build-backend" in config["build-system"]
