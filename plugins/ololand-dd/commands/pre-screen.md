---
description: Run a pre-LOI screen on a public or private target. Branches on the resolver's classification. For public targets, constrains evidence to pre-cutoff filings (10-K + FMP). For private targets, uses PCS-traced signal evidence (SEC N-PORT marks, counter-party 10-Ks, USAspending, S-1 if filed) plus scoped web research. Outputs a 1-page brief with bear/base/bull SOTP framing.
---

# Pre-Announcement Screen — public or private target

Run an end-to-end **stage-1** screen of a target company. This command auto-detects whether the target is public or private and routes accordingly:

- **Public target** (resolver returns `classification == "public"`): constrain evidence to the latest 10-K + FMP financial snapshot. Web search is **off** so the artifact reflects only what was knowable from pre-cutoff filings.
- **Private target** (resolver returns `classification == "private"`): use the PrivateCompanySnapshot (PCS) seeded from the four primary-source signal adapters (SEC N-PORT marks, counter-party 10-K mentions, USAspending federal contract awards, and the S-1 watcher if the target has filed). Deep-research web search is **on** — there is no 10-K to anchor against, so press / news / Sacra-style commentary IS the public-trace evidence layer for a private target. Honor the `as-of` cutoff if supplied.

The audit log at the end is what separates this from "an LLM wrote a memo." Always surface it.

## Usage

```
/pre-screen <ticker or company name> [as-of YYYY-MM-DD]
```

## Arguments

- `<ticker or company name>` (required) — Free text. Examples: `GBTG`, `Amex GBT`, `Snowflake`, `SpaceX`, `Anthropic`.
- `as-of <YYYY-MM-DD>` (optional) — Cutoff date. The screen ignores any filing, news, or evidence dated after this. Defaults to today. Use for retrospective screens against a target whose deal or IPO has already been announced.

---

## Orchestration

### Step 1 — Resolve the company

1. Call `resolve_company` with the user's query. For clean tickers (`GBTG`, `MSFT`, `BRK.B`) pass `hint="public"`. For obviously-private targets (`SpaceX`, `Anthropic`, `Stripe`) pass `hint="private"`. When ambiguous, omit the hint and let the resolver pick.
2. If multiple candidates come back above 0.7 confidence, list the top 3-5 and ask which one. Don't guess.
3. Capture the picked name + ticker/CIK (if public) + classification.

If the resolver returns `classification == "unresolved"`, halt and tell the user: "I couldn't resolve the target. Try the full legal name (e.g. 'Space Exploration Technologies Corp.' instead of 'SpaceX'), or pass a ticker / website domain."

If `classification == "public"`, go to **Step 2-Public**. If `classification == "private"`, go to **Step 2-Private**.

---

## PUBLIC TARGET BRANCH

### Step 2-Public — Create the deal

Call `create_deal` with:

- `query` — the user's original text
- `ticker_override` — from Step 1
- `cik_override` — from Step 1
- `hint` — `"public"`
- `deal_mode` — `"screening"`

Watch ingestion with `check_task_status` until `state == "SUCCESS"`. Public-filer ingestion typically completes in 15-30s. Capture the resulting `deal_id`.

### Step 3-Public — Confirm the document set is pre-cutoff and pristine

Call `list_deal_documents(deal_id)`. Expected output: exactly the 10-K from EDGAR plus the FMP financial snapshot. Nothing else.

If you see ANY additional uploaded PDFs (proxy statements, merger communications, 8-K announcement decks, transaction press releases, news articles), halt and tell the user: this deal was pre-seeded with announcement-era materials and is not a clean pre-screen target. Recommend creating a fresh deal via `/new-deal` and retrying.

If `as-of` was provided, verify the 10-K's `filing_date` is before the cutoff. If the most recent available 10-K post-dates the cutoff, walk back to the prior fiscal year's 10-K and surface this as a known limitation.

### Step 4-Public — Read the financial spine from explicit tiles

**Web-off** run. The whole point of the public branch is the artifact reflects only what was knowable from pre-cutoff filings.

**Deny-list — do NOT call any of these on the public branch:**

- `run_due_diligence`, `deep_market_research`, `research_market`, `fetch_public_deal_facts`, `generate_investment_memo`, `WebFetch`, `WebSearch`, `tavily_*`, `mcp__claude-in-chrome__*`, or any MCP tool whose description says "search the web."

**Use instead:**

- `get_financial_snapshot(deal_id)` — base revenue, EBITDA, net debt, cash, CapEx, growth, margins. Source: FMP snapshot. Inspect the `as_of` date.
- `get_deal_risks(deal_id, limit=150)` — 10-K-extracted risks. Every `source_excerpt` must reference the 10-K filename. Any risk whose `file_name` is NOT the 10-K is a contamination signal — surface as `[gap]` and exclude.
- `search_deal_documents(deal_id, query)` — for specific quotes or numbers.

