---
id: TASK-SKEL-004
title: Add Claude Desktop configuration template and run quality checks
task_type: scaffolding
parent_review: TASK-REV-87CD
feature_id: FEAT-SKEL-001
wave: 4
implementation_mode: direct
complexity: 1
dependencies:
- TASK-SKEL-003
status: in_review
priority: normal
tags:
- configuration
- claude-desktop
- quality
created: 2026-03-06 17:35:00+00:00
autobuild_state:
  current_turn: 6
  max_turns: 25
  worktree_path: /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.guardkit/worktrees/FEAT-SKEL-001
  base_branch: main
  started_at: '2026-03-08T14:03:32.246022'
  last_updated: '2026-03-08T14:18:35.727335'
  turns:
  - turn: 1
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 MCP Inspector can discover\
      \ the ping tool (manual verification)"
    timestamp: '2026-03-08T14:03:32.246022'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 130ad0dd0 by <Task pending name=''Task-544'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 2
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `.mcp.json.template` exists\
      \ with correct MCP server configuration\n  \u2022 Template uses placeholder\
      \ variables `${VENV_PATH}` and `${PROJECT_PATH}`\n  \u2022 Template includes\
      \ PYTHONPATH and LOG_LEVEL env vars\n  \u2022 `ruff check src/ tests/` passes\
      \ with no errors\n  \u2022 `mypy src/` passes with no errors (strict mode)"
    timestamp: '2026-03-08T14:07:00.397908'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 130f9bd10 by <Task pending name=''Task-640'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 3
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `.mcp.json.template` exists\
      \ with correct MCP server configuration\n  \u2022 Template uses placeholder\
      \ variables `${VENV_PATH}` and `${PROJECT_PATH}`\n  \u2022 Template includes\
      \ PYTHONPATH and LOG_LEVEL env vars\n  \u2022 `ruff check src/ tests/` passes\
      \ with no errors\n  \u2022 `mypy src/` passes with no errors (strict mode)\n\
      \  (1 more)"
    timestamp: '2026-03-08T14:10:09.380081'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 131488950 by <Task pending name=''Task-971'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 4
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `.mcp.json.template` exists\
      \ with correct MCP server configuration\n  \u2022 Template uses placeholder\
      \ variables `${VENV_PATH}` and `${PROJECT_PATH}`\n  \u2022 Template includes\
      \ PYTHONPATH and LOG_LEVEL env vars\n  \u2022 `ruff check src/ tests/` passes\
      \ with no errors\n  \u2022 `mypy src/` passes with no errors (strict mode)\n\
      \  (1 more)"
    timestamp: '2026-03-08T14:12:03.813393'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 13140d490 by <Task pending name=''Task-1153'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 5
    decision: feedback
    feedback: "- Not all acceptance criteria met:\n  \u2022 `.mcp.json.template` exists\
      \ with correct MCP server configuration\n  \u2022 Template uses placeholder\
      \ variables `${VENV_PATH}` and `${PROJECT_PATH}`\n  \u2022 Template includes\
      \ PYTHONPATH and LOG_LEVEL env vars\n  \u2022 `ruff check src/ tests/` passes\
      \ with no errors\n  \u2022 `mypy src/` passes with no errors (strict mode)\n\
      \  (1 more)"
    timestamp: '2026-03-08T14:13:49.329240'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 13148bdd0 by <Task pending name=''Task-1374'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
  - turn: 6
    decision: approve
    feedback: null
    timestamp: '2026-03-08T14:16:09.488510'
    player_summary: '[RECOVERED via player_report] Original error: Cancelled: Cancelled
      via cancel scope 130f99cd0 by <Task pending name=''Task-1681'' coro=<<async_generator_athrow
      without __name__>()>>'
    player_success: true
    coach_success: true
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
