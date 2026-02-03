---
id: TASK-FSE-003
title: Add mcp vs fastmcp package clarification
status: completed
created: 2026-02-03T22:30:00Z
updated: 2026-02-03T23:05:00Z
completed: 2026-02-03T23:05:00Z
priority: medium
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 2
implementation_mode: direct
tags: [documentation, installation, fastmcp]
target_files:
  - docs/features/FEAT-SKEL-001-basic-mcp-server.md
workflow:
  mode: micro
  intensity: minimal
  duration_seconds: 60
  phases_executed: [1, 3, 4, 5]
  phases_skipped: [2, 2.5A, 2.5B, 2.7, 2.8]
completion:
  verified_criteria:
    - "FEAT-SKEL-001 has Package Choice section (line 37)"
    - "Clear recommendation for mcp package (lines 65-71)"
    - "Code examples use mcp.server.fastmcp import (lines 47, 75, 97)"
    - "pyproject.toml shows mcp>=1.0.0 (line 145)"
  quality_gates:
    documentation: passed
    syntax_valid: passed
  location: tasks/completed/feature-spec-enhancements/TASK-FSE-003/
---

# Task: Add mcp vs fastmcp Package Clarification

## Problem

The spec shows `from fastmcp import FastMCP` but doesn't clarify that FastMCP is available from two different packages:
1. `mcp` - Official MCP SDK (includes FastMCP)
2. `fastmcp` - Standalone FastMCP package

This causes confusion about which to install.

## Solution

Add a clear "Package Choice" section to FEAT-SKEL-001 explaining the options.

## Content to Add

Add after the "Installation" section:

```markdown
### Package Choice: mcp vs fastmcp

FastMCP is available from two packages. Choose ONE:

#### Option A: mcp package (Recommended)
```bash
pip install mcp
```

```python
from mcp.server.fastmcp import FastMCP
```

**Pros**: Official Anthropic package, includes full MCP SDK, stable API
**Cons**: Slightly larger install

#### Option B: fastmcp standalone
```bash
pip install 'fastmcp<3'
```

```python
from fastmcp import FastMCP
```

**Pros**: Smaller install, latest features in 3.x beta
**Cons**: Separate from official SDK

#### Recommendation

For this project, use **Option A** (`mcp` package) because:
- Official support from Anthropic
- More likely to stay compatible with Claude Desktop
- Simpler dependency management

Update imports accordingly:
```python
# Use this import
from mcp.server.fastmcp import FastMCP

# NOT this
from fastmcp import FastMCP
```
```

## Also Update

Update the code example in "Server Entry Point" section to use the mcp package import:

```python
# Change from:
from fastmcp import FastMCP

# To:
from mcp.server.fastmcp import FastMCP
```

## Acceptance Criteria

- [x] FEAT-SKEL-001 has "Package Choice" section explaining both options
- [x] Clear recommendation for which to use
- [x] Code examples updated to use `mcp.server.fastmcp` import
- [x] pyproject.toml shows `mcp>=1.0.0` as dependency
