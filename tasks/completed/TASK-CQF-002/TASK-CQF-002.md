---
id: TASK-CQF-002
title: Fix lint errors and register custom pytest marks
status: completed
created: 2026-03-10T12:00:00Z
updated: 2026-03-10T12:35:00Z
completed: 2026-03-10T12:35:00Z
priority: low
tags: [lint, pytest, configuration, code-quality]
complexity: 2
task_type: infrastructure
parent_review: TASK-REV-8D32
feature_id: FEAT-CQF
wave: 1
implementation_mode: direct
dependencies: []
---

# Task: Fix lint errors and register custom pytest marks

## Description

Fix the 13 remaining ruff lint errors and register the unregistered `seam` and `integration_contract` pytest marks in `pyproject.toml`.

## Acceptance Criteria

1. `ruff check src/ tests/` reports zero errors
2. `seam` and `integration_contract` marks are registered in `pyproject.toml` under `[tool.pytest.ini_options]`
3. `pytest tests/ -v` produces zero warnings about unregistered marks
4. All existing tests still pass

## Implementation Notes

### Ruff Errors

- 8 auto-fixable: Run `ruff check src/ tests/ --fix`
- 5 manual fixes required:
  - 1 unused import `VideoNotFoundError` — remove or mark as `__all__` export
  - Remaining 4 — inspect and fix individually

### Pytest Marks

Add to `[tool.pytest.ini_options]` `markers` list in `pyproject.toml`:

```toml
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests requiring network access (run with '-m integration')",
    "seam: marks seam tests verifying cross-module contracts",
    "integration_contract: marks integration contract tests",
]
```

## Coach Validation

- `ruff check src/ tests/` — zero errors
- `pytest tests/ -v` — zero unregistered mark warnings
- `pytest tests/ -v --tb=short` — all tests pass
