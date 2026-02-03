# Implementation Guide: Feature Spec Enhancements

## Overview

This guide details the implementation strategy for enhancing feature specifications based on review findings from TASK-REV-A1B2.

## Wave Breakdown

### Wave 1: HIGH Priority (1 task)

These fixes are critical for implementation success.

| Task | Description | Method | Est. Time |
|------|-------------|--------|-----------|
| TASK-FSE-001 | Fix dependency consistency | Direct edit | 15 min |

**Rationale**: Inconsistent dependencies will cause installation failures.

---

### Wave 2: MEDIUM Priority (3 tasks, parallel)

These enhance code quality patterns in the specs.

| Task | Description | Method | Est. Time |
|------|-------------|--------|-----------|
| TASK-FSE-002 | Add CancelledError pattern | Direct edit | 20 min |
| TASK-FSE-003 | Add mcp/fastmcp clarification | Direct edit | 10 min |
| TASK-FSE-004 | Add Critical MCP Patterns table | Direct edit | 25 min |

**Rationale**: These patterns prevent common async and configuration mistakes.

**Parallel Execution**: All 3 tasks edit different sections of the specs. Can run simultaneously.

---

### Wave 3: LOW Priority (2 tasks, parallel)

Nice-to-have improvements for developer experience.

| Task | Description | Method | Est. Time |
|------|-------------|--------|-----------|
| TASK-FSE-005 | Add internal import warning | Direct edit | 5 min |
| TASK-FSE-006 | Add JSON output example | Direct edit | 15 min |

**Rationale**: Improves documentation clarity but not blocking.

---

## Execution Commands

### Wave 1
```bash
# Direct edit - no task-work needed
# Edit docs/features/FEAT-SKEL-001-basic-mcp-server.md
# Edit docs/features/FEAT-SKEL-002-video-info-tool.md
# Edit docs/features/FEAT-INT-001-insight-extraction.md
```

### Wave 2
```bash
# Can be done in parallel (different file sections)
# TASK-FSE-002: Edit FEAT-SKEL-002 and FEAT-SKEL-003
# TASK-FSE-003: Edit FEAT-SKEL-001
# TASK-FSE-004: Edit all 4 specs
```

### Wave 3
```bash
# Can be done in parallel
# TASK-FSE-005: Edit FEAT-SKEL-003
# TASK-FSE-006: Edit FEAT-INT-001
```

## File Change Summary

| File | Tasks Affecting |
|------|-----------------|
| FEAT-SKEL-001-basic-mcp-server.md | FSE-001, FSE-003, FSE-004 |
| FEAT-SKEL-002-video-info-tool.md | FSE-001, FSE-002, FSE-004 |
| FEAT-SKEL-003-transcript-tool.md | FSE-001, FSE-002, FSE-004, FSE-005 |
| FEAT-INT-001-insight-extraction.md | FSE-001, FSE-004, FSE-006 |

## Verification

After all waves complete:

1. Review each spec for consistency
2. Verify pyproject.toml snippets match across specs
3. Confirm Critical MCP Patterns table appears in all specs
4. Run `/feature-plan` on FEAT-SKEL-001 to test
