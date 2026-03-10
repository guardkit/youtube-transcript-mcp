---
id: TASK-SKEL-001
title: Project scaffolding - pyproject.toml, src package, test directories
task_type: scaffolding
parent_review: TASK-REV-87CD
feature_id: FEAT-SKEL-001
wave: 1
implementation_mode: direct
complexity: 1
dependencies: []
status: in_review
priority: high
tags:
- scaffolding
- mcp
- setup
created: 2026-03-06 17:35:00+00:00
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-SKEL-001
  base_branch: main
  started_at: '2026-03-08T13:53:53.421041'
  last_updated: '2026-03-08T13:56:09.462987'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-08T13:53:53.421041'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 125ef9190 by <Task pending name=''Task-101'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
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
