# Claude Code & Cowork

Use youtube-insights-mcp as an interactive skill in [Claude Code](https://docs.anthropic.com/en/docs/claude-code) or [Claude Cowork](https://docs.anthropic.com/en/docs/claude-code).

## Overview

The project includes a `/yt-insights` slash command that provides a guided workflow for extracting insights from YouTube videos. It:

1. Asks for a YouTube URL (or accepts one as an argument)
2. Presents focus areas as a selectable list
3. Fetches the transcript and video metadata
4. Extracts structured insights using Claude
5. Saves both an insights file and a transcript file as markdown

## Prerequisites

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) installed
- youtube-insights-mcp installed (see [Installation](installation.md))

## Setup

### Step 1: Configure the MCP server

Add the MCP server to your project's `.mcp.json` or global `~/.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "/absolute/path/to/youtube-mcp-env/bin/youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

!!! warning "Full path required"
    Claude Code needs the full absolute path to the command. Find it with:
    ```bash
    which youtube-insights-mcp
    ```

### Step 2: Get the skill

The `/yt-insights` skill is included in the repository at `.claude/commands/yt-insights.md`. There are two ways to use it:

=== "From the cloned repo"

    If you've cloned the repository, the skill is automatically available when Claude Code is running in the project directory:

    ```bash
    cd youtube-transcript-mcp
    claude  # or start Cowork
    ```

    The `/yt-insights` command will be listed in your available skills.

=== "Copy to another project"

    To use the skill in a different project, copy the command file:

    ```bash
    mkdir -p your-project/.claude/commands
    cp youtube-transcript-mcp/.claude/commands/yt-insights.md your-project/.claude/commands/
    ```

    Or copy it to your global commands for use in all projects:

    ```bash
    cp youtube-transcript-mcp/.claude/commands/yt-insights.md ~/.claude/commands/
    ```

## Usage

### Basic usage

```
/yt-insights https://www.youtube.com/watch?v=VIDEO_ID
```

### Interactive mode

Just run `/yt-insights` without arguments and the skill will prompt you for the URL.

### Focus area selection

After providing a URL, you'll be asked to choose one or more focus areas:

| Focus Area | What it extracts |
|-----------|-----------------|
| **General** | Key points, action items, notable quotes, context |
| **Entrepreneurial** | Business strategies, growth tactics, lessons learned, mistakes to avoid |
| **Investment** | Market trends, opportunities, risks, recommendations |
| **Technical** | Technologies, tools, best practices, pitfalls |
| **YouTube Channel** | Channel strategy, content ideas, audience growth, production tips |
| **AI & Learning** | AI concepts, AI tools, mental models, practical applications |
| **All** | Extract across every category |

You can select multiple focus areas for a combined analysis (e.g., "Entrepreneurial" + "Investment").

## Output

The skill saves two markdown files:

### Insights file

Saved to `insights/{Video Title}.md` with:

- Executive summary
- Key quotes from the video
- Categorised insights with supporting quotes
- Action checklist of concrete next steps

### Transcript file

Saved to `transcripts/{Video Title}.md` with:

- Video metadata (source URL, channel, language, duration)
- Full transcript text for future reference

## Cowork Mode

When using Claude Cowork, the skill is automatically converted to a Cowork skill. In Cowork mode, it uses the MCP tools directly through the protocol (rather than CLI commands), providing a seamless integrated experience.

The workflow is the same — Cowork will present the focus area selection as an interactive choice, fetch the transcript via the MCP server, and save the output files.

## Example Session

Here's what a typical session looks like:

```
> /yt-insights https://www.youtube.com/watch?v=MWiiQDgvL-c

Which focus areas would you like insights extracted for?
> YouTube Channel

Fetching transcript...
Extracting insights...

Saved:
- insights/How to Actually Talk on YouTube.md
- transcripts/How to Actually Talk on YouTube.md

Extracted 12 insights across Channel Strategy, Content Ideas,
Audience Growth, and Production Tips.
```

## Customisation

### Output directory

By default, files are saved to a `YouTube Channel` directory. To change this, edit the output path in `.claude/commands/yt-insights.md`.

### Adding to your own project

The skill file at `.claude/commands/yt-insights.md` is a plain markdown file that describes the workflow. You can customise it to:

- Change the default output directory
- Adjust the insight format
- Add additional processing steps
- Modify the focus area options
