---
description: Create a new deal from a company name or ticker — auto-fetches the latest canonical annual filing (10-K, 20-F, or 40-F, plus substantive exhibits) and 5 years of financials for public companies; seeds private companies with web research and auto-ingests a public S-1 if the target has filed to go public.
---

# New Deal

Create an OloLand deal in seconds. Type a public ticker (e.g. `SNOW`) and the system auto-pulls the latest canonical annual filing (10-K, 20-F, or 40-F, with substantive exhibits) from the relevant filing source plus 5 years of standardized financials from FMP. Type a private company name and it seeds the workspace from web research — and if that private target has filed a **public** S-1 / IPO-registration statement, the `s1_watcher` pipeline auto-fetches the S-1 into the data room so the analysis can cite it by S-1 page. A **confidential** DRS draft cannot be ingested — its body is sealed at the SEC until conversion to a public S-1, so the read stays press-based until then.

## Usage

```
/new-deal <company name or ticker>
```

## Arguments

- `<company name or ticker>` (required) — Free text. Examples: `Snowflake`, `SNOW`, `MSFT`, `Stripe`, `stripe.com`.

## Execution

The instruction below is for the model executing this command.

> **Developer can create deals.** Developer is a bounded single-deal trial — `create_deal` runs on Developer (one active deal, metered against the monthly credit budget). Never pre-refuse deal creation; if the one-deal limit is reached, surface the tool's upgrade CTA.

1. **Resolve the company first.** Call the `resolve_company` MCP tool with the user's query. If the user typed a clean ticker (`SNOW`, `MSFT`, `BRK.B`), pass `hint="public"`. Otherwise leave `hint` unset.

2. **Show the candidates.** If `resolve_company` returns multiple candidates above 0.7 confidence, list them concisely (top 3-5) with name, ticker (if any), exchange, and Public/Private classification. Ask which one the user means. If a single high-confidence match comes back, you can skip the confirmation.

3. **Create the deal.** Call `create_deal` with:
   - `query` — the user's original text (preserved for the audit trail).
   - `ticker_override` — set to the picked candidate's ticker (uppercased) if the user disambiguated. This bypasses the resolver so we don't risk a different result the second time.
   - `cik_override` — set to the picked candidate's CIK if available.
   - `hint` — `"public"` or `"private"` if the user was explicit.
   - `analysis_policy` — `"screen"` (default) or `"full"`. Prefer this canonical analysis-depth control. The legacy `deal_mode` (`"screening"` / `"formal_dd"`) is a compatibility alias; ask only if the user signals interest in formal DD.

4. **Report what was kicked off.** From the `create_deal` response, tell the user:
   - The `deal_id` and `classification` (public/private/unresolved).
   - For public: that the latest canonical annual filing (10-K, 20-F, or 40-F, plus substantive exhibits) is downloading and 5 years of FMP financials are being pulled. The `task_id` lets them poll progress.
   - The `resource_uri` (e.g. `ololand://deals/deal_abc123`) — they can subscribe to it via `resources/read` to watch the deal hydrate, instead of repeatedly calling `get_deal`.
   - A direct link to the deal in the web app: `https://app.ololand.ai/deals/{deal_id}/dataroom` (public) or `https://app.ololand.ai/deals/{deal_id}/summary` (private).
   - For a private target that has filed an S-1: the S-1 is auto-ingested during creation. Confirm via `list_deal_documents(deal_id)` — an S-1 in the data room shows up as a normal document; a detected-but-not-yet-ingested filing shows up as a `kind="pending_filing"` entry. If it's `pending_ingest`, call `ingest_s1(deal_id)` to fetch it; if it's `sealed`, the draft is confidential and nothing can be pulled yet. **Never tell the user OloLand can't ingest S-1s — it can, for public filings.**

5. **Watch ingestion (optional).** If the user wants live progress, call `check_task_status(task_id)` every ~5 seconds until status is `success` or `failure`. For a large public filer like MSFT or NVDA, expect 15-30 seconds end-to-end (10-K download + FMP financials + snapshot persist).

## Disambiguation pattern

OloLand's MCP server runs in stateless mode — there's no mid-tool elicitation. Disambiguation happens here in conversation. The flow is always:

1. `resolve_company(query)` → see candidates.
2. Pick one (with the user's confirmation when ambiguous).
3. `create_deal(query, ticker_override=<picked ticker>, cik_override=<picked cik>)` → bypasses re-resolution.

Don't call `create_deal` first when the query could match multiple companies — it will pick the top hit silently, which surprises users. Always resolve first when in doubt.

## After Completion

Suggested next steps to offer the user:
- `/dd-analyze <deal_id>` — run extraction, reconciliation, risk, and financial-snapshot processing once the annual filing (10-K, 20-F, or 40-F; or ingested S-1) finishes processing.
- `/valuation <deal_id> read all` — inspect governed DCF/LBO and source-backed Comps without starting a model run.
- `/valuation <deal_id> run all` — explicitly create fresh DCF/LBO/Monte Carlo candidates when the user asks to execute new models.
- `/risk-report <deal_id>` — risk taxonomy breakdown (67 categories / 311 risk factors).
- `/talk-to-deal <deal_id> "<question>"` — voice-optimized Q&A on the deal.
