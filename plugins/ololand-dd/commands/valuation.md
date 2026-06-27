---
description: Run financial valuation models (DCF, LBO, Monte Carlo, Comps) with risk-adjusted assumptions from OloLand's deterministic engines.
---

# Financial Valuation

Run deterministic financial valuation models using OloLand's computation engines.

## Usage

```
/valuation <deal_id> [method]
```

## Arguments

- `deal_id` (required) — The deal ID to value.
- `method` (optional) — Valuation method: `dcf` (default), `lbo`, `monte-carlo`, `comps`, `all`.

## Execution

1. Get current financials with `get_financial_snapshot`.
2. Fetch risk analysis with `get_deal_risks` to identify risk-adjusted assumptions.
3. Run the selected valuation:
   - **DCF**: `get_dcf_valuation` — WACC via CAPM, 5-year EBITDA projections, terminal value, sensitivity analysis
   - **Monte Carlo**: `run_monte_carlo_simulation` — Stochastic valuation with distribution output (P5/P25/P50/P75/P95, VaR, CVaR)
   - **LBO**: `run_lbo_model` — fetches the deal's latest persisted `LBORun`: IRR, money multiple (MOIC), equity investment, exit proceeds, entry/exit enterprise value and EBITDA, entry/exit multiples, net debt, equity value, holding period, tax rate, and any model warnings. If the deal has no `LBORun` yet, `run_lbo_model` returns nothing — call `run_deal_model` with `stages=["dcf", "lbo"]` first to build and persist one (no assumptions required; the engines read the deal snapshot), then re-fetch with `run_lbo_model`.
   - **Comps**: Trading multiples and precedent transactions from deal context
4. For `all`: run DCF + LBO + Monte Carlo + present combined football field range. (If no `LBORun` exists, build it once with `run_deal_model` as above; that single call persists both the DCFRun and LBORun.)

## After Completion

Report:
- Implied equity value range (low/mid/high)
- Key assumptions with sources (WACC, growth rate, terminal multiple)
- Sensitivity table (2-way: WACC vs terminal growth)
- Risk adjustments applied (from risk analysis)
- For LBO: IRR and MOIC at the modeled entry/exit, the entry/exit multiples and holding period that drive them, and any engine warnings
- Comparison to deal price (premium/discount analysis)
- Football field visualization (text-based: DCF range, LBO sponsor return, Monte Carlo P25-P75, Comps range)
