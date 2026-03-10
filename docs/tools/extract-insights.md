# extract_insights

Prepare a transcript for Claude-assisted insight extraction. This tool structures the transcript, selects relevant insight categories based on focus areas, and returns an extraction prompt that Claude uses to perform the actual analysis.

!!! info "Two-step process"
    This tool **prepares** the data — the actual insight extraction happens through Claude's analysis of the returned prompt and transcript. Call this tool, then let Claude process the result.

## Parameters

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `transcript` | `string` | Yes | — | Full transcript text (minimum 100 characters) |
| `focus_areas` | `string` | No | `"general"` | Comma-separated focus area names |
| `video_id` | `string` | No | `""` | YouTube video ID for reference tracking |
| `max_insights` | `string` | No | `"10"` | Maximum number of insights to extract |

### Focus Area Values

| Value | Description |
|-------|-------------|
| `general` | Key points, action items, notable quotes, context |
| `entrepreneurial` | Business strategies, growth tactics, lessons learned |
| `investment` | Market trends, opportunities, risks, recommendations |
| `technical` | Technologies, tools, best practices, pitfalls |
| `youtube-channel` | Channel strategy, content ideas, audience growth |
| `ai-learning` | AI concepts, AI tools, mental models, practical applications |
| `all` | Every category from all focus areas (24 categories) |

Multiple focus areas can be combined with commas: `"entrepreneurial,investment"`.

See the [Focus Areas Reference](../focus-areas/presets.md) for full details on each preset and its categories.

## Chunking Behaviour

Long transcripts are automatically split into chunks for processing:

- **Threshold**: Transcripts over 30,000 characters are chunked
- **Split strategy**: Paragraph boundaries (`\n\n`) are preferred to maintain context
- **Overlap**: 500 characters of overlap between chunks to avoid losing context at boundaries
- **Fallback**: If a single paragraph exceeds the limit, it is force-split at character boundaries with overlap

When chunking occurs, the response includes:

- `needs_chunking: true`
- `chunk_count` with the number of chunks
- `chunks` array containing all chunk strings
- `extraction_prompt` built from the first chunk

## Response Format

### Success Response

```json
{
  "video_id": "dQw4w9WgXcQ",
  "focus_areas": ["entrepreneurial", "investment"],
  "categories": [
    "business_strategy",
    "growth_tactic",
    "lesson_learned",
    "mistake_to_avoid",
    "market_trend",
    "opportunity",
    "risk",
    "recommendation"
  ],
  "category_definitions": {
    "business_strategy": "Core business approaches, models, and strategic decisions",
    "growth_tactic": "Specific tactics for user/revenue/market growth",
    "lesson_learned": "Key learnings from experience, both positive and negative",
    "mistake_to_avoid": "Common pitfalls, errors, and things that didn't work",
    "market_trend": "Industry trends, market movements, and predictions",
    "opportunity": "Investment or business opportunities identified",
    "risk": "Potential risks, downsides, or concerns mentioned",
    "recommendation": "Specific recommendations or advice given"
  },
  "transcript_length": 15432,
  "chunk_count": 1,
  "needs_chunking": false,
  "max_insights": 10,
  "extraction_prompt": "Analyze this transcript and extract actionable insights...",
  "chunks": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `video_id` | `string\|null` | Video ID if provided |
| `focus_areas` | `array` | Resolved focus area names |
| `categories` | `array` | Insight category values to extract |
| `category_definitions` | `object` | Human-readable description for each category |
| `transcript_length` | `integer` | Character count of the original transcript |
| `chunk_count` | `integer` | Number of chunks (1 if not chunked) |
| `needs_chunking` | `boolean` | Whether the transcript was split |
| `max_insights` | `integer` | Requested insight limit |
| `extraction_prompt` | `string` | Ready-to-use prompt for Claude analysis |
| `chunks` | `array\|null` | List of chunk strings if chunked, `null` otherwise |

### Chunked Response

When the transcript exceeds 30,000 characters:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "focus_areas": ["general"],
  "categories": ["key_point", "action_item", "notable_quote", "context"],
  "transcript_length": 85000,
  "chunk_count": 3,
  "needs_chunking": true,
  "max_insights": 10,
  "extraction_prompt": "Analyze this transcript and extract...",
  "chunks": [
    "First 30,000 characters...",
    "...overlapping 500 chars + next 29,500...",
    "...overlapping 500 chars + remaining..."
  ]
}
```

## Error Handling

| Code | Category | Description |
|------|----------|-------------|
| `INVALID_PARAMETER` | `client_error` | `max_insights` is not a valid integer |
| `INVALID_FOCUS_AREA` | `client_error` | One or more focus area names are not recognised |
| `TRANSCRIPT_TOO_SHORT` | `client_error` | Transcript is shorter than 100 characters |
| `EXTRACTION_PREP_ERROR` | `server_error` | Unexpected error during extraction preparation |

### Invalid Focus Area Example

```json
{
  "error": {
    "category": "client_error",
    "code": "INVALID_FOCUS_AREA",
    "message": "Invalid focus areas: ['cooking']. Valid options: ['general', 'entrepreneurial', 'investment', 'technical', 'youtube-channel', 'ai-learning', 'all']"
  }
}
```

## Examples

### General Insights (default)

```
extract_insights(transcript="<full transcript text>")
```

### Multiple Focus Areas

```
extract_insights(
  transcript="<full transcript text>",
  focus_areas="entrepreneurial,investment",
  video_id="dQw4w9WgXcQ",
  max_insights="15"
)
```

### All Categories

```
extract_insights(
  transcript="<full transcript text>",
  focus_areas="all"
)
```

### Typical Workflow

1. Fetch the transcript:
   ```
   get_transcript(video_url="https://youtube.com/watch?v=VIDEO_ID")
   ```

2. Pass the `full_text` to extract insights:
   ```
   extract_insights(
     transcript="<full_text from step 1>",
     focus_areas="technical",
     video_id="VIDEO_ID"
   )
   ```

3. Claude analyses the `extraction_prompt` and returns structured insights.

## Source

Defined in [`src/__main__.py`](https://github.com/appmilla/youtube-transcript-mcp/blob/main/src/__main__.py) using `prepare_for_extraction()` from [`src/services/insight_extractor.py`](https://github.com/appmilla/youtube-transcript-mcp/blob/main/src/services/insight_extractor.py).
