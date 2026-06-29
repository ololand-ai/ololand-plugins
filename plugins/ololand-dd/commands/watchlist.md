---
description: Create, inspect, and promote OloLand watchlists for continuous company and signal monitoring.
argument-hint: "[list|create|matches|promote] ..."
---

# Watchlist

Use this command when the user wants ongoing monitoring for a sourcing thesis, signal-driven target tracking, or promotion of a watchlist match into a deal.

## Usage

```
/watchlist list
/watchlist create "Healthcare IT carveouts" criteria='{"query":"healthcare IT carveouts","company_scope":"both"}'
/watchlist matches <watchlist_id>
/watchlist promote <watchlist_id> <match_id>
```

## Execution

1. `list` — call `mcp__ololand__list_watchlists`.
2. `create` — ask for a name and criteria if absent, then call `mcp__ololand__create_watchlist`.
3. `matches` — call `mcp__ololand__list_watchlist_matches`, defaulting to active/non-dismissed matches.
4. `promote` — confirm the user wants to create a deal, then call `mcp__ololand__promote_watchlist_match`.
5. If the user starts from prose instead of a watchlist id, run `/company-discovery` first and use its filters as watchlist criteria.

## Output

- For lists: watchlist name, matched count, threshold, last matched time, and criteria.
- For matches: company, match score, match reason, signal count, promoted deal id if present.
- For promote: created deal id, canonical company name, and returned `view_url`.

## Guardrails

- Promotion creates a real deal row. Confirm before calling `promote_watchlist_match`.
- Dismissal/pinning remains a UI workflow unless the user explicitly asks for match state updates.
- Watchlists are monitoring infrastructure, not diligence conclusions.

