---
description: Draft an in-session IC investment memo with one bounded Monte Carlo run using the skeptical tile-stitching pattern — public-facts refresh, individual engine tiles, web fetches, and explicit gap-vs-finding framing. Refuses to render against a stale stored deal record or an unbound simulation.
---

# Skeptical IC Memo

Compose an IC-defensible investment memo using OloLand's lower-level tile + web-fetch pattern. Designed to produce the output style that survives IC scrutiny — every $-figure cited, every engine output framed as `[finding]` or `[gap]`, no boilerplate gating conditions, no overtrusted simulation outputs.

This is the **preferred** memo entry point as of 2026-05-12. `run_due_diligence` is a separate bounded extraction pipeline; it does not run valuation, war-game, forensic QoE, conflict detection, or memo generation. The deprecated `generate_investment_memo` entry point invokes the memo task without the public-facts freshness precondition. `/ic-memo-skeptical` makes each additional read or bounded engine call explicit and hard-codes the orchestration that produces tighter artifacts.

## Usage

```
/ic-memo-skeptical <deal_id>
```

## Arguments

- `deal_id` (required) — The deal to memo. Works on both public-target (ticker / CIK) and private deals; the public-facts gate only fires when applicable.

## Bounded Monte Carlo authority

The user's explicit invocation of, or unambiguous request to run, `/ic-memo-skeptical <deal_id>` authorizes exactly one `run_monte_carlo_simulation(deal_id, n_simulations=10000, seed=42)` call in Step 4 for that deal. It does not authorize any other valuation engine, war-game, different deal, retry, or later/background run. Automatic routing to this command or a generic request for memo commentary does not grant this authority. If the call fails or returns no `simulation_id`, record Monte Carlo as a `[gap]` and stop before drafting. If it succeeds, only the exact response carrying that new `simulation_id` may be used in the in-session draft. **Never call `compose_ic_memo` from this command:** that tool has no simulation-binding or MC-exclusion parameter and could reuse an older persisted simulation even after a successful new run. Never infer, substitute, or reuse a prior simulation identity.

## Orchestration (every step is required; do not skip)

Execute in order. The model invoking this command must walk each step, log the result, and surface gaps as diligence asks rather than papering over them.

### Step 1 — Ground the deal record

1. Call `get_deal` to read the stored Deal.value, Deal.stage, ticker, and CIK.
2. **If ticker or CIK is set**, immediately call `fetch_public_deal_facts(deal_id)`. This is the freshness check required before the in-session draft.
3. Inspect the response's `staleness.is_stale`. When `true`, the stored row is older than a recent public 8-K announcement. Surface this as a banner ABOVE the executive summary; do not silently use the stored EV/stage as authoritative. Quote the announcement date and source URL.

### Step 2 — Build the financial spine from tiles, not from a black-box DD pipeline

Call each of these individually. Do NOT call `run_due_diligence`. The point of this command is that the model assembles the memo from explicit tile reads it can each skeptically frame:

- `export_deal_dossier(deal_id)` — financial snapshot, comparable companies, precedent transactions, deal metadata. Inspect `failed_sources`: if non-empty, name those gaps in the memo.
- `get_dcf_valuation(deal_id)` — DCF enterprise value, equity value, WACC, terminal growth. Note whether the run uses a Gordon Growth perpetuity or a transaction-multiple exit; both are valid but produce different EVs.
- `render_risk_matrix_tile(deal_id)` and `get_deal_indicators(deal_id)` — risk-taxonomy concentration (67 categories / 311 risk factors) + deal health score. Do NOT paste the raw 85+ risk count; use the ranked clusters that come back in the tile.
- `analyze_forensic_qoe(deal_id)` — Beneish M-Score, Benford's Law, EBITDA bridge, lapping detection. For each primitive, classify the output as `[finding]` (engine ran, result computed) or `[gap]` (status in `{insufficient_data, insufficient_sample, not_reliable, unavailable, not_computed}` — diligence ask, not clean bill of health).
- `find_similar_deals(deal_id)` — institutional memory check. If the response is `status: "no_usable_corpus"`, say so explicitly; do not fabricate a cohort.

### Step 3 — Web-fetch the current public record

For deals with a ticker:
- Fetch the most recent 10-K and Q-most-recent earnings release directly from SEC EDGAR or the company investor-relations page.
- Fetch the transaction announcement press release if `fetch_public_deal_facts.facts.inferred_stage == "announced"`.
- Cross-check the dossier's `revenue`, `ebitda`, `net_debt`, `cash` against the public filing. If they disagree by more than 2%, note as a reconciliation gap.

For private deals, skip this step. The freshness gate doesn't apply.

### Step 4 — Run the one authorized Monte Carlo strictly as a diligence prompt

- Under the bounded authority above, call `run_monte_carlo_simulation(deal_id, n_simulations=10000, seed=42)` exactly once. Require a non-empty `simulation_id` in that exact response before using any returned Monte Carlo value, and carry that identity into the Step 5 audit log. Inspect `assumption_provenance` per parameter. When `default_used` is true on 2+ of revenue_growth / ebitda_margin / wacc / terminal_growth, present the MC output as **sensitivity analysis ONLY** — do not cite mean / median / P5 / P95 / VaR / CVaR numerics in the main memo body. Caveat that the distribution reflects default priors and is not a defended forecast. Appendix-only. If the call fails or returns no `simulation_id`, record the exact `[gap]` statement from the authority section, **stop before Step 5 and report that governed memo drafting is unavailable because the run cannot be bound**. Do not retry or reuse any older simulation.
- DO NOT invoke `run_war_game_simulation` from this command. War-game is opt-in; the user has to ask for it explicitly. The robustness score is a composite (35% EV stability + 35% path consistency + 30% tail resilience), not a probability, and pasting "base case is robust at 74%" as IC evidence is the exact failure mode this command exists to prevent.

