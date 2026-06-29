---
description: Review or preview OloLand's value-impact ledger for a deal or firm. Shows hours saved, labor/advisor cost avoided, platform cost completeness, and methodology snapshots.
argument-hint: "<deal_id|company|preview> [workflow]"
---

# Value Impact

Use this command when the user asks for ROI, hours saved, avoided QoE/advisor cost, value multiple, or the evidence behind OloLand's value-impact claims.

## Usage

```
/value-impact <deal_id>
/value-impact company [start=YYYY-MM-DD] [end=YYYY-MM-DD] [workflow=<workflow_key>]
/value-impact preview workflows=pre_loi_screen,full_qoe deals=12 cost=238800
```

## Execution

1. If the first argument is a deal id, call `mcp__ololand__get_deal_value_impact(deal_id)`.
2. If the first argument is `company` or the user asks for firm-wide ROI, call `mcp__ololand__get_company_value_impact` with any date/workflow filters.
3. If the user asks "what would this be worth if..." call `mcp__ololand__preview_value_impact` with `workflows`, `workflow_counts`, `deals_per_year`, and optional `annual_platform_cost_cents`.
4. If the user asks what assumptions drive the ledger, call `mcp__ololand__get_value_impact_assumptions`.
5. Only call `mcp__ololand__update_value_impact_assumptions` when the user explicitly asks to change company ROI assumptions and confirms the values. That tool is company-admin gated.

## Output

Render:

- **Value summary**: hours saved, labor cost avoided, advisor cost avoided, gross value, net value if platform cost is complete.
- **Cost completeness**: `ololand_cost_is_complete`, missing-cost count, and whether `value_multiple` is known or intentionally withheld.
- **Top events**: workflow, source, completed time, confidence, and methodology note.
- **Assumptions**: hourly rates, display mode, external QoE baseline when relevant.
- **Next action**: open the returned `view_url`, adjust assumptions, or run the workflow that would create missing events.

## Guardrails

- Never convert unknown OloLand cost to zero. If `net_value_cents` or `value_multiple` is null because cost is incomplete, say that directly.
- Treat the ledger as substantiated estimate, not a guarantee of actual savings.
- Preserve confidence and methodology notes when presenting dollar figures.

