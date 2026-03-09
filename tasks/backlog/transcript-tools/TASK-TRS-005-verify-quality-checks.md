---
id: TASK-TRS-005
title: Verify MCP Inspector, linting, and type checking
task_type: testing
parent_review: TASK-REV-9AD6
feature_id: FEAT-SKEL-003
status: in_review
priority: high
wave: 5
implementation_mode: direct
complexity: 2
dependencies:
- TASK-TRS-003
- TASK-TRS-004
tags:
- verification
- quality
- linting
- mypy
estimated_minutes: 30
autobuild_state:
  current_turn: 3
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6F80
  base_branch: main
  started_at: '2026-03-09T21:58:51.588998'
  last_updated: '2026-03-09T22:07:46.386396'
  turns:
  - turn: 1
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `get_transcript` tool\
      \ visible in MCP Inspector tool list\n  \u2022 `list_available_transcripts`\
      \ tool visible in MCP Inspector tool list\n  \u2022 `ruff check src/ tests/`\
      \ passes with zero errors\n  \u2022 `mypy src/` passes with zero errors\n  \u2022\
      \ All existing tests (ping, video_info) still pass (no regressions)"
    timestamp: '2026-03-09T21:58:51.588998'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 11d0c1e50 by <Task pending name=''Task-666'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 2
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `ruff check src/ tests/`\
      \ passes with zero errors\n  \u2022 `mypy src/` passes with zero errors\n  \u2022\
      \ All existing tests (ping, video_info) still pass (no regressions)"
    timestamp: '2026-03-09T22:03:23.940977'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 11d0c2ed0 by <Task pending name=''Task-676'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 3
    decision: approve
    feedback: null
    timestamp: '2026-03-09T22:05:41.287118'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 11d1f0dd0 by <Task pending name=''Task-772'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
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
