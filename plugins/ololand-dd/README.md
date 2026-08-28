# OloLand — Institutional Underwriting for Claude

The underwriting layer inside Claude. Every hour of your diligence survives into the deal record.

Anthropic's native `private-equity` plugin ships DD checklists, memo drafts, and unit-economics prompts — the scaffold. OloLand ships the institutional layer on top: deterministic financial engines, a risk taxonomy of 311 risk factors across 67 diligence categories, forensic quality of earnings, cross-document reconciliation with source hierarchy, and a model fine-tuned on your firm's own deal history.

## Install

```bash
claude plugin add github:ololand-ai/ololand-dd-plugin
```

On first use, the plugin opens a browser tab for OAuth sign-in. Your agent key is provisioned automatically, a sample deal is seeded, and your first 100 tool calls are free. No copy-paste, no env vars.

## Quick Start

```
/dd-analyze
```

That's it. The plugin authenticates on first invocation, seeds a sample deal if your account is empty, and drops you into the analysis flow.

## Commands

| Command | What it does |
|---------|--------------|
| `/pre-screen` | Pre-NDA public/private screen — public targets receive one bounded Monte Carlo run; private targets receive a signal-only PCS brief with valuation withheld until a dedicated governed private-company tool exists |
| `/dd-analyze` | Run the bounded deal extraction, risk, and financial-snapshot pipeline; it does not itself authorize a fresh Monte Carlo run or perform cross-document reconciliation |
| `/ic-memo-skeptical` | Stage-2 IC memo with one bounded Monte Carlo run, skeptical tile-stitching, public-facts freshness gate, citation audit, and explicit gap-vs-finding framing |
| `/risk-report` | Risk matrix across 67 diligence categories (311 tracked risk factors) with evidence links, dollar quantification, and industry overlays |
| `/valuation` | Read governed DCF/LBO and source-backed Comps by default; create a DCF/LBO/Monte Carlo candidate only with explicit `/valuation <deal_id> run <method>` or `/valuation <deal_id> refresh <method>` syntax; bare and legacy method-only calls are read-only |
| `/qoe-analysis` | Deal-scoped QoE workbench: latest cached result or fresh revenue quality, EBITDA bridge, and working-capital analysis |
| `/compliance-analysis` | OFAC, HSR, and CFIUS analysis using the deal's context-aware compliance workbench |
| `/scenario-analysis` | Stress testing, market simulation, and real-options valuation from the scenario workbench |
| `/earnings-analysis` | Earnings-call transcript analysis for management tone, guidance deltas, and diligence signals |
| `/verification-marketplace` | Request or track human verification for a forensic screen and signed IC appendix provenance |
| `/ic-package` | Generate or approve the canonical IC package with assumption and verifier blockers preserved |
| `/value-impact` | Review or preview the deal/firm value-impact ledger |
| `/deal-health` | Summarize deal health, open actions, and meeting blockers |
| `/workbook` | List, read, create, or template-populate deal-scoped analysis workbooks; includes the persisted/downloadable LBO-oriented Excel-model bridge (DCF generation not ready) |
| `/company-discovery` | Search company discovery from natural-language or structured criteria |
| `/watchlist` | Create and inspect continuous monitoring watchlists |
| `/advisory` | Request or inspect buyer-side advisory engagements |
| `/financing` | Acquisition-financing prep — deterministic analysis, provider-sourcing prep, lender pre-read packages, rule-governed capital-programme eligibility signals |
| `/managed-context-agent` | Launch a configured managed context agent when enabled |
| `/managed-agent` | Run a cloud-hosted deal specialist (risk, forensic QoE, pre-LOI screen, financing prep, IC memo, or the parallel IC coordinator) asynchronously with full run provenance |
| `/okf-export` | Export a machine-readable OKF deal bundle |
| `/unit-economics` | Cohort analysis, CAC payback, NDR, LTV:CAC, magic number — for SaaS and services targets |
| `/similar-deals` | Cross-deal pattern match against your firm's closed deals with outcome accuracy |
| `/record-outcome` | Close the institutional-learning flywheel — mint predictions at IC, record realized exit EV / IRR / MOIC post-close, and score every prediction against actuals (the write side `/calibrate-vs-history` reads from) |
| `/record-decision` | Capture the qualitative WHY when a deal is closed, passed, exited, or withdrawn — rationale, validated/invalidated assumptions, and pattern tags that `/similar-deals` and `/playbook-recall` surface later |
| `/deal-search` | Hybrid vector + keyword + reranked search across the full data room |
| `/war-game` | RL-powered competitive strategy simulation (MaskablePPO, 1,000-episode rollouts, 16 quarters) |
| `/talk-to-deal` | Voice-optimized Q&A over the deal's full system of record, with rounded numbers and recommendations |
| `/source` | Find deals matching your firm's investment criteria across sourcing signals; create standing sourcing-thesis mandates that drive the Search Monitor |
| `/precedents` | Search ~61K public M&A transactions (2006-2026) for precedent deals and market context, with outcome labels and SEC filing citations |
| `/firm-calibration` | How accurate this firm's own predictions have been — accuracy by prediction type, systematic biases, risk-category precision, and the fields analysts keep overriding (firm-wide; `/calibrate-vs-history` is the per-deal counterpart) |
| `/deal-canvas` | Create or update charts, KPI rows, tables, and infographics on the deal canvas — every value engine-bound or cited, never invented |

