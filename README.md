# OloLand DD — Due Diligence Plugin for Claude Code

The first punch + second punch for M&A due diligence.

OloLand structures the chaos of a data room into deterministic financial models, risk taxonomies, and cross-deal intelligence. Claude reasons over the result. Together they produce institutional-grade due diligence that neither can achieve alone.

## Install

```bash
claude plugin add github:ololand-ai/ololand-dd-plugin
```

## Quick Start

1. **Install the plugin** (see above).
2. **Connect your account** — open [ololand.ai/connect](https://ololand.ai/connect), sign in, and copy your agent key.
3. **Set the key** in your environment:
   ```bash
   export OLOLAND_AGENT_KEY=olo_agent_sk_...
   ```
4. **Run your first analysis**:
   ```
   /dd-analyze
   ```

## Commands

| Command | Description |
|---------|-------------|
| `/dd-analyze` | Run full due diligence on a deal — risk, valuation, forensic QoE, and investment memo. |
| `/risk-report` | Generate a structured risk report across OloLand's 246-category taxonomy. |
| `/valuation` | Run DCF, LBO, comparable transactions, and Monte Carlo valuation models. |
| `/similar-deals` | Find historically similar deals and surface cross-deal patterns. |
| `/deal-search` | Search across all documents in a deal's data room with hybrid vector + keyword search. |
| `/war-game` | Simulate competitive strategy scenarios using RL-powered market dynamics. |
| `/talk-to-deal` | Ask a natural-language question about any deal and get a sourced answer. |

## What's Different from Raw Claude

Using Claude alone on a data room is like reading every document yourself — thorough but slow, with no structure and no memory across deals. OloLand + Claude is a one-two punch:

### First Punch (OloLand)

Before Claude sees a single token, OloLand has already:

- **Classified risk** across a 246-category taxonomy with a fine-tuned Qwen 3 4B model
- **Indexed every document** into a hybrid vector + sparse search index with cross-document reconciliation
- **Built a knowledge graph** linking entities, claims, and financial figures across hundreds of files
- **Run forensic QoE** — Beneish M-Score, Benford's Law, and revenue/expense reconciliation to flag manipulation
- **Computed valuations** — DCF, LBO, Monte Carlo, comparable transactions, and real options with deterministic engines (not LLM math)
- **Matched against prior deals** — cross-deal learning surfaces patterns from every deal your firm has analyzed

### Second Punch (Claude)

Claude then reasons over a filtered, structured subset — not raw PDFs. It synthesizes findings, identifies what matters, and produces investment memos grounded in OloLand's deterministic outputs.

### The Flywheel

Every deal makes the system smarter. Analyst corrections refine risk models. Outcome tracking calibrates predictions. Cross-deal patterns compound. This is institutional memory that no single-session LLM can replicate.

### Benchmark

OloLand scores **87.7%** vs Claude's **81.5%** on the Gauntlet v4 institutional due diligence evaluation (3 tracks, 24 questions, dual-judge scoring by Gemini 3.1 Pro + Claude Opus 4.6).

## MCP Tools (33)

The plugin connects to OloLand's MCP server, which exposes 30 tools grouped by category:

| Category | Tools |
|----------|-------|
| **Deal Intelligence** | `list_deals`, `get_deal_summary`, `get_deal_timeline` |
| **Financial Valuation** | `run_dcf`, `run_lbo`, `run_monte_carlo`, `run_comparables`, `get_financial_data` |
| **Risk Analysis** | `get_risk_report`, `get_risk_categories`, `get_risk_quantification` |
| **Documents** | `search_deal_documents`, `get_document`, `list_documents` |
| **Knowledge Graph** | `query_knowledge_graph`, `get_entity_relationships`, `get_entity_details` |
| **Cross-Deal Learning** | `find_similar_deals`, `get_deal_patterns`, `get_outcome_predictions` |
| **Reports** | `generate_memo`, `generate_cim_summary`, `export_report` |
| **Market Intelligence** | `get_market_data`, `get_industry_benchmarks`, `get_comparable_companies` |
| **Strategy** | `run_war_game`, `get_strategy_scenarios` |
| **Corp Dev** | `analyze_build_vs_buy`, `generate_acquisition_thesis`, `batch_triage_companies` |
| **Voice** | `create_audio_brief` |
| **Workflow** | `get_approval_status`, `submit_for_review` |

## Links

- **Website**: [ololand.ai](https://ololand.ai)
- **App**: [app.ololand.ai](https://app.ololand.ai)
- **API Docs**: [ma-workbench-api-303576587005.us-central1.run.app/docs](https://ma-workbench-api-303576587005.us-central1.run.app/docs)
- **Support**: [aleks@ololand.ai](mailto:aleks@ololand.ai)
