---
name: financial-valuation
description: Use when performing financial valuations, building DCF/LBO models, running Monte Carlo simulations, or analyzing comparable transactions. Provides deterministic valuation framework with strict unit enforcement.
---

# Financial Valuation Methodology

## Deterministic Engines (Not LLM-Generated)

OloLand uses validated computation engines for all financial models. Never generate financial model outputs as prose — use MCP tools.

### DCF (Discounted Cash Flow)
- **Tool**: `get_dcf_valuation(deal_id)`
- **Engine**: EBITDA → Free Cash Flow projection (5-10 years) → Terminal value (perpetuity growth) → WACC discount
- **WACC**: CAPM-calculated (risk-free rate + beta * equity risk premium + size premium)
- **Sensitivity**: Revenue growth rate vs EBITDA margin vs terminal growth rate
- **Unit system**: `StrictFinancialValue` — ACTUAL dollars in storage, MILLIONS in calculation, Smart B/M/K in display

### LBO (Leveraged Buyout)
- Multi-tranche debt: Senior, Mezzanine, Subordinated, Revolver
- Cash sweep ordering: Revenue → Operations → Debt repayment → Equity
- PIK (Payment-in-Kind) toggle per tranche
- Leverage covenants: Total leverage ratio, interest coverage ratio
- Returns: IRR and MOIC at exit under multiple scenarios

### Monte Carlo Simulation
- **Tool**: `run_monte_carlo_simulation(deal_id, n_simulations, seed)`
- **Execution boundary**: This tool creates and persists a new simulation. Authority must come from exactly one of these contexts:
  1. A direct `/valuation <deal_id> run monte-carlo`, `/valuation <deal_id> refresh monte-carlo`, `/valuation <deal_id> run all`, or `/valuation <deal_id> refresh all` call.
  2. The user's explicit invocation of, or unambiguous request to run, a named fixed-purpose workflow whose visible contract declares one Monte Carlo run, currently the **public branch only** of `/pre-screen`, `/ic-memo-skeptical`, or DD Analyst **Full DD mode**. That invocation authorizes only the single call, deal, and parameters declared by that workflow; it does not require a second `/valuation run` phrase. The private `/pre-screen` branch authorizes no valuation engine and must remain signal-only until a dedicated governed private-company tool exists.
- Auto-loading this skill, routing to an agent, a generic diligence/memo question, a background task, a prior run, or merely recommending Monte Carlo grants no authority. A failed authorized call also grants no automatic retry. When neither context applies, do not call the tool; report that there is no governed Monte Carlo read endpoint.
- Vectorized stochastic engine (not loop-bound)
- Distribution support: Normal, LogNormal, Triangular
- Gaussian copula for correlated variables
- Output: Full EV/equity distribution + P5/P25/P50/P75/P95 + VaR/CVaR

### Comparable Analysis
- Trading multiples: EV/Revenue, EV/EBITDA, P/E
- Precedent transactions: Recent M&A deal premiums
- Peer selection by industry, size, geography, margin profile

## Cross-Document Reconciliation

Before any valuation, verify input data consistency:
- Compare revenue/EBITDA across: CIM, audited financials, management model, tax returns
- Source hierarchy: CPA audited > tax return > management model > AI extracted
- Flag discrepancies > 2% spread
- Treat separately reconciled document values as evidence about a discrepancy, not as permission to rewrite an identified model. Report the exact model-returned input and the higher-confidence document value side by side, with their distinct citations and the variance.
- Never substitute, recalculate, relabel, or explain a governed DCF/LBO using a separately reconciled figure unless the exact model lineage (run, publication, snapshot, and receipt) proves that figure was applied. Otherwise preserve the governed model as returned and report the discrepancy in a separate reconciliation section.
- A reconciled value may enter a new model only through an explicitly authorized model workflow that records that exact value in its returned assumption/input lineage. Until a governed read binds the resulting run to the required identity, keep that result an unpublished candidate and do not imply the existing governed model incorporated the reconciliation.

## Risk Context and Model Integrity

Risk findings must remain separate from the governed valuation unless the
identified model's own returned assumption lineage proves an approved,
source-derived bridge for that exact model identity.

- Present automated dollar impacts and WACC premiums as separately labeled
  `heuristic_scenario` context. They are not source-derived or approved model
  inputs merely because the risk engine returned them.
- Do not alter, relabel, or substitute a governed DCF/LBO case using automated
  risk amounts or WACC premiums. Do not require or invent a risk-adjusted range.
- An adjustment may be described as applied only when the exact governed model
  identity (run, publication, snapshot, and receipt) returns assumption lineage
  proving a `source_derived` approved bridge. Otherwise report the governed
  base case and the risk scenario separately, with `dcf_application_allowed`
  stated as returned.
- Keep the publication/candidate identity rules intact: a candidate run is not
  the current decision artifact until a governed read binds it to the required
  publication, receipt, snapshot, and matching run identity.
