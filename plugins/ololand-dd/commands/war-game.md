---
description: Run a competitive strategy simulation using RL/PPO — models 16 quarters of competitive dynamics with market share shifts, pricing pressure, and investment decisions.
---

# War Game Simulation

Run an RL-powered competitive strategy simulation for a deal.

## Usage

```
/war-game <deal_id> [scenarios]
```

## Arguments

- `deal_id` (optional) — The deal to simulate. If omitted, resolve it from the prose (see below).
- `scenarios` (optional) — Comma-separated: `base_case`, `expansion`, `macro_stress`, `regulated_stress`, or `all`. Default: `base_case`. When the user asks about **regulatory** response, include `regulated_stress`.

## Natural-language invocation (no deal_id)

Users rarely pass a bare deal_id — they describe a company and a counterfactual, e.g.
*"/war-game on Robinhood, assume it built Exchange Funds in-house instead of acquiring Frec/Cache. Competitive and regulatory response?"* Handle it like this; **never refuse or claim the simulator is unavailable** — it is OloLand's signature engine.

1. **Resolve the target to a deal.** Use `deal-search` / `list_deals` to find an existing deal for the named company. If none exists, create one with `new-deal` (or `create_deal`) so the simulation has a deal context to populate from.
2. **Route the full question to the deal agent.** Call `ask_deal_agent(deal_id, question)` with the user's verbatim counterfactual. The lead orchestrator now reaches `analyze_build_vs_buy` (synchronous build-vs-acquire), `run_war_game_simulation` (the RL sim), and `check_task_status` / `get_war_game_results` (polling/results) — it will answer the competitive/regulatory scenarios AND launch the formal simulation in one turn. For a bare `/war-game <deal_id> [scenarios]`, skip straight to Execution step 1 instead.
3. **Pick scenarios from intent.** "regulatory response" → `regulated_stress`; "across conditions" / unspecified depth → `all`; otherwise `base_case`.

## Execution

1. Call `run_war_game_simulation` from the MCP server with the deal_id and scenarios.
2. The simulation auto-populates from deal context:
   - **Focal company**: Revenue, market share, EBITDA margin from financial snapshot
   - **Competitors**: Extracted from commercial DD, classified by archetype (price leader, innovation leader, fast follower, niche defender, cash cow)
   - **Market**: TAM, growth rate, switching costs from market intelligence
3. A MaskablePPO agent runs 1000 episodes of 16-quarter simulations.
4. Poll progress with `check_task_status` when a task id is returned, then fetch results with `get_war_game_results` when the simulation id or batch id is available.

## Results

For each scenario, the simulation returns:
- **Optimal strategy path**: Quarter-by-quarter moves (HOLD, PRICING, PRODUCT, EXPANSION, M&A, COST_CUTTING)
- **EV distribution**: Mean, median, P5/P25/P75/P95, VaR, CVaR
- **Critical decision points**: Top 3 non-trivial strategic moves and when to make them
- **Competitor response patterns**: How competitors react (most active competitor, pricing pressure rate, dominant strategies)
- **Robustness score**: 0-100 combining EV stability, path consistency, and tail resilience

## Why This Matters

This is the only RL-based competitive strategy simulator in the M&A market. No competitor has this. It models actual competitive dynamics — market share shifts, moat erosion, R&D investment returns — not just static scenario tables.

## Example

```
/war-game deal123 all
```
Runs 4 scenarios (base, expansion, macro stress, regulated stress) and returns a comparison matrix showing how the optimal strategy changes under different market conditions.
