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
*"/war-game on Robinhood, assume it built Exchange Funds in-house instead of acquiring Frec/Cache. Competitive and regulatory response?"* Treat the counterfactual as a caller-supplied hypothetical. If the simulator or required deal evidence is unavailable, relay that result; do not present an empty or inferred result as a simulation.

1. **Resolve the target to an existing deal.** Use `deal-search` / `list_deals` to find an existing deal for the named company. If none exists, say that a deal context is required; do not create one automatically.
2. **Separate review from execution.** For an audit, review, or read-only request, follow `/plan`: create or reuse the deal conversation session, submit the user's verbatim counterfactual with `submit_plan_for_approval`, render the plan, and stop for approval. After approval, direct the user to continue the same session in the OloLand app or normal SSE/message endpoint with the exact plan attached as `approved_plan` on `SubmitMessageRequest`. Do not call the MCP `ask_deal_agent` or `talk_to_deal` tools for this planned execution: they cannot carry the server-bound field, and quoted plan prose is not approval. If the client cannot use the normal endpoint, report the governed review as unavailable on this rail; do not run a simulation or infer an answer. For a request that explicitly asks to run the simulation, continue to Execution step 1; that is a bounded, fixed-purpose tool call rather than a conversational executor turn.
3. **Pick scenarios from intent.** "regulatory response" → `regulated_stress`; "across conditions" / unspecified depth → `all`; otherwise `base_case`.
4. Separate factual buyer premises from simulator predictions. Do not claim a buyer/acquirer identity, observed strategy, historical action, expected synergy, or any other real-world premise unless a tenant-authorized returned source supports it with an inline citation. Keep caller-provided buyer premises labeled hypothetical. A completed simulator's modeled strategy, likely action, competitor response, EV distribution, or robustness score may be relayed without a document citation only when it is clearly labeled **simulator prediction** and tied to the exact returned simulation identity and scenario; never restate that prediction as a sourced fact.

## Execution

1. Confirm that the user explicitly requested execution, then call `run_war_game_simulation` from the MCP server with the deal_id and scenarios.
2. The simulation auto-populates from deal context:
   - **Focal company**: Revenue, market share, EBITDA margin from financial snapshot
   - **Competitors**: Extracted from commercial DD, classified by archetype (price leader, innovation leader, fast follower, niche defender, cash cow)
   - **Market**: TAM, growth rate, switching costs from market intelligence
3. A MaskablePPO agent runs 1000 episodes of 16-quarter simulations.
4. Poll progress with `check_task_status` when a task id is returned, then fetch results with `get_war_game_results` when the simulation id or batch id is available.
5. Relay an unavailable or error status as such. Do not infer scenario output, buyer behavior, or completion from a queued task or missing result. Present predictions only from a completed result that returns its `simulation_id` and `scenario_label`; a task id, batch id, or prose description alone is not prediction provenance.

## Results

For each completed scenario, report the returned values under a heading such as `Simulator prediction — simulation <simulation_id>, scenario <scenario_label>`. These prediction fields do not need document citations because the simulation identity is their provenance; any factual input or buyer premise repeated alongside them still does. The simulation returns:
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
