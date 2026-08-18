---
description: Capture the structured decision rationale when a deal is closed, passed, exited, or withdrawn — the qualitative WHY behind the outcome, tagged with risks/opportunities and pattern tags so cross_deal_learning_service can surface it as a comparable deal later.
---

# Record Decision

`/record-outcome` closes the *quantitative* flywheel loop — predicted vs. realized EV/IRR/MOIC. This command closes the *qualitative* one: the reasoning an analyst gives when a deal reaches a decision point. "We passed because customer concentration was too high at 45%" is not capturable as a number, but it is exactly the kind of institutional memory that makes `/similar-deals` and `/playbook-recall` sharper over time — a future deal with the same concentration profile should surface this one, with the reason attached.

Every decision is recorded as its own row. Unlike outcome tracking (one row per deal, initialized once), a deal can accumulate several decisions over its life — a pass that gets reconsidered and later closes, a close that later gets unwound. Nothing is overwritten; the history stays queryable.

## Usage

```
/record-decision <deal_id>
```

## Arguments

- `<deal_id>` (required) — the deal this decision is about.

## Execution

The instructions below are for the model executing this command.

1. **Determine `decision_type`.** Must be one of: `closed`, `passed`, `exited`, `withdrawn`. Infer it from what the user said (e.g. "we're passing on this" → `passed`; "we closed the deal" → `closed`; "seller walked away during exclusivity" → `withdrawn`; "we sold our stake" → `exited`). If it's ambiguous, ask.

2. **Get `decision_rationale`.** This is the one truly required field beyond the type — it must be at least 10 characters and should capture the actual reasoning, not a restatement of the decision. "Passed" is not a rationale; "customer concentration was too high at 45%, and the two largest accounts had no long-term contracts" is. If the user's message already contains the reasoning, use it verbatim (lightly cleaned up); don't ask them to repeat themselves.

3. **Call `record_deal_decision`** with `deal_id`, `decision_type`, `decision_rationale`, plus whatever of the following the conversation actually supports — never invent values for fields the user didn't mention:
   - `key_risks_identified` — risk tags that drove the decision (e.g. `["customer_concentration", "key_person_dependency"]`).
   - `key_opportunities_identified` — opportunity tags, if the decision was opportunity-driven (e.g. a close driven by expansion potential).
   - `assumptions_validated` / `assumptions_invalidated` — which underwriting assumptions held up or didn't (e.g. `{"revenue_growth": "held, actually beat by 3pp"}` or `{"synergy_estimate": "was roughly 2x too optimistic"}`).
   - `lessons_learned` — freeform, for future deals of this shape.
   - `would_reconsider` / `reconsider_conditions` — if the user signals this decision isn't necessarily final (e.g. "we'd revisit if the price came down 20%").
   - `deal_patterns` — pattern tags for cross-deal learning, e.g. `["high_customer_concentration", "saas_rollup"]`. These are what `/similar-deals` matches on later, so tag generously when the conversation supports it.
   - `sector` — only if the deal's own profile doesn't already carry the right industry; the tool auto-populates from the deal's company profile when omitted.

4. **Report back plainly.** Confirm the decision was recorded (`decision_id`, `decision_type`), and if the tool's response includes a `view_url`, surface it. Don't over-narrate the tags you set — briefly restate the ones that will matter for future recall (patterns, key risks) so the user can correct them if you got one wrong.

## Complementary, not redundant, with `/record-outcome`

Use both when a deal closes out — they capture different things and neither substitutes for the other:

- `/record-outcome` — the numbers: realized EV, IRR, MOIC, scored against what was predicted at IC time.
- `/record-decision` — the reasoning: why the deal went the way it did, in language, tagged for pattern matching.

A deal with only outcome numbers and no decision rationale is graded but not explained; a deal with only a decision and no outcome numbers is explained but not graded. Both together are what let a future `/similar-deals` answer say *"we passed on three deals like this before, all for customer-concentration reasons — here's what we told ourselves each time."*

## What this unlocks

- `/similar-deals <deal_id>` — cross-deal pattern match now has qualitative reasoning to surface, not just outcome metrics.
- `/playbook-recall` — what the firm has said before about deals shaped like this one.
- IC prep on a new deal that resembles a past pass or close: the rationale is one query away instead of living only in someone's memory.

## Notes

- `record_deal_decision` is **free** (zero-credit) — recording institutional reasoning must never be gated by a credit balance.
- No existing-row check: call this as many times as the deal actually has decision points. Each call creates a new row; nothing is merged or overwritten.
- `decision_rationale` is validated server-side (non-empty, ≥10 characters) — a call with a placeholder rationale like "passed" will be rejected with a clear error; give the model's real reasoning instead of retrying with padding.

## Related commands

- `/record-outcome` — the quantitative half of the same close-out moment.
- `/similar-deals` — pattern match weighted by both outcome accuracy and recorded decisions.
- `/playbook-recall` — what worked / didn't / was missed in similar past deals.
