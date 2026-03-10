---
id: TASK-CQF-003
title: Clean up empty test directories
status: in_review
created: 2026-03-10T12:00:00Z
updated: 2026-03-10T12:30:00Z
previous_state: backlog
priority: low
tags: [testing, cleanup, code-quality]
complexity: 1
task_type: infrastructure
parent_review: TASK-REV-8D32
feature_id: FEAT-CQF
wave: 2
implementation_mode: direct
dependencies: [TASK-CQF-001]
---

# Task: Clean up empty test directories

## Description

The `tests/e2e/` and `tests/protocol/` directories exist but contain no test files. These were created during the autobuild as placeholders for planned test categories that were never implemented.

## Acceptance Criteria

1. Either add placeholder test files with clear docstrings explaining planned test categories, OR remove the empty directories entirely
2. If directories are removed, ensure no imports or configuration reference them
3. All existing tests still pass

## Implementation Notes

### Current State

- `tests/e2e/` — empty directory
- `tests/protocol/` — contains only `__pycache__/`

### Decision

**Recommended: Remove the empty directories.** They create confusion about what testing exists. If e2e or protocol tests are needed later, they can be created at that time.

If keeping, add a `test_placeholder.py` with:
```python
"""E2E tests for youtube-transcript-mcp.

TODO: Implement end-to-end tests covering:
- Full MCP protocol round-trip
- Real YouTube API integration
"""
```

## Coach Validation

- Verify directories removed or populated
- `pytest tests/ -v --tb=short` — all tests pass
