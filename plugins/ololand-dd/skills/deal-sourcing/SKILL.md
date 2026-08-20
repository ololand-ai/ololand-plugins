---
name: deal-sourcing
description: Use when sourcing M&A or PE deals — discovering target companies from criteria, persisting a tenant-owned candidate ledger, capturing supported contacts, and preparing reviewable outreach copy.
---

# Deal Sourcing

## Why this exists

Generic "sourcing" prompts produce a list of company names and end there. This
skill closes the loop: discovery → durable mandate/candidates → contact graph →
reviewable outreach copy → deal conversion. Persistence happens before contact capture,
so a missing connector never loses the analyst's market map.

## Pipeline

### Thesis routing

Classify thesis intent before starting this one-off pipeline. Requests to
create, list, update, deactivate, or review matches for a standing sourcing
mandate must go directly to the corresponding thesis MCP operation; do not
run discovery, create a watchlist, persist candidates, import contacts, or
draft outreach first. A thesis is a long-lived sourcing mandate, not a SWOT
or strategy framework.

### 1. Discovery
- Use `mcp__ololand__search_company_discovery` with `mode: "discover"`,
  `company_scope: "private"`, and explicit filters (sector, geography, size,
  ownership type if PE-relevant).
- Cap initial set to 25 per run. Quality > quantity. If user wants more, run again with refined criteria.

### 2. Durable mandate and candidates
- Create or reuse a materially identical watchlist with
  `mcp__ololand__create_watchlist`.
- Pass the selected company-discovery result objects unchanged to
  `mcp__ololand__save_sourcing_candidates`, with `watchlist_id` set to the
  created/reused watchlist ID and `candidates` set to the selected result
  objects.
- This is the required persistence step. The tool is idempotent and preserves
  discovery snapshots, source systems, evidence references, score/rationale,
  workflow stage, and later deal-conversion lineage.

### 3. Contact capture
- Inspect the company-discovery result for returned executives and actual
  identity evidence: email, phone number, or LinkedIn URL.
- Pick at most one contact. Priority: founder > CEO > CFO > head of corp dev.
- When supported evidence exists, import it through
  `mcp__ololand__openclaw_import_contacts` using
  `source_system: "company_discovery"`. This is the tenant-scoped relationship
  graph and central suppression/dedupe boundary.
- Link the returned contact to the candidate with
  `mcp__ololand__update_sourcing_candidate`, passing the same `watchlist_id`,
  the saved candidate `match_id`, and advancing it to `enriched`.
- When no supported identity evidence exists, leave the candidate shortlisted
  and report that contact enrichment remains outstanding.

### 4. Hook (signal sourcing)
- Prefer the discovery result's `search_snippets`, `signal_summary`, and
  `ma_signal_summary`. If necessary, run a current public-web search.
- Look for: funding round, hiring spike, leadership change, product launch, news mention, expansion announcement.
- If no signal found, fall back to a thesis-based hook ("we focus on X, you operate in X") — but flag this row as "weak hook" so the user can decide whether to send.
- Do not call `deep_market_research` or `research_market` before a Deal exists;
  both are deal-scoped.

### 5. Outreach copy
Format constraints:
- 60-90 words. Hard cap at 100.
- Opens with the SPECIFIC signal ("Saw your Series B in March...").
- One sentence connecting it to the fund's thesis.
- One sentence proposing a 20-min call. No calendar links in the first email.
- Sign-off: from the user.

Return the proposed copy for human review. The plugin declares only OloLand's
MCP server, so this step does not save a Gmail draft or create an OloLand
`OutreachDraft`. Do not advance the candidate to `outreach_drafted` unless a
future, supported connector actually persists the draft.

### 6. Persistence
Persistence is completed in step 2 and contact linkage in step 3. Do not use
`log_sourced_lead`; that tool writes the global marketing-lead table and is not
the tenant-owned sourcing system of record.

Never claim Apollo or Gmail execution. Preserve the saved candidates and
report missing contact evidence. Never invent contact, signal, or draft
identifiers.

## Output format

Always produce a markdown table:

```
| Company | Contact evidence | Hook | Candidate stage | Outreach copy |
|---------|------------------|------|-----------------|---------------|
| ...     | ...              | ...  | enriched        | ...           |
```

Plus a summary line: `Discovered N • Saved M • Updated/deduped D • Contacts captured C • Weak-hook L`.

## Anti-patterns

- **Do not auto-send.** Drafts only. Always.
- **Do not enrich more than 1 contact per company.** Multi-touch on first email is spammy.
- **Do not use generic templates.** If you can't find a hook, flag the row instead of inventing one.
- **Do not skip tenant-ledger persistence.** A connector failure must not erase the market map.
- **Do not use the marketing Lead table.** Sourcing candidates and contacts are company-owned.
