---
complexity: 2
created: 2026-03-06 10:00:00+00:00
dependencies:
- TASK-CLI-001
feature_id: FEAT-CLI-001
id: TASK-CLI-002
implementation_mode: task-work
parent_review: TASK-REV-E5FC
priority: high
status: design_approved
tags:
- cli
- entry-point
- FEAT-CLI-001
task_type: feature
title: Update __main__.py with CLI/MCP mode switching
wave: 2
---

# Task: Update __main__.py with Mode Switching

## Description

Add mode-switching logic to `src/__main__.py` so that `python -m src` runs the MCP server (existing behaviour) and `python -m src cli <command>` runs the CLI wrapper.

## Acceptance Criteria

- [ ] `python -m src` still starts the MCP server (no regression)
- [ ] `python -m src cli <command>` dispatches to `src.cli.main()`
- [ ] CLI arguments after `cli` are passed correctly (e.g., `python -m src cli get-transcript URL --language fr`)
- [ ] Exit code from CLI is propagated via `sys.exit()`
- [ ] No import of `src.cli` happens in MCP server mode (lazy import)

## Implementation Notes

- Add at bottom of `__main__.py` inside `if __name__ == "__main__":` block
- Check `sys.argv[1] == "cli"` to switch modes
- Pass `sys.argv[2:]` to `src.cli.main()` to strip the `cli` prefix
- Reference: `docs/features/FEAT-CLI-001-cli-wrapper.md` § "Updated Entry Point"