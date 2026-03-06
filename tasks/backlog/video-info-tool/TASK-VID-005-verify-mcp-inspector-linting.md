---
id: TASK-VID-005
title: "Verify tool in MCP Inspector and run linting"
status: pending
created: 2026-03-06T00:00:00Z
updated: 2026-03-06T00:00:00Z
priority: normal
tags: [verification, linting, feat-skel-002]
task_type: testing
parent_review: TASK-REV-7005
feature_id: FEAT-SKEL-002
wave: 3
implementation_mode: direct
complexity: 1
dependencies:
  - TASK-VID-003
  - TASK-VID-004
---

# Task: Verify tool in MCP Inspector and run linting

## Description

Final verification step: run `ruff check`, `mypy`, and confirm the `get_video_info` tool is discoverable via MCP Inspector.

## Acceptance Criteria

- [ ] `ruff check src/ tests/` passes with no errors
- [ ] `mypy src/` passes with no errors
- [ ] `get_video_info` tool visible in MCP Inspector (`npx @anthropic-ai/mcp-inspector python -m src`)
- [ ] Tool shows correct parameter schema (video_url: string)
- [ ] Tool docstring visible for LLM discovery
- [ ] All existing tests still pass: `pytest tests/ -v`

## Implementation Notes

```bash
# Linting
ruff check src/ tests/
ruff format --check src/ tests/

# Type checking
mypy src/

# MCP Inspector
npx @anthropic-ai/mcp-inspector python -m src

# Full test suite
pytest tests/ -v --cov=src --cov-report=term
```
