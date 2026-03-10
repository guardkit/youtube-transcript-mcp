---
id: TASK-CLI-002
title: Update __main__.py with CLI/MCP mode switching
task_type: feature
parent_review: TASK-REV-E5FC
feature_id: FEAT-CLI-001
wave: 2
implementation_mode: task-work
complexity: 2
dependencies:
- TASK-CLI-001
status: in_review
priority: high
tags:
- cli
- entry-point
- FEAT-CLI-001
created: 2026-03-06 10:00:00+00:00
autobuild_state:
  current_turn: 2
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6CE9
  base_branch: main
  started_at: '2026-03-10T06:55:04.219166'
  last_updated: '2026-03-10T07:03:11.613538'
  turns:
  - turn: 1
    decision: feedback
    feedback: '- Coverage threshold not met'
    timestamp: '2026-03-10T06:55:04.219166'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
  - turn: 2
    decision: approve
    feedback: null
    timestamp: '2026-03-10T06:58:31.799003'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Update __main__.py with Mode Switching

## Description

Add mode-switching logic to `src/__main__.py` so that `python -m src` runs the MCP server (existing behaviour) and `python -m src cli <command>` runs the CLI wrapper.

## Acceptance Criteria

- [ ] `python -m src` still starts the MCP server (no regression)
- [ ] `python -m src cli <command>` dispatches to `src.cli.main()`
- [ ] CLI arguments after `cli` are passed correctly (e.g., `python -m src cli get-transcript URL --language fr`)
- [ ] Exit code from CLI is propagated via `sys.exit()`
- [ ] No import of `src.cli` happens in MCP server mode (lazy import)

## Implementation Notes

- Add at bottom of `__main__.py` inside `if __name__ == "__main__":` block
- Check `sys.argv[1] == "cli"` to switch modes
- Pass `sys.argv[2:]` to `src.cli.main()` to strip the `cli` prefix
- Reference: `docs/features/FEAT-CLI-001-cli-wrapper.md` § "Updated Entry Point"
