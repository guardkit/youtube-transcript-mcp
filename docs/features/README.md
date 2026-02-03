# YouTube MCP - Feature Index

## Overview

This document tracks all planned features for the youtube-mcp project.

## Implementation Phases

### Phase 1: Walking Skeleton
Get a basic MCP server running that Claude can connect to and use to fetch YouTube transcripts.

### Phase 2: Intelligence Layer
Add insight extraction capabilities to transform raw transcripts into actionable nuggets.

### Phase 3: Future Integration
Connect with Google Sheets MCP and Podcast MCP for complete content digestion pipeline.

---

## Feature List

### Phase 1: Walking Skeleton

| Feature ID | Name | Status | Complexity | Dependencies |
|------------|------|--------|------------|--------------|
| `FEAT-SKEL-001` | [Walking Skeleton - Basic MCP Server](./FEAT-SKEL-001-walking-skeleton.md) | 🔲 Planned | Low (2/10) | None |
| `FEAT-SKEL-002` | [Video Info Tool](./FEAT-SKEL-002-video-info-tool.md) | 🔲 Planned | Medium (4/10) | FEAT-SKEL-001 |
| `FEAT-SKEL-003` | [Transcript Fetching Tool](./FEAT-SKEL-003-transcript-tool.md) | 🔲 Planned | Medium (5/10) | FEAT-SKEL-001 |

### Phase 2: Intelligence Layer

| Feature ID | Name | Status | Complexity | Dependencies |
|------------|------|--------|------------|--------------|
| `FEAT-INT-001` | [Insight Extraction Tool](./FEAT-INT-001-insight-extraction.md) | 🔲 Planned | Medium-High (6/10) | FEAT-SKEL-003 |

---

## Implementation Order

Recommended order for implementation:

```
1. FEAT-SKEL-001 (Walking Skeleton)
   └── Establishes basic MCP server, ping tool, Docker setup
   
2. FEAT-SKEL-002 (Video Info Tool)
   └── Adds video metadata fetching with yt-dlp
   
3. FEAT-SKEL-003 (Transcript Tool)
   └── Adds transcript fetching with youtube-transcript-api
   
4. FEAT-INT-001 (Insight Extraction)
   └── Adds intelligence layer for insight extraction
```

## Status Legend

| Icon | Status |
|------|--------|
| 🔲 | Planned |
| 🔄 | In Progress |
| ✅ | Completed |
| ❌ | Blocked |
| ⏸️ | On Hold |

---

## Quick Start

To implement the next feature:

```bash
# Navigate to project
cd /Users/richardwoollcott/Projects/appmilla_github/youtube-mcp

# Plan the feature (creates tasks from feature spec)
/feature-plan "implement FEAT-SKEL-001 walking skeleton basic MCP server"

# Build the feature autonomously
/feature-build TASK-XXX

# Complete and merge
/feature-complete TASK-XXX
```

## Feature Specification Template

When adding new features, create a spec file in `docs/features/` with:

1. **Feature ID**: Unique identifier (e.g., `FEAT-XXX-001`)
2. **Overview**: What the feature does
3. **Goal**: Why we're building it
4. **Success Criteria**: Checkboxes for acceptance
5. **Technical Requirements**: API specs, structure changes
6. **Implementation Notes**: Key patterns, gotchas
7. **Testing Strategy**: Unit, integration, protocol tests
8. **Dependencies**: Required features
9. **Estimated Complexity**: 1-10 scale
