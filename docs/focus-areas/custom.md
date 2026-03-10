# Custom Focus Areas

The insight extraction system uses 24 categories organized across 6 focus areas. This page documents every category and explains how to combine them for custom analysis.

## How the Category System Works

When you call `extract_insights`, the `focus_areas` parameter selects which categories to use:

1. **Preset name** (e.g., `"general"`) maps to 4 predefined categories
2. **Multiple presets** (e.g., `"entrepreneurial,technical"`) merges their categories
3. **`"all"`** selects all 24 categories

The selected categories are included in the extraction prompt, guiding Claude to look for those specific types of insights in the transcript.

## All 24 Insight Categories

### General Categories

| Category | Value | Description |
|----------|-------|-------------|
| Key Point | `key_point` | Main takeaways and central ideas |
| Action Item | `action_item` | Specific actions viewers can take |
| Notable Quote | `notable_quote` | Memorable or impactful statements |
| Context | `context` | Background context, framing, and important situational details |

### Entrepreneurial Categories

| Category | Value | Description |
|----------|-------|-------------|
| Business Strategy | `business_strategy` | Core business approaches, models, and strategic decisions |
| Growth Tactic | `growth_tactic` | Specific tactics for user/revenue/market growth |
| Lesson Learned | `lesson_learned` | Key learnings from experience, both positive and negative |
| Mistake to Avoid | `mistake_to_avoid` | Common pitfalls, errors, and things that didn't work |

### Investment Categories

| Category | Value | Description |
|----------|-------|-------------|
| Market Trend | `market_trend` | Industry trends, market movements, and predictions |
| Opportunity | `opportunity` | Investment or business opportunities identified |
| Risk | `risk` | Potential risks, downsides, or concerns mentioned |
| Recommendation | `recommendation` | Specific recommendations or advice given |

### Technical Categories

| Category | Value | Description |
|----------|-------|-------------|
| Technology | `technology` | Technologies, platforms, or systems mentioned |
| Tool | `tool` | Tools, software, or resources recommended |
| Best Practice | `best_practice` | Recommended approaches and methodologies |
| Pitfall | `pitfall` | Common problems and anti-patterns to avoid |

### YouTube Channel Categories

| Category | Value | Description |
|----------|-------|-------------|
| Channel Strategy | `channel_strategy` | High-level channel positioning, niche, and growth direction |
| Content Idea | `content_idea` | Specific video ideas, formats, series concepts to steal or adapt |
| Audience Growth | `audience_growth` | Tactics for growing subscribers, views, and engagement |
| Production Tip | `production_tip` | Filming, editing, thumbnails, titles, SEO, workflow improvements |

### AI Learning Categories

| Category | Value | Description |
|----------|-------|-------------|
| AI Concept | `ai_concept` | Core AI/ML concepts, architectures, or techniques explained |
| AI Tool | `ai_tool` | Specific AI tools, libraries, frameworks, or services discussed |
| Mental Model | `mental_model` | Frameworks and mental models for thinking about AI systems |
| Practical Application | `practical_application` | Concrete ways to apply AI concepts to real projects |

## Combining Focus Areas

Pass multiple preset names as a comma-separated string to merge their categories:

```
focus_areas: "entrepreneurial,investment"
```

This produces 8 categories: `business_strategy`, `growth_tactic`, `lesson_learned`, `mistake_to_avoid`, `market_trend`, `opportunity`, `risk`, `recommendation`.

### Common Combinations

| Combination | Categories | Use Case |
|-------------|-----------|----------|
| `general` | 4 | Default all-purpose analysis |
| `entrepreneurial,investment` | 8 | Startup fundraising and business content |
| `technical,ai-learning` | 8 | AI/ML engineering talks |
| `youtube-channel,entrepreneurial` | 8 | Creator business strategy |
| `all` | 24 | Comprehensive extraction across all domains |

!!! note
    Duplicate categories are automatically deduplicated when combining presets.

## Insight Structure

Each extracted insight contains:

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | One of the 24 `InsightCategory` values |
| `title` | string | Brief title, 10-15 words |
| `summary` | string | 2-3 sentence summary |
| `quote` | string or null | Verbatim quote from transcript, if applicable |
| `timestamp_hint` | string or null | Approximate timestamp reference |
| `confidence` | float | Confidence score from 0.0 to 1.0 |
| `actionable` | boolean | Whether this insight is directly actionable |

## Controlling Output Volume

Use the `max_insights` parameter to limit the number of insights returned:

```
max_insights: "5"   # Focused summary
max_insights: "10"  # Default
max_insights: "20"  # Comprehensive analysis
```

!!! tip
    For long videos (1+ hours), use `max_insights: "15"` or higher with a single focused preset for best results.