### Step 5-Public — Run Monte Carlo

Call `run_monte_carlo_simulation(deal_id, n_simulations=10000, seed=42)`. Report mean / median EV ($M), P5 / P25 / P75 / P95 EV ($M), VaR(5%) and CVaR(5%), mean / median equity value, `assumption_provenance` breakdown, `assumption_coverage` (target ≥0.6).

UNLIKE `/ic-memo-skeptical`, MC numerics belong in the BODY of the public brief, not the appendix. Pre-NDA, the MC distribution **is** the value-add — caveat defaulted assumptions inline; don't suppress the numbers.

### Step 6-Public — Pull deal indicators

`get_deal_indicators(deal_id)` + `render_risk_matrix_tile(deal_id)`. Report severity counts (high / medium / low), top 3-5 risk categories, 246-taxonomy concentration.

### Step 7-Public — Forensic Screen skip

Do NOT call `generate_forensic_screen_pdf`. In the brief: "The Pre-LOI Forensic Screen (Beneish, Benford, EBITDA bridge, journal-entry testing, lapping detection) is a stage-2 product. It requires management-supplied transaction-level data and runs once the NDA is signed. Pre-NDA, the closest signal is the Revenue Quality risk class flagged from the 10-K."

### Step 8-Public — Compose the public brief

Output the public template (see below in **Public brief template**).

### Step 9-Public — Audit log

See **Audit log** section. Hand off.

---

## PRIVATE TARGET BRANCH

### Step 2-Private — Create the deal (this seeds the PCS automatically)

Call `create_deal` with:

- `query` — the user's original text
- `hint` — `"private"`
- `deal_mode` — `"screening"`

`create_deal` for private targets dispatches `research_private_company_task` which runs in sequence: Apollo enrichment + GLEIF + Wayback first/investor snapshot + Sonnet synthesis + **PCS seed**. The PCS seed step runs four primary-source adapters with `watchlist=[target_name]` and persists `RawSignal` rows for everything found:

- `s1_watcher` (reliability 95) — SEC DRS / S-1 / S-1/A / F-1 / 424B / EFFECT filings. **A hit here promotes the target to S-1-citable analysis** — the brief should then cite by S-1 page number, not just N-PORT mark.
- `mutual_fund_marks` (88) — N-PORT-P / N-CSR Level-3 valuation disclosures.
- `counter_party_10k` (80) — public filer 10-K / 10-Q mentions of the target.
- `usaspending` (70) — federal contract awards.

Poll `check_task_status(task_id)` until `state == "SUCCESS"`. Typical end-to-end: 30-90s.

### Step 3-Private — Inspect the PCS + signal evidence

```
pcs = get_private_company_snapshot(deal_id)
signals = list_pcs_signals(deal_id, limit=50)
```

The `signals.summary_by_source` map gives the headline number for the brief: "We found X mutual fund disclosures, Y counter-party 10-K mentions, Z federal contracts, and W S-1 filings."

**If `signals.summary_by_source` totals zero across all sources, halt** and tell the user: "No public-trace evidence found for this target in the last 30 days across SEC N-PORT, counter-party 10-Ks, USAspending, or SEC IPO registrations. Pre-screen ends here. Either (a) the target is too obscure for these data sources, or (b) the target name didn't match the canonical form filers use — try the alternate legal name (e.g. 'Space Exploration Technologies Corp.' instead of 'SpaceX')."

**If `signals.summary_by_source.s1_watcher > 0`**, this is the SpaceX-class case: the target just filed S-1. The brief should explicitly call this out in the headline (see template) and the recommendation should reflect that pre-screen has more rigor than usual because the S-1 fills in segment financials.

### Step 4-Private — Deep research IS allowed (scoped)

Unlike the public branch, web research is the public-trace layer for private targets — they don't file 10-Ks. The discipline is in WHAT you search for, not whether you search.

**Allowed for the private branch:**

- `deep_research(query, as_of=...)` — scoped to press, sell-side commentary, Sacra-style analyst notes, and S-1 mirror sites if S-1 ingestion hasn't completed yet.
- `tavily_search` / `tavily_extract` / `tavily_research` — for citation density.
- `search_deal_documents(deal_id, query)` — once S-1 has been ingested (look for it in `list_deal_documents` output), search inside it directly.

**Honor the `as-of` cutoff strictly** — every web result must be dated before the cutoff. Discard anything newer.

**Still off-limits even on the private branch:**

- `mcp__claude-in-chrome__*` — too unbounded; the artifact must be replayable.
- `generate_forensic_screen_pdf` — still stage-2 even for private targets with S-1.

