---
description: Sponsor-side purchase price for an announced take-private — re-runs the published LBO at the announced offer, finds the highest price per share at which it still meets a target IRR, and lays DCF, comps, and precedents on one per-share football field. A ceiling from the published model, not a recommended price. Can also save a one-prompt announced-deal analysis as a draft for review.
argument-hint: "<deal_id> [target_irr] | draft \"<prompt>\""
---

# Take-Private Purchase Price

Use this when the user is the sponsor on an announced public deal and asks what to pay, or wants the whole announced-deal analysis set up from one prompt.

## Usage

```
/take-private <deal_id>
/take-private <deal_id> 0.22
/take-private draft "Analyze the announced acquisition of <target> by <acquirer> from the sponsor's side"
```

## Execution

1. Price: call `mcp__ololand__determine_purchase_price(deal_id, target_irr)`. `target_irr` is a decimal (0.20 is 20%); omit it to use the firm playbook, else 0.20. The deal needs a published Full Analysis.
2. `draft`: pass the user's message verbatim to `mcp__ololand__draft_announced_deal_workflow(prompt)`. It saves a draft only. Give the user the returned `review_path`; they confirm there, which costs 50 credits.

## Output

- Football field: each method's low and high per share, with the announced offer marked.
- The highest price per share that still meets the target IRR, the returned range (from the price at target IRR plus 5 points up to that ceiling), and the `run_id`.
- Every part returned as `refused`, with its `reason` code.
- A non-reliance note: illustrative analysis for qualified professionals, not a bid recommendation, an investment recommendation, or a fairness opinion.

## Guardrails

- Report a refused part; never estimate the figure it would have held.
- Money is actual USD, and keys ending `_per_share` are per share. Do not mix the two.
- This reads the published models. It does not publish, change the governed DCF or LBO, or approve anything.
- After `draft`, never say the analysis has started, a deal was created, or credits were charged.
- For a non-principal view of the same deal (premium, accretion/dilution, HHI) use `/dd-merger-analyze`.
