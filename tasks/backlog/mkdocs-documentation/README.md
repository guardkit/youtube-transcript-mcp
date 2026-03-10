# Feature: MkDocs Documentation Site

**Feature ID**: FEAT-DOC-MKDOCS
**Parent Review**: [TASK-DOC-FCD8](../../backlog/TASK-DOC-FCD8-generate-mkdocs-documentation.md)
**Review Report**: [TASK-DOC-FCD8-review-report.md](../../../.claude/reviews/TASK-DOC-FCD8-review-report.md)

## Problem Statement

The YouTube Transcript MCP project has no documentation beyond a minimal README. Users need comprehensive documentation for MCP tool usage, CLI commands, configuration, and the insight extraction system.

## Solution Approach

Create an MkDocs documentation site using Material for MkDocs theme, deployed to GitHub Pages via GitHub Actions. This follows the identical pattern established in GuardKit and RequireKit repositories.

**Stack**: `mkdocs` + `mkdocs-material` + `pymdown-extensions` (3 dependencies)
**Theme**: Red primary / Amber accent (YouTube branding)
**Deployment**: GitHub Actions with OIDC → GitHub Pages

## Subtask Summary

| Task | Title | Wave | Complexity | Status |
|------|-------|------|-----------|--------|
| TASK-DOC-001 | MkDocs skeleton + CI/CD | 1 | 3 | backlog |
| TASK-DOC-002 | MCP Tools reference pages | 2 | 4 | backlog |
| TASK-DOC-003 | CLI guide pages | 2 | 3 | backlog |
| TASK-DOC-004 | Getting Started pages | 2 | 3 | backlog |
| TASK-DOC-005 | Focus Areas + Troubleshooting | 3 | 3 | backlog |
| TASK-DOC-006 | Development pages | 3 | 3 | backlog |
| TASK-DOC-007 | Polish and deploy | 4 | 2 | backlog |

## Documentation Structure (18 pages)

```
docs/
├── index.md                     # Homepage
├── troubleshooting.md           # FAQ and troubleshooting
├── getting-started/             # Installation, quickstart, config
├── tools/                       # 4 MCP tool reference pages
├── cli/                         # CLI commands and examples
├── focus-areas/                 # Presets and custom categories
└── development/                 # Architecture and contributing
```

## Getting Started

```bash
# Start with Wave 1
/task-work TASK-DOC-001

# Then parallel Wave 2
/task-work TASK-DOC-002  # (parallel)
/task-work TASK-DOC-003  # (parallel)
/task-work TASK-DOC-004  # (parallel)
```

See [IMPLEMENTATION-GUIDE.md](./IMPLEMENTATION-GUIDE.md) for full execution strategy.
