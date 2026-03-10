# Troubleshooting

## Common Errors

### TranscriptsDisabled

**Error code:** `TRANSCRIPTS_DISABLED`

```json
{
  "error": {
    "category": "client_error",
    "code": "TRANSCRIPTS_DISABLED",
    "message": "Transcripts are disabled for video: VIDEO_ID"
  }
}
```

**Cause:** The video owner has disabled transcripts/captions for this video.

**Solutions:**

- This cannot be bypassed — the video owner controls this setting.
- Try a different video covering the same topic.
- Check if the video has community-contributed captions (rare but possible).

---

### VideoUnavailable

**Error code:** `VIDEO_UNAVAILABLE`

```json
{
  "error": {
    "category": "client_error",
    "code": "VIDEO_UNAVAILABLE",
    "message": "Video is unavailable: VIDEO_ID"
  }
}
```

**Cause:** The video does not exist, is private, has been deleted, or is region-restricted.

**Solutions:**

- Verify the video ID or URL is correct.
- Check that the video is publicly accessible (not private or unlisted without the link).
- Try opening the video URL in a browser to confirm it's available.
- If region-restricted, the transcript cannot be fetched from your location.

---

### NoTranscriptFound (Language Not Found)

**Error code:** `NO_TRANSCRIPT_FOUND`

```json
{
  "error": {
    "category": "client_error",
    "code": "NO_TRANSCRIPT_FOUND",
    "message": "No transcript found for video: VIDEO_ID",
    "available_languages": ["es", "fr", "de"]
  }
}
```

**Cause:** No transcript exists in the requested language, and the fallback strategy could not find an alternative.

**Solutions:**

1. Check `available_languages` in the error response for alternatives.
2. Use `list_available_transcripts` to see all available languages before fetching.
3. The server already tries a 4-step fallback:
    - Exact language match
    - Auto-generated version of requested language
    - Any English variant
    - First available transcript
4. If none of these work, the video genuinely has no transcripts.

---

### Invalid URL

**Error code:** `INVALID_URL`

```json
{
  "error": {
    "category": "client_error",
    "code": "INVALID_URL",
    "message": "Could not extract video ID from: ..."
  }
}
```

**Cause:** The provided URL or video ID could not be parsed.

**Solutions:**

- Use one of the supported URL formats (see FAQ below).
- Ensure the video ID is exactly 11 characters.
- Remove any extra query parameters or fragments that may interfere.

---

### Transcript Too Short

**Error code:** `TRANSCRIPT_TOO_SHORT`

Returned by `extract_insights` when the transcript is under 100 characters.

**Solutions:**

- Ensure you're passing the full transcript text, not just a URL.
- Very short videos may not have enough content for insight extraction.

---

### Server Connection Issues

If the MCP server is not responding or Claude Desktop shows connection errors:

1. **Check absolute paths** in `.mcp.json` — relative paths will fail:
   ```json
   {
     "mcpServers": {
       "youtube-transcript": {
         "command": "/absolute/path/to/.venv/bin/python",
         "args": ["-m", "src"],
         "cwd": "/absolute/path/to/youtube-transcript-mcp",
         "env": {
           "PYTHONPATH": "/absolute/path/to/youtube-transcript-mcp"
         }
       }
     }
   }
   ```
2. **Set PYTHONPATH** in the `env` section to the project root directory.
3. **Restart Claude Desktop** after any configuration changes.
4. **Check stderr logs** — the server logs all output to stderr, not stdout.
5. **Verify the virtual environment** — the `command` path must point to the correct Python binary with dependencies installed.

---

## FAQ

### What URL formats are supported?

All of the following formats work with `get_transcript` and `list_available_transcripts`:

| Format | Example |
|--------|---------|
| Standard watch URL | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
| Short URL | `https://youtu.be/dQw4w9WgXcQ` |
| Without www | `https://youtube.com/watch?v=dQw4w9WgXcQ` |
| Embed URL | `https://youtube.com/embed/dQw4w9WgXcQ` |
| Mobile URL | `https://m.youtube.com/watch?v=dQw4w9WgXcQ` |
| Plain video ID | `dQw4w9WgXcQ` |

URLs with extra query parameters (e.g., `&t=120`, `&list=PLxxxx`) are handled correctly — the video ID is extracted and the rest is ignored.

### Is there rate limiting?

YouTube may rate-limit transcript requests if you make too many in a short period. There is no hard-coded rate limit in the MCP server itself.

**Best practices for bulk operations:**

- Space out requests when processing many videos.
- Use `list_available_transcripts` first to check availability before fetching.
- Cache transcripts locally if you need to re-analyze the same video.

### What's the difference between manual and auto-generated transcripts?

| Aspect | Manual | Auto-generated |
|--------|--------|----------------|
| **Source** | Uploaded by the video creator or community | Created by YouTube's speech recognition |
| **Accuracy** | Typically high — human-reviewed | Variable — depends on audio quality and accents |
| **Punctuation** | Usually includes proper punctuation | Often lacks punctuation |
| **Availability** | Only if someone uploaded them | Available for most videos with clear speech |

The `is_auto_generated` field in the response tells you which type was returned. The language fallback strategy prefers manual transcripts over auto-generated ones for the same language.

### How does language fallback work?

When the requested language isn't available, the server tries these steps in order:

1. **Exact match** — the requested language code (e.g., `en`)
2. **Auto-generated** — auto-generated version of the requested language
3. **English variant** — any transcript with a language code starting with `en`
4. **First available** — whatever transcript exists

The response always includes the actual `language` and `language_code` of the returned transcript so you know what you got.

### How does transcript chunking work?

For long transcripts, `extract_insights` automatically splits the text into manageable chunks. The response includes:

- `needs_chunking`: Whether the transcript was split
- `chunk_count`: Number of chunks created
- `chunks`: The individual chunk strings (if chunked)

Each chunk is processed independently for insight extraction.

### Can I use the CLI instead of MCP?

Yes. The CLI provides direct terminal access to all MCP tool functionality:

```bash
# Fetch a transcript
python -m src cli get-transcript "https://youtu.be/VIDEO_ID"

# List available languages
python -m src cli list-transcripts "https://youtu.be/VIDEO_ID"

# Extract insights
python -m src cli extract-insights --focus entrepreneurial --video-id VIDEO_ID < transcript.txt

# List focus areas
python -m src cli list-focus-areas
```

See the [CLI Guide](cli/index.md) for full command documentation.
