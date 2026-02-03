# YouTube MCP Project Knowledge

## Project: youtube-mcp

A Model Context Protocol (MCP) server for YouTube content digestion that enables extraction of actionable insights from videos.

---

## Project Overview

### Purpose
Enable automated extraction of actionable content from YouTube videos and podcasts. Focus areas include entrepreneurial strategies, investment trends, and technical insights. Designed for consumption during activities like driving, walking, or cycling.

### Architecture
- **Type**: MCP Server (Model Context Protocol)
- **Framework**: FastMCP (Python)
- **Transport**: STDIO (local development), HTTP/SSE (production)
- **Pattern**: Walking skeleton with iterative feature addition

---

## Core Tools

### 1. ping()
Health check tool that validates server connectivity.
- **Status**: Planned (FEAT-SKEL-001)
- **Returns**: Server status, version, timestamp

### 2. get_video_info(video_url)
Retrieves metadata for a YouTube video without downloading.
- **Status**: Planned (FEAT-SKEL-002)
- **Dependencies**: yt-dlp library
- **Returns**: Title, channel, duration, description, caption availability

### 3. get_transcript(video_url, language)
Fetches transcript/captions for a YouTube video.
- **Status**: Planned (FEAT-SKEL-003)
- **Dependencies**: youtube-transcript-api library
- **Returns**: Timestamped segments, full text, language info

### 4. extract_insights(transcript, focus_areas)
Analyzes transcript text and extracts actionable insights.
- **Status**: Planned (FEAT-INT-001)
- **Pattern**: Claude-assisted analysis with structured output
- **Focus Presets**: entrepreneurial, investment, technical, general

---

## Technology Decisions

### FastMCP over raw MCP SDK
- **Decision**: Use FastMCP 2.x for server implementation
- **Rationale**: Higher-level API, automatic schema generation, better error handling
- **Trade-off**: Slight abstraction overhead vs. significant development speed

### yt-dlp for metadata
- **Decision**: Use yt-dlp instead of YouTube Data API
- **Rationale**: No API key required, more reliable, handles edge cases
- **Trade-off**: Scraping-based (may break), but actively maintained

### youtube-transcript-api for transcripts
- **Decision**: Purpose-built library for transcript extraction
- **Rationale**: Lightweight, handles both auto-generated and manual captions
- **Alternative considered**: yt-dlp can also fetch subtitles but less convenient API

### STDIO transport for development
- **Decision**: Start with STDIO, add HTTP/SSE later
- **Rationale**: Simplest setup for Claude Desktop integration
- **Security**: Process isolation provides security boundary

---

## Critical Implementation Patterns

### Logging to stderr (NEVER stdout)
MCP uses JSON-RPC over STDIO. Writing to stdout corrupts the protocol.
```python
import sys
logging.basicConfig(stream=sys.stderr, ...)
```

### Async wrappers for sync libraries
Both yt-dlp and youtube-transcript-api are synchronous. Use asyncio.to_thread:
```python
async def get_info(url):
    return await asyncio.to_thread(_sync_get_info, url)
```

### Structured error responses
Return error objects instead of raising exceptions to MCP layer:
```python
return {"error": {"category": "client_error", "code": "INVALID_URL", ...}}
```

---

## Feature Specifications

### FEAT-SKEL-001: Walking Skeleton
- Basic FastMCP server with ping tool
- Docker configuration
- Claude Desktop integration template
- Test infrastructure

### FEAT-SKEL-002: Video Info Tool
- yt-dlp integration
- URL parsing for multiple formats
- Metadata extraction and normalization

### FEAT-SKEL-003: Transcript Tool
- youtube-transcript-api integration
- Language selection with fallback
- Timestamped segment extraction

### FEAT-INT-001: Insight Extraction
- Claude-assisted content analysis
- Focus area presets and custom areas
- Structured insight output schema

---

## Development Workflow

### Walking Skeleton Approach
1. Get basic MCP server running (FEAT-SKEL-001)
2. Add video metadata tool (FEAT-SKEL-002)
3. Add transcript tool (FEAT-SKEL-003)
4. Add insight extraction (FEAT-INT-001)
5. Iterate based on real-world usage

### GuardKit Integration
- Use `/feature-plan` for specification refinement
- Use `/feature-build` for implementation
- Follow walking skeleton methodology

---

## Collaboration Context

### Brandon's Requirements
- Data flowing into Google Sheets via AI/MCP
- YouTube and podcast content digestion
- Actionable nuggets: entrepreneurial strategies, investment trends
- Content for consumption during drives/walks/rides
- Learning through implementation

### MCP vs LangChain Decision
- **Choice**: MCP for this use case
- **Reasoning**: Conversational workflow with Claude, discrete tools, easier iteration
- **Future**: Can wrap in LangChain agent later if autonomous operation needed

---

## Project Dependencies

### Runtime
- fastmcp>=2.0,<3 (MCP framework)
- yt-dlp>=2024.1.0 (video metadata)
- youtube-transcript-api>=1.0.0 (transcripts)
- pydantic>=2.0 (validation)

### Development
- pytest, pytest-asyncio, pytest-cov (testing)
- ruff (linting)
- mypy (type checking)

---

## Related Projects

- **guardkit**: Feature planning and build commands
- **youtube-transcript-mcp**: Possible alternate implementation
- **agentecflow_platform**: Parent platform project

---

## Open Questions

1. Should insight extraction use embedded LLM (Anthropic API) or be Claude-assisted?
2. Pagination strategy for very long transcripts?
3. Caching strategy for repeated requests?
4. Google Sheets integration approach (separate MCP or tool in this one)?
