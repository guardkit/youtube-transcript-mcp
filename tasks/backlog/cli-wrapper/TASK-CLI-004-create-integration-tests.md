---
id: TASK-CLI-004
title: Create integration tests for CLI with real network calls
task_type: testing
parent_review: TASK-REV-E5FC
feature_id: FEAT-CLI-001
wave: 4
implementation_mode: task-work
complexity: 2
dependencies:
- TASK-CLI-001
- TASK-CLI-002
status: in_review
priority: normal
tags:
- cli
- testing
- integration
- FEAT-CLI-001
created: 2026-03-06 10:00:00+00:00
autobuild_state:
  current_turn: 1
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-6CE9
  base_branch: main
  started_at: '2026-03-10T07:03:11.631944'
  last_updated: '2026-03-10T07:06:55.234540'
  turns:
  - turn: 1
    decision: approve
    feedback: null
    timestamp: '2026-03-10T07:03:11.631944'
    player_summary: Implementation via task-work delegation
    player_success: true
    coach_success: true
---

# Task: Create CLI Integration Tests

## Description

Create integration tests that exercise the CLI with real YouTube API calls. These tests verify end-to-end functionality including transcript fetching and video metadata retrieval.

## Acceptance Criteria

- [ ] `tests/integration/test_cli_integration.py` exists with `TestCLIIntegration` class
- [ ] Tests marked with `@pytest.mark.slow` and `@pytest.mark.integration`
- [ ] `test_get_transcript_real_video` verifies full transcript fetch for known public video (dQw4w9WgXcQ)
- [ ] `test_video_info_real_video` verifies video metadata fetch
- [ ] All results are valid JSON with expected fields
- [ ] Exit codes are correct (0 for success)
- [ ] Tests can be run selectively: `pytest -m integration`

## Implementation Notes

- Reference: `docs/features/FEAT-CLI-001-cli-wrapper.md` § "Integration Test" contains complete test code
- Uses known stable YouTube video (Rick Astley - Never Gonna Give You Up)
- These tests require network access and may be slow
- Ensure `conftest.py` registers the `slow` and `integration` markers
- These tests depend on FEAT-SKEL-003 (Transcript Tool) and FEAT-SKEL-002 (Video Info Tool) being implemented
