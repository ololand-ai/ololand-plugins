---
name: dcf-methodology
description: Use when computing or discussing DCF valuation — establishes OloLand's deterministic DCF conventions (units, defaults, terminal value, WACC, sensitivity bands) so model output is reproducible and comparable across deals.
---

# DCF Methodology

OloLand's deterministic DCF engine has specific conventions. Use these when discussing, requesting, or interpreting DCF output from any OloLand MCP tool.

## Unit system

- **Storage** — `FinancialDataSnapshot` stores values in ABSOLUTE DOLLARS.
- **Calculation** — DCF engine internally works in MILLIONS.
- **Display** — format as smart B/M/K via `format_smart()` (the platform helper).
- Never mix units across periods or inputs without explicit conversion.

## Default assumptions (when not specified by the user or the deal)

- **Tax rate** — 17% (use the deal-specific effective tax rate when filings provide it)
- **CapEx % of revenue** — 5% (override with historical 3-year average when available)
- **Terminal growth rate** — 2.5%
- **WACC** — CAPM-calculated using a deal-specific beta from comps; default to 9.5% if comps unavailable
- **Projection horizon** — 5 years explicit + terminal value
- **Working capital** — % of revenue, projected at the historical average

## Terminal value

- Use Gordon Growth (perpetuity) as the primary method.
- Cross-check with the exit-multiple method (terminal year EBITDA × industry median EV/EBITDA).
- If the two methods diverge by **>25%**, surface the discrepancy and explain which anchor is more credible for this deal.

## Sensitivity

- Always report a sensitivity matrix on WACC (±1.5%) × terminal growth (±0.5%).
- For PE deal review, also report sensitivity on exit-year EBITDA (±20%).

## Interpretation guardrails

- DCF is a scenario, not truth. State the key assumption drivers (revenue growth, EBITDA margin trajectory, terminal multiple).
- Bind every DCF claimed as current, published, or governed to the run, publication, financial-snapshot, and receipt identifiers returned by the valuation tool. Do not infer its basis from the newest financial snapshot or from a separate financial read.
- After an explicitly authorized fresh run, you may show the returned result as a separate **unpublished candidate** before publication only when it has its own candidate run identity and returned assumption provenance. State the missing publication/receipt fields and exclude the candidate from the governed decision range, football field, and bid input until a governed read binds it to the full identity.
- State whether each material assumption was returned as applied, caller-supplied, or defaulted. Do not claim an assumption was used merely because it appears in a separate deal, risk, or market response.
- If neither the full governed identity nor an explicitly authorized candidate run identity is present, or enterprise value is returned as `ev_not_meaningful`, withhold the valuation conclusion and label the result unavailable/not meaningful. A new model run is a write-like workflow and requires the user's explicit request; after it runs, re-fetch the DCF before claiming any candidate became current.
- The current canonical snapshot may have collapsed reported and adjusted EBITDA labels. Treat the returned model as `canonical_snapshot` only when its exact governed identity does not carry a publication-bound EBITDA bridge proving a distinct basis. When that lineage does prove a distinct adjusted basis, preserve the returned basis label and `adjusted_case` status. Never infer a second case from an uncited CIM number or a latest QoE result.
- If liquidity, covenant, control, or audit evidence contradicts the DCF, the deterministic engines (forensic QoE, scenario defense) override the DCF anchor. Use the `forensic-qoe` skill to find those signals first.
- Surface when a DCF is computed on data flagged for material weakness — that diminishes confidence regardless of the math. Use the `citation-discipline` skill to cite the material-weakness disclosure inline alongside the DCF output.

## Output format

When citing DCF output to a user, include:

- **EV** (smart-formatted, e.g. `$84.3M`)
- **Implied EV/EBITDA multiple**
- **Sensitivity band** (low / base / high EV)
- **Key assumptions used** (WACC, terminal growth, tax rate, CapEx %)
- **Model identity** (returned run/publication/snapshot/receipt identifiers) and assumption-application status
- **EBITDA basis** exactly as returned for that identity, including `adjusted_case` status
- **A one-sentence credibility note** tying back to evidence from filings — anchored with `[N]` citations to the source documents.

Illustrative format — replace every placeholder with the exact returned value and identifier:

> DCF Enterprise Value: `<base EV>` base, `<low EV>` low / `<high EV>` high. Model identity: run `<dcf_run_id>`, publication `<publication_id>`, snapshot `<snapshot_id>`, receipt `<receipt_id>`; EBITDA basis `<returned basis>`, `adjusted_case=<returned status>`. Assumptions: WACC `<value>` (`<applied|supplied|defaulted>`), terminal growth `<value>` (`<status>`), tax rate `<value>` (`<status>`), CapEx `<value>` (`<status>`). Implied EV/EBITDA = `<multiple>` base. Key driver: `<source-backed driver>` [1]. Credibility caveat: `<source-backed limitation>` [2]; the DCF is a scenario and contradictory covenant, liquidity, or audit evidence should override it for entry-price decisions.
