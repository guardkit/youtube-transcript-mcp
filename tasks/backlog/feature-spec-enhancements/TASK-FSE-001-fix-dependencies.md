---
id: TASK-FSE-001
title: Fix dependency consistency across feature specs
status: backlog
created: 2026-02-03T22:30:00Z
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

## Changes Required

### FEAT-SKEL-001
Update pyproject.toml section to show base dependencies and note about mcp vs fastmcp:

```toml
dependencies = [
    "mcp>=1.0.0",  # Includes FastMCP via mcp.server.fastmcp
]

# Alternative: standalone fastmcp package
# dependencies = ["fastmcp>=2.0,<3"]
```

### FEAT-SKEL-002
Change from:
```toml
dependencies = [
    "mcp>=1.0.0",
    "yt-dlp>=2024.1.0",
]
```

To full list showing cumulative deps.

### FEAT-INT-001
Add `pydantic>=2.0` to dependencies since models use Pydantic v2 features.

## Acceptance Criteria

- [ ] All specs show complete dependency list for their feature
- [ ] mcp vs fastmcp choice is clearly documented
- [ ] pydantic is included in FEAT-INT-001
- [ ] Comments explain each dependency's purpose
