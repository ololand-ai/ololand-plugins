---
description: Search ~61K public M&A transactions (2006-2026) for precedent deals, private-target comps, or quote-verified deal-break gotchas (`--gotchas`) — with SEC filing citations.
argument-hint: "[--gotchas] <query or filters, e.g. '--gotchas sector=services max_ev=250'>"
---

# Precedent Deals & Deal-Break Gotchas

Search OloLand's public M&A corpus for market context and precedent transactions — or pass `--gotchas` to surface quote-verified historical SEC-filed deals in a sector/size band that failed to close and why.

## Usage

```
/precedents [--gotchas] <query> [min_ev=$M] [max_ev=$M] [from=YYYY] [to=YYYY] [outcome=completed|terminated] [sector=...] [sector_scope=either|target|acquirer] [target_ownership=public|private] [termination_category=...]
```

## Arguments

- `--gotchas` (optional) — deal-break warning mode: sets `outcome="terminated"` and `require_verified_termination_reason=True` so only quote-verified merger breaks (`termination_quote_verified=True`, excluding ancillary `not_a_deal_break` rows) are returned.
- `query` (optional) — free text matched against deal summaries and company names.
- `min_ev` / `max_ev` (optional) — enterprise-value band, in millions.
- `from` / `to` (optional) — announcement-year range.
- `outcome` (optional) — `completed` or `terminated`. Omit for any/unresolved (forced to `terminated` when `--gotchas` is passed).
- `sector` (optional) — one SEC SIC division: `agriculture`, `mining`, `construction`, `manufacturing`, `transport_utilities`, `wholesale`, `retail`, `finance_insurance_real_estate`, `services`, `public_administration`.
- `sector_scope` (optional) — `either` (default, matching target OR public-acquirer SIC so private-target acquisitions without a target CIK remain discoverable), `target`, or `acquirer`.
- `target_ownership` (optional) — `public` (SEC-reporting target with CIK) or `private` (non-filer target acquired by a public filer).
- `termination_category` (optional) — `regulatory_blocked`, `financing_failure`, `mac_dispute`, `shareholder_rejected`, `competing_bid`, `covenant_or_condition_breach`, or `mutual_termination`.
- `exclude_mini_tenders` (optional) — defaults to `true`, filtering `<5%` mini-tender solicitations (e.g. MacKenzie/TRC) unless the user explicitly asks to include them (`exclude_mini_tenders=false`).

## Execution

1. Call `mcp__ololand__search_precedent_deals` with the mapped arguments (`sector_scope` defaults to `"either"`, `exclude_mini_tenders` defaults to `True`; when `--gotchas` is present, pass `outcome="terminated"` and `require_verified_termination_reason=True`). Cap `limit` at 25; if the user wants a specific ordinal offset for citations across a multi-step research turn, pass `citation_start_number` accordingly (shared counter with `search_deal_documents`).
2. **This is PUBLIC filing data covering the whole market — not this firm's own deals.** If the user actually means the firm's pipeline ("our deals like this one"), use `/similar-deals` or `compare_deals_by_attribute` instead; do not silently redirect without saying so.
3. **Read the returned `corpus_coverage` note before drawing any conclusion from an empty result or a null field.** A `NULL` premium, target financial, or multiple means "not disclosed in the source filing," never "zero." Outcome and close data are still being backfilled — a missing `outcome` means unresolved, not that the deal failed to close.
4. **Never state a base rate, break-rate percentage, or deal-specific failure probability from this output.** `count` is a bounded page size (at most 25), not a market census. In `--gotchas` mode, frame findings strictly as: *"Historical SEC-filed deals in this sector/band that failed to close and why — verify against the target's data room."*
5. Do not assert a sector or period has no comparable deals or deal breaks from an empty page alone; report what the query found and what `corpus_coverage` says about coverage.

## Citing

Every deal with a source filing carries a `citation_number` — use it for claims about the transaction itself (parties, announcement date). For an OUTCOME, CLOSE DATE, or TERMINATION REASON / VERBATIM BREAK QUOTE specifically, cite `outcome_citation_number` as `[N]` (never raw URLs; if `outcome_citation_number` is null, state the disposition without a bracket marker). For a PREMIUM, MULTIPLE, or TARGET FINANCIAL specifically, cite `valuation_citation_numbers[<field>]` instead. All markers share one `[N]` namespace. Never attach a bracket marker to a value lacking its field-specific citation number.

## Output

- **Standard mode:** Report a table: Target | Acquirer | Announced | Sector | EV ($M, cited) | Premium (cited, or "not disclosed") | Outcome | `[N]`.
- **`--gotchas` mode:** Title the section **"Historical SEC-Filed Deal-Break Precedents (Verify Against Data Room)"** and report: Target | Acquirer | Announced | EV ($M, cited or "not disclosed") | Verified Break Category | Filing Excerpt & Diligence Question to Check | `[outcome_citation_number]`.

Follow with the `corpus_coverage` note and a brief non-reliance note reminding the reader that public SEC precedent intelligence is illustrative research context for qualified professionals, not investment or legal advice.

## After Completion

If the user is evaluating a specific deal, suggest `/valuation <deal_id> read all` to compare the precedent range with governed DCF/LBO and source-backed Comps without starting a model run, or `/buyer-list` to identify repeat public strategic acquirers in the same sector and EV band.
