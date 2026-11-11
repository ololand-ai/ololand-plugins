---
description: Rank repeat public strategic acquirers and roll-up buyers by sector, EV band, and disclosed multiples from ~61K SEC-filed M&A deals.
argument-hint: "<sector or query, e.g. 'sector=manufacturing max_ev=250 from=2021'>"
---

# Strategic Buyer List (SEC-Filed Repeat Acquirers)

Aggregate repeat public strategic acquirers and roll-up platforms from OloLand's SEC EDGAR M&A corpus — who has repeatedly bought companies in a sector and enterprise-value band, at what disclosed multiples, with direct SEC filing citations.

## Usage

```
/buyer-list [<deal_id> | <query>] [sector=...] [sector_scope=either|target|acquirer] [min_ev=$M] [max_ev=$M] [from=YYYY] [to=YYYY] [min_deals=2]
```

## Arguments

- `deal_id` (optional) — if supplied, read `mcp__ololand__get_deal` and `mcp__ololand__get_financial_snapshot` first to derive the target's sector and indicative EV band transparently before querying buyers (never invent an EV band when deal size/financials are missing; run sector-only and disclose the missing band).
- `query` (optional) — keyword filter matched against deal summaries and company names (e.g. `"HVAC"`, `"dental"`, `"managed IT"`).
- `sector` (optional) — SEC SIC division: `agriculture`, `mining`, `construction`, `manufacturing`, `transport_utilities`, `wholesale`, `retail`, `finance_insurance_real_estate`, `services`, `public_administration`.
- `sector_scope` (optional) — `either` (default, capturing private-target roll-ups whose SIC code is recorded on the public acquirer), `target`, or `acquirer`.
- `min_ev` / `max_ev` (optional) — enterprise-value band in `$M`. Deals without disclosed EV are excluded whenever an EV bound is applied.
- `from` / `to` (optional) — announcement-year bounds (`1990`–`9999`).
- `min_deals` (optional) — minimum deduplicated acquisitions per buyer (default `2`).
- `exclude_mini_tenders` (optional) — defaults to `true` so `<5%` mini-tender bidders do not appear as strategic roll-up buyers.

## Execution

1. If a `deal_id` was provided, resolve the deal via `mcp__ololand__get_deal` (and `mcp__ololand__get_financial_snapshot` when needed) without triggering any model or pipeline run. Map the target's industry to one of the ten SEC SIC divisions when unambiguous and state the derived filters explicitly.
2. Call `mcp__ololand__search_strategic_acquirers` with the resolved parameters (`min_deals=2` default, `sector_scope="either"` default, `exclude_mini_tenders=True` default, `limit` up to `25`). Pass `citation_start_number` when chaining citations in a multi-tool turn.
3. **Mandatory SEC-filing scope boundary:** Explicitly state that this ranking covers **SEC-reporting public strategic acquirers and public roll-up platforms** whose acquisitions appear in EDGAR filings. It **does not** cover non-reporting private-equity sponsors, private-to-private add-ons with no SEC filer on either side, or PE fund hold-period clocks. If the user also wants private-equity sponsor candidates, offer `mcp__ololand__search_pe_buyers` as a separate step rather than blending the two sources.
4. **Preserve disclosure gaps:** `disclosed_ev_count` and `median_ev_ebitda` reflect only the subset of acquisitions where filings stated those figures; `NULL` means "not disclosed in the filing," never zero. Multi-filing rows of the same acquisition are already deduplicated server-side before `min_deals` is applied.

## Citing

Each buyer's `sample_deals` carry a `citation_number` when an openable SEC filing URL exists. Cite sample transactions inline as `[N]` using only that `citation_number` (never raw URLs, and never attach a bracket marker to a sample deal whose `citation_number` is null).

## Output

Report a table: Acquirer | CIK | Deals Matched (`completed` / `terminated`) | Disclosed EV Range ($M) | Median EV/EBITDA | Last Announced | Sample Cited Acquisitions `[N]`.

Follow with:
1. The returned `corpus_coverage` disclosure (including SEC-reporting strategic scope vs non-reporting private sponsors).
2. A concise diligence/exit-positioning takeaway (e.g., active consolidators vs occasional buyers, and whether disclosed multiples are sparse).
3. A non-reliance reminder that public SEC filing aggregations are illustrative market intelligence for qualified professionals, not investment banking or financial advice.
