# ololand-forensic-qoe

> Forensic Quality-of-Earnings primitives as a standalone Claude plugin. The Pre-LOI Forensic Screen wedge.

This plugin wraps OloLand's deterministic forensic-QoE engines as a standalone SKU on Claude Cowork. It's the math layer of QoE — the same battery Big-4 runs in their $150-500K Quality-of-Earnings opinion, available as a Pre-LOI Forensic Screen for $99 with a 72-hour SLA. Full QoE is $999.

## Commands

| Command | Wraps | What it does |
|---|---|---|
| `/forensic-screen` | `analyze_forensic_qoe` (full battery) | Runs every primitive whose required inputs are present; returns an IC-defensible exclusion schedule. |
| `/beneish` | Beneish M-Score primitive | 8-variable earnings-manipulation probability, private-company adjusted. |
| `/benford` | Benford's Law primitive | First-digit testing on GL transactions; detects fabricated / selectively-entered postings. |
| `/ebitda-bridge` | EBITDA bridge + adjustment classifier | Walks reported EBITDA to normalized EBITDA, classifying every add-back as one-time / pro-forma / recurring / questionable. |
| `/journal-test` | Journal-entry tester | Period-end concentration, round-number frequency, weekend postings, reversing-entry anomalies. |
| `/lapping-check` | Lapping detector | Detects AR-lapping fraud cycles by tracing customer-to-cash application. |

## Install

```bash
claude plugin marketplace add ololand-ai/ololand-plugins
claude plugin install ololand-forensic-qoe@ololand-plugins
```

## What you need set up

Each command calls OloLand's MCP server through this plugin's `ololand` connector. Interactive users authenticate through OAuth on first use; no agent key is required. Headless/CI users can use an `OLOLAND_AGENT_KEY` only if they add their own Authorization header to the MCP server config.

Required setup:
- An OloLand account and an authorized `ololand` MCP connector
- The deal already created (use `/new-deal` from the `ololand-dd` plugin, or create it in the web app)
- Source documents uploaded to the deal's data room (CIM, audited financials, tax returns, GL export, AR aging, management bridges)

The forensic engine auto-detects which primitives have sufficient input and skips the rest. `/forensic-screen` reports which primitives ran and which were skipped due to missing inputs.

## Why this exists

Big-4 QoE engagements take 4-8 weeks and cost $150-500K. Most of that price is fieldwork, a signed CPA partner opinion, and E&O coverage — not the math. The deterministic statistical layer (Beneish, Benford, EBITDA bridge, journal-entry testing, lapping) is software-margin work. We sell it standalone, pre-LOI, with full methodology disclosure, and offer a $999 Full QoE workflow when the buyer wants a deeper package.

For the broader OloLand DD plugin (deterministic DCF/LBO, 246-category risk taxonomy, cross-deal memory), install [`ololand-dd`](../ololand-dd) from the same marketplace.

For the comparison vs. Big-4 QoE, see [ololand.ai/compare/vs-big-4-qoe](https://ololand.ai/compare/vs-big-4-qoe).

## License

Apache-2.0.
