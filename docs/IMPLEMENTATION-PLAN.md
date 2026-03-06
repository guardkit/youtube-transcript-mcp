# YouTube Transcript MCP - Implementation Plan

## What's Been Done

All research is complete. Feature specs exist for every feature. The project scaffold
(GuardKit MCP template, `.claude/` rules, templates) is in place.

No system plan is required - the architecture is well-defined in the research docs and
feature specs. Proceed directly to feature-plan → feature-build cycles.

---

## Feature Execution Order

```
FEAT-SKEL-001  →  FEAT-SKEL-002  →  FEAT-SKEL-003  →  FEAT-INT-001
                                                    →  FEAT-CLI-001 (parallel)
```

FEAT-CLI-001 can be built immediately after FEAT-SKEL-003 is complete, in parallel
with FEAT-INT-001 if desired (it has no dependency on FEAT-INT-001's models at build
time - but should be merged after INT-001 so all commands are wired up).

---

## Step-by-Step Commands

### Stage 1 — FEAT-SKEL-001: Walking Skeleton

**Spec:** `docs/features/FEAT-SKEL-001-basic-mcp-server.md`

```bash
cd /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp

/feature-plan "implement FEAT-SKEL-001 basic FastMCP server with ping tool" \
  --context docs/features/FEAT-SKEL-001-basic-mcp-server.md
```

Review the plan, then build:

```bash
/feature-build FEAT-<id-from-plan>
```

**Verify:**
```bash
# Unit tests
pytest tests/unit/test_ping.py -v

# MCP protocol smoke test
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | python -m src 2>/dev/null | head -1 | python -c "import sys,json; d=json.load(sys.stdin); print('✓ MCP OK' if 'result' in d else '✗ FAIL')"

# MCP Inspector (interactive)
fastmcp dev src/__main__.py
```

---

### Stage 2 — FEAT-SKEL-002: Video Info Tool

**Spec:** `docs/features/FEAT-SKEL-002-video-info-tool.md`

```bash
/feature-plan "implement FEAT-SKEL-002 get_video_info tool using yt-dlp" \
  --context docs/features/FEAT-SKEL-002-video-info-tool.md

/feature-build FEAT-<id>
```

**Verify:**
```bash
pytest tests/unit/test_video_info.py -v

# Manual via MCP Inspector - call get_video_info with a real URL
fastmcp dev src/__main__.py
```

---

### Stage 3 — FEAT-SKEL-003: Transcript Tool

**Spec:** `docs/features/FEAT-SKEL-003-transcript-tool.md`

```bash
/feature-plan "implement FEAT-SKEL-003 get_transcript and list_available_transcripts tools" \
  --context docs/features/FEAT-SKEL-003-transcript-tool.md

/feature-build FEAT-<id>
```

**Verify:**
```bash
pytest tests/unit/test_transcript.py -v

# Integration test with real video (requires network)
pytest tests/integration/ -v -m integration
```

**Walking skeleton is complete at this point.** The server can be connected to
Claude Desktop and used for real transcript fetching.

---

### Stage 4a — FEAT-INT-001: Insight Extraction

**Spec:** `docs/features/FEAT-INT-001-insight-extraction.md`

Key additions vs. original spec: `youtube-channel` and `ai-learning` presets, `list_focus_areas` tool.

```bash
/feature-plan "implement FEAT-INT-001 insight extraction with all 6 presets including youtube-channel and ai-learning" \
  --context docs/features/FEAT-INT-001-insight-extraction.md

/feature-build FEAT-<id>
```

**Verify:**
```bash
pytest tests/unit/test_insights.py -v

# Check all presets registered
python -m src cli list-focus-areas  # (after CLI is built - or test via MCP Inspector)
```

---

### Stage 4b — FEAT-CLI-001: CLI Wrapper

**Spec:** `docs/features/FEAT-CLI-001-cli-wrapper.md`

Can run in parallel with FEAT-INT-001. Merge after INT-001 is complete so all
commands are wired up.

```bash
/feature-plan "implement FEAT-CLI-001 CLI wrapper for all MCP tools with JSON stdout output" \
  --context docs/features/FEAT-CLI-001-cli-wrapper.md

/feature-build FEAT-<id>
```

