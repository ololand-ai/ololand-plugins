---
description: Summarize deal health, open actions, and meeting-prep blockers from OloLand's deal-health surface.
argument-hint: "<deal_id> [actions|create-action]"
---

# Deal Health

Use this command when the user asks "what is the state of this deal?", "what is blocking us?", "prep me for the Monday meeting", or asks to add/list critical actions.

## Usage

```
/deal-health <deal_id>
/deal-health <deal_id> actions [open|in_progress|blocked|done]
/deal-health <deal_id> create-action "Pull AR aging from seller" priority=high
```

## Execution

1. Call `mcp__ololand__get_deal_health_summary(deal_id)` first.
2. If the user asks for actions or blockers, call `mcp__ololand__list_deal_actions` with optional `status` or `priority`.
3. If the user asks to add an action, confirm the title and priority, then call `mcp__ololand__create_deal_action`.
4. If the answer needs supporting evidence, pair this with `mcp__ololand__search_deal_documents` or `mcp__ololand__search_extracted_knowledge` and cite the result.

## Output

Render:

- **Overall status**: score, status, and recommendation.
- **Dimensions**: financial, risk, operational scores and the reason each is high/low.
- **Open actions**: count and top five action items.
- **Risk count**: high/medium/low risks from the health payload.
- **Next action**: what should happen before the next IC/workstream review.

## Guardrails

- Do not treat a health score as IC approval. Pair IC readiness with `/ic-approve-readiness`.
- When creating actions, keep titles concrete and owner-ready.
- Use tool-returned `view_url` values instead of hand-building app links.

