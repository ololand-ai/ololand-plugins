---
description: Search OloLand's company-discovery surface using structured or natural-language criteria, then hand promising targets into watchlists or deals.
argument-hint: "<query> [private|public|both]"
---

# Company Discovery

Use this command when the user wants to discover companies, screen a market, search by natural-language criteria, or find sourcing candidates before creating a watchlist or deal.

## Usage

```
/company-discovery "vertical SaaS payments companies with sponsor ownership" both
/company-discovery "industrial distributors in the Midwest with succession risk" private
```

## Execution

1. Prefer `mcp__ololand__natural_language_company_search` for prose queries with multiple criteria. It decomposes intent and filters.
2. Use `mcp__ololand__search_company_discovery` when the user supplies structured filters, mode, company scope, or wants lookup/discover/signals explicitly.
3. For each promising result, present the canonical name, domain/ticker when present, source summary, signal count, and why it matched.
4. If the user wants ongoing monitoring, route to `/watchlist` and call `mcp__ololand__create_watchlist` with the same criteria.
5. If the user wants to diligence a result immediately, use `/new-deal` or `mcp__ololand__create_deal` with the selected company.

## Output

Render a concise table:

| Company | Type | Domain/Ticker | Match reason | Signals | Next action |

Then summarize:

- Query interpretation and filters applied.
- Degraded sources, if any.
- Recommended watchlist criteria if the user wants continuous monitoring.

## Guardrails

- Do not create a deal automatically from a discovery result unless the user asks.
- Do not claim a result is proprietary if it came from public/signal sources.
- For investment recommendations, move from discovery into `/pre-screen` or `/dd-analyze`.

