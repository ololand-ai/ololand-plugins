---
description: Read or explicitly run financial valuation models (DCF, LBO, Monte Carlo, Comps) with governed model identity and assumption provenance.
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

1. Treat an explicit `run` or `refresh` request as permission to execute only the requested mutating engines. A read-only request must use governed reads and must not create a candidate run.
2. For `dcf` only, fetch the persisted DCF with `get_dcf_valuation`. For an explicit DCF run/refresh, call `run_deal_model` exactly once with `stages=["dcf"]`, even when an older usable DCF exists; do not call it again as part of a later LBO/all step. (The `all` method owns its single combined `stages=["dcf", "lbo"]` call in step 6.) Treat its result as an **unpublished candidate run**, not as the current decision artifact: this lightweight tool does not itself create an eligible publication. Re-fetch `get_dcf_valuation` separately. Call the candidate current/published only if the governed read returns a publication, receipt, matching snapshot, and the same DCF run identity; otherwise present the candidate and current governed model in separate labeled sections and state that Full Analysis (or another explicit publication workflow) is required before the candidate becomes current. Do not launch Full Analysis automatically. Without an explicit run/refresh request, preserve the request as read-only and use the governed DCF when that read returns a usable, meaningful model with the required identity; report it as unavailable only when that governed read is missing, unusable, or not meaningful.
3. If the returned valuation has no run/publication/snapshot/receipt identity, or labels enterprise value `ev_not_meaningful`, report it as unavailable or not meaningful; do not supply an implied range, football-field point, or substitute from a latest snapshot.
4. Fetch `get_deal_risks` only as separately labeled downside context. Automated dollar impacts and WACC premiums are heuristic scenarios, not source-derived or approved DCF/bid inputs. Do not imply that the risk read changed the identified DCF; claim a risk adjustment was applied only when that DCF's own returned assumption lineage explicitly says so.
5. Run the selected valuation:
   - **DCF only**: use the identified `get_dcf_valuation` result — WACC, 5-year EBITDA projections, terminal value, and sensitivity analysis only as returned for that identity.
   - **Monte Carlo only**: there is no governed read endpoint in this workflow. For a read-only `monte-carlo` request, report Monte Carlo as unavailable; call `run_monte_carlo_simulation` exactly once only when the user explicitly requested a run/refresh. Label its distribution as a candidate unless the tool returns the required governed identity.
   - **LBO only**: `get_lbo_valuation` reads only the `LBORun` bound to the active eligible publication and returns its run/publication/snapshot/receipt identity, IRR, money multiple (MOIC), equity investment, exit proceeds, entry/exit enterprise value and EBITDA, entry/exit multiples, net debt, equity value, holding period, tax rate, warnings, and EBITDA-case status. If a pre-upgrade server does not expose `get_lbo_valuation`, use `run_lbo_model` once as a compatibility read and require the same identity fields; despite that legacy name it must not be treated as evidence that a model was run. For an explicit run/refresh of `lbo`, call `run_deal_model` exactly once with `stages=["dcf", "lbo"]` even if an eligible LBO already exists; this combined call supplies the DCF and LBO candidates and avoids a duplicate DCF run. Re-fetch governed DCF and LBO reads after the candidate call. Do not claim either candidate is current unless the corresponding governed read returns matching run/snapshot plus publication and receipt identity.
   - **Comps**: Trading multiples and precedent transactions from deal context
6. For `all`, do not execute any method-specific mutation from step 5. In read-only mode, retrieve DCF + LBO and report Monte Carlo unavailable; present a combined football field only for returned, meaningful, identified model outputs. On an explicit run/refresh, call `run_deal_model` exactly once with `stages=["dcf", "lbo"]` and call `run_monte_carlo_simulation` exactly once, then re-fetch the governed DCF and LBO. These are the only mutating calls for `all`; do not repeat either call in a method branch.

## After Completion

Report:
- Implied equity value range (low/mid/high)
- DCF run/publication/snapshot/receipt identity exactly as returned, plus whether assumptions were returned as applied, supplied, or defaulted
- For an explicit lightweight refresh, the unpublished candidate identity and the current governed identity as separate rows; never collapse them when they do not match
- Treat both DCF and LBO as the `canonical_snapshot` case unless a publication-bound EBITDA bridge proves a distinct basis. Always report the returned `adjusted_case` status; never relabel the canonical case as reported or adjusted from a CIM figure alone.
- Key assumptions with sources (WACC, growth rate, terminal multiple)
- Sensitivity table (2-way: WACC vs terminal growth)
- Risk scenarios reviewed, with `source_derived`, `heuristic_scenario`, and `dcf_application_allowed` stated; list an adjustment as applied only when the identified model's own assumption lineage proves it
- For LBO: IRR and MOIC at the modeled entry/exit, the entry/exit multiples and holding period that drive them, and any engine warnings
- Comparison to deal price (premium/discount analysis)
- Football field visualization (text-based: DCF range, LBO sponsor return, Monte Carlo P25-P75, Comps range)
- Inline citations for every deal fact and every assumption source; if a result or evidence is unavailable, state that limitation instead of estimating it
