---
description: Run scenario stress tests, market-condition simulations, and real-options valuation from OloLand's deal-scoped scenario workbench.
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

## Execution

1. For `stress` or `all`, call `run_scenario_stress_test(deal_id)`. Default scenario types are recession, rate spike, and sector downturn unless the user provides a list. Pass `severity` and `base_params` if supplied.
2. For `market` or `all`, call `simulate_market_conditions`. Required inputs are `current_rate`, `mean_rate`, and `volatility`; ask for them if missing. Use `years`, `n_scenarios`, and `seed` only when supplied or clearly requested.
3. For `real-options` or `all`, call `value_real_options(deal_id, options)`. Ask the user for the options list if it is missing; do not invent expansion, abandonment, or deferral options without labeling them as illustrative.
4. Use returned `view_url` values for web app handoff.

## Output

Render:

- **Stress-test results** - base case vs downside cases, EBITDA/covenant/IRR impact, breakpoints.
- **Market simulation** - distribution, P10/P50/P90 outputs, and most sensitive inputs.
- **Real options** - option type, value, assumptions, exercise trigger, and strategic implication.
- **Decision implication** - bid adjustment, covenant ask, data-room ask, or no-action conclusion.

## Output URL Conventions

Use the tool-returned `view_url`. Canonical surfaces:

- Scenario workbench: `https://app.ololand.ai/deals/{deal_id}/valuation/scenarios`
- Real options: `https://app.ololand.ai/deals/{deal_id}/valuation/real-options`