## What's Different From Raw Claude

Using Claude alone on a 1,000-document data room is thorough but slow, non-deterministic, and without memory across deals. The benchmarks tell the story: LLMs fail 10–20% of complex financial calculations ([FAITH](https://arxiv.org/pdf/2508.05201v1)) and hallucinate 81% of long-context financial answers ([PHANTOM](https://openreview.net/pdf?id=5YQAo0S3Hm)). Scale errors — reporting "$150" when the answer is "$150M" — are structural, not fixable by prompting.

OloLand + Claude is the one-two punch.

### First Punch — OloLand (the governed record and workflows)

OloLand separates durable source records from explicitly invoked analysis workflows:

- **Ingested every document** into a hybrid vector + sparse index with Anthropic's Contextual Retrieval method (67% fewer failed retrievals)
- **Persists risk findings** with taxonomy, source, and run lineage when the relevant extraction workflow runs
- **Preserves financial provenance** and applies the source hierarchy when a reconciliation workflow has the required evidence; it does not claim that every number is automatically reconciled
- **Built a knowledge graph** linking entities, covenants, and claims across the corpus
- **Runs forensic QoE when invoked and adequately sourced** — Beneish M-Score, Benford's Law, EBITDA bridge, revenue quality, journal entry testing, and lapping detection; unavailable inputs remain explicit gaps
- **Runs and publishes valuation workflows when invoked on an eligible basis** — DCF, LBO, Monte Carlo, and real-options outputs retain their model and source identities
- **Surfaces firm-history comparisons when invoked** — accuracy bands, mitigation history, and covenant outcomes from available recorded deals

### Second Punch — Claude (the reasoning)

Claude reasons over the structured, provenance-bearing evidence and completed workflow outputs that are actually available. It synthesizes, writes the memo, builds the deck, and keeps missing or unverified work visible rather than treating it as completed.

### The Track Record

Every deal compounds. Analyst corrections feed the retraining pipeline on Vertex AI. Outcome tracking calibrates predictions against actuals. Cross-deal patterns surface when the next CIM arrives. The firm's memory is institutional infrastructure, not a per-machine folder.

## Benchmark

**Gauntlet v4 T5 (institutional due diligence):** OloLand 90.5%, Claude alone 88.5%. Dual-judge scoring (Gemini 3.1 Pro + Claude Opus 4.6). Gap widens on forensic, reconciliation, and visual-decision tasks.

## MCP Tools (100+)

| Category | Tools |
|----------|-------|
| **Deal Intelligence** | `list_deals`, `get_deal`, `get_deal_summary_tiles`, `get_deal_indicators` |
| **Financial Valuation** | `get_financial_snapshot`, `get_dcf_valuation`, `run_monte_carlo_simulation`, `analyze_unit_economics`, `run_scenario_stress_test`, `simulate_market_conditions`, `value_real_options` |
| **QoE + Forensics** | `analyze_forensic_qoe`, `generate_forensic_screen_pdf`, `run_qoe_analysis`, `get_latest_qoe_analysis`, `run_beneish`, `run_benford`, `build_ebitda_bridge` |
| **Risk Analysis** | `get_deal_risks`, `get_evidence_links`, `render_risk_matrix_tile`, `run_atomic_verifiers`, `check_citation_coverage`, `reconcile_documents`, `add_manual_risk`, `set_firm_risk_policy` |
| **Compliance** | `run_ofac_screen`, `run_hsr_analysis`, `run_cfius_risk` |
| **Human Verification** | `get_deal_verification_status`, `list_deal_verification_requests`, `request_verified_forensic_screen` |
| **Assumption Controls + IC Package** | `list_deal_assumptions`, `get_assumption_control_summary`, `get_assumption_evidence_pack`, `set_assumption_status`, `get_ic_package`, `generate_ic_package` (IC approval is app/human-session only; never call `approve_ic_package` via MCP) |
| **Value Impact** | `get_deal_value_impact`, `get_company_value_impact`, `get_value_impact_assumptions`, `preview_value_impact`, `update_value_impact_assumptions` |
| **Deal Health + Workbooks** | `get_deal_health_summary`, `list_deal_actions`, `create_deal_action`, `list_deal_workbooks`, `get_workbook`, `create_deal_workbook` |
| **Deal Canvas** | `create_deal_chart`, `create_deal_artifact`, `update_deal_artifact` |
| **Company Discovery + Watchlists** | `search_company_discovery`, `natural_language_company_search`, `list_watchlists`, `create_watchlist`, `list_watchlist_matches`, `promote_watchlist_match` |
| **Sourcing Theses** | `create_thesis`, `update_thesis`, `deactivate_thesis`, `list_theses`, `list_thesis_matches` |
| **Earnings Analysis** | `analyze_earnings_call` |
| **Documents** | `list_deal_documents`, `search_deal_documents`, `upload_deal_document`, `list_deal_files`, `read_deal_file`, `grep_deal_files`, `read_section`, `read_table`, `read_note` |
| **Extracted Knowledge** | `search_extracted_knowledge` plus compatibility aliases `query_knowledge_graph`, `get_entity_neighbors`, `search_knowledge_graph` |
| **Cross-Deal Learning** | `find_similar_deals`, `compare_deals_by_attribute`, `get_firm_calibration` |
| **Reports + Exports** | `generate_investment_memo`, `generate_cim`, `export_deal_dossier`, `export_deal_okf_bundle` |
| **Advisory + Managed Agents** | `list_deal_advisory_engagements`, `request_advisory_engagement`, `launch_managed_context_agent` |
| **Market Intelligence** | `research_market`, `deep_market_research`, `search_pe_buyers`, `search_targets`, `search_ma_deals`, `search_precedent_deals` |
| **Strategy** | `run_war_game_simulation`, `analyze_build_vs_buy`, `generate_acquisition_thesis` |
| **Sourcing** | `batch_triage_companies`, `save_sourcing_candidates`, `update_sourcing_candidate`, `log_sourced_lead` |
| **Financing** | `get_financing_workflow_status`, `run_financing_analysis`, `prepare_financing_sourcing`, `prepare_financing_lender_package`, `list_capital_programs`, `prepare_capital_plan`, `evaluate_capital_eligibility` |
| **Voice** | `talk_to_deal` |
| **CRE Underwriting** | `run_cre_stress_test`, `run_cre_debt_sizing`, `verify_sponsor_assumptions` |
| **Conversation Sessions** | `create_conversation_session`, `list_conversation_sessions`, `get_conversation_session_summary` |
| **Workflow** | `run_due_diligence`, `check_task_status`, `decompose_intent`, `get_plan_status`, `list_missions` |

## Pricing

| Tier | Price | For |
|------|-------|-----|
| **Developer** | Free | Sample-deal access and developer testing |
| **Pro** | $199/mo | Associate or VP running deals weekly |
| **Team** | $499/mo | 2 seats included, +$199/additional seat — SSO, audit logs, playbook enforcement |
| **Enterprise** | Custom | Multi-fund, VDR integration, data residency |
| **Forensic reports** (Pre-LOI Forensic Screen, Full QoE) | Included in Pro and above | Generated in-app or via `generate_forensic_screen_pdf`; no per-deal price since 2026-08-26 |

First 100 tool calls free on install. Upgrade at [ololand.ai/pricing](https://ololand.ai/pricing).

## Links

- **Product**: [ololand.ai](https://ololand.ai)
- **App**: [app.ololand.ai](https://app.ololand.ai)
- **Pricing**: [ololand.ai/pricing](https://ololand.ai/pricing)
- **Methodology**: [docs.ololand.ai/methodology](https://docs.ololand.ai/methodology)
- **Support**: [support@ololand.ai](mailto:support@ololand.ai)

## Disclaimer

OloLand assists with financial and investment workflows but does not provide financial or investing advice. Deterministic computation and reconciliation do not eliminate the need for professional judgment. All outputs — valuations, risk assessments, forensic findings, memos, and recommendations — should be reviewed by qualified financial professionals before being relied upon for investment decisions.

## Contributing

After cloning, install the git hooks once so commits are checked for manifest version drift:

```bash
./scripts/install-hooks.sh
```

The pre-commit hook runs `scripts/check-version-sync.sh`, which fails the commit if `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` disagree on the plugin version. When bumping the version, update both files in the same commit.

## License

Apache-2.0. See [LICENSE](./LICENSE).
