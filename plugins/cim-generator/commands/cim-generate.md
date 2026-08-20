---
description: Generate or read the latest 14-section Confidential Information Memorandum (CIM) for a deal, built from OloLand's reconciled deal data rather than LLM prose.
argument-hint: "<deal_id> [section, section, ...] | read <deal_id> [section, section, ...]"
---

# CIM Generate

Generate a Confidential Information Memorandum (CIM) — the sell-side marketing document used in M&A to present a target company to potential buyers. OloLand's generator pulls from the deal's reconciled financial snapshots, knowledge-graph risk/opportunity insights, and market research already on the platform, and only falls back to fresh web research for gaps that platform data doesn't cover — so exhibits are traceable to a source, not synthesized whole-cloth.

## Usage

```
/cim-generate <deal_id> [section, section, ...]
/cim-generate read <deal_id> [section, section, ...]
```

## Arguments

- `deal_id` (required) — The deal to generate or read a CIM for. Must already exist in OloLand with at least a financial snapshot; run due diligence first if it doesn't.
- `sections` (optional) — A subset of the 14 sections to generate or read, if the user only wants part of the CIM (see the list below). Default: all 14.

## Execution — generate (default)

1. If the user asked for specific sections, map each user-phrased name to its exact snake_case identifier from the 14-section list below before calling the tool (e.g. "Executive Summary" → `executive_summary`, "risk section" → `risk_factors`, "financials" → `financial_performance` and/or `financial_projections` — confirm with the user when ambiguous). Only these identifiers are valid `sections` values; the backend silently drops anything else.
2. Call `generate_cim(deal_id, sections=<optional list>)` from the MCP server. This is a long-running operation — it returns a `task_id`, not the CIM itself.
3. Tell the user generation has started and poll `check_task_status(task_id)` every ~5 seconds, up to a maximum of ~24 attempts (~2 minutes), until the status is `success` or `failure`. A full 14-section CIM typically takes 30-90 seconds (platform data aggregation, then targeted market research for gaps, then section synthesis).
4. If the task is still pending after the polling budget, stop polling — do not loop indefinitely. Tell the user generation continues server-side, give them the `task_id`, and invite them to ask again in a minute (you'll re-check with `check_task_status(task_id)`); the finished CIM also appears in the deal workspace regardless.
5. On success, the task result includes the `cim_id`, `sections_count`, and `word_count`.
6. On failure, surface the error from the task result — do not retry silently more than once.

## Execution — read (`/cim-generate read <deal_id>`)

Use this when the user wants to see, quote, or reason about a CIM that was already generated, instead of starting a new generation run.

1. Call `mcp__ololand__get_latest_cim(deal_id, sections=<optional list>)`. This reads the most recently completed CIM draft — it does not trigger generation, so if none exists yet, tell the user to run `/cim-generate <deal_id>` first rather than treating an empty result as an error.
2. **The returned CIM is a generated artifact, not primary source evidence.** Before relying on any claim in it for diligence or an external deliverable, validate it against the data-room retrieval tools (`search_deal_documents`, `get_financial_snapshot`, etc.) — never present CIM prose as if it were itself the cited source.
3. Present the requested sections' content, and note if any requested section wasn't found in the latest draft.

## The 14 sections

`executive_summary`, `investment_highlights`, `company_history`, `products_services`, `market_analysis`, `sales_marketing`, `customer_analysis`, `management_employees`, `operations_technology`, `industry_competition`, `growth_opportunities`, `financial_performance`, `financial_projections`, `risk_factors`.

## After generation

The CIM is not returned as chat text — it is a structured document persisted on the deal, with an audit trail back to the platform data and searches used to build it. Report to the user:

- **`cim_id`** and how many of the 14 sections were generated.
- **Where to view/edit/export it**: the deal workspace's Artifacts panel at `https://app.ololand.ai/deals/{deal_id}` — the CIM appears there as a `CIM` artifact with PDF, DOCX, and PPTX export on demand, and inline section editing.
- Suggest `/forensic-screen <deal_id>` (from the `ololand-forensic-qoe` plugin, if installed) as a pre-LOI complement if the user is preparing a sell-side process and wants the buy-side forensic view too.

## After read

- Present the requested sections' content directly in the response, and note any requested section that was not found in the latest draft.
- Remind the user that the CIM is a generated artifact rather than primary source evidence; cite or validate underlying claims against the data-room tools before relying on them for diligence or an external deliverable.

## Notes

- This command only starts/reports on generation, or reads back the latest completed draft. Editing individual sections and exporting to a file format happen in the deal workspace UI, not over this MCP connector.
- If `generate_cim` or `get_latest_cim` returns a company-scope error, the connector's OloLand account is not attached to a company with access to that deal — check the deal ID and the account used to authenticate the connector.
