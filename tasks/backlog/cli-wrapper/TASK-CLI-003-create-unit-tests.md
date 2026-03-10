---
id: TASK-CLI-003
title: Create unit tests for CLI parser and output format
task_type: testing
parent_review: TASK-REV-E5FC
feature_id: FEAT-CLI-001
wave: 3
implementation_mode: task-work
complexity: 2
dependencies:
- TASK-CLI-001
status: in_review
priority: high
tags:
- cli
- testing
- unit-tests
- FEAT-CLI-001
created: 2026-03-06 10:00:00+00:00
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6CE9
  base_branch: main
  started_at: '2026-03-10T06:55:04.216847'
  last_updated: '2026-03-10T06:58:40.646574'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-10T06:55:04.216847'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Create CLI Unit Tests

## Description

Create unit tests covering CLI argument parsing and JSON output format. Tests verify that the argparse configuration is correct and that all commands produce valid JSON on stdout with appropriate exit codes.

## Acceptance Criteria

- [ ] `tests/unit/test_cli.py` exists with `TestCliParser` and `TestCliOutput` classes
- [ ] Parser tests cover all 6 subcommands: ping, video-info, get-transcript, list-transcripts, extract-insights, list-focus-areas
- [ ] Parser tests verify default values (language=en, no_segments=False, focus_areas=general, max_insights=10)
- [ ] Parser tests verify flag parsing (--language, --no-segments, --focus, --video-id, --max-insights)
- [ ] Output tests verify `ping` returns valid JSON with `status=healthy` and `mode=cli`
- [ ] Output tests verify error results produce exit code 1
- [ ] Output tests verify `list-focus-areas` returns all presets
- [ ] All tests pass with `pytest tests/unit/test_cli.py -v`

## Implementation Notes

- Reference: `docs/features/FEAT-CLI-001-cli-wrapper.md` § "Unit Tests" contains complete test code
- Use `capsys` fixture to capture stdout for JSON validation
- Some commands may need mocking if dependent services aren't available yet
- Mark tests that need network access with `@pytest.mark.integration`
