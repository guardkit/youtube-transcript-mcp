---
id: TASK-CQF-001
title: Consolidate duplicate test files and create shared conftest.py
status: completed
created: 2026-03-10T12:00:00Z
updated: 2026-03-10T12:00:00Z
completed: 2026-03-10T18:00:00Z
completed_location: tasks/completed/TASK-CQF-001/
priority: medium
tags: [testing, code-quality, maintenance]
complexity: 3
task_type: refactor
parent_review: TASK-REV-8D32
feature_id: FEAT-CQF
wave: 1
implementation_mode: task-work
dependencies: []
---

# Task: Consolidate duplicate test files and create shared conftest.py

## Description

Merge overlapping test files between root `tests/` and `tests/unit/` directories, and extract duplicated mock helpers into a shared `tests/conftest.py`. The autobuild created test files in both locations with overlapping coverage.

## Acceptance Criteria

1. `tests/test_transcript_client.py` is merged into `tests/unit/test_transcript.py` (unique tests preserved, duplicates removed)
2. `tests/test_cli.py` is merged into `tests/unit/test_cli.py` (unique tests preserved, duplicates removed)
3. MCP tool regression tests from `tests/test_main_mode_switching.py` that duplicate `tests/unit/test_mcp_tools.py` are removed (unique mode-switching tests preserved)
4. A `tests/conftest.py` exists with shared fixtures extracted from duplicated mock helpers
5. All 381+ passing tests still pass after consolidation (zero test regression)
6. Test coverage remains at 96% or above
7. No test duplication remains between root `tests/` and `tests/unit/`

## Implementation Notes

### Overlapping Files

| Root-level file | Unit-level file | Action |
|-----------------|-----------------|--------|
| `tests/test_transcript_client.py` | `tests/unit/test_transcript.py` | Merge unique tests into unit, delete root |
| `tests/test_cli.py` | `tests/unit/test_cli.py` | Merge unique tests into unit, delete root |
| `tests/test_main_mode_switching.py` | `tests/unit/test_mcp_tools.py` | Remove duplicate MCP tests from mode_switching |

### Shared Fixtures for conftest.py

Common mock patterns to extract:
- `TranscriptClient` mock with configurable responses
- `YouTubeClient` mock with URL parsing responses
- MCP server mock for tool discovery tests
- Standard test video IDs and transcript fixtures

### Approach

1. Diff each pair of overlapping files to identify unique vs duplicate tests
2. Merge unique tests from root-level into `tests/unit/` files
3. Extract common mock helpers into `tests/conftest.py`
4. Delete consolidated root-level files
5. Run full test suite to verify zero regression

## Coach Validation

- `pytest tests/ -v --tb=short` — all tests pass
- `pytest tests/ --cov=src --cov-report=term` — coverage >= 96%
- Verify no remaining test files in root `tests/` that duplicate `tests/unit/`
- Verify `tests/conftest.py` exists and is used by test files
