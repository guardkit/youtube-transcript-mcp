# list_focus_areas

List all available focus area presets and their insight categories. Use this to understand what kinds of insights can be extracted before calling [`extract_insights`](extract-insights.md).

## Parameters

This tool takes no parameters.

## Response Format

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
  "usage_tip": "Pass focus areas as comma-separated: 'entrepreneurial,investment'"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `focus_areas` | `object` | Mapping of preset name to its list of category values |
| `category_definitions` | `object` | Mapping of every category to a human-readable description |
| `usage_tip` | `string` | Quick-start hint for using focus areas with `extract_insights` |

## Available Presets

### general

Default focus area. Extracts broad, universally useful insights.

| Category | Description |
|----------|-------------|
| `key_point` | Main takeaways and central ideas |
| `action_item` | Specific actions viewers can take |
| `notable_quote` | Memorable or impactful statements |
| `context` | Background context, framing, and important situational details |

### entrepreneurial

Business and startup-focused insights.

| Category | Description |
|----------|-------------|
| `business_strategy` | Core business approaches, models, and strategic decisions |
| `growth_tactic` | Specific tactics for user/revenue/market growth |
| `lesson_learned` | Key learnings from experience, both positive and negative |
| `mistake_to_avoid` | Common pitfalls, errors, and things that didn't work |

### investment

Market and investment analysis insights.

| Category | Description |
|----------|-------------|
| `market_trend` | Industry trends, market movements, and predictions |
| `opportunity` | Investment or business opportunities identified |
| `risk` | Potential risks, downsides, or concerns mentioned |
| `recommendation` | Specific recommendations or advice given |

### technical

Software engineering and technology insights.

| Category | Description |
|----------|-------------|
| `technology` | Technologies, platforms, or systems mentioned |
| `tool` | Tools, software, or resources recommended |
| `best_practice` | Recommended approaches and methodologies |
| `pitfall` | Common problems and anti-patterns to avoid |

### youtube-channel

YouTube content creation insights.

| Category | Description |
|----------|-------------|
| `channel_strategy` | High-level channel positioning, niche, and growth direction |
| `content_idea` | Specific video ideas, formats, series concepts to steal or adapt |
| `audience_growth` | Tactics for growing subscribers, views, and engagement |
| `production_tip` | Filming, editing, thumbnails, titles, SEO, workflow improvements |

### ai-learning

AI and machine learning insights.

| Category | Description |
|----------|-------------|
| `ai_concept` | Core AI/ML concepts, architectures, or techniques explained |
| `ai_tool` | Specific AI tools, libraries, frameworks, or services discussed |
| `mental_model` | Frameworks and mental models for thinking about AI systems |
| `practical_application` | Concrete ways to apply AI concepts to real projects |

## Example

```
list_focus_areas()
```

## Source

Defined in [`src/__main__.py`](https://github.com/appmilla/youtube-transcript-mcp/blob/main/src/__main__.py) using `FOCUS_PRESETS` and `CATEGORY_DEFINITIONS` from [`src/models/insight.py`](https://github.com/appmilla/youtube-transcript-mcp/blob/main/src/models/insight.py).
