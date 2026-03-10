# Focus Area Presets

YouTube Transcript MCP includes 6 built-in focus area presets, each containing 4 specialized insight categories. Pass preset names to the `extract_insights` tool via the `focus_areas` parameter.

## General

The default preset for broad, all-purpose transcript analysis.

| Category | Description |
|----------|-------------|
| `key_point` | Main takeaways and central ideas |
| `action_item` | Specific actions viewers can take |
| `notable_quote` | Memorable or impactful statements |
| `context` | Background context, framing, and important situational details |

**When to use:** Any video where you want a balanced overview — interviews, lectures, podcasts, news segments.

**Example usage:**

```
focus_areas: "general"
```

---

## Entrepreneurial

Optimized for startup, business, and founder content.

| Category | Description |
|----------|-------------|
| `business_strategy` | Core business approaches, models, and strategic decisions |
| `growth_tactic` | Specific tactics for user/revenue/market growth |
| `lesson_learned` | Key learnings from experience, both positive and negative |
| `mistake_to_avoid` | Common pitfalls, errors, and things that didn't work |

**When to use:** Founder interviews, Y Combinator talks, business case studies, startup retrospectives.

**Example usage:**

```
focus_areas: "entrepreneurial"
```

---

## Investment

Designed for financial analysis, market commentary, and investment-focused content.

| Category | Description |
|----------|-------------|
| `market_trend` | Industry trends, market movements, and predictions |
| `opportunity` | Investment or business opportunities identified |
| `risk` | Potential risks, downsides, or concerns mentioned |
| `recommendation` | Specific recommendations or advice given |

**When to use:** Market analysis videos, earnings discussions, economic forecasts, investment thesis breakdowns.

**Example usage:**

```
focus_areas: "investment"
```

---

## Technical

Built for software engineering, architecture, and technical tutorial content.

| Category | Description |
|----------|-------------|
| `technology` | Technologies, platforms, or systems mentioned |
| `tool` | Tools, software, or resources recommended |
| `best_practice` | Recommended approaches and methodologies |
| `pitfall` | Common problems and anti-patterns to avoid |

**When to use:** Conference talks, coding tutorials, architecture discussions, tech reviews.

**Example usage:**

```
focus_areas: "technical"
```

---

## YouTube Channel

Tailored for creator economy and YouTube growth strategy content.

| Category | Description |
|----------|-------------|
| `channel_strategy` | High-level channel positioning, niche, and growth direction |
| `content_idea` | Specific video ideas, formats, series concepts to steal or adapt |
| `audience_growth` | Tactics for growing subscribers, views, and engagement |
| `production_tip` | Filming, editing, thumbnails, titles, SEO, workflow improvements |

**When to use:** Creator advice videos, YouTube analytics breakdowns, channel reviews, production tutorials.

**Example usage:**

```
focus_areas: "youtube-channel"
```

---

## AI Learning

Focused on artificial intelligence, machine learning, and applied AI content.

| Category | Description |
|----------|-------------|
| `ai_concept` | Core AI/ML concepts, architectures, or techniques explained |
| `ai_tool` | Specific AI tools, libraries, frameworks, or services discussed |
| `mental_model` | Frameworks and mental models for thinking about AI systems |
| `practical_application` | Concrete ways to apply AI concepts to real projects |

**When to use:** AI research paper walkthroughs, tool demos, ML tutorials, AI strategy discussions.

**Example usage:**

```
focus_areas: "ai-learning"
```

---

## Combining Presets

You can combine multiple presets by passing a comma-separated list:

```
focus_areas: "entrepreneurial,investment"
```

This merges the categories from both presets (8 categories total in this example).

To use **all 24 categories** at once:

```
focus_areas: "all"
```

!!! tip
    Using fewer, more targeted focus areas tends to produce higher-quality insights. Start with one preset and add more only if needed.
