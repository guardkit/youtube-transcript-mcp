---
id: TASK-SKEL-004
title: "Add Claude Desktop configuration template and run quality checks"
task_type: scaffolding
parent_review: TASK-REV-87CD
feature_id: FEAT-SKEL-001
wave: 4
implementation_mode: direct
complexity: 1
dependencies:
  - TASK-SKEL-003
status: pending
priority: normal
tags: [configuration, claude-desktop, quality]
created: 2026-03-06T17:35:00Z
---

# TASK-SKEL-004: Configuration Template + Quality Checks

## Description

Create the `.mcp.json.template` file for Claude Desktop configuration and verify all quality checks pass (ruff, mypy).

## Acceptance Criteria

- [ ] `.mcp.json.template` exists with correct MCP server configuration
- [ ] Template uses placeholder variables `${VENV_PATH}` and `${PROJECT_PATH}`
- [ ] Template includes PYTHONPATH and LOG_LEVEL env vars
- [ ] `ruff check src/ tests/` passes with no errors
- [ ] `mypy src/` passes with no errors (strict mode)
- [ ] MCP Inspector can discover the ping tool (manual verification)

## Implementation Notes

Refer to the feature spec for exact template content:
- [FEAT-SKEL-001 Claude Desktop Config](../../../docs/features/FEAT-SKEL-001-basic-mcp-server.md#claude-desktop-configuration-mcpjsontemplate)

Config file locations for reference:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
