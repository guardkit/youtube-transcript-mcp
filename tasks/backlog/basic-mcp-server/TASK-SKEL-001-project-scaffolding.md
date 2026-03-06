---
id: TASK-SKEL-001
title: "Project scaffolding - pyproject.toml, src package, test directories"
task_type: scaffolding
parent_review: TASK-REV-87CD
feature_id: FEAT-SKEL-001
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
status: pending
priority: high
tags: [scaffolding, mcp, setup]
created: 2026-03-06T17:35:00Z
---

# TASK-SKEL-001: Project Scaffolding

## Description

Create the foundational project structure for the YouTube Transcript MCP server. This includes `pyproject.toml` with dependencies, the `src/` package with `__init__.py`, and the `tests/` directory structure.

## Acceptance Criteria

- [ ] `pyproject.toml` exists with correct project metadata
- [ ] `pyproject.toml` declares `mcp>=1.0.0` as dependency
- [ ] `pyproject.toml` declares dev dependencies: pytest, pytest-asyncio, pytest-cov, ruff, mypy
- [ ] `pyproject.toml` configures `asyncio_mode = "auto"` for pytest
- [ ] `pyproject.toml` configures ruff with `line-length = 100`, `target-version = "py310"`
- [ ] `pyproject.toml` configures mypy with `python_version = "3.10"`, `strict = true`
- [ ] `src/__init__.py` exists (empty package marker)
- [ ] `tests/unit/` directory exists
- [ ] `tests/protocol/` directory exists
- [ ] Project is installable with `pip install -e ".[dev]"`

## Implementation Notes

Refer to the feature spec for exact `pyproject.toml` content:
- [FEAT-SKEL-001-basic-mcp-server.md](../../../docs/features/FEAT-SKEL-001-basic-mcp-server.md#project-configuration-pyprojecttoml)

Key patterns:
- Build system: hatchling
- Python requirement: `>=3.10`
- Package discovery: `src/` layout
