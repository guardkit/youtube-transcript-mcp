---
id: TASK-CLI-001
title: Create src/cli.py with argparse parser and command dispatch
task_type: feature
parent_review: TASK-REV-E5FC
feature_id: FEAT-CLI-001
wave: 1
implementation_mode: task-work
complexity: 3
dependencies: []
status: in_review
priority: high
tags:
- cli
- argparse
- FEAT-CLI-001
created: 2026-03-06 10:00:00+00:00
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6CE9
  base_branch: main
  started_at: '2026-03-10T06:48:31.446752'
  last_updated: '2026-03-10T06:55:02.989169'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-10T06:48:31.446752'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Create CLI Module (src/cli.py)

## Description

Create the CLI entry point module that wraps all MCP tool functions as CLI commands with JSON stdout output. Uses argparse for argument parsing and delegates to the same service classes used by MCP tools.

**Approach**: argparse as specified in FEAT-CLI-001 feature spec.

## Acceptance Criteria

- [ ] `src/cli.py` exists with `make_parser()`, `output_json()`, `exit_code_from_result()`, `run_command()`, and `main()` functions
- [ ] Subcommands registered: `ping`, `video-info`, `get-transcript`, `list-transcripts`, `extract-insights`, `list-focus-areas`
- [ ] All stdout output is valid JSON via `output_json()` only
- [ ] All logging goes to stderr
- [ ] `--help` works on all subcommands with clear argument descriptions
- [ ] Exit code 0 on success, 1 on error (based on `"error"` key in result dict)
- [ ] `extract-insights` supports `-` for stdin input (pipe support)
- [ ] `get-transcript` supports `--language` and `--no-segments` flags
- [ ] `extract-insights` supports `--focus`, `--video-id`, and `--max-insights` flags
- [ ] Async command dispatch via `asyncio.run()`

## Implementation Notes

- Reference: `docs/features/FEAT-CLI-001-cli-wrapper.md` contains the full implementation code
- Critical constraint: stdout is JSON only - no print statements outside `output_json()`
- Import services lazily inside `run_command()` to avoid import errors when services not yet available
- Use `datetime.now(timezone.utc)` not `utcnow()` (per MCP patterns)
- Structured error responses with category/code/message format
