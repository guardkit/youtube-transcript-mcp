---
id: TASK-FSE-001
title: Fix dependency consistency across feature specs
status: completed
created: 2026-02-03T22:30:00Z
updated: 2026-02-03T23:10:00Z
completed: 2026-02-03T23:10:00Z
priority: high
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 1
implementation_mode: direct
tags: [documentation, dependencies, pyproject]
target_files:
  - docs/features/FEAT-SKEL-001-basic-mcp-server.md
  - docs/features/FEAT-SKEL-002-video-info-tool.md
  - docs/features/FEAT-INT-001-insight-extraction.md
previous_state: in_review
state_transition_reason: "Task completed - all acceptance criteria met"
workflow_mode: micro
completed_location: tasks/completed/TASK-FSE-001/
duration_actual: "~5 minutes"
---

# Task: Fix Dependency Consistency

## Problem

The pyproject.toml snippets in feature specs show inconsistent dependencies:
- FEAT-SKEL-001 shows `fastmcp>=2.0,<3`
- FEAT-SKEL-002 shows `mcp>=1.0.0`
- FEAT-INT-001 doesn't explicitly show pydantic

This will cause confusion during implementation.

## Solution

Standardize all pyproject.toml snippets to show the complete dependency set:

```toml
[project]
dependencies = [
    "mcp>=1.0.0",                    # MCP SDK (includes FastMCP)
    "yt-dlp>=2024.1.0",              # Video metadata
    "youtube-transcript-api>=1.0.0", # Transcript fetching
    "pydantic>=2.0",                 # Data validation
]
```

## Changes Made

### FEAT-SKEL-001 ✅
Updated pyproject.toml section to show base dependencies with mcp vs fastmcp choice documented:
```toml
dependencies = [
    "mcp>=1.0.0",        # MCP SDK - includes FastMCP via mcp.server.fastmcp
]

# Alternative: standalone fastmcp package (if not using MCP SDK)
# dependencies = ["fastmcp>=2.0,<3"]
```

### FEAT-SKEL-002 ✅
Updated to include explanatory comments:
```toml
dependencies = [
    "mcp>=1.0.0",        # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",  # YouTube video metadata extraction
]
```

### FEAT-SKEL-003 ✅ (bonus - not in original scope)
Updated for consistency:
```toml
dependencies = [
    "mcp>=1.0.0",                    # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",              # YouTube video metadata extraction
    "youtube-transcript-api>=1.0.0", # Transcript fetching (official API)
]
```

### FEAT-INT-001 ✅
Added explicit pyproject.toml section with pydantic:
```toml
dependencies = [
    "mcp>=1.0.0",                    # MCP SDK - includes FastMCP via mcp.server.fastmcp
    "yt-dlp>=2024.1.0",              # YouTube video metadata extraction
    "youtube-transcript-api>=1.0.0", # Transcript fetching
    "pydantic>=2.0",                 # Data validation (v2 features: Field, BaseModel)
]
```

## Acceptance Criteria

- [x] All specs show complete dependency list for their feature
- [x] mcp vs fastmcp choice is clearly documented
- [x] pydantic is included in FEAT-INT-001
- [x] Comments explain each dependency's purpose

## Completion Summary

| Metric | Value |
|--------|-------|
| Files Modified | 4 (3 target + 1 bonus) |
| Duration | ~5 minutes |
| Workflow Mode | Micro-task |
| Quality Gates | N/A (documentation) |

