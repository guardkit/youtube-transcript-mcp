# CLI Examples

Practical usage patterns for the YouTube Transcript MCP CLI. All commands output JSON to stdout, making them composable with tools like `jq`.

## Basic Transcript Fetch

```bash
# Fetch transcript using a full URL
youtube-insights-mcp cli get-transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Fetch using just the video ID
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ

# Fetch in a specific language
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ --language es

# Fetch without timestamped segments (smaller output)
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ --no-segments
```

## Piping to jq

Use `jq` to extract specific fields from the JSON output.

```bash
# Get just the transcript text
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ | jq -r '.full_text'

# Get video title and duration
youtube-insights-mcp cli video-info dQw4w9WgXcQ | jq '{title, duration_formatted}'

# List available languages as a simple list
youtube-insights-mcp cli list-transcripts dQw4w9WgXcQ | jq -r '.transcripts[].language_code'

# Get the first 5 segments with timestamps
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ | jq '.segments[:5]'

# Check if a video has captions
youtube-insights-mcp cli video-info dQw4w9WgXcQ | jq '.has_captions'
```

## Extracting Insights from Stdin

The `extract-insights` command accepts `-` to read transcript text from stdin. This enables piping a transcript directly into insight extraction.

```bash
# Pipe transcript text into insight extraction
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ | \
  jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - --focus technical

# Extract entrepreneurial insights with a custom limit
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ | \
  jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - --focus entrepreneurial --max-insights 5

# Combine multiple focus areas
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ | \
  jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - --focus "entrepreneurial,investment" --video-id dQw4w9WgXcQ

# Extract from a saved transcript file
cat transcript.txt | youtube-insights-mcp cli extract-insights - --focus ai-learning
```

## Batch Processing

Process multiple videos in a loop.

```bash
# Fetch transcripts for a list of videos
for video_id in dQw4w9WgXcQ abc123defgh xyz789abcde; do
  echo "Processing: $video_id" >&2
  youtube-insights-mcp cli get-transcript "$video_id" --no-segments > "transcripts/${video_id}.json"
done

# Get metadata for multiple videos
cat video_ids.txt | while read -r video_id; do
  youtube-insights-mcp cli video-info "$video_id" | jq '{video_id, title, duration_formatted}'
done

# Check which videos have captions available
cat video_ids.txt | while read -r video_id; do
  has_captions=$(youtube-insights-mcp cli video-info "$video_id" 2>/dev/null | jq -r '.has_captions // "error"')
  echo "$video_id: $has_captions"
done
```

## Shell Script Integration

### Transcript-to-insights pipeline

```bash
#!/usr/bin/env bash
set -euo pipefail

VIDEO_ID="${1:?Usage: $0 <video_id> [focus_area]}"
FOCUS="${2:-general}"

# Step 1: Check video exists
info=$(youtube-insights-mcp cli video-info "$VIDEO_ID")
if echo "$info" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$info" | jq -r '.error.message')" >&2
  exit 1
fi

title=$(echo "$info" | jq -r '.title')
echo "Processing: $title" >&2

# Step 2: Fetch transcript
transcript=$(youtube-insights-mcp cli get-transcript "$VIDEO_ID" --no-segments)
if echo "$transcript" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$transcript" | jq -r '.error.message')" >&2
  exit 1
fi

# Step 3: Extract insights
echo "$transcript" | jq -r '.full_text' | \
  youtube-insights-mcp cli extract-insights - \
    --focus "$FOCUS" \
    --video-id "$VIDEO_ID" \
    --max-insights 10
```

### Health check script

```bash
#!/usr/bin/env bash
# Quick health check for CI/CD or monitoring

result=$(youtube-insights-mcp cli ping)
status=$(echo "$result" | jq -r '.status')

if [ "$status" = "healthy" ]; then
  echo "OK: server healthy"
  exit 0
else
  echo "FAIL: unexpected status '$status'"
  exit 1
fi
```

### Find available languages before fetching

```bash
#!/usr/bin/env bash
VIDEO_ID="${1:?Usage: $0 <video_id>}"
PREFERRED_LANG="${2:-en}"

# List available languages
available=$(youtube-insights-mcp cli list-transcripts "$VIDEO_ID")
count=$(echo "$available" | jq '.count')

echo "Found $count transcript(s) for $VIDEO_ID" >&2

# Check if preferred language is available
has_lang=$(echo "$available" | jq --arg lang "$PREFERRED_LANG" \
  '[.transcripts[].language_code] | index($lang) != null')

if [ "$has_lang" = "true" ]; then
  echo "Fetching $PREFERRED_LANG transcript..." >&2
  youtube-insights-mcp cli get-transcript "$VIDEO_ID" --language "$PREFERRED_LANG"
else
  echo "Language '$PREFERRED_LANG' not available, using fallback..." >&2
  youtube-insights-mcp cli get-transcript "$VIDEO_ID"
fi
```

## Error Handling

All commands return a non-zero exit code on error. Use `$?` or `set -e` to handle failures.

```bash
# Check exit code
youtube-insights-mcp cli get-transcript INVALID_ID
if [ $? -ne 0 ]; then
  echo "Failed to fetch transcript" >&2
fi

# Extract error message from JSON
result=$(youtube-insights-mcp cli get-transcript INVALID_ID 2>/dev/null)
if echo "$result" | jq -e '.error' > /dev/null 2>&1; then
  echo "Error: $(echo "$result" | jq -r '.error.message')" >&2
fi
```

## Output Redirection

Since all logging goes to stderr, stdout contains only clean JSON.

```bash
# Save JSON output, see logs in terminal
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ > transcript.json

# Suppress all output
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ > transcript.json 2>/dev/null

# Save logs separately
youtube-insights-mcp cli get-transcript dQw4w9WgXcQ > transcript.json 2> fetch.log
```
