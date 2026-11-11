---
description: Run a strategy or strategy-economics framework (Porter's five forces, SWOT, value chain, blue ocean, 7S, market economics, marginal analysis, economic cycles) against a deal's existing diligence evidence.
argument-hint: "<deal_id> <framework>"
---

# Strategy Frameworks

Use this when the user wants a structured strategic read of a target from the evidence already in the deal.

## Usage

```
/strategy <deal_id> porters_five_forces
/strategy <deal_id> market_economics
```

## Execution

1. Call `mcp__ololand__run_strategy_framework(deal_id, framework)`. Frameworks: `porters_five_forces`, `swot`, `value_chain`, `blue_ocean`, `seven_s`, `market_economics`, `marginal_analysis`, `economic_cycles`.
2. Run one framework per call. For a combined view, run each separately and keep their citations separate.
3. For competitive dynamics over time use `/war-game`. For market sizing use `research_market`.

## Output

Render the framework's sections with the citations the response returns. Close with what the framework could not assess for lack of evidence.

## Guardrails

- Read-only. No model run is persisted and no valuation changes.
- The output is derived from retrieved deal evidence. When evidence is thin, say so, and label anything drawn from general knowledge as such.
- A framework is a structured read of the evidence, not an investment recommendation.
