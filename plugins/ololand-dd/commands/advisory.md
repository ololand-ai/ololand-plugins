---
description: Request or inspect buyer-side advisory engagements attached to a deal.
argument-hint: "<deal_id> [list|request]"
---

# Advisory Engagement

Use this command when the user asks for an OloLand advisor, diligence support, external expert help, or the status of an advisory request.

## Usage

```
/advisory <deal_id> list
/advisory <deal_id> request buy_side_diligence
```

## Execution

1. Call `mcp__ololand__list_deal_advisory_engagements(deal_id)` first.
2. If action is `request`, confirm the requested engagement type, scope, and any fee estimate, then call `mcp__ololand__request_advisory_engagement`.
3. Render status and deliverable state from the returned engagement payload.

## Output

- Engagement id, type, status, requested time, assigned advisor summary if present.
- Scope and deliverables, if present.
- Conflict or manual-fulfillment notes when returned.
- Next step: wait for assignment, clarify scope, or review deliverable.

## Guardrails

- Do not imply instant advisor assignment or automated payment. This is a buyer-side request workflow.
- Admin queue, assignment, and fulfillment remain native OloLand operations.
- Do not bypass reviewer/advisor conflict checks.

