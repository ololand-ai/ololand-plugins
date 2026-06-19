---
description: Run or retrieve OloLand's deal-scoped Quality of Earnings analytical workbench for revenue quality, EBITDA adjustments, working capital, and evidence-backed QoE findings.
---

# QoE Analysis

Run the deal-scoped Quality of Earnings workbench. The backend auto-hydrates from the latest financial snapshot when explicit data is not provided, while still accepting overrides for replay or power-user workflows.

## Usage

```
/qoe-analysis <deal_id> [latest|run]
```

## Arguments

- `deal_id` (required) - The deal to analyze.
- `mode` (optional) - `latest` to inspect the cached result; `run` to create a fresh analysis. Default: `latest`, then run if no result exists.

## Execution

1. Call `get_latest_qoe_analysis(deal_id)`.
2. If there is no cached result, or the user asks to rerun, call `run_qoe_analysis(deal_id)`.
3. If the user supplied structured overrides, pass them through to `run_qoe_analysis`: `revenue_items`, `expense_items`, `financial_data`, `transactions`, `adjustments`, `reported_ebitda`, `revenue_data`, and `working_capital_data`.
4. Use the returned `view_url` for the web app handoff.

## Output

Render:

- **QoE verdict** - clean / watch / concern / blocker, based on the returned risk and adjustment profile.
- **EBITDA bridge** - reported EBITDA -> normalized EBITDA, with adjustment classes and dollar impacts.
- **Revenue quality** - concentration, cut-off, recurring/non-recurring indicators, and any source gaps.
- **Working capital** - DSO/DPO/DIO and normalization flags.
- **Evidence gaps** - data classes that prevented stronger conclusions.

## Output URL Conventions

Use the tool-returned `view_url`. Canonical surface:

- QoE workbench: `https://app.ololand.ai/deals/{deal_id}/valuation/qoe`
