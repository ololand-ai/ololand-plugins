---
description: Find similar completed deals from your firm's history, or compare a metric across an attribute-filtered slice of the pipeline — transfer learning insights, accuracy patterns, and valuation benchmarks.
argument-hint: "<deal_id> | compare <metric,metric,...> [sector] [structure] [size_band]"
---

# Similar Deals

Find similar completed deals and extract institutional learning patterns, or run
an attribute-filtered metric comparison across the firm's own pipeline.

## Usage

```
/similar-deals <deal_id>
/similar-deals compare <metric,metric,...> [sector=...] [structure=...] [size_band=...] [min_deal_size=...] [max_deal_size=...]
```

## Arguments

- `deal_id` — The current deal to find comparisons for (first form).
- `compare` mode: one or more `metrics` (e.g. `revenue,ebitda,ebitda_margin`),
  and optional `sector`, `structure`, `size_band` (`small`|`lower_mid`|`mid`|
  `upper_mid`|`large`), `min_deal_size`/`max_deal_size` filters.

## Execution — similarity ranking (`/similar-deals <deal_id>`)

1. Call `find_similar_deals` from the MCP server.
2. **If the response is `status: "no_usable_corpus"`** — stop here. Tell the user that strict similarity filters (deal type, sector family, size ratio) could not form a usable cohort. Do NOT relax filters or invent a cohort.
3. For each similar deal in a usable cohort, present:
   - **Deal profile**: Industry, size, type, outcome
   - **Similarity score**: Breakdown by industry (35%), size (25%), type (20%), margin (20%)
   - **Learning insights**:
     - Accuracy patterns: "Revenue projections were overestimated by 15% in 4/6 similar deals"
     - Common risks: "Customer concentration was flagged in 5/6 deals and materialized in 3"
     - Valuation ranges: "Median EV/EBITDA was 8.2x for similar deals"
4. Synthesize actionable recommendations:
   - Which risk categories to watch most carefully
   - Where historical predictions were systematically biased
   - How to calibrate financial assumptions based on past outcomes

## Execution — attribute comparison (`/similar-deals compare ...`)

Use this instead of the similarity ranking above when the user asks something
like "how does deal X's EBITDA margin compare to our other software deals" or
"show revenue across our mid-size deals" — an attribute-filtered comparison
table over the firm's pipeline, not a ranking against one reference deal. It
does **not** require the firm to have any closed/decided deals: it queries the
deal pool directly, so an all-open pipeline still returns a comparison.

1. Call `mcp__ololand__compare_deals_by_attribute(metrics, sector, structure, size_band, min_deal_size, max_deal_size, limit)`. `limit` is capped at 50. On an `invalid_metric` response, retry with one of the returned `allowed_metrics`.
2. Note that `structure` is **not** a true deal-structure taxonomy (no lbo/merger/asset-purchase field exists yet) — it matches the closed-deal decision type (`closed`/`passed`/`exited`/`withdrawn`) when the deal has one, else the deal's free-text pipeline stage. A miss on this filter means "no deal has that exact label," not "the firm has no such deals" — do not assert firm-wide absence from an empty result on this filter alone.
3. Compare the returned `matched_total` (all attribute-matching deals) against `deal_count` (the truncated size actually shown) and state whether the table is complete or partial.

## Output — compare mode

Table: Deal | Sector | Structure/Stage | Size band | {metric columns...}, followed by `matched_total` vs `deal_count`.

## Why This Matters

This is institutional intelligence — knowledge that accumulates across your firm's deal history. It's the compounding advantage that a general-purpose AI cannot provide because it doesn't have access to your prior deal outcomes.
