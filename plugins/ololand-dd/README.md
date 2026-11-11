# OloLand — Institutional Underwriting for Claude

The underwriting layer inside Claude. Every hour of your diligence survives into the deal record.

Anthropic's native `private-equity` plugin ships DD checklists, memo drafts, and unit-economics prompts — the scaffold. OloLand ships the institutional layer on top: deterministic financial engines, a risk taxonomy of 311 risk factors across 67 diligence categories, forensic quality of earnings, and cross-document reconciliation with source hierarchy.

## Install

```bash
claude plugin marketplace add ololand-ai/ololand-plugins
claude plugin install ololand-dd@ololand-plugins
```

In the plugin's Connectors tab or your host's MCP settings, connect OloLand and complete OAuth sign-in on api.ololand.ai. Use your intended OloLand account and review the requested access. The plugin does not provision keys or seed deals automatically. Account permissions, available deal data, and current plan limits determine which workflows are available.

## Quick Start

```
/dd-analyze
```

After connecting, list the accessible deals and select the intended workspace and deal before starting analysis. If there is no suitable deal, use the normal OloLand app to prepare one; do not claim a sample was created or an analysis ran.

## Commands

| Command | What it does |
|---------|--------------|
| `/pre-screen` | Pre-NDA public/private screen — public targets receive one bounded Monte Carlo run; private targets receive a signal-only PCS brief with valuation withheld until a dedicated governed private-company tool exists |
| `/dd-analyze` | Run the bounded deal extraction, risk, and financial-snapshot pipeline; it does not itself authorize a fresh Monte Carlo run or perform cross-document reconciliation |
| `/ic-memo-skeptical` | Stage-2 IC memo with one bounded Monte Carlo run, skeptical tile-stitching, public-facts freshness gate, citation audit, and explicit gap-vs-finding framing |
| `/risk-report` | Risk matrix across 67 diligence categories (311 tracked risk factors) with evidence links, dollar quantification, and industry overlays |
| `/valuation` | Read governed DCF/LBO and source-backed Comps by default; create a DCF/LBO/Monte Carlo candidate only with explicit `/valuation <deal_id> run <method>` or `/valuation <deal_id> refresh <method>` syntax; bare and legacy method-only calls are read-only |
| `/qoe-analysis` | Deal-scoped QoE workbench: latest cached result or fresh revenue quality, EBITDA bridge, and working-capital analysis |
| `/compliance-analysis` | OFAC, HSR, and CFIUS analysis using the deal's context-aware compliance workbench (OFAC list is simulated; HSR thresholds at 2024 values) |
| `/scenario-analysis` | Stress testing, market simulation, and real-options valuation from the scenario workbench |
| `/earnings-analysis` | Earnings-call transcript analysis for management tone, guidance deltas, and diligence signals |
| `/verification-marketplace` | Request or track a human reviewer's check of a forensic screen; the sign-off is evidence attached to the IC package, not a signed opinion |
| `/ic-package` | Generate or approve the canonical IC package with assumption and verifier blockers preserved |
| `/value-impact` | Review or preview the deal/firm value-impact ledger |
| `/deal-health` | Summarize deal health, open actions, and meeting blockers |
| `/workbook` | List, read, create, or template-populate deal-scoped analysis workbooks; includes the persisted/downloadable LBO-oriented Excel-model bridge (DCF generation not ready) |
| `/company-discovery` | Search company discovery from natural-language or structured criteria |
| `/watchlist` | Create and inspect continuous monitoring watchlists |
| `/advisory` | Request or inspect buyer-side advisory engagements |
| `/deal-network` | Find Deal Network providers, draft a seller listing, and request an introduction on a match — intros are admin-released unless the counterparty has consented to direct contact |
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
| `/talk-to-deal` | The fast conversational answer: a quick read-only question over the deal's system of record, asking for rounded numbers and a bottom line |
| `/source` | Map and persist a private-company research universe (`map`), prepare a read-only watchlist brief (`brief`), inspect source access (`connections`), or run sourcing and standing-thesis workflows |
| `/precedents` | Search ~61K public M&A transactions (2006-2026) for precedent deals, private-target comps (`sector_scope=either`), or quote-verified deal-break gotchas (`--gotchas`), with SEC filing citations |
| `/buyer-list` | Rank repeat SEC-reporting strategic acquirers and roll-up platforms by sector, EV band, and disclosed multiples from ~61K public M&A filings |
| `/firm-calibration` | How accurate this firm's own predictions have been — accuracy by prediction type, systematic biases, risk-category precision, and the fields analysts keep overriding (firm-wide; `/calibrate-vs-history` is the per-deal counterpart) |
| `/deal-canvas` | Create or update charts, KPI rows, tables, and infographics on the deal canvas — every value engine-bound or cited, never invented |
| `/new-deal` | Create a deal from a company name or ticker; public companies get the latest annual filing fetched |
| `/plan` | Get a structured plan from the planner before any work runs |
| `/cockpit` | Deal or firm-wide Cockpit: readiness gates, pending approvals, drivers outside tolerance, dispatch ledger, and the financial briefing |
| `/deal-team` | What the virtual deal team filed in the last 24 hours, its proposals awaiting a human decision, or one asynchronous question to one seat (asynchronous desks are still in verification) |
| `/diligence-requests` | List diligence requests, prepare a sourced draft response from frozen evidence, and submit it for human review |
| `/strategy` | Porter's five forces, SWOT, value chain, and five more frameworks run against the deal's own evidence |
| `/take-private` | Sponsor-side price ceiling for an announced take-private: the highest price per share at which the published LBO still meets a target IRR, on a per-share football field; not a recommended price |
| `/dd-merger-analyze` | Third-party analysis of an announced or rumored merger: premium, accretion/dilution, antitrust HHI, combined DCF |
| `/dd-merger-readiness` | Per-side data readiness for a merger-analysis deal |
| `/dd-merger-rerun-math` | Re-run the merger engines with input overrides for sensitivity |
| `/assumption-controls` | Review the assumption ledger that gates IC approval |
| `/ic-approve-readiness` | Pre-flight check of what blocks IC approval; approval itself stays in the app |
| `/verify` | Check every number and citation in an artifact, including an externally drafted memo, against source documents and engine runs |
| `/risk-matrix` | Render the risk matrix as an inline tile |
| `/cap-table` | Inspect capitalization evidence and model a supported financing or equity-proceeds scenario |
| `/meeting-prep` | One-page, source-cited question list for a diligence meeting |
| `/firm-playbook` | Read the firm's standing investment criteria, or record a standing rule |
| `/playbook-recall` | What worked and what was missed in similar past deals from your firm |
| `/calibrate-vs-history` | Apply your firm's historical projection bias to this deal's headline numbers |
| `/remember`, `/recall` | Persist and read analyst-confirmed deal facts across sessions |
| `/dd-correct` | Submit a correction on a claim in an agent output |
| `/inspect-run` | Inspect an agent run: header, span tree, grader verdict |
| `/replay-run` | Re-run a recorded agent run for reproducibility (admin or compliance role) |
| `/regulator-export` | Queue a regulator export pack mapped to a compliance framework (admin or compliance role) |
| `/ai-finserv-moves` | Browse recent AI financial-services moves from the competitive scanner |