**Verify:**
```bash
pytest tests/unit/test_cli.py -v

# Smoke tests
python -m src cli ping
python -m src cli list-focus-areas
python -m src cli video-info dQw4w9WgXcQ
python -m src cli get-transcript dQw4w9WgXcQ --no-segments
python -m src cli list-transcripts dQw4w9WgXcQ

# MCP server still works (no regression)
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | python -m src 2>/dev/null | head -1 | python -c "import sys,json; d=json.load(sys.stdin); print('✓ MCP still OK' if 'result' in d else '✗ FAIL')"
```

---

## Claude Desktop Integration

After FEAT-SKEL-001 is built, add to Claude Desktop config to start using immediately:

**Config file:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "youtube-transcript-mcp": {
      "command": "/Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.venv/bin/python",
      "args": ["-m", "src"],
      "cwd": "/Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp",
      "env": {
        "PYTHONPATH": "/Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

Restart Claude Desktop after editing. Test with: *"ping the youtube-transcript-mcp server"*

---

## End-to-End Workflow Examples

### Brandon: entrepreneurial insights pipeline
```
Claude Desktop:
  → get_video_info(url)          # check captions available
  → get_transcript(url)          # fetch transcript
  → extract_insights(transcript, focus_areas="entrepreneurial,investment")
  → [Claude analyses returned prompt]
  → [Manually paste insights to Google Sheets]
```

### Rich: YouTube channel planning
```
Claude Desktop:
  → get_transcript(url)
  → extract_insights(transcript, focus_areas="youtube-channel")
  → [Claude returns channel_strategy, content_idea, audience_growth, production_tip]
```

### Rich: AI concept learning
```
CLI (planning session, no Claude Desktop needed):
  python -m src cli get-transcript "$URL" --no-segments > /tmp/transcript.json
  cat /tmp/transcript.json | jq -r '.full_text' | \
    python -m src cli extract-insights - --focus ai-learning
```

### Deep agent (future)
```python
import subprocess, json

result = subprocess.run(
    ["python", "-m", "src", "cli", "get-transcript", video_url, "--no-segments"],
    capture_output=True, text=True, cwd=PROJECT_PATH
)
if result.returncode == 0:
    data = json.loads(result.stdout)
    transcript = data["full_text"]
    # pass to insight extraction...
```

---

## File Reference Index

| File | Purpose |
|------|---------|
| `docs/features/FEAT-SKEL-001-basic-mcp-server.md` | Spec: FastMCP server + ping tool |
| `docs/features/FEAT-SKEL-002-video-info-tool.md` | Spec: yt-dlp video metadata |
| `docs/features/FEAT-SKEL-003-transcript-tool.md` | Spec: youtube-transcript-api |
| `docs/features/FEAT-INT-001-insight-extraction.md` | Spec: insight extraction + 6 presets |
| `docs/features/FEAT-CLI-001-cli-wrapper.md` | Spec: CLI wrapper for all tools |
| `docs/research/implementation-research.md` | FastMCP patterns, critical gotchas |
| `docs/research/youtube-mcp-implementation-research.md` | yt-dlp + transcript-api reference |
| `docs/research/feature-plan-snippets.md` | Ready-to-use code snippets for feature-plan |
| `docs/research/GRAPHITI-KNOWLEDGE.md` | Project knowledge for Graphiti seeding |
| `.claude/CLAUDE.md` | MCP development rules for Claude Code |
| `.claude/rules/mcp-patterns.md` | 10 critical MCP patterns |

---

## Notes on Testing the `/feature-build` Command

This is a good moment to test GuardKit's autobuild capability. FEAT-SKEL-001 is an
ideal candidate:

- Low complexity (2/10)
- No external dependencies to mock
- Clear acceptance criteria with specific test assertions
- Protocol test is mechanical and verifiable

Recommended flow:
1. Run `/feature-plan` for FEAT-SKEL-001 - review the generated task
2. Run `/feature-build` on that task
3. Manually verify with the MCP protocol smoke test above
4. If autobuild produces a working server, proceed with FEAT-SKEL-002 the same way
