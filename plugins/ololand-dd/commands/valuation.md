---
description: Read financial valuation evidence or explicitly run DCF, LBO, and Monte Carlo models with governed identity and assumption provenance.
argument-hint: "<deal_id> <read|run|refresh> [dcf|lbo|monte-carlo|comps|all]"
---

# Financial Valuation

Read sourced valuation evidence or run deterministic financial models using OloLand's computation engines.

## Usage

```
/valuation <deal_id> read [method]
/valuation <deal_id> run <method>
/valuation <deal_id> refresh <method>
```

## Arguments

- `deal_id` (required) — The deal ID to value.
- `action` (required for mutation) — `read`, `run`, or `refresh`. Only the literal `run` or `refresh` action authorizes the named engine calls for this invocation. If the action is omitted, or an older invocation supplies a method in this position, treat the request as `read`; never infer mutation from the method name.
- `method` — Valuation method: `dcf`, `lbo`, `monte-carlo`, `comps`, or `all`. It defaults to `dcf` only for `read`. `run` and `refresh` require an explicit method; ask the user to name one rather than defaulting a write-like operation. `comps` is read-only, so reject `run comps` and `refresh comps` as unsupported without calling a model engine.

Examples:

```text
/valuation deal123 read all
/valuation deal123 run dcf
/valuation deal123 refresh lbo
/valuation deal123 refresh all
```

## Execution

1. Parse `action` before selecting any tool. Treat the literal `run` or `refresh` action as permission to execute only the requested mutating engines and only at the call counts below. `read`, an omitted action, or a legacy method-only invocation must use governed reads and must not create a candidate run.
2. For `dcf` only, fetch the persisted DCF with `get_dcf_valuation`. For an explicit DCF run/refresh, call `run_deal_model` exactly once with `stages=["dcf"]`, even when an older usable DCF exists; do not call it again as part of a later LBO/all step. (The `all` method owns its single combined `stages=["dcf", "lbo"]` call in step 6.) Treat its result as an **unpublished candidate run**, not as the current decision artifact: this lightweight tool does not itself create an eligible publication. Re-fetch `get_dcf_valuation` separately. Call the candidate current/published only if the governed read returns a publication, receipt, matching snapshot, and the same DCF run identity; otherwise present the candidate and current governed model in separate labeled sections and state that Full Analysis (or another explicit publication workflow) is required before the candidate becomes current. Do not launch Full Analysis automatically. Without an explicit run/refresh request, preserve the request as read-only and use the governed DCF when that read returns a usable, meaningful model with the required identity; report it as unavailable only when that governed read is missing, unusable, or not meaningful.
3. For **model-run outputs** (DCF, LBO, and Monte Carlo), require run/publication/snapshot/receipt identity before calling an output **current**, **published**, or **governed**, or including it in a combined decision range or football field. An explicitly requested fresh model result may be shown before publication as a separate **unpublished candidate**, including its returned range, only when it carries its own candidate run/simulation identity and returned assumption provenance. State which publication/receipt fields are absent, and never call that candidate current, use it as bid input, or combine it with governed outputs. If neither the full governed identity nor an explicit candidate identity is returned, or enterprise value is `ev_not_meaningful`, report the model result as unavailable/not meaningful; do not substitute from a latest snapshot.

   This model-identity gate does **not** apply to comparable-company or precedent-transaction observations: those are sourced market evidence, not DCF/LBO/Monte Carlo runs. Keep each Comps/Precedents lane usable when the returned observations carry source provenance from an authorized tool response and each material multiple, premium, target financial, and transaction value has its returned value-specific citation or equivalent returned source mapping. A supported market-evidence range may appear alone or as a separately labeled lane in a combined football field without model run/publication identifiers. Omit unsupported observations and any range that cannot be reproduced from the remaining sourced observations; never call the market-evidence lane a governed model. Even when a Comps/Precedents lane is usable, keep every unpublished model candidate out of the combined/governed football field and decision range.
