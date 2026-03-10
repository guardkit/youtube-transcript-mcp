---
complexity: 2
created: 2026-03-06 10:00:00+00:00
dependencies:
- TASK-CLI-001
feature_id: FEAT-CLI-001
id: TASK-CLI-003
implementation_mode: task-work
parent_review: TASK-REV-E5FC
priority: high
status: design_approved
tags:
- cli
- testing
- unit-tests
- FEAT-CLI-001
task_type: testing
title: Create unit tests for CLI parser and output format
wave: 3
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