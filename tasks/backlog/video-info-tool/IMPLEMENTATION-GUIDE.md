# Implementation Guide: FEAT-SKEL-002 Video Info Tool

## Overview

Implement the `get_video_info` MCP tool using yt-dlp to fetch YouTube video metadata. This builds on FEAT-SKEL-001 (basic server) by adding external library integration, a service layer, async wrappers, and structured error handling.

**Approach**: Option 1 — Direct yt-dlp integration with YouTubeClient service layer
**Testing**: Standard (quality gates: unit tests, linting, type checking)
**Feature Spec**: `docs/features/FEAT-SKEL-002-video-info-tool.md`

---

## Data Flow: Read/Write Paths

```mermaid
flowchart LR
    subgraph Writes["Write Paths"]
        W1["MCP Client\n(Claude/Inspector)"]
    end

    subgraph Processing["Processing"]
        T1["get_video_info()\n(@mcp.tool)"]
        S1["YouTubeClient\n.get_video_info()"]
        S2["asyncio.to_thread()\n→ _sync_get_info()"]
        P1["extract_video_id()\nURL parser"]
    end

    subgraph External["External"]
        YT[("YouTube\n(yt-dlp scrape)")]
    end

    subgraph Reads["Read Paths"]
        R1["MCP Client\n← VideoInfo dict"]
        R2["MCP Client\n← Structured error"]
    end

    W1 -->|"video_url param"| T1
    T1 -->|"url_or_id"| P1
    P1 -->|"video_id"| S1
    S1 -->|"async wrapper"| S2
    S2 -->|"extract_info()"| YT
    YT -->|"metadata dict"| S2
    S2 -->|"VideoInfo"| S1
    S1 -->|"VideoInfo"| T1
    T1 -->|"success"| R1
    T1 -->|"error"| R2

    style YT fill:#ffc,stroke:#aa0
    style R1 fill:#cfc,stroke:#090
    style R2 fill:#cfc,stroke:#090
```

_All write paths (input) have corresponding read paths (output). No disconnections detected._

---

## Integration Contracts

```mermaid
sequenceDiagram
    participant C as MCP Client
    participant T as get_video_info()
    participant P as extract_video_id()
    participant YC as YouTubeClient
    participant TH as asyncio.to_thread
    participant YT as yt-dlp / YouTube

    C->>T: call_tool("get_video_info", video_url)
    T->>P: extract_video_id(video_url)

    alt Invalid URL
        P-->>T: raise InvalidURLError
        T-->>C: {"error": {"category": "client_error", "code": "INVALID_URL"}}
    end

    P-->>T: video_id (11 chars)
    T->>YC: await get_video_info(video_url)
    YC->>TH: to_thread(_sync_get_info, url, id)
    TH->>YT: YoutubeDL.extract_info(url)

    alt Video Not Found
        YT-->>TH: raise DownloadError
        TH-->>YC: raise VideoNotFoundError
        YC-->>T: raise VideoNotFoundError
        T-->>C: {"error": {"category": "client_error", "code": "VIDEO_NOT_FOUND"}}
    end

    alt Cancelled
        Note over YC: CancelledError caught
        YC-->>YC: log + re-raise
    end

    YT-->>TH: info dict
    TH-->>YC: VideoInfo dataclass
    YC-->>T: VideoInfo
    T-->>C: {"video_id": "...", "title": "...", ...}
```

_Shows complete request lifecycle including all error paths. No data is fetched and discarded._

---

## Task Dependencies

```mermaid
graph TD
    T1[TASK-VID-001: Add yt-dlp dependency] --> T2[TASK-VID-002: Create YouTubeClient service]
    T2 --> T3[TASK-VID-003: Register get_video_info tool]
    T2 --> T4[TASK-VID-004: Create unit tests]
    T3 --> T5[TASK-VID-005: Verify MCP Inspector + linting]
    T4 --> T5

    style T1 fill:#cfc,stroke:#090
    style T2 fill:#cfc,stroke:#090
```

_Tasks with green background are in Wave 1 and can start first. Wave 2 tasks (TASK-VID-003, TASK-VID-004) can run in parallel after Wave 1 completes._

---

## §4: Integration Contracts

### Contract: YouTubeClient
- **Producer task:** TASK-VID-002
- **Consumer task(s):** TASK-VID-003
- **Artifact type:** Python module import
- **Format constraint:** `from src.services.youtube_client import YouTubeClient, VideoNotFoundError, InvalidURLError` must resolve. `YouTubeClient` must have async method `get_video_info(url_or_id: str) -> VideoInfo`.
- **Validation method:** Import check — verify `YouTubeClient`, `VideoNotFoundError`, `InvalidURLError` are importable from `src.services.youtube_client`

---

## Execution Strategy

### Wave 1 (Foundation)
| Task | Mode | Description |
|------|------|-------------|
| TASK-VID-001 | direct | Add yt-dlp to pyproject.toml |
| TASK-VID-002 | task-work | Create YouTubeClient service layer |

TASK-VID-001 is trivial and should be completed first. TASK-VID-002 depends on it (needs yt-dlp installed).

### Wave 2 (Integration + Testing)
| Task | Mode | Description |
|------|------|-------------|
| TASK-VID-003 | task-work | Register tool in __main__.py |
| TASK-VID-004 | task-work | Create unit tests |

These can run in parallel — TASK-VID-003 modifies `__main__.py`, TASK-VID-004 creates a new test file. No file conflicts.

### Wave 3 (Verification)
| Task | Mode | Description |
|------|------|-------------|
| TASK-VID-005 | direct | Run linting, type checking, MCP Inspector |

Final verification after all code is in place.

---

## Key MCP Patterns Applied

| Pattern | Applied In | Details |
|---------|-----------|---------|
| stderr logging | youtube_client.py | `logger = logging.getLogger(__name__)` |
| Module-level tools | __main__.py | `@mcp.tool()` at module level |
| String parameters | get_video_info | `video_url: str` parameter |
| Async wrappers | YouTubeClient | `asyncio.to_thread()` for sync yt-dlp |
| CancelledError | YouTubeClient | Catch, log, re-raise |
| Structured errors | get_video_info | Category/code/message pattern |

---

## Prerequisite

**FEAT-SKEL-001 must be implemented first.** This feature requires:
- `src/__main__.py` with FastMCP server and `mcp` instance
- `src/__init__.py` package marker
- `pyproject.toml` with base dependencies
- Working test infrastructure (`pytest`, `pytest-asyncio`)

---

## Files Created/Modified

| File | Action | Task |
|------|--------|------|
| `pyproject.toml` | Modified | TASK-VID-001 |
| `src/services/__init__.py` | Created | TASK-VID-002 |
| `src/services/youtube_client.py` | Created | TASK-VID-002 |
| `src/__main__.py` | Modified | TASK-VID-003 |
| `tests/unit/test_video_info.py` | Created | TASK-VID-004 |