4. Fetch `get_deal_risks` only as separately labeled downside context. Automated dollar impacts and WACC premiums are heuristic scenarios, not source-derived or approved DCF/bid inputs. Do not imply that the risk read changed the identified DCF; claim a risk adjustment was applied only when that DCF's own returned assumption lineage explicitly says so.
5. Run the selected valuation:
   - **DCF only**: use the identified `get_dcf_valuation` result — WACC, 5-year EBITDA projections, terminal value, and sensitivity analysis only as returned for that identity.
   - **Monte Carlo only**: there is no governed read endpoint in this workflow. For a read-only `monte-carlo` request, report Monte Carlo as unavailable; call `run_monte_carlo_simulation` exactly once only when the user explicitly requested a run/refresh. Label its distribution as a candidate unless the tool returns the required governed identity.
   - **LBO only**: `get_lbo_valuation` reads only the `LBORun` bound to the active eligible publication and returns its run/publication/snapshot/receipt identity, IRR, money multiple (MOIC), equity investment, exit proceeds, entry/exit enterprise value and EBITDA, entry/exit multiples, net debt, equity value, holding period, tax rate, warnings, and EBITDA-case status. If a pre-upgrade server does not expose `get_lbo_valuation`, use `run_lbo_model` once as a compatibility read and require the same identity fields; despite that legacy name it must not be treated as evidence that a model was run. For an explicit run/refresh of `lbo`, call `run_deal_model` exactly once with `stages=["dcf", "lbo"]` even if an eligible LBO already exists; this combined call supplies the DCF and LBO candidates and avoids a duplicate DCF run. Re-fetch governed DCF and LBO reads after the candidate call. Do not claim either candidate is current unless the corresponding governed read returns matching run/snapshot plus publication and receipt identity.
   - **Comps**: Read returned trading-comparable and precedent-transaction observations from deal context; use `search_precedent_deals` when a public-precedent query is appropriate. Preserve the returned company/transaction identity, period and metric basis, source URL/citation mapping, and coverage warnings. Build a range only from usable observations carrying a value-specific citation or equivalent returned source mapping; a null or unsupported value is unavailable, not zero and not permission to estimate.
6. For `all`, do not execute any method-specific mutation from step 5. In read-only mode, retrieve DCF + LBO, report Monte Carlo unavailable, and read Comps/Precedents evidence. A combined football field may include returned, meaningful model outputs that pass the full identity gate plus separately labeled Comps/Precedents ranges that pass the source-provenance gate. It must exclude every unpublished model candidate. On an explicit run/refresh, call `run_deal_model` exactly once with `stages=["dcf", "lbo"]` and call `run_monte_carlo_simulation` exactly once, then re-fetch the governed DCF and LBO and read Comps/Precedents without mutating them. These are the only mutating calls for `all`; do not repeat either call in a method branch.

## After Completion

Report:
- Implied equity value range (low/mid/high), inside a clearly labeled governed-model, unpublished-candidate, or source-backed-market-evidence section as applicable
- For each DCF/LBO/Monte Carlo model output, run/publication/snapshot/receipt identity exactly as returned, plus whether assumptions were returned as applied, supplied, or defaulted
- For an explicit lightweight refresh, the unpublished candidate identity and the current governed identity as separate rows; never collapse them when they do not match
- Treat both DCF and LBO as the `canonical_snapshot` case unless a publication-bound EBITDA bridge proves a distinct basis. Always report the returned `adjusted_case` status; never relabel the canonical case as reported or adjusted from a CIM figure alone.
- Key assumptions with sources (WACC, growth rate, terminal multiple)
- Sensitivity table (2-way: WACC vs terminal growth)
- Risk scenarios reviewed, with `source_derived`, `heuristic_scenario`, and `dcf_application_allowed` stated; list an adjustment as applied only when the identified model's own assumption lineage proves it
- For LBO: IRR and MOIC at the modeled entry/exit, the entry/exit multiples and holding period that drive them, and any engine warnings
- Comparison to deal price (premium/discount analysis)
- Football field visualization (text-based: governed DCF range, governed LBO sponsor return, governed Monte Carlo P25-P75, and separately labeled source-backed Comps/Precedents ranges); exclude unpublished model candidates
- Inline citations for every deal fact and every assumption source; if a result or evidence is unavailable, state that limitation instead of estimating it
