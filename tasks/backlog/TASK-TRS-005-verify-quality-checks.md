---
id: TASK-TRS-005
title: "Verify MCP Inspector, linting, and type checking"
task_type: testing
parent_review: TASK-REV-9AD6
feature_id: FEAT-SKEL-003
status: pending
priority: high
wave: 5
implementation_mode: direct
complexity: 2
dependencies:
  - TASK-TRS-003
  - TASK-TRS-004
tags: [verification, quality, linting, mypy]
estimated_minutes: 30
---

# Task: Verify MCP Inspector, Linting, and Type Checking

## Objective

Run all quality gates to verify the transcript tools implementation meets project standards. Both new tools must be visible in MCP Inspector, all code must pass ruff and mypy, and tests must achieve >80% coverage.

## Acceptance Criteria

- [ ] `get_transcript` tool visible in MCP Inspector tool list
- [ ] `list_available_transcripts` tool visible in MCP Inspector tool list
- [ ] `ruff check src/ tests/` passes with zero errors
- [ ] `mypy src/` passes with zero errors
- [ ] `pytest tests/ --cov=src --cov-report=term` shows >80% coverage for transcript modules
- [ ] All existing tests (ping, video_info) still pass (no regressions)

## Verification Steps

### Step 1: Linting
```bash
ruff check src/services/transcript_client.py
ruff check src/__main__.py
ruff check tests/unit/test_transcript.py
```

### Step 2: Type Checking
```bash
mypy src/services/transcript_client.py
mypy src/__main__.py
```

### Step 3: Full Test Suite
```bash
pytest tests/ -v --cov=src --cov-report=term
```

### Step 4: MCP Inspector (Manual)
```bash
# Start server
python -m src

# In another terminal, use MCP Inspector or:
# Verify tools are discoverable via MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m src
```

### Step 5: Regression Check
```bash
# All existing tests must still pass
pytest tests/unit/test_ping.py -v
pytest tests/unit/test_video_info.py -v
```

## Implementation Notes

- If ruff finds issues, fix them in the relevant source files
- If mypy finds type errors, add type annotations as needed
- MCP Inspector verification may be manual if Inspector not installed
- No new files created in this task — verification only