## What's Different From Raw Claude

Using Claude alone on a 1,000-document data room is thorough but slow, non-deterministic, and without memory across deals. The benchmarks tell the story: LLMs fail 10–20% of complex financial calculations ([FAITH](https://arxiv.org/pdf/2508.05201v1)) and hallucinate 81% of long-context financial answers ([PHANTOM](https://openreview.net/pdf?id=5YQAo0S3Hm)). Scale errors — reporting "$150" when the answer is "$150M" — are structural, not fixable by prompting.

OloLand + Claude is the one-two punch.

### First Punch — OloLand (the governed record and workflows)

OloLand separates durable source records from explicitly invoked analysis workflows:

- **Ingested every document** into a hybrid vector + sparse index with Anthropic's Contextual Retrieval method
- **Persists risk findings** with taxonomy, source, and run lineage when the relevant extraction workflow runs
- **Preserves financial provenance** and applies the source hierarchy when a reconciliation workflow has the required evidence; it does not claim that every number is automatically reconciled
- **Extracts entities, covenants, and claims** into a searchable store (`search_extracted_knowledge`)
- **Runs forensic QoE when invoked and adequately sourced** — Beneish M-Score, Benford's Law, EBITDA bridge, revenue quality, journal entry testing, and lapping detection; unavailable inputs remain explicit gaps
- **Runs and publishes valuation workflows when invoked on an eligible basis** — DCF, LBO, Monte Carlo, and real-options outputs retain their model and source identities
- **Surfaces firm-history comparisons when invoked** — accuracy bands, mitigation history, and covenant outcomes from available recorded deals

### Second Punch — Claude (the reasoning)

Claude reasons over the structured, provenance-bearing evidence and completed workflow outputs that are actually available. It synthesizes, writes the memo, builds the deck, and keeps missing or unverified work visible rather than treating it as completed.

### The Track Record

Every deal compounds. Your firm's reviewed corrections and recorded outcomes are fed into that firm's later risk analysis. Outcome tracking scores predictions against actuals. Cross-deal patterns surface when the next CIM arrives. The firm's memory is institutional infrastructure, not a per-machine folder.

## Published evaluations

Two evaluations are published with their methodology and limitations: [restatement recall](https://ololand.ai/benchmarks/restatement-recall) and [Vals finance agent](https://ololand.ai/benchmarks/vals-finance-agent).

## MCP Tools (100+)

| Category | Tools |
|----------|-------|
| **Deal Intelligence** | `list_deals`, `get_deal`, `get_deal_summary_tiles`, `get_deal_indicators` |
| **Financial Valuation** | `get_financial_snapshot`, `get_dcf_valuation`, `run_monte_carlo_simulation`, `analyze_unit_economics`, `run_scenario_stress_test`, `simulate_market_conditions`, `value_real_options` |
| **QoE + Forensics** | `analyze_forensic_qoe`, `generate_forensic_screen_pdf`, `run_qoe_analysis`, `get_latest_qoe_analysis`, `run_beneish`, `run_benford`, `build_ebitda_bridge` |
| **Risk Analysis** | `get_deal_risks`, `get_evidence_links`, `render_risk_matrix_tile`, `run_atomic_verifiers`, `check_citation_coverage`, `reconcile_documents`, `add_manual_risk`, `propose_risk_resolution`, `set_firm_risk_policy` |
| **Compliance** | `run_ofac_screen`, `run_hsr_analysis`, `run_cfius_risk` |
| **Human Verification** | `get_deal_verification_status`, `list_deal_verification_requests`, `request_verified_forensic_screen` |
| **Assumption Controls + IC Package** | `list_deal_assumptions`, `get_assumption_control_summary`, `get_assumption_evidence_pack`, `set_assumption_status`, `get_ic_package`, `generate_ic_package` (IC approval is app/human-session only; never call `approve_ic_package` via MCP) |
| **Value Impact** | `get_deal_value_impact`, `get_company_value_impact`, `get_value_impact_assumptions`, `preview_value_impact`, `update_value_impact_assumptions` |
| **Deal Health + Workbooks** | `get_deal_health_summary`, `list_deal_actions`, `create_deal_action`, `list_deal_workbooks`, `get_workbook`, `create_deal_workbook` |
| **Deal Canvas** | `create_deal_chart`, `create_deal_artifact`, `update_deal_artifact` |
| **Company Discovery + Watchlists** | `search_company_discovery`, `natural_language_company_search`, `search_company_universe`, `list_watchlists`, `create_watchlist`, `list_watchlist_matches`, `promote_watchlist_match` |
| **Sourcing Theses** | `create_thesis`, `update_thesis`, `deactivate_thesis`, `list_theses`, `list_thesis_matches` |
| **Earnings Analysis** | `analyze_earnings_call` |
| **Documents** | `list_deal_documents`, `search_deal_documents`, `upload_deal_document`, `list_deal_files`, `read_deal_file`, `grep_deal_files`, `read_section`, `read_table`, `read_note` |
| **Extracted Knowledge** | `search_extracted_knowledge` plus compatibility aliases `query_knowledge_graph`, `get_entity_neighbors`, `search_knowledge_graph` |
| **Cross-Deal Learning** | `find_similar_deals`, `compare_deals_by_attribute`, `get_firm_calibration`, `recall_firm_playbook`, `set_firm_playbook_criteria` |
| **Reports + Exports** | `generate_investment_memo`, `generate_cim`, `export_deal_dossier`, `export_deal_okf_bundle` |
| **Advisory + Managed Agents** | `list_deal_advisory_engagements`, `request_advisory_engagement`, `launch_managed_context_agent` |
| **Deal Network** | `list_network_participants`, `create_network_listing`, `request_network_intro` |
| **Market Intelligence** | `research_market`, `deep_market_research`, `search_pe_buyers`, `search_targets`, `search_ma_deals`, `search_precedent_deals`, `search_strategic_acquirers` |
| **Strategy** | `run_war_game_simulation`, `run_strategy_framework`, `analyze_build_vs_buy`, `generate_acquisition_thesis` |
| **Cockpit + Briefing** | `get_deal_cockpit`, `get_portfolio_cockpit`, `get_financial_briefing` |
| **Deal Team** | `get_team_briefing`, `list_team_proposals`, `get_team_work_item`, `ask_team_seat` |
| **Diligence Requests** | `list_diligence_requests`, `create_diligence_request`, `update_diligence_request`, `submit_diligence_request`, `begin_diligence_preparation`, `read_diligence_evidence`, `complete_diligence_preparation` |
| **Announced Deals** | `analyze_announced_merger`, `get_merger_readiness`, `determine_purchase_price`, `draft_announced_deal_workflow` |
| **Sourcing** | `batch_triage_companies`, `save_sourcing_candidates`, `update_sourcing_candidate`, `log_sourced_lead` |
| **Financing** | `get_financing_workflow_status`, `run_financing_analysis`, `prepare_financing_sourcing`, `prepare_financing_lender_package`, `list_capital_programs`, `prepare_capital_plan`, `evaluate_capital_eligibility` |
| **Quick answer** | `talk_to_deal` |
| **CRE Underwriting** | `run_cre_stress_test`, `run_cre_debt_sizing`, `verify_sponsor_assumptions` |
| **Conversation Sessions** | `create_conversation_session`, `list_conversation_sessions`, `get_conversation_session_summary` |
| **Workflow** | `run_due_diligence`, `check_task_status`, `decompose_intent`, `get_plan_status`, `list_missions` |

## Pricing

| Plan | Price | Notes |
|------|-------|-------|
| **Pro** | $199/mo | 7-day free trial, no card |
| **Team** | $499/mo | 2 seats included, +$199 per additional seat |
| **Enterprise** | Custom | |

Forensic reports (Pre-LOI Forensic Screen, Full QoE) are included in Pro and above; there is no per-deal price. When a trial ends without a plan the account becomes read-only: existing deals can be read, but there are no credits and no new deals. Plans are managed in the app under [Settings → Billing](https://app.ololand.ai/settings/billing).

## Links

- **Product**: [ololand.ai](https://ololand.ai)
- **App**: [app.ololand.ai](https://app.ololand.ai)
- **Methodology**: [docs.ololand.ai/methodology](https://docs.ololand.ai/methodology)
- **Support**: [support@ololand.ai](mailto:support@ololand.ai)

## Disclaimer

OloLand assists with financial and investment workflows but does not provide financial or investing advice. Deterministic computation and reconciliation do not eliminate the need for professional judgment. All outputs — valuations, risk assessments, forensic findings, memos, and recommendations — should be reviewed by qualified financial professionals before being relied upon for investment decisions.

## Contributing

See the [repository README](../../README.md#contributing).

## License

Apache-2.0. See [LICENSE](./LICENSE).
