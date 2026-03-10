# Code Quality Fixes: youtube-transcript-mcp

## Problem Statement

The TASK-REV-7D5B autobuild review (82/100) identified several code quality issues in the youtube-transcript-mcp codebase. While the server is functional and well-tested (96% coverage, 382 tests), there are maintenance and hygiene improvements needed:

1. **Test file duplication** — Multiple test files cover the same functionality (root `tests/` and `tests/unit/` overlap)
2. **No shared test fixtures** — Mock helpers duplicated across test files; no `conftest.py`
3. **Unregistered pytest marks** — `seam` and `integration_contract` marks produce 5 warnings
4. **13 ruff lint errors** — 8 auto-fixable, 5 manual
5. **Empty test directories** — `tests/e2e/` and `tests/protocol/` exist with no tests

## Solution Approach

Three implementation tasks:

1. **TASK-CQF-001**: Consolidate test files and create shared conftest.py
2. **TASK-CQF-002**: Fix lint configuration (pytest marks + ruff errors)
3. **TASK-CQF-003**: Clean up empty test directories

## Source

- Parent review: TASK-REV-8D32 (GuardKit analysis)
- Source review: TASK-REV-7D5B (youtube-transcript-mcp autobuild review)
- Review report: GuardKit repo `.claude/reviews/TASK-REV-8D32-review-report.md`

## Execution Strategy

```
Wave 1 (parallel):
  TASK-CQF-001: Test consolidation + conftest
  TASK-CQF-002: Lint + pytest config fixes

Wave 2:
  TASK-CQF-003: Empty test directory cleanup
```
