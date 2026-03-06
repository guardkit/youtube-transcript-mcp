---
id: TASK-REV-7005
title: "Plan: implement FEAT-SKEL-002 get_video_info tool using yt-dlp"
status: completed
created: 2026-03-06T00:00:00Z
updated: 2026-03-06T00:00:00Z
priority: high
tags: [review, planning, feat-skel-002, video-info, yt-dlp]
task_type: review
complexity: 4
decision_required: true
feature_ref: FEAT-SKEL-002
review_results:
  mode: decision
  depth: standard
  findings_count: 3
  recommendations_count: 1
  decision: implement
  approach: "Option 1: yt-dlp with service layer"
clarification:
  context_a:
    focus: all
    tradeoff: balanced
  context_b:
    approach: yt-dlp
    testing: standard
---

# Task: Plan: implement FEAT-SKEL-002 get_video_info tool using yt-dlp

## Description

Plan the implementation of the `get_video_info` MCP tool that uses yt-dlp to fetch YouTube video metadata. This tool accepts YouTube URLs or video IDs and returns title, channel, duration, description snippet, and caption availability.

## Context

- Feature spec: docs/features/FEAT-SKEL-002-video-info-tool.md
- Dependency: FEAT-SKEL-001 (Basic MCP Server)
- Complexity: 4/10
- Key patterns: async wrapper for sync yt-dlp, structured error responses, URL parsing

## Review Focus

- All aspects (technical feasibility, architecture, testing, error handling)
- Trade-off priority: Balanced

## Acceptance Criteria

- [x] Technical options analyzed (3 options: yt-dlp, pytubefix, YouTube API)
- [x] Architecture implications reviewed (service layer pattern)
- [x] Effort estimation provided (3-4 hours, complexity 4/10)
- [x] Risk analysis completed (low risk, yt-dlp reliability)
- [x] Implementation breakdown created (5 subtasks in 3 waves)

## Implementation Notes

Decision: Option 1 — Direct yt-dlp integration with YouTubeClient service layer.

Implementation structure created at: `tasks/backlog/video-info-tool/`
Feature YAML: `.guardkit/features/FEAT-2AAA.yaml`

Subtasks:
1. TASK-VID-001: Add yt-dlp dependency (Wave 1, direct)
2. TASK-VID-002: Create YouTubeClient service (Wave 1, task-work)
3. TASK-VID-003: Register get_video_info tool (Wave 2, task-work)
4. TASK-VID-004: Create unit tests (Wave 2, task-work)
5. TASK-VID-005: Verify MCP Inspector + linting (Wave 3, direct)
