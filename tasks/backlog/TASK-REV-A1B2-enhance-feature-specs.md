---
id: TASK-REV-A1B2
title: Enhance feature specs with research findings
status: review_complete
review_results:
  score: 85
  findings_count: 8
  recommendations_count: 8
  decision: implement
  implementation_feature: FEAT-FSE
  subtasks_created: 6
created: 2026-02-03T22:10:00Z
updated: 2026-02-03T22:10:00Z
priority: high
task_type: review
tags: [documentation, research, feature-specs, review]
complexity: 4
source_files:
  - docs/research/youtube-mcp-implementation-research.md
  - docs/research/implementation-research.md
  - docs/research/feature-plan-snippets.md
  - docs/research/GRAPHITI-KNOWLEDGE.md
target_files:
  - docs/features/FEAT-SKEL-001-basic-mcp-server.md
  - docs/features/FEAT-SKEL-002-video-info-tool.md
  - docs/features/FEAT-SKEL-003-transcript-tool.md
  - docs/features/FEAT-INT-001-insight-extraction.md
---

# Task: Enhance Feature Specifications from Research

## Description

Review task to analyze files in `docs/research/` and use the findings to enhance the `docs/features/` specification files. These specs are designed to be passed to the `/feature-plan` command for implementation planning.

## Research Files to Analyze

| File | Purpose |
|------|---------|
| `youtube-mcp-implementation-research.md` | Comprehensive implementation patterns and library documentation |
| `implementation-research.md` | Core patterns and project structure |
| `feature-plan-snippets.md` | Ready-to-use code snippets for each feature |
| `GRAPHITI-KNOWLEDGE.md` | Project knowledge base and decisions |

## Feature Specs to Enhance

| Feature | Current State | Enhancement Focus |
|---------|--------------|-------------------|
| FEAT-SKEL-001 | Good base | FastMCP version pinning, logging patterns |
| FEAT-SKEL-002 | Good base | Error handling, async patterns |
| FEAT-SKEL-003 | Good base | youtube-transcript-api v1.2+ syntax |
| FEAT-INT-001 | Good base | Complete code examples |

## Key Enhancements Required

### 1. Version-Specific API Details (youtube-transcript-api v1.2+)

**Current Issue**: Some specs may use old class-method syntax.

**Correct Pattern**:
```python
# v1.2+ instance method pattern (CORRECT)
api = YouTubeTranscriptApi()
transcript = api.fetch(video_id, languages=['en'])
transcript_list = api.list(video_id)

# Access transcript data
for snippet in transcript.snippets:
    print(snippet.start, snippet.duration, snippet.text)
```

**Transcript Object Structure**:
```python
FetchedTranscript:
    - snippets: List[FetchedTranscriptSnippet]
    - video_id: str
    - language: str
    - language_code: str
    - is_generated: bool

FetchedTranscriptSnippet:
    - text: str
    - start: float
    - duration: float
```

### 2. Complete Error Handling Patterns

All feature specs should include comprehensive error handling:

```python
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
    NoTranscriptAvailable,
)

try:
    transcript = api.fetch(video_id, languages=[language])
except TranscriptsDisabled:
    return {"error": {"category": "client_error", "code": "TRANSCRIPTS_DISABLED", ...}}
except NoTranscriptFound:
    return {"error": {"category": "client_error", "code": "NO_TRANSCRIPT", ...}}
except VideoUnavailable:
    return {"error": {"category": "client_error", "code": "VIDEO_UNAVAILABLE", ...}}
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    return {"error": {"category": "server_error", "code": "INTERNAL_ERROR", ...}}
```

### 3. Installation Notes (FastMCP Version Pinning)

**Critical**: Clarify the difference between `mcp` and `fastmcp` packages.

**pyproject.toml**:
```toml
dependencies = [
    "mcp>=1.0.0",  # For importing from mcp.server.fastmcp
    # OR
    "fastmcp>=2.0,<3",  # Standalone fastmcp package
]
```

**CLI Installation**:
```bash
# Stable (recommended)
pip install 'fastmcp<3'

# Beta with latest features
pip install fastmcp==3.0.0b1
```

### 4. Critical MCP Patterns to Reinforce

Each feature spec should highlight these patterns:

| Pattern | Description | Example |
|---------|-------------|---------|
| **stderr logging** | NEVER log to stdout | `logging.basicConfig(stream=sys.stderr)` |
| **Module-level tools** | Register at module level | `@mcp.tool()` outside functions |
| **String parameters** | MCP sends strings | `count_int = int(count)` |
| **Timezone-aware datetime** | Never use utcnow() | `datetime.now(timezone.utc)` |
| **Async wrappers** | Wrap sync libs | `await asyncio.to_thread(sync_fn)` |
| **CancelledError** | Always re-raise | `except CancelledError: log; raise` |

## Acceptance Criteria

- [ ] FEAT-SKEL-001 has correct FastMCP installation and version info
- [ ] FEAT-SKEL-002 includes complete async wrapper pattern for yt-dlp
- [ ] FEAT-SKEL-003 uses youtube-transcript-api v1.2+ syntax throughout
- [ ] FEAT-INT-001 has complete, runnable code examples
- [ ] All specs include comprehensive error handling patterns
- [ ] All specs highlight critical MCP patterns
- [ ] Code examples are copy-paste ready for implementation
- [ ] Installation commands are correct and version-pinned

## Implementation Notes

This is a **review/enhancement task**, not a code implementation task. The goal is to improve documentation quality so that `/feature-plan` can produce better implementation plans.

### Workflow

1. Read each research file to extract relevant details
2. For each feature spec:
   - Identify gaps vs. research findings
   - Add missing code patterns
   - Update API syntax to v1.2+
   - Add/improve error handling examples
   - Reinforce critical MCP patterns
3. Validate specs are ready for `/feature-plan`

## References

- MCP Specification: https://modelcontextprotocol.io/specification
- youtube-transcript-api: https://pypi.org/project/youtube-transcript-api/
- FastMCP: https://gofastmcp.com/
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
