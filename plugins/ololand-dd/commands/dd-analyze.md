---
description: Run the deal's bounded due-diligence extraction pipeline — financial snapshot, five-dimension risk extraction, and target-only commercial findings. Valuation, forensic QoE, conflict detection, war-game, and memo generation are separate explicit actions.
---

# Due Diligence Analysis

Run the bounded extraction and risk-analysis pipeline on a deal using OloLand's institutional control system. This command does not run DCF/LBO/Monte Carlo, war-game, forensic QoE, cross-document conflict detection, or memo generation.

## Usage

```
/dd-analyze <deal_id>
```

## Arguments

- `deal_id` (required) — The deal ID to analyze. The backend tool does not accept a narrower scope parameter.

## Execution

1. Verify the deal exists using the `get_deal` MCP tool.
2. **Status-only questions never start a run.** This command uses the legacy Celery extraction rail, not canonical Full Analysis. Require the original `task_id` returned by `run_due_diligence` and call `check_task_status(task_id)` only to report its launch state under the rules below. If the caller does not have that task ID, report that this legacy dispatch's status is unavailable; do not substitute `get_analysis_run_status`, because it reads a different canonical `AnalysisRun` workflow.
3. Call `run_due_diligence(deal_id)` exactly once. The backend dispatches `master_data_extraction_task`, whose bounded contract is:
   - Simplified financial statement extraction into the deal snapshot
   - Risk extraction across the five dimensions: HR, Legal, Tech, Commercial, and Financial
   - Target-only commercial opportunities, insights, and synergies extraction
   - No DCF, LBO, Monte Carlo, war-game, forensic QoE, conflict detector, memo, or other valuation engine
4. Poll the returned parent `task_id` with `check_task_status`, but treat `SUCCESS` only as **launch confirmed**. The current parent task dispatches five child jobs asynchronously and returns before they all finish; its terminal state is not an analysis-complete signal.
5. After launch confirmation, read `get_financial_snapshot` and `get_deal_risks` separately:
   - Record the request time before invoking `run_due_diligence`. Treat the financial leg as fresh only when the returned snapshot's `created_at` is at or after that request time. Otherwise report it as pending or stale.
   - `get_deal_risks` exposes the latest available register but does not prove that this legacy dispatch refreshed it. Label those rows **latest available risks**, not “risks extracted by this run.”
   - This MCP rail exposes no durable completion/read receipt for the three commercial child jobs. Report their completion as unverified; do not attribute existing commercial findings to this run.
   - `get_deal_summary_tiles` may be read separately when useful, but do not claim this extraction run created or refreshed those tiles.
6. Never call the parent task “complete” or infer all-child completion from its success. If the freshness checks above do not pass, return `launch confirmed; results pending/unverified` and the exact missing proof.

## After Completion

Report:
- Parent dispatch status: `launch confirmed`, `launch failed`, or `unknown` — never `analysis complete`
- Count and severity mix of the latest risk rows returned within `get_deal_risks`' tool limit, explicitly not a total-register count and not attributed to this run without a durable receipt
- Top 5 latest available risks with evidence citations
- Financial snapshot (revenue, EBITDA, margins) only when its `created_at` proves post-request freshness; otherwise state pending/stale
- Commercial child completion: unverified on this legacy MCP rail
- Any source or coverage gaps returned by the extraction tools
- Explicitly note that conflict detection, forensic QoE, valuation, and memo generation were not run
- Suggested next steps: `/valuation <deal_id> read all` to inspect governed models and source-backed market evidence, or `/valuation <deal_id> run all` only when the user explicitly asks to create fresh model candidates; `/risk-report <deal_id>` for deep risk analysis

## Output URL Conventions (STRICT)

When linking to OloLand web app pages in your output, use ONLY these canonical patterns. The domain is **`app.ololand.ai`** — never `.com`. Path segments are exact (e.g. `dataroom` not `data-room`; `due-diligence` with hyphen).

- Risks view: `https://app.ololand.ai/deals/{deal_id}/risks`
- Data room: `https://app.ololand.ai/deals/{deal_id}/dataroom`
- Valuations: `https://app.ololand.ai/deals/{deal_id}/valuations`
- Deal summary: `https://app.ololand.ai/deals/{deal_id}/summary`
- Due diligence: `https://app.ololand.ai/deals/{deal_id}/due-diligence`

If a tool response gives you a `view_url`, render that verbatim. Never construct a URL the tool didn't return when the tool gave you one.