### Step 5 — Draft directly from the exact collected outputs

Author the memo in the current session from only the Step 1-4 responses and the public sources fetched in Step 3. Do not call `compose_ic_memo`, `generate_investment_memo`, or another persisted memo generator. Those rails cannot bind the exact Step 4 simulation, so using them would make simulation lineage ambiguous. Include the exact Step 4 `simulation_id` in the skeptic's audit log and use Monte Carlo values only from the same response that supplied it. This deliverable is an explicitly **non-persisted draft**, not a canonical IC package; canonical memo generation remains unavailable on this command until the backend exposes simulation binding or exclusion.

Before presenting the draft, verify the following:

1. The Executive Summary opens with the staleness banner (if `staleness.is_stale` was true in step 1).
2. The Recommendation section opens with exactly one of `Pass:` / `Needs More Data:` / `Conditional Go:` / `Go:` (verbatim, with colon). The post-process audit will rewrite an invented label like "CONDITIONAL GO" to canonical casing, but flag if you see one.
3. Every headline $-figure (revenue, EBITDA, debt, EV, transaction value) is followed by a `[source: X]` suffix. Scan the completed draft and count any un-cited figures yourself; this direct-draft path has no generated `metadata.citation_audit` object.
4. The Conditions Precedent list under the Recommendation cites the engine signals each condition came from. No boilerplate "obtain legal opinion" unless tied to a specific finding.
5. Monte Carlo numerics do not appear in the main body when the default-heavy rule in Step 4 requires appendix-only treatment, and every Monte Carlo value used comes from the response carrying the audit log's exact `simulation_id`.

If any of the five checks fail, correct the in-session draft or surface the violation to the user — do not paper over it.

### Step 5.5 — Mandatory atomic-claim verification before FINAL

A `[source: X]` suffix proves a citation was *attached*, not that the number is *correct*. The citation audit in Step 5 counts un-cited figures; it does NOT confirm the cited figures match the filing. Before presenting the memo as FINAL, verify every number against the deal's ingested documents:

1. Assemble the full memo body text and call `run_atomic_verifiers(deal_id, text=<memo body>)`.
2. Read `gate_passed` and `blocking_failures`:
   - `gate_passed: true` → every figure is supported by the retrieved corpus. Proceed to hand-off.
   - `gate_passed: false` → each entry in `blocking_failures` is a number the ingested filing does **not** support within tolerance (or the corpus is empty). You MUST NOT label the memo FINAL. Correct or remove every unsupported figure and regenerate, OR present the memo to the user as **DRAFT** with the `blocking_failures` list shown verbatim.
3. Never present a memo as IC-ready / FINAL while `gate_passed` is false.

`run_atomic_verifiers` checks each $-figure and percentage against the top-ranked retrieved chunks at 5% tolerance, so a number that isn't in the filing — *even with a citation attached* — fails. This is the authoring-time mirror of the deterministic gate that blocks `approve_package` server-side: a confident-but-wrong figure (e.g. a revenue number that contradicts the S-1) gets caught here, before the memo reaches committee.

### Step 6 — Hand off

Output the memo + a short skeptic's audit log:

- Freshness: `fetch_public_deal_facts` called at <timestamp>; staleness verdict.
- Reconciliation: any discrepancies the dossier vs public filings showed.
- Forensic: list of `[gap]` primitives that need data pulls before bid commitment.
- Monte Carlo lineage: exact `simulation_id` from the single authorized Step 4 response and whether its numerics were limited to the appendix.
- Citation audit: count of un-cited $-figures (target: 0).
- Verification: `run_atomic_verifiers` `gate_passed` verdict + count of `blocking_failures` (target: `gate_passed: true`, 0 failures). If any failures, list them — they are unsupported numbers, not minor nits.
- Derived gating conditions: count by source class (forensic / reconciler / assumption / judgment).

The user gets the non-persisted memo draft AND the audit — the audit is what differentiates this command from `/dd-analyze`.

## Why this command exists

The Project Atlas / GBTG IC memo (2026-05-11, deal4fdd2334a0bd) was generated via `/dd-analyze` → `dd-analyst` Opus sub-agent → `generate_investment_memo`. It shipped with:

- "Initial Outreach / $6.0B" stored deal facts a week after the public $6.3B announcement
- Monte Carlo Mean $1.08B pasted as evidence against deterministic DCF $4.34B (internally contradictory)
- War-game robustness 74% framed as IC evidence
- "CONDITIONAL GO" — an invented verdict label, no matching enum
- Boilerplate conditions precedent untied to engine signals

The root cause is structural: a single high-level template can't be retrofitted with skepticism after the fact. `/ic-memo-skeptical` enforces the orchestration that produces tighter artifacts — at the cost of more tokens per memo, more steps for the user to follow, and no "one command, one PDF" magic.

There is no fast or old memo path. Do not route a memo request to `/dd-analyze`: that command is extraction-only and does not produce an investment memo. Use this command's complete orchestration for memo generation; explain the distinction if the user asks for a faster or legacy path.

## URL Conventions (STRICT)

- Domain is `app.ololand.ai`. Not `.com`. Not any other TLD.
- Deal summary: `https://app.ololand.ai/deals/{deal_id}/summary`
- Risks view: `https://app.ololand.ai/deals/{deal_id}/risks`
- Valuations: `https://app.ololand.ai/deals/{deal_id}/valuations`
- IC package: `https://app.ololand.ai/deals/{deal_id}/ic-package`

When a tool response includes a `view_url`, render verbatim — never construct a URL the tool didn't return.
