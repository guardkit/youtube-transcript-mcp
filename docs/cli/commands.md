# Command Reference

All commands output JSON to stdout and log to stderr. Exit code `0` indicates success; `1` indicates an error (the JSON will contain an `error` object).

```bash
youtube-insights-mcp cli <command> [options]
```

---

## ping

Health check. Verifies that server components are importable.

```bash
youtube-insights-mcp cli ping
```

**Arguments:** None

**Output:**

```json
{
  "status": "healthy",
  "server": "youtube-insights-mcp",
  "version": "0.1.3",
  "timestamp": "2026-03-10T12:00:00+00:00",
  "mode": "cli"
}
```

---

## video-info

Fetch metadata for a YouTube video.

```bash
youtube-insights-mcp cli video-info <video_url>
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `video_url` | Yes | YouTube URL or 11-character video ID |

**Accepted URL formats:**

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `VIDEO_ID` (11-character ID directly)

**Output:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video title",
  "channel": "Channel Name",
  "channel_id": "UCxxxxxx",
  "duration_seconds": 212,
  "duration_formatted": "3:32",
  "description_snippet": "First part of description...",
  "view_count": 1500000,
  "upload_date": "2009-10-25",
  "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "has_captions": true,
  "has_auto_captions": true,
  "available_languages": ["en", "es", "fr"]
}
```

**Errors:**

| Code | Meaning |
|------|---------|
| `INVALID_URL` | The URL/ID could not be parsed |
| `VIDEO_NOT_FOUND` | Video does not exist or is private |

---

## get-transcript

Fetch the transcript for a YouTube video.

```bash
youtube-insights-mcp cli get-transcript <video_url> [--language LANG] [--no-segments]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `video_url` | Yes | - | YouTube URL or 11-character video ID |
| `--language` | No | `en` | Preferred language code. Falls back intelligently if unavailable |
| `--no-segments` | No | - | Omit timestamped segments from output (smaller payload) |

**Language fallback strategy:**

1. Exact match for requested language (manual transcript)
2. Auto-generated transcript in requested language
3. Any available transcript

**Output (default):**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "English",
  "language_code": "en",
  "is_auto_generated": false,
  "full_text": "Complete transcript text...",
  "total_segments": 42,
  "total_duration_seconds": 212.5,
  "segments": [
    {
      "start": 0.0,
      "duration": 4.2,
      "text": "First segment text"
    }
  ]
}
```

**Output (with `--no-segments`):**

The `segments` array is omitted, resulting in a smaller response containing only the `full_text` and metadata.

**Errors:**

| Code | Meaning |
|------|---------|
| `INVALID_URL` | The URL/ID could not be parsed |
| `TRANSCRIPTS_DISABLED` | The video has transcripts disabled |
| `NO_TRANSCRIPT_FOUND` | No transcript available in requested or fallback languages |
| `VIDEO_UNAVAILABLE` | Video is unavailable (deleted, private, region-locked) |

---

## list-transcripts

List all available transcript languages for a video.

```bash
youtube-insights-mcp cli list-transcripts <video_url>
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `video_url` | Yes | YouTube URL or 11-character video ID |

**Output:**

```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcripts": [
    {
      "language": "English",
      "language_code": "en",
      "is_generated": false
    },
    {
      "language": "Spanish",
      "language_code": "es",
      "is_generated": true
    }
  ],
  "count": 2
}
```

**Errors:**

| Code | Meaning |
|------|---------|
| `INVALID_URL` | The URL/ID could not be parsed |

---

## extract-insights

Prepare transcript text for insight extraction. Returns a structured prompt and metadata that Claude can use to extract insights.

```bash
youtube-insights-mcp cli extract-insights <transcript> [--focus AREAS] [--video-id ID] [--max-insights N]
```

**Arguments:**

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `transcript` | Yes | - | Full transcript text, or `-` to read from stdin |
| `--focus` | No | `general` | Focus areas (comma-separated). See [Focus Areas](../focus-areas/index.md) |
| `--video-id` | No | `""` | Optional video ID to include in output |
| `--max-insights` | No | `10` | Maximum number of insights to extract |

**Available focus areas:** `general`, `entrepreneurial`, `investment`, `technical`, `youtube-channel`, `ai-learning`. See [Focus Areas](../focus-areas/index.md) for details on each preset.

Multiple focus areas can be combined: `--focus entrepreneurial,investment`

**Stdin support:**

Pass `-` as the transcript argument to read from stdin. This enables piping:

```bash
youtube-insights-mcp cli get-transcript VIDEO_ID | \
  jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - --focus technical
