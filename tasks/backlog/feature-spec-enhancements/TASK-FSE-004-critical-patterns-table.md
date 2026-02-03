---
id: TASK-FSE-004
title: Add Critical MCP Patterns table to all specs
status: backlog
created: 2026-02-03T22:30:00Z
priority: medium
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 2
implementation_mode: direct
tags: [documentation, patterns, standardization]
target_files:
  - docs/features/FEAT-SKEL-001-basic-mcp-server.md
  - docs/features/FEAT-SKEL-002-video-info-tool.md
  - docs/features/FEAT-SKEL-003-transcript-tool.md
  - docs/features/FEAT-INT-001-insight-extraction.md
---

# Task: Add Critical MCP Patterns Table to All Specs

## Problem

Each spec has some MCP patterns documented, but the coverage is inconsistent. A standardized table ensures implementers see all critical patterns regardless of which spec they're working on.

## Solution

Add a consistent "Critical MCP Patterns" section to all 4 feature specs.

## Standard Table to Add

Add this section to each spec under "Implementation Notes":

```markdown
## Critical MCP Patterns

These patterns are REQUIRED for correct MCP server behavior.

| # | Pattern | Why | Example |
|---|---------|-----|---------|
| 1 | **stderr logging** | stdout = MCP JSON-RPC protocol | `logging.basicConfig(stream=sys.stderr)` |
| 2 | **Module-level tools** | Required for Claude Code discovery | `@mcp.tool()` at module level in `__main__.py` |
| 3 | **String parameters** | MCP sends all params as strings | `count_int = int(count)` |
| 4 | **Timezone-aware datetime** | `utcnow()` is deprecated | `datetime.now(timezone.utc)` |
| 5 | **Async wrappers** | Don't block event loop | `await asyncio.to_thread(sync_fn)` |
| 6 | **CancelledError** | Must re-raise for cleanup | `except CancelledError: logger.info(...); raise` |
| 7 | **Structured errors** | Consistent error format | `{"error": {"category": "...", "code": "...", "message": "..."}}` |

### Pattern Details

<details>
<summary>1. stderr logging (CRITICAL)</summary>

```python
import sys
import logging

# CORRECT
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# WRONG - breaks MCP protocol
print("Debug")  # stdout corrupts JSON-RPC
logging.basicConfig()  # Defaults to stdout!
```
</details>

<details>
<summary>2. Module-level tool registration</summary>

```python
# CORRECT - in __main__.py at module level
@mcp.tool()
async def my_tool():
    pass

# WRONG - tools registered in functions won't be discovered
def setup():
    @mcp.tool()
    async def my_tool():
        pass
```
</details>

<details>
<summary>3. String parameter conversion</summary>

```python
@mcp.tool()
async def process(count: str, enabled: str) -> dict:
    # MCP sends "10" not 10, "true" not True
    count_int = int(count)
    enabled_bool = enabled.lower() in ("true", "1", "yes")
    return {"count": count_int, "enabled": enabled_bool}
```
</details>
```

## Specs to Update

### FEAT-SKEL-001
Already has a patterns table. Update to match standard format with all 7 patterns.

### FEAT-SKEL-002
Add the full table. Currently only has error response pattern documented.

### FEAT-SKEL-003
Add the full table. Currently mentions async wrapper but not other patterns.

### FEAT-INT-001
Add the full table. Currently shows string param conversion but not complete pattern set.

## Acceptance Criteria

- [ ] All 4 specs have identical "Critical MCP Patterns" section
- [ ] Table includes all 7 patterns
- [ ] Expandable details with code examples
- [ ] Positioned consistently in each spec
