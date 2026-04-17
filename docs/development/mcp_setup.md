For Claude Code, the MCP server is configured per-project (or globally) via .mcp.json. Here's what you need:

1. Add the MCP server config
Either in your content creation project's .mcp.json:


{
  "mcpServers": {
    "youtube-insights-mcp": {
      "command": "/Users/richardwoollcott/youtube-mcp-env/bin/youtube-insights-mcp",
      "env": {
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
Or globally at ~/.claude/.mcp.json so it's available in every project.

2. Get the /yt-insights skill
Copy the skill to your content creation project:


mkdir -p your-project/.claude/commands
cp /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.claude/commands/yt-insights.md your-project/.claude/commands/
Or to make it available globally across all projects:


cp /Users/richardwoollcott/Projects/appmilla_github/youtube-transcript-mcp/.claude/commands/yt-insights.md ~/.claude/commands/
3. That's it
Claude Code will automatically start the MCP server when it needs it. No manual server start required. You can verify it's connected by running /yt-insights or just asking Claude Code to fetch a transcript.

Key difference from Claude Desktop: Claude Code reads .mcp.json (not claude_desktop_config.json), and skills come from .claude/commands/ directories. But the MCP server itself is the same — same absolute path, same auto-start behaviour.