```

**Output:**

```json
{
  "video_id": null,
  "focus_areas": ["general"],
  "categories": ["key_point", "action_item", "notable_quote", "context"],
  "category_definitions": {
    "key_point": "Main takeaways and central ideas",
    "action_item": "Specific actions viewers can take",
    "notable_quote": "Memorable or impactful statements",
    "context": "Background context, framing, and important situational details"
  },
  "transcript_length": 15234,
  "chunk_count": 1,
  "needs_chunking": false,
  "max_insights": 10,
  "extraction_prompt": "Analyze this transcript and extract...",
  "chunks": null
}
```

When the transcript exceeds 30,000 characters, it is automatically chunked at paragraph boundaries with 500-character overlap. The `chunks` field will contain the array of chunks and `needs_chunking` will be `true`.

---

## list-focus-areas

List all available focus area presets and their insight categories.

```bash
youtube-insights-mcp cli list-focus-areas
```

**Arguments:** None

**Output:**

```json
{
  "focus_areas": {
    "general": ["key_point", "action_item", "notable_quote", "context"],
    "entrepreneurial": ["business_strategy", "growth_tactic", "lesson_learned", "mistake_to_avoid"],
    "investment": ["market_trend", "opportunity", "risk", "recommendation"],
    "technical": ["technology", "tool", "best_practice", "pitfall"],
    "youtube-channel": ["channel_strategy", "content_idea", "audience_growth", "production_tip"],
    "ai-learning": ["ai_concept", "ai_tool", "mental_model", "practical_application"]
  },
  "category_definitions": {
    "key_point": "Main takeaways and central ideas",
    "action_item": "Specific actions viewers can take",
    "notable_quote": "Memorable or impactful statements",
    "context": "Background context, framing, and important situational details",
    "business_strategy": "Core business approaches, models, and strategic decisions",
    "growth_tactic": "Specific tactics for user/revenue/market growth",
    "lesson_learned": "Key learnings from experience, both positive and negative",
    "mistake_to_avoid": "Common pitfalls, errors, and things that didn't work",
    "market_trend": "Industry trends, market movements, and predictions",
    "opportunity": "Investment or business opportunities identified",
    "risk": "Potential risks, downsides, or concerns mentioned",
    "recommendation": "Specific recommendations or advice given",
    "technology": "Technologies, platforms, or systems mentioned",
    "tool": "Tools, software, or resources recommended",
    "best_practice": "Recommended approaches and methodologies",
    "pitfall": "Common problems and anti-patterns to avoid",
    "channel_strategy": "High-level channel positioning, niche, and growth direction",
    "content_idea": "Specific video ideas, formats, series concepts to steal or adapt",
    "audience_growth": "Tactics for growing subscribers, views, and engagement",
    "production_tip": "Filming, editing, thumbnails, titles, SEO, workflow improvements",
    "ai_concept": "Core AI/ML concepts, architectures, or techniques explained",
    "ai_tool": "Specific AI tools, libraries, frameworks, or services discussed",
    "mental_model": "Frameworks and mental models for thinking about AI systems",
    "practical_application": "Concrete ways to apply AI concepts to real projects"
  },
  "usage_tip": "Pass focus areas as comma-separated: 'entrepreneurial,investment' or 'youtube-channel'"
}
```

---

## Error Response Format

All commands use a consistent error structure:

```json
{
  "error": {
    "category": "client_error",
    "code": "INVALID_URL",
    "message": "Could not extract video ID from: not-a-url"
  }
}
```

| Category | Meaning |
|----------|---------|
| `client_error` | Invalid input (bad URL, missing argument) |
| `server_error` | Internal failure or unavailable service |
