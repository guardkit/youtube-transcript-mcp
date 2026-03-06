---
id: TASK-REV-9AD6
title: "Plan: implement FEAT-SKEL-003 get_transcript and list_available_transcripts tools"
status: completed
created: 2026-03-06T00:00:00Z
updated: 2026-03-06T00:00:00Z
priority: high
tags: [review, planning, transcript, mcp-tool, feat-skel-003]
task_type: review
complexity: 5
decision_required: true
review_results:
  mode: decision
  depth: standard
  score: 87
  findings_count: 3
  recommendations_count: 1
  decision: implement
  approach: "Direct feature spec implementation"
clarification:
  context_a:
    focus: all
    tradeoff: quality
  context_b:
    approach: direct_spec
    execution: sequential
    testing: standard
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Plan FEAT-SKEL-003 Transcript Tools

## Description

Plan the implementation of FEAT-SKEL-003: get_transcript and list_available_transcripts MCP tools. This feature adds YouTube transcript fetching capabilities using youtube-transcript-api with intelligent language fallback.

## Context

- **Feature Spec**: docs/features/FEAT-SKEL-003-transcript-tool.md
- **Dependency**: FEAT-SKEL-001 (Basic MCP Server)
- **Complexity**: 5/10
- **Estimated Time**: 4-5 hours

## Key Components

1. TranscriptClient service (`src/services/transcript_client.py`)
2. `get_transcript` MCP tool registration
3. `list_available_transcripts` MCP tool registration
4. Language fallback strategy (requested → auto-generated → English → first available)
5. Unit tests with mocked youtube-transcript-api
6. pyproject.toml dependency addition

## Review Focus

- All aspects (comprehensive analysis)
- Trade-off priority: Quality/reliability

## Acceptance Criteria

- [ ] Technical options analyzed for transcript implementation
- [ ] Architecture implications assessed
- [ ] Risk analysis completed
- [ ] Implementation breakdown created
- [ ] Decision checkpoint reached

## Implementation Notes

**Decision**: Implement (Option 1: Direct Feature Spec Implementation)

**Generated artifacts**:
- Feature folder: `tasks/backlog/transcript-tools/`
- Feature YAML: `.guardkit/features/FEAT-6F80.yaml`
- 5 subtasks: TASK-TRS-001 through TASK-TRS-005
- Implementation guide with data flow, integration contract, and task dependency diagrams

**Subtask summary**:
1. TASK-TRS-001: Add youtube-transcript-api dependency (scaffolding, 1/10)
2. TASK-TRS-002: Create TranscriptClient service (feature, 5/10)
3. TASK-TRS-003: Register MCP tools (feature, 4/10)
4. TASK-TRS-004: Create unit tests (testing, 4/10)
5. TASK-TRS-005: Verify quality checks (testing, 2/10)
