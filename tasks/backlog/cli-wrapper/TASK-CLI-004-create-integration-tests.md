---
id: TASK-CLI-004
title: "Create integration tests for CLI with real network calls"
task_type: testing
parent_review: TASK-REV-E5FC
feature_id: FEAT-CLI-001
wave: 4
implementation_mode: task-work
complexity: 2
dependencies:
  - TASK-CLI-001
  - TASK-CLI-002
status: pending
priority: normal
tags: [cli, testing, integration, FEAT-CLI-001]
created: 2026-03-06T10:00:00Z
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
