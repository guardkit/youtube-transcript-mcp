# Implementation Guide: Code Quality Fixes

## Overview

This feature addresses code quality issues identified in the TASK-REV-7D5B autobuild review of youtube-transcript-mcp. The codebase is functional and well-tested (96% coverage, 382 tests) but has maintenance debt from the autobuild process.

## Wave 1: Parallel Tasks

### TASK-CQF-001: Test Consolidation + conftest.py

**Approach**: Diff-then-merge strategy.

1. For each overlapping pair, diff the files to identify:
   - Identical tests (remove from root-level file)
   - Unique tests in root-level (move to unit-level)
   - Unique tests in unit-level (keep as-is)

2. Extract shared fixtures:
   - Identify mock patterns used in 3+ test files
   - Create `tests/conftest.py` with `@pytest.fixture` functions
   - Update test files to use fixtures instead of inline mocks

3. Verify:
   - `pytest tests/ -v --tb=short` — all 381+ tests pass
   - `pytest tests/ --cov=src --cov-report=term` — coverage >= 96%

**Risk**: Merging may introduce import order issues. Run tests after each file merge, not just at the end.

### TASK-CQF-002: Lint + Pytest Config

**Approach**: Automated then manual.

1. `ruff check src/ tests/ --fix` — fixes 8 auto-fixable errors
2. Manually fix remaining 5 errors:
   - Inspect each with `ruff check src/ tests/ --output-format=json`
   - Fix individually
3. Add pytest marks to `pyproject.toml`

**Risk**: None — straightforward configuration changes.

## Wave 2: After Wave 1

### TASK-CQF-003: Empty Test Directories

**Decision required**: Remove or populate. Recommendation is to remove.

1. `rm -rf tests/e2e/ tests/protocol/`
2. Verify no references in `pyproject.toml` or test configuration
3. Run tests to confirm

## Testing Strategy

All tasks validated by running the full test suite:
```bash
pytest tests/ -v --tb=short
pytest tests/ --cov=src --cov-report=term
ruff check src/ tests/
```

## Success Criteria

| Metric | Before | After |
|--------|--------|-------|
| Test files with duplication | 3 pairs | 0 |
| conftest.py | Missing | Present with shared fixtures |
| Pytest mark warnings | 5 | 0 |
| Ruff errors | 13 | 0 |
| Empty test directories | 2 | 0 |
| Test count | 381+ passing | 381+ passing (may decrease slightly if duplicates removed) |
| Coverage | 96% | >= 96% |
