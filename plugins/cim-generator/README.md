# cim-generator

> 14-section CIM generator with provenance. Built from your reconciled deal data, not LLM prose.

This plugin wraps OloLand's deterministic CIM (Confidential Information Memorandum) generator as a standalone Claude plugin. A CIM is the sell-side marketing document used in M&A to present a target company to potential buyers — this generates the full 14-section draft from the deal's platform data (financial snapshots, knowledge-graph risk/opportunity insights, prior diligence findings) and targeted market research, rather than synthesizing it from prose alone.

## Commands

| Command | Wraps | What it does |
|---|---|---|
| `/cim-generate` | `generate_cim` (async, poll via `check_task_status`) | Generates all 14 CIM sections (or a chosen subset) for a deal and reports the result location. |

## Install

```bash
claude plugin marketplace add ololand-ai/ololand-plugins
claude plugin install cim-generator@ololand-plugins
```

## What you need set up

`/cim-generate` calls OloLand's MCP server through this plugin's `ololand` connector. Interactive users authenticate through OAuth on first use; no agent key is required.

Required setup:
- An OloLand account and an authorized `ololand` MCP connector
- The deal already created (use `/new-deal` from the `ololand-dd` plugin, or create it in the web app), with at least a financial snapshot on file

## The 14 sections

Executive Summary, Investment Highlights, Company History & Overview, Products & Services, Market Analysis, Sales & Marketing, Customer Analysis, Management & Employees, Operations & Technology, Industry & Competitive Landscape, Growth Opportunities, Financial Performance, Financial Projections, Risk Factors.

## Viewing and exporting

Generation happens over the MCP connector, but the finished CIM is a persisted, editable document on the deal — not chat output. Open the deal in the web app (`https://app.ololand.ai/deals/{deal_id}`) to review sections, edit them inline, and export to PDF, DOCX, or PPTX on demand.

## Why this exists

Anthropic's finance-vertical plugins draft CIM/pitch content from prompts. OloLand's generator ties every financial exhibit and comp back to a reconciled snapshot or a cited research source, so a section can be defended at IC instead of re-verified from scratch. It's the sell-side counterpart to [`ololand-forensic-qoe`](../ololand-forensic-qoe) (buy-side forensic screening) and complements [`ololand-dd`](../ololand-dd) (full due-diligence workbench).

## License

Apache-2.0.
