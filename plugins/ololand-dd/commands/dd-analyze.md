---
description: Run the deal's due-diligence extraction pipeline — financial extraction, reconciliation, risk assessment, and summary tiles. Fresh valuation models are separate explicit actions.
---

# Due Diligence Analysis

Run the due-diligence extraction and risk-analysis pipeline on a deal using OloLand's institutional control system. This command does not directly run DCF/LBO/Monte Carlo engines or generate a memo.

## Usage

```
/dd-analyze <deal_id> [scope]
```

## Arguments

- `deal_id` (required) — The deal ID to analyze.
- `scope` (optional) — Analysis scope: `full` (default), `financial`, `commercial`, `legal`, `hr`, `tech`.

## Execution

1. Verify the deal exists using the `get_deal` MCP tool.
2. **Status-only questions never start a run.** If the user is asking whether an analysis finished or what it produced (rather than asking to run one), call `mcp__ololand__get_analysis_run_status(deal_id)` — compact status and provenance for the canonical Full Analysis run (which stages committed, artifact lineage, and the post-run managed review verdict when one exists; pass `analysis_run_id` for a specific run) — and stop there.
3. Run `run_due_diligence` with the specified scope. This triggers a multi-agent analysis:
   - Financial statement extraction and validation
   - Risk extraction across 67 categories / 311 risk factors (5 dimensions: HR, Legal, Tech, Commercial, Financial)
   - Cross-document reconciliation with source hierarchy
   - Forensic QoE analysis (Beneish M-Score, Benford's Law)
4. Monitor progress with `check_task_status`.
5. When complete, summarize findings using `get_deal_summary_tiles`.

## After Completion

Report:
- Total risks extracted (by severity: Critical/High/Medium/Low)
- Top 5 risks with evidence citations
- Financial snapshot (revenue, EBITDA, margins)
- Any data reconciliation discrepancies
- Suggested next steps: `/valuation <deal_id> read all` to inspect governed models and source-backed market evidence, or `/valuation <deal_id> run all` only when the user explicitly asks to create fresh model candidates; `/risk-report <deal_id>` for deep risk analysis

## Output URL Conventions (STRICT)

When linking to OloLand web app pages in your output, use ONLY these canonical patterns. The domain is **`app.ololand.ai`** — never `.com`. Path segments are exact (e.g. `dataroom` not `data-room`; `due-diligence` with hyphen).

- Risks view: `https://app.ololand.ai/deals/{deal_id}/risks`
- Data room: `https://app.ololand.ai/deals/{deal_id}/dataroom`
- Valuations: `https://app.ololand.ai/deals/{deal_id}/valuations`
- Deal summary: `https://app.ololand.ai/deals/{deal_id}/summary`
- Due diligence: `https://app.ololand.ai/deals/{deal_id}/due-diligence`

If a tool response gives you a `view_url`, render that verbatim. Never construct a URL the tool didn't return when the tool gave you one.