### Step 5-Private — Valuation: PCS-driven Monte Carlo

If `pcs.revenue_band.mid` is populated (S-1 hit, user-supplied, or a future heuristic fills this):

- Call `run_combined_dcf(deal_id, ...)` for the P5/P50/P95 enterprise value distribution. The MC kernel from PR #1644 samples from `Triangular(revenue_band.low, mid, high)` per iteration and applies the PCS-resident WACC inputs (applied_beta, illiquidity_discount, private_company_risk_premium). Report mean/median + P5/P95 EV and equity.
- Report `pcs.wacc_inputs` so the brief shows the explicit private-co adjustments (typically: `illiquidity_discount = 0.15`, `private_company_risk_premium = 0.04`, applied_beta from the PCS comp set).

If `pcs.revenue_band.mid` is NULL (the PR B contract — no heuristic yet):

- **Skip Monte Carlo** and note explicitly in the brief: "Revenue band requires either an ingested S-1 (`s1_watcher` will detect when one drops) or user-supplied input via `/dd-correct`. Pre-screen recommendation defaults to PURSUE-TO-NDA if signal coverage is strong, PASS if signal coverage is thin."

### Step 6-Private — Pull what risks exist

Call `get_deal_risks(deal_id, limit=50)`. Pre-NDA private targets typically have THIN risk extraction (no 10-K), so report counts but don't overstate. If `signals.summary_by_source.s1_watcher > 0` AND the S-1 has been ingested into `list_deal_documents`, expect 50-150 risks from the S-1 risk-factors section and treat as you would 10-K risks on the public branch.

### Step 7-Private — Forensic Screen still skipped

Same boundary as public: even when S-1 is filed, full Forensic QoE requires management transaction-level data (DRS / journals / detailed GL). The S-1's audited financials enable Beneish M-score and EBITDA bridge ONLY if the S-1 income statement extraction has completed — note as future-stage in the brief.

### Step 8-Private — Compose the private brief

Output the private template (see **Private brief template** below). Bear/base/bull SOTP by segment is the default; MC percentiles render in an appendix.

### Step 9-Private — Audit log

Identical structure to the public branch. The signal counts + reliability scores are what differentiate this from "an LLM web-searched and made up numbers."

---

## Public brief template

```
# Pre-Announcement Public Screen — {Company Name} ({Ticker})

**As-of:** {cutoff date or "today"}
**Sources:** 10-K dated {filing_date} (period: {period_of_report}) + FMP financial snapshot. No web search, no news, no transaction filings.
**Deal ID:** {deal_id}
**Run:** {ISO timestamp}

## Headline
{One sentence stating the MC finding in terms the user asked about.}

## Financial spine
| Metric | Value | Source |
|---|---|---|
| Revenue (LTM) | $X.XB | FMP / 10-K |
| EBITDA (LTM) | $XM | FMP / 10-K |
| EBITDA margin | X.X% | derived |
| Net debt | $X.XB | balance sheet |
| Revenue growth (5yr CAGR) | X.X% | historical |
| CapEx % revenue | X.X% | FMP |

## Monte Carlo valuation (10,000 simulations)
| Percentile | Enterprise Value | Equity Value |
|---|---|---|
| P5 | $XXX M | $XX M |
| P25 | $XXX M | $XX M |
| Median | $X.XB | $XX M |
| Mean | $X.XB | $XXX M |
| P75 | $X.XB | $XXX M |
| P95 | $X.XB | $XXX M |

VaR(5%): $XXX M | CVaR(5%): $XXX M | Assumption coverage: XX% (sourced) / XX% (defaulted)

## Risk concentration (X categorized risks from 10-K only)
| Severity | Count |
|---|---|
| High | X |
| Medium | XX |
| Low | XX |

Top 5 risk clusters with one-line summaries and 10-K page references.

## Recommendation
Exactly one of: Pass / Pursue to NDA / More public data needed.

Deal summary: https://app.ololand.ai/deals/{deal_id}/summary
```

---

## Private brief template

