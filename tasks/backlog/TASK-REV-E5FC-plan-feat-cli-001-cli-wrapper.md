---
id: TASK-REV-E5FC
title: "Plan: implement FEAT-CLI-001 CLI wrapper for all MCP tools with JSON stdout output"
status: review_complete
created: 2026-03-06T10:00:00Z
updated: 2026-03-06T10:30:00Z
review_results:
  mode: decision
  depth: standard
  findings_count: 3
  recommendations_count: 1
  decision: implement
  approach: argparse_as_specified
priority: high
task_type: review
tags: [cli, feature-planning, FEAT-CLI-001]
complexity: 3
feature: FEAT-CLI-001
test_results:
  status: pending
  coverage: null
  last_run: null
---

# Task: Plan FEAT-CLI-001 CLI Wrapper

## Description

Plan the implementation of FEAT-CLI-001: a CLI wrapper that provides command-line access to all MCP tools, outputting JSON to stdout. This enables use from deep agents, shell scripts, cron jobs, and direct terminal usage without requiring the MCP transport layer.

## Context

- Feature spec: docs/features/FEAT-CLI-001-cli-wrapper.md
- Complexity: 3/10 (Low)
- Dependencies: FEAT-SKEL-003 (Transcript Tool), FEAT-INT-001 (Insight Extraction)
- Architecture: Single entry point with mode switching (MCP vs CLI)
- Key constraint: stdout is JSON only, all logging to stderr

## Review Focus

- All aspects (comprehensive analysis)
- Trade-off priority: Speed of delivery

## Acceptance Criteria

- [x] Technical options analysis completed
- [x] Implementation approach recommended (argparse as specified)
- [x] Subtask breakdown created (4 tasks in tasks/backlog/cli-wrapper/)
- [x] Risk assessment completed

## Clarification Decisions

### Context A (Review Scope)
- Focus: All aspects
- Trade-off priority: Speed of delivery

### Context B (Implementation Preferences)
- Approach: argparse as specified in FEAT-CLI-001
- Execution: Sequential
- Testing: Standard (quality gates)

## Generated Artefacts
- Feature folder: `tasks/backlog/cli-wrapper/`
- Feature YAML: `.guardkit/features/FEAT-6CE9.yaml`
- Implementation guide: `tasks/backlog/cli-wrapper/IMPLEMENTATION-GUIDE.md`
