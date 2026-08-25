---
description: Read how accurate your firm's own past predictions have been — prediction accuracy, systematic biases, risk-category precision, and the fields analysts keep overriding. Firm-wide, not deal-scoped.
argument-hint: "[sector=<sector>]"
---

# Firm Calibration

Answers "how accurate have *we* been?" — the firm's own track record on predictions that have since been scored against realized outcomes. This is the institutional-memory read behind any claim that a forecast from this firm is trustworthy.

Firm-wide by construction. There is **no deal argument**: the scope always comes from your authenticated workspace, and the tool cannot be pointed at another firm's data.

## Usage

```
/firm-calibration [sector=<sector>]
```

## Arguments

- `sector` (optional) — restrict to one deal sector, e.g. `sector=Healthcare`. See the coverage caveat below: this filter does **not** reach every section.

## Execution

1. Call `mcp__ololand__get_firm_calibration`, passing `sector` only if the user gave one.
2. **Check `suppressed` first.** If `suppressed: true` with `suppression_reason: "ethical_wall_enforced"`, stop and report that calibration is *withheld* for this workspace because it carries an enforced ethical wall — the underlying sources aggregate company-wide and cannot be filtered to the deals you're cleared for. This is **not** "no data" and must never be reported as an un-calibrated firm.
3. **Read each row's `evidence_grade` before quoting anything.** The grade decides the *shape* of what you may say — it is never a reason to answer "insufficient history" and stop. Thresholds ride on the payload as `evidence_grade_thresholds`.
   - `none` — predictions recorded, none scored against a realized outcome yet. Say that, and point at the outcome-capture debt.
   - `anecdotal` — too few to average. `mean_accuracy` is **null on purpose**; `observations` holds the individual predicted/actual pairs. Report those verbatim — *"two exit-multiple predictions: one 9% high, one 12% low"* — never a percentage. There is no number to quote.
   - `emerging` — a mean with a 95% `accuracy_interval` {low, high}. Quote the range and n together, never the point alone — *"~80%, plausibly 62–98% on 6 deals"*.
   - `calibrated` — the point estimate the platform itself trusts for forecast adjustment. Still report n.
   - `overall_accuracy` is null unless at least one type is `emerging` or better, and `overall_evidence_grade` is the **weakest** grade behind it. Never call the firm "calibrated" from anything below that grade.
4. Report the sections that carry data. Skip empty ones rather than printing empty tables.
5. If the user asked how a *specific deal's* projections should shift given this history, that is `/calibrate-vs-history` — this command gives the firm-level picture, not a per-deal adjustment.

## Reading the payload honestly

**Nulls mean "not measured", never zero.** In `category_accuracy`, only `precision` is aggregated upstream. `recall`, `true_positives`, `false_positives`, and `false_negatives` come back **null** — render them as `—`. Printing `0` would state that the firm was measured and made zero errors, which is materially false calibration evidence. The same applies to `confidence` in `correction_patterns`.

**The sector filter does not reach everything.** The payload's `sector_filter_applies_to` names the sections it reached — `prediction_stats`, `systematic_biases`, `correction_patterns`. `category_accuracy`, `deal_count`, and `coverage` stay **firm-wide** even on a sector request. If the user passed a sector, say so explicitly; never present the whole readout as one coherent sector-scoped calibration.

**Nothing here describes model retraining.** Model/retraining performance is deliberately absent — those metrics carry no per-firm dimension and would mix other firms' data in. Do not infer anything about model quality or retraining from this tool.

**`total_predictions` vs `total_with_outcomes`** — the first is every prediction recorded, the second only those with a realized actual. The gap between them is the firm's outcome-capture debt, and it is often the more actionable number: an un-calibrated firm usually has a recording problem, not a modelling problem.

## Output

Lead with the headline and its sample size, then only the populated sections:

| Prediction type | Predictions | With outcomes | Evidence | Accuracy | Bias |
|---|---|---|---|---|---|
| exit_multiple | 14 | 8 | emerging (n=8) | 90% (82–98%) | overestimate 12% |
| revenue_growth | 5 | 2 | anecdotal (n=2) | — see observations | — |
| irr | 6 | 0 | none | — | — |

For an `anecdotal` row, list its observations under the table instead of a figure:

> revenue_growth — 2 scored outcomes: predicted 20% vs actual 30% (−50% error); predicted 20% vs actual 25% (−25% error).

| Risk category | Precision | Recall | TP/FP/FN |
|---|---|---|---|
| Customer Concentration | 75% | — | — |

| Field analysts override | Corrections | Avg shift | Sectors |
|---|---|---|---|
| risk.severity | 7 | -1.25 | Healthcare |

Close with one line on what the firm should do about it — e.g. "the firm's exit-multiple forecasts run 12% high on an 8-deal sample (emerging evidence — the range is 82–98%); discount new exit assumptions accordingly, and note 6 of 14 predictions still have no recorded outcome."

`systematic_biases` entries carry their own `evidence_grade`; a bias is only reported by the platform from `emerging` evidence upward, so an absent bias row on a thin type is expected, not a clean bill.

## Cost

A metered read (1 credit), on the same footing as the other institutional-memory reads. Not available on the free post-trial allowlist — if a call returns `tier_gated: true`, surface the upgrade CTA from the response rather than pre-refusing.

## Why this matters

Every AI tool will produce a forecast. Almost none can tell you whether *your firm's* forecasts have historically been right, or in which direction they've been wrong. That answer lives only in your own recorded outcomes — which is why the calibration and the outcome-capture debt are reported together.

## Related commands

- `/calibrate-vs-history` — applies historical bias to **one deal's** projections (deal-scoped counterpart to this command)
- `/record-outcome` — records realized actuals; this is what makes calibration possible at all
- `/playbook-recall` — what worked, didn't, or was missed on similar past deals