```
# Pre-Announcement Private Screen — {Company Name}

**As-of:** {cutoff date or "today"}
**Classification:** Private target
**S-1 status:** {one of:
  - "Public S-1 filed YYYY-MM-DD (accession ...). Brief cites by S-1 page where applicable."
  - "DRS (confidential draft) detected YYYY-MM-DD. Content not yet public; form-level metadata only."
  - "No SEC IPO registration on file."
}
**Signal evidence base:** {N S-1 events, M mutual fund marks, K counter-party 10-Ks, L federal contracts}
**Web research:** {N press / Sacra / sell-side sources cited inline below, all dated ≤ as-of}
**Deal ID:** {deal_id}
**Run:** {ISO timestamp}

## Headline
{One sentence. Examples:
  - With S-1 ingested: "S-1 reveals $X.XB FY revenue, growing Y%. SOTP base case $ZZB anchors against the {$1.75T} IPO ask at a {-30%} discount."
  - With PCS band but no S-1: "PCS-implied revenue band $X.X-X.XB anchored on N mutual-fund marks from {fund families}. Base-case EV $XXB, P95 $YYB."
  - Signal-only (band NULL): "Signal-traced evidence: {N S-1, M N-PORT marks, K counter-party 10-Ks, L federal contracts}. Revenue band not yet derivable without management input or S-1 ingestion."
}

## Signal-traced evidence base
| Source | Count | Reliability | Latest as-of |
|---|---|---|---|
| S-1 / DRS filings | X | 95 | YYYY-MM-DD |
| Mutual fund N-PORT marks | XX | 88 | YYYY-MM-DD |
| Counter-party 10-K mentions | XX | 80 | YYYY-MM-DD |
| Federal contract awards (USAspending) | XX | 70 | YYYY-MM-DD |

Every quantitative claim below uses inline `[N]` markers. `[S:N]` = ingested S-1 page reference, `[R:N]` = signal_observations row, `[W:N]` = web/press citation. Click-through opens the source.

## Revenue band (if derivable)
| Estimate | Value | Source |
|---|---|---|
| Low | $X.XB | {source — e.g. "USAspending floor"} |
| Mid | $X.XB | {source — e.g. "mutual fund implied, Baillie Gifford Q1 2026"} confidence X.XX |
| High | $X.XB | {source — e.g. "S-1 § Operations p.42"} |

## SOTP by segment (bear / base / bull)
This is the IC-room frame. MC percentiles render in the appendix.

| Segment | Bear ($B) | Base ($B) | Bull ($B) | Multiple anchor | Source |
|---|---|---|---|---|---|
| {Segment 1} | X | X | X | {e.g. "10-35× LTM revenue"} | {[S:N] or [R:N]} |
| ... | | | | | |
| **Equity value (SOTP)** | **$XXX** | **$XXX** | **$XXX** | — | — |

vs current valuation anchor: {last_round_post_money / mutual_fund_implied / IPO target}

## Optionality not in the base SOTP
- **Termination clauses** in named contracts (e.g. "Customer X has 90-day mutual termination on the $YYB contract — value as real option with walk-away floor of $ZZB").
- **Acquisition options** disclosed (strike, expiry, probability-weighted intrinsic value).
- **Milestone-vested comp dilution** if disclosed.

## Risks (from S-1 risk factors if ingested, else thin)
Severity counts + top clusters with `[S:N]` page citations where available.

## Where the private-target screen stops
- Audited financial statements pre-S-1: not available — wait for S-1 or NDA.
- Cap-table waterfall under exit scenarios: needs NDA + waterfall doc.
- Customer concentration top-N list: only aggregated >10% disclosures available pre-NDA.
- Forensic QoE full battery: stage-2 even with S-1 (needs transaction-level data).

## Recommendation
Exactly one of: Pass / Pursue to NDA / Watch (set up signal alerting).

If "Watch" — the OloLand signal pipeline will continue scanning; set the deal's `monitoring_enabled=true` and the agent will alert on the next material signal (especially an S-1 hit).

Deal summary: https://app.ololand.ai/deals/{deal_id}/summary

## Appendix — Monte Carlo (if revenue band populated)
Standard P5/P25/P50/P75/P95 EV + Equity table, identical to the public template. The bear/base/bull above is the legible IC frame; this is the distributional backup.
```

---

## Audit log (applies to both branches)

After presenting the brief, output:

- **Source set verified:** list of documents (public: 10-K + FMP; private: S-1 if any + PCS provenance + web sources cited)
- **Contamination check:** any document outside the expected set, with reasoning
- **MC assumption coverage:** sourced / defaulted breakdown (public) OR signal_count by source (private)
- **Forensic Screen:** correctly refused — confirmed stage-2 boundary
- **Cutoff respected:** as-of date + filing dates / web result dates verified
- **Reproducibility hook:** "Reproducible via `/inspect-run` on deal_id {deal_id}; submit corrections via `/dd-correct`."

That last line is the moat. Always surface it.

---

## URL Conventions (STRICT)

- Domain is `app.ololand.ai`. Not `.com`. Not any other TLD.
- Deal summary: `https://app.ololand.ai/deals/{deal_id}/summary`
- Risks view: `https://app.ololand.ai/deals/{deal_id}/risks`
- Valuations: `https://app.ololand.ai/deals/{deal_id}/valuations`
- Data room: `https://app.ololand.ai/deals/{deal_id}/dataroom`

When a tool response includes a `view_url`, render verbatim — never construct a URL the tool didn't return.
