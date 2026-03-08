---
complexity: 2
created: 2026-03-06 17:35:00+00:00
dependencies:
- TASK-SKEL-001
feature_id: FEAT-SKEL-001
id: TASK-SKEL-002
implementation_mode: task-work
parent_review: TASK-REV-87CD
priority: high
status: design_approved
tags:
- mcp
- fastmcp
- ping
- health-check
task_type: feature
title: Implement FastMCP server entry point with ping health check tool
wave: 2
---

# TASK-SKEL-002: FastMCP Server with Ping Tool

## Description

Implement the MCP server entry point in `src/__main__.py` using FastMCP from the official `mcp` package. Register a `ping` health check tool at module level that returns server status with version and UTC timestamp.

## Acceptance Criteria

- [ ] `src/__main__.py` imports FastMCP from `mcp.server.fastmcp`
- [ ] Logging configured to stderr only (`stream=sys.stderr`)
- [ ] FastMCP instance created with name `youtube-transcript-mcp`, version `0.1.0`
- [ ] `ping` tool registered at module level with `@mcp.tool()` decorator
- [ ] `ping` returns dict with: status, server name, version, UTC ISO timestamp
- [ ] Timestamp uses `datetime.now(timezone.utc)` (not `utcnow()`)
- [ ] Server runs with `mcp.run(transport="stdio")` in `__main__` block
- [ ] No print statements to stdout (would break MCP protocol)
- [ ] Server starts without errors: `python -m src`

## Critical MCP Patterns

| Pattern | Requirement |
|---------|-------------|
| stderr logging | `logging.basicConfig(stream=sys.stderr)` |
| Module-level tools | `@mcp.tool()` at top level in `__main__.py` |
| Timezone-aware datetime | `datetime.now(timezone.utc)` |
| No stdout | Zero `print()` calls |

## Implementation Notes

Refer to the feature spec for exact implementation code:
- [FEAT-SKEL-001-basic-mcp-server.md](../../../docs/features/FEAT-SKEL-001-basic-mcp-server.md#server-entry-point-src__main__py)