---
description: Inspect capitalization evidence, model a supported financing or equity-proceeds scenario, and read exact published ownership results.
argument-hint: "<deal_id> [status|current|simulate]"
---

# Cap table

Use this workflow for holder ownership, dilution, supported SAFE/note conversion,
and company-security proceeds. It is separate from an LP/GP fund waterfall.

1. Resolve the deal explicitly, then call `get_cap_table(deal_id)` to inspect
   issuers, exact baseline revision IDs, source references, and review state.
   A supplied ledger and a reviewed baseline are distinct from a published result.
2. For decision-facing ownership call `get_current_cap_table(deal_id,
   capability="capitalization.ownership")`. For a published financing or proceeds
   workpaper select `capitalization.pro_forma` or `capitalization.proceeds`.
   Report publication ID, receipt hash, revision and run IDs with the figures.
   A missing/currently ineligible publication is a gap; do not substitute a newer
   candidate or invent its missing values.
3. For an explicitly requested sensitivity, call `simulate_cap_table` with the
   exact issuer/revision, a named scenario and a stable idempotency key. Reuse the
   key only to retry the identical request. Pass exact decimal strings.
   Financing uses `pre_money_value`, `subscriptions` (holder ID/name/amount),
   optional fractional `target_unallocated_pool`, and explicit confirmations
   `standard_terms_confirmed` and `pricing_basis_confirmed`.
   The supported price denominator includes outstanding common equivalents,
   awards, existing reserve, conversion shares and the round's pool increase.
   Ask for that convention and supported new-share rights; never infer confirmation.
   Post-money SAFE baselines also require explicit capitalization-definition confirmation;
   their cap denominator excludes the new round pool increase.
4. Proceeds require supplied **equity consideration**, seller expenses, escrow,
   and `election_basis="hypothetical_optimization"`. Documented transaction elections
   are unsupported until dated election evidence can be bound by an adapter.
   Nonzero pro-rata escrow additionally requires `escrow_pro_rata_confirmed`.
   Do not substitute enterprise value or add exercise/financing cash twice.
5. Show current and pro-forma ownership separately. Disclose treasury exclusions,
   pending convertibles, denominator, unsupported rights, assumptions, calculation
   gaps and source locations. Candidate calculations remain supplied-input
   scenarios even when arithmetic checks pass. No payment or securities issue occurs.
6. Baseline creation/import, source correction, human review and inclusion in
   Full Analysis occur in the app's **Cap table** view. Never approve a baseline
   or IC package through MCP. Publication is independently gated by exact source
   and revision identity; a scenario does not become current on creation. Financing
   and proceeds also require a resolved, evidenced Assumption Controls record
   pinned to the exact transaction basis hash. The app can prepare an unverified
   control; human resolution and a new baseline revision pin the reviewed state.

If the connected server does not expose these tools, say the cap-table capability
is unavailable on that server. Do not claim deployment from plugin installation.
The first implementation supports US corporations and a restricted instrument
matrix. Unsupported net exercise, bespoke conversion rights, anti-dilution,
secondary/rollover transactions or contractual settlement rounding require an
explicit gap and a supported adapter, not a generic formula.
