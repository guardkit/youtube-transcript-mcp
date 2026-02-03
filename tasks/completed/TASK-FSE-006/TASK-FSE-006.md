---
id: TASK-FSE-006
title: Add concrete JSON output example
status: completed
created: 2026-02-03T22:30:00Z
updated: 2026-02-03T22:55:00Z
completed: 2026-02-03T22:55:00Z
priority: low
parent_review: TASK-REV-A1B2
feature_id: FEAT-FSE
wave: 3
implementation_mode: direct
tags: [documentation, examples, insight-extraction]
target_files:
  - docs/features/FEAT-INT-001-insight-extraction.md
previous_state: in_review
state_transition_reason: Task completed - all acceptance criteria verified
completed_location: tasks/completed/TASK-FSE-006/
---

# Task: Add Concrete JSON Output Example

## Problem

The spec defines the insight extraction prompt and JSON schema, but doesn't show a concrete example of what the actual output looks like. This makes it harder to understand the expected format and test the implementation.

## Solution

Add a concrete JSON example showing real-world output from the insight extraction.

## Content to Add

Add after the `build_extraction_prompt` function in the service code section:

```markdown
### Example Output

Here's a concrete example of the expected JSON output when analyzing an entrepreneurial video:

```json
{
  "insights": [
    {
      "category": "business_strategy",
      "title": "Start with community building before product development",
      "summary": "The speaker emphasizes that successful startups build an engaged community first, then create products for that community. This reduces risk and ensures product-market fit from day one.",
      "quote": "Your community is your moat. Build the audience before you build the product.",
      "timestamp_hint": "around 5:30",
      "confidence": 0.92,
      "actionable": true
    },
    {
      "category": "mistake_to_avoid",
      "title": "Don't undercharge in early stages to win customers",
      "summary": "A key lesson learned: initially pricing too low attracted the wrong customers who churned quickly. Premium pricing filters for serious customers who value the offering.",
      "quote": null,
      "timestamp_hint": "around 12:45",
      "confidence": 0.88,
      "actionable": true
    },
    {
      "category": "growth_tactic",
      "title": "Use content marketing to build authority before selling",
      "summary": "The speaker grew from 0 to 10K subscribers by posting valuable content daily for 6 months before ever mentioning their product. Authority-first approach led to 40% conversion on launch.",
      "quote": "Give away your best stuff for free. The people who want more will pay.",
      "timestamp_hint": "around 18:20",
      "confidence": 0.85,
      "actionable": true
    }
  ],
  "key_quotes": [
    {
      "text": "Your community is your moat. Build the audience before you build the product.",
      "context": "Discussing why community-first approach reduces startup risk",
      "speaker": null
    },
    {
      "text": "Give away your best stuff for free. The people who want more will pay.",
      "context": "Explaining content marketing strategy that led to successful launch",
      "speaker": null
    }
  ],
  "summary": "This video covers community-driven product development, pricing strategies for early-stage startups, and content marketing as a growth lever. Key takeaway: build audience and authority before launching products."
}
```

This example shows:
- 3 insights across different categories
- Mix of insights with and without direct quotes
- Confidence scores based on how explicitly stated the insight was
- Actionability flags for practical advice
- Overall summary capturing the video's main themes
```

## Where to Add

In FEAT-INT-001, add this section after the `build_extraction_prompt` function (around line 257) and before the `chunk_transcript` function.

## Acceptance Criteria

- [x] Concrete JSON example added with realistic data
- [x] Example shows multiple insight categories
- [x] Example demonstrates optional fields (quote, timestamp_hint)
- [x] Brief explanation of what the example illustrates
