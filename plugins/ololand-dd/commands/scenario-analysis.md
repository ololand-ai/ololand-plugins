---
description: Run scenario stress tests, market-condition simulations, and real-options valuation, or preview an explicit annual fixed-cost correction when the connected server supports it.
---

# Scenario Analysis

Use OloLand's deterministic scenario workbench to stress the underwriting case and value strategic flexibility.

## Usage

```
/scenario-analysis <deal_id> [stress|market|real-options|all]
```

## Arguments

- `deal_id` (required) - The deal to analyze.
- `mode` (optional) - `stress`, `market`, `real-options`, or `all`. Default: `stress`.

## Explicit fixed-cost corrections

A request to add a specified annual fixed cost (for example, incremental CFO
cost) is a bounded correction to an identified baseline. It is not a market
simulation or a generic recession stress test; do not substitute those tools.

1. Discover the connected server's callable tools and schema. Use
   `preview_fixed_cost_scenario` only if it is actually exposed with the required
   parameters. Otherwise explain that this rail cannot preview the correction
   and hand off to the native scenario workbench. Do not request expanded OAuth
   permissions, invent a tool, fabricate a baseline, or claim a run occurred.
2. With an authorized deal and native conversation ID, call that tool without a
   correction to inspect the server-selected typed parent baseline and its
   identity/digest. A missing or ineligible baseline is a gap, not permission to
   rebuild historical actuals from chat or another model.
3. For the user's explicitly requested correction, follow the current schema:
   preserve returned parent identity/digest; supply a unique adjustment ID, the
   annual dollar cost and its status/provenance. Distinguish user assumptions
   from source-supported cost evidence. Do not reuse an adjustment ID to apply
   a cost twice or bypass a parent mismatch, unsupported period, or validation
   failure. No ad-hoc prorating or historical changes.
4. Show returned base/downside deltas and input lineage as a **hypothetical
   preview**. Deterministic arithmetic does not verify a cost's source. Preserve
   actuals and unrelated assumptions; state any returned limitations. This read
   does not persist, publish, approve, or replace a DCF/LBO/IC artifact. Use the
   returned handoff for a separately authorized app workflow when needed.

Do not run stress/market/real-options modes after a correction preview unless
that additional work is explicitly requested.

## Execution

1. For `stress` or `all`, call `run_scenario_stress_test(deal_id)`. Default scenario types are recession, rate spike, and sector downturn unless the user provides a list. Pass `severity` and `base_params` if supplied.
2. For `market` or `all`, call `simulate_market_conditions`. Required inputs are `current_rate`, `mean_rate`, and `volatility`; ask for them if missing. Use `years`, `n_scenarios`, and `seed` only when supplied or clearly requested.
3. For `real-options` or `all`, call `value_real_options(deal_id, options)`. Ask the user for the options list if it is missing; do not invent expansion, abandonment, or deferral options without labeling them as illustrative.
4. Use returned `view_url` values for web app handoff.

## Output

Render only fields actually returned; absent covenant/IRR, percentile, or option
outputs are gaps, not values to calculate from an unrelated model.

Render:

- **Stress-test results** - base case vs downside cases, EBITDA/covenant/IRR impact, breakpoints.
- **Market simulation** - distribution, P10/P50/P90 outputs, and most sensitive inputs.
- **Real options** - option type, value, assumptions, exercise trigger, and strategic implication.
- **Decision implication** - bid adjustment, covenant ask, data-room ask, or no-action conclusion.

## Output URL Conventions

Use the tool-returned `view_url`. Canonical surfaces:

- Scenario workbench: `https://app.ololand.ai/deals/{deal_id}/valuation/scenarios`
- Real options: `https://app.ololand.ai/deals/{deal_id}/valuation/real-options`
