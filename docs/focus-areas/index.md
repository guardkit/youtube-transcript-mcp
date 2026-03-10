# Focus Areas

Focus areas control how the `extract_insights` tool categorizes and structures insights from YouTube transcripts.

## Overview

The insight extraction system provides **6 focus area presets**, each containing **4 specialized categories** — 24 categories in total. When you call `extract_insights`, you specify which presets to use, and the system targets those specific types of insights.

## Built-in Presets

| Preset | Categories | Best For |
|--------|------------|----------|
| **general** | key_point, action_item, notable_quote, context | General-purpose analysis |
| **entrepreneurial** | business_strategy, growth_tactic, lesson_learned, mistake_to_avoid | Business and startup content |
| **investment** | market_trend, opportunity, risk, recommendation | Financial and investment content |
| **technical** | technology, tool, best_practice, pitfall | Technical tutorials and talks |
| **youtube-channel** | channel_strategy, content_idea, audience_growth, production_tip | Creator and channel growth content |
| **ai-learning** | ai_concept, ai_tool, mental_model, practical_application | AI and machine learning content |

## Usage

Pass preset names to the `extract_insights` tool:

```
# Single preset
focus_areas: "general"

# Multiple presets (comma-separated)
focus_areas: "entrepreneurial,investment"

# All 24 categories
focus_areas: "all"
```

## Learn More

- [Presets Reference](presets.md) — detailed descriptions, categories, and when to use each preset
- [Custom Focus Areas](custom.md) — all 24 category values, combining presets, and controlling output
