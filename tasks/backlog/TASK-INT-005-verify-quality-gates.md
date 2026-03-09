---
id: TASK-INT-005
title: "Verify quality gates and integration"
task_type: testing
parent_review: TASK-REV-A880
feature_id: FEAT-INT-001
wave: 5
implementation_mode: direct
complexity: 2
dependencies:
  - TASK-INT-004
status: pending
priority: high
tags: [insight-extraction, quality, verification]
---

# Task: Verify Quality Gates and Integration

## Description

Run all quality checks to verify FEAT-INT-001 implementation meets standards. This includes linting, type checking, test coverage, and regression verification against existing tests.

## Acceptance Criteria

- [ ] `ruff check src/ tests/` passes with zero errors
- [ ] `mypy src/` passes with zero errors
- [ ] `pytest tests/ -v` — all tests pass
- [ ] `pytest tests/ --cov=src --cov-report=term` — >80% coverage overall
- [ ] `src/models/insight.py` has >90% coverage
- [ ] `src/services/insight_extractor.py` has >90% coverage
- [ ] No regressions in existing tests (test_ping, test_video_info, test_transcript if they exist)
- [ ] Both `extract_insights` and `list_focus_areas` tools are discoverable via MCP
- [ ] `pydantic>=2.0` is listed in pyproject.toml dependencies (if not already)

## Implementation Notes

Quality gate commands:
```bash
ruff check src/ tests/
mypy src/
pytest tests/ -v
pytest tests/ --cov=src --cov-report=term
```

If any quality gate fails, fix the issue in the relevant source file and re-run.
