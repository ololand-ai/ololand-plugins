---
description: Read the deal or firm-wide Cockpit — readiness gates, pending approvals, valuation drivers outside tolerance, the dispatch ledger, and the precomputed financial briefing.
argument-hint: "<deal_id> [gates|approvals|drivers|actions|briefing] | portfolio [risks|approvals|actions]"
---

# Cockpit

Use this for "is this deal ready for IC?", "what is waiting on my approval?", "what needs attention across the portfolio?", or as the first stop for a financial question.

## Usage

```
/cockpit <deal_id>
/cockpit <deal_id> drivers
/cockpit <deal_id> briefing
/cockpit portfolio approvals
```

## Execution

1. Deal view: call `mcp__ololand__get_deal_cockpit(deal_id)`. Pass `lane` (`gates` | `approvals` | `drivers` | `actions`) when the user asks for one lane.
2. Portfolio view: call `mcp__ololand__get_portfolio_cockpit()`. Pass `lane` (`risks` | `approvals` | `actions`) and `limit` when asked. Portfolio risk rows carry no evidence fields; open a deal's register with `get_deal_risks` for file, page, and excerpt.
3. `briefing`: call `mcp__ololand__get_financial_briefing(deal_id)`. It is a deterministic read over ledgers the deal already holds: the engine-basis snapshot with provenance, historical revenue and EBITDA, the EBITDA bridge, debt and liquidity, cash flow, the covenant view of the latest financing run, and open cross-document conflicts. Pass `refresh=true` only when the user asks for a rebuild.

## Output

- **Gates**: each gate, its status, and whether it is derived (computed, cannot be set) or manual.
- **Approvals**: pending document patches, the latest draft IC package, open verification requests.
- **Drivers**: assumptions outside tolerance, from the deal's own valuation runs.
- **Actions**: newest dispatches with their status.
- **Briefing**: figures with the returned `citation_number`, then every section whose `coverage` is unavailable and the action that fills it.

## Guardrails

- Read-only. Approving stays in the OloLand app; `approve_patch` and `approve_ic_package` fail closed over this connection by design.
- A section marked `unavailable` is a gap. Name the action that fills it (Full Analysis, `/qoe-analysis`, `/financing`) and never infer the figure.
- When `basis_is_canonical` is false, say so and recommend Full Analysis instead of quoting a valuation.
- `kind="unavailable"` approval rows are outage placeholders, not work items. Report each lane's `truncated` flag.
- Closed, passed, and sample deals never appear in the portfolio view; do not read their absence as a clean book.
