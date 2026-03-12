# /yt-insights - YouTube Video Insights Extractor

Extract insights and transcript from a YouTube video using the youtube-insights-mcp CLI, then save both as markdown files.

## Workflow

### Step 1: Get the YouTube URL

If the user provided a URL as an argument (`$ARGUMENTS`), use that. Otherwise, ask for one using AskUserQuestion.

### Step 2: Choose Focus Areas

Present the focus areas as a multi-select question using AskUserQuestion:

| Option | Description |
|--------|-------------|
| **General** | Key points, action items, notable quotes, context |
| **Entrepreneurial** | Business strategies, growth tactics, lessons learned, mistakes to avoid |
| **Investment** | Market trends, opportunities, risks, recommendations |
| **Technical** | Technologies, tools, best practices, pitfalls |
| **YouTube Channel** | Channel strategy, content ideas, audience growth, production tips |
| **AI & Learning** | AI concepts, AI tools, mental models, practical applications |
| **All** | Extract across every category |

Allow the user to select multiple focus areas (unless they pick "All"). The "Other" option lets them describe a custom focus — in that case, use "general" as the CLI focus but include their custom description in the analysis instructions.

### Step 3: Fetch the Transcript

Run the CLI to get the transcript with segments:

```bash
youtube-insights-mcp cli get-transcript "VIDEO_URL" --language en
```

**IMPORTANT — CLI path resolution:** The `youtube-insights-mcp` command may not be on PATH. Try in this order:
1. `youtube-insights-mcp` (if on PATH)
2. `python3 -m youtube_insights_mcp` (if in the project directory)
3. `/Users/richardwoollcott/youtube-mcp-env/bin/youtube-insights-mcp` (installed venv)

If all fail, ask the user for the path.

Parse the JSON output to extract:
- `full_text` — the complete transcript text
- `video_id` — for reference
- `language` — transcript language
- `total_duration_seconds` — video length

### Step 4: Get Video Info (optional)

Try to get video metadata for the title:

```bash
youtube-insights-mcp cli video-info "VIDEO_URL"
```

Extract: `title`, `channel`, `upload_date`, `duration_formatted`. If this fails, derive a title from the URL or ask the user.

### Step 5: Extract Insights

Run the extraction CLI:

```bash
echo "FULL_TRANSCRIPT_TEXT" | youtube-insights-mcp cli extract-insights - --focus "FOCUS_AREAS" --max-insights 15
```

Where `FOCUS_AREAS` is the comma-separated selection from Step 2 (e.g., `"entrepreneurial,investment"` or `"youtube-channel"`).

This returns JSON containing:
- `extraction_prompt` — a structured prompt for Claude to analyse the transcript
- `categories` — the insight categories to extract
- `category_definitions` — descriptions of each category
- `chunks` — chunked transcript if it was too long

### Step 6: Analyse and Generate Insights

Use the `extraction_prompt` from Step 5 as your guide. Analyse the transcript and produce structured insights following the format and categories specified in the prompt.

For each insight, include:
- Category (from the focus areas)
- Title (brief, 10-15 words)
- Explanation (2-3 sentences)
- Supporting quote from the transcript (when available)
- Whether it's actionable

Also produce:
- An executive summary (2-3 sentences)
- 2-4 key quotes with context
- An action checklist of concrete next steps

### Step 7: Save the Files

Save two markdown files to `/Users/richardwoollcott/Projects/YouTube Channel/`:

#### Insights file: `insights/{Video Title}.md`

Use this format (matching the existing style in that directory):

```markdown
# {Video Title}

**Source:** [{Video Title}]({video_url})
**Channel:** {channel_name}
**Focus Areas:** {focus area names, dot-separated}
**Extracted:** {YYYY-MM-DD}

---

## Summary

{2-3 sentence executive summary}

---

## Key Quotes

> *"{quote 1}"*

> *"{quote 2}"*

> *"{quote 3}"*

---

## Insights

### {Category Emoji} {Category Name}

#### 1. {Insight Title}
**Category:** {category}
**Actionable:** {yes/no emoji}

{2-3 sentence explanation}

> *"{supporting quote}"*

---

{...more insights...}

---

## Action Checklist

- [ ] {action item 1}
- [ ] {action item 2}
- [ ] {action item 3}
```

Category emojis to use:
- General/Key Points: `#`
- Entrepreneurial/Business: `#`
- Investment: `#`
- Technical: `#`
- YouTube Channel: `#`
- AI & Learning: `#`

(Use `#` markdown headers — no actual emojis unless the user requests them.)

#### Transcript file: `transcripts/{Video Title}.md`

```markdown
# {Video Title} - Transcript

**Source:** [{Video Title}]({video_url})
**Channel:** {channel_name}
**Language:** {language}
**Duration:** {duration_formatted}
**Fetched:** {YYYY-MM-DD}

---

{full_text}
```

### Step 8: Confirm

After saving both files, tell the user:
- The paths of both saved files
- A brief summary of what was extracted (number of insights, focus areas covered)
- Suggest they can re-run with different focus areas if they want a different perspective

## Error Handling

- **Video not found / unavailable**: Tell the user and suggest checking the URL
- **Transcripts disabled**: Tell the user this video doesn't have captions available
- **No transcript in requested language**: Show available languages and ask if they want to try another
- **IP blocked**: Suggest configuring a proxy (PROXY_URL env var)

## Examples

```
/yt-insights https://www.youtube.com/watch?v=MWiiQDgvL-c
/yt-insights https://youtu.be/dQw4w9WgXcQ
/yt-insights
```
