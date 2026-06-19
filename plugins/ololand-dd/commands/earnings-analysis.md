---
description: Analyze an earnings-call transcript for management tone, topic risk, guidance deltas, and deal-relevant diligence signals.
---

# Earnings Analysis

Run the deal-scoped earnings-call workbench. Use this for public-company targets, public comps, or any target with management-call transcripts that should feed diligence.

## Usage

```
/earnings-analysis <deal_id> <transcript_or_segments>
```

## Arguments

- `deal_id` (required) - The deal to analyze.
- `segments` (required) - Transcript segments. Accept a pasted transcript, a local file path, or structured segment objects.
- `company_name` (optional) - Company name to display in the analysis.
- `call_date` (optional) - Call date.

## Execution

1. If the user provides a file path, read the transcript and split it into speaker-aware segments when possible.
2. Call `analyze_earnings_call(deal_id, segments, company_name, call_date)`.
3. Use the returned `view_url` for web app handoff.

## Output

Render:

- **Management tone** - sentiment, vocal/tone stress where available, and notable topic shifts.
- **Guidance deltas** - changed revenue, EBITDA, margin, cash-flow, or capex expectations.
- **Risk signals** - evasive answers, customer concentration, pricing pressure, churn, regulatory, liquidity, covenant, or working-capital flags.
- **Follow-up asks** - documents or management questions that should enter the diligence request list.

## Guardrails

- Do not overstate vocal stress as deception. Treat it as a diligence signal that needs corroborating evidence.
- Preserve citations or transcript timestamps for any quote or numerical claim.

## Output URL Conventions

Use the tool-returned `view_url`. Canonical surface:

- Earnings analysis: `https://app.ololand.ai/deals/{deal_id}/analysis/earnings`
