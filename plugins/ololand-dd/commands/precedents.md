---
description: Search ~61K public M&A transactions (2006-2026) for precedent deals and market context — outcome-labeled, with SEC filing citations.
argument-hint: "<query or filters, e.g. 'industrial services roll-ups since 2022'>"
---

# Precedent Deals

Search OloLand's public M&A corpus for market context and precedent transactions — "who has bought companies like this, when, and roughly for how much".

## Usage

```
/precedents <query> [min_ev=$M] [max_ev=$M] [from=YYYY] [to=YYYY] [outcome=completed|terminated] [sector=...]
```

## Arguments

- `query` (optional) — free text matched against deal summaries and company names.
- `min_ev` / `max_ev` (optional) — enterprise-value band, in millions.
- `from` / `to` (optional) — announcement-year range.
- `outcome` (optional) — `completed` or `terminated`. Omit for any/unresolved.
- `sector` (optional) — one SEC SIC division: `agriculture`, `mining`, `construction`, `manufacturing`, `transport_utilities`, `wholesale`, `retail`, `finance_insurance_real_estate`, `services`, `public_administration`.

## Execution

1. Call `mcp__ololand__search_precedent_deals` with the mapped arguments. Cap `limit` at 25; if the user wants a specific ordinal offset for citations across a multi-step research turn, pass `citation_start_number` accordingly (shared counter with `search_deal_documents`).
2. **This is PUBLIC filing data covering the whole market — not this firm's own deals.** If the user actually means the firm's pipeline ("our deals like this one"), use `/similar-deals` or `compare_deals_by_attribute` instead; do not silently redirect without saying so.
3. **Read the returned `corpus_coverage` note before drawing any conclusion from an empty result or a null field.** A `NULL` premium, target financial, or multiple means "not disclosed in the source filing," never "zero." Outcome and close data are still being backfilled — a missing `outcome` means unresolved, not that the deal failed to close.
4. Do not assert a sector or period has no comparable deals from an empty page alone; report what the query found and what the corpus note says about coverage.

## Citing

Every deal with a source filing carries a `citation_number` — use it for claims about the transaction itself (parties, dates, outcome). For a PREMIUM, MULTIPLE, or TARGET FINANCIAL specifically, cite `valuation_citation_numbers[<field>]` instead — it numbers the exact filing URL substantiating that value, which is often a different filing from `citation_number`. Both live in one `[N]` namespace. A value absent from `valuation_citation_numbers`, or a deal with no `citation_number`, has no openable source — do not attach a bracket-number marker to it.

## Output

Report a table: Company | Acquirer | Announced | Sector | EV ($M, cited) | Premium (cited, or "not disclosed") | Outcome | `[N]`.

Follow with the `corpus_coverage` note verbatim (or a faithful summary of it), then a one-line takeaway on what this precedent set implies for the deal at hand.

## After Completion

If the user is evaluating a specific deal, suggest `/valuation <deal_id> read all` to compare the precedent range with governed DCF/LBO and source-backed Comps without starting a model run.
