---
description: Prepare acquisition financing for a deal — deterministic financing analysis, capital-provider sourcing prep, and internal lender pre-read packages.
argument-hint: "<deal_id> [status|analyze|sourcing|lender-package]"
---

# Financing

Use this command when the user asks "how do I finance this acquisition?", "what leverage can this deal support?", "which lenders fit this deal?", or wants a lender pre-read package prepared.

## Usage

```
/financing <deal_id>                    # status of the deal's financing workflow
/financing <deal_id> analyze [scenario] [lbo_run_id]   # deterministic financing analysis (base|upside|downside)
/financing <deal_id> sourcing [amount] [provider_types] # provider sourcing from the latest (or a named) analysis
/financing <deal_id> lender-package [provider_match_ids] # internal lender pre-read package
```

## Execution

1. **status** (default) — call `mcp__ololand__get_financing_workflow_status(deal_id)`. Reports the latest financing analysis, sourcing run, and where the deal sits in the financing workflow.
2. **analyze** — call `mcp__ololand__run_financing_analysis(deal_id, scenario)`. This is a deterministic engine run (debt capacity, structure candidates, coverage ratios), optionally seeded from an existing LBO run via `lbo_run_id`. Default scenario is `base`.
3. **sourcing** — call `mcp__ololand__prepare_financing_sourcing(deal_id)`, optionally with `requested_financing_amount`, `target_provider_types`, or a specific `financing_run_id`. Returns matched provider types and draft outreach copy for human review.
4. **lender-package** — call `mcp__ololand__prepare_financing_lender_package(deal_id)`, optionally scoped to `provider_match_ids` from a sourcing run. Returns an internal pre-read with an application checklist.
5. Pair conclusions with evidence: cite the financing analysis figures the tools return; do not restate them from memory.

## Output

- **Status**: workflow stage, latest analysis id/scenario, sourcing-run summary.
- **Analysis**: supportable debt, structure candidates, key coverage/leverage ratios, assumptions used.
- **Sourcing prep**: provider matches (type, fit rationale), draft outreach for review — clearly labeled DRAFT.
- **Lender package**: pre-read contents and the application checklist, with the in-app `view_url` when returned.

## Guardrails

- **Prepare-only over this rail.** These tools analyze, match, and draft. Provider enrollment, sending outreach or emails, sharing anything with a lender, and submitting applications are human-approved actions that happen in the OloLand app's Financing flow — never claim to have contacted or applied to anyone.
- Outreach copy returned by sourcing prep is a draft for human review; present it as such.
- Financing figures come from the deterministic engine output. Do not blend in your own leverage estimates without labeling them as unverified commentary.
