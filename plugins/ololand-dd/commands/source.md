---
description: Source deals — discover and persist targets, capture supported contacts, and prepare outreach copy for review.
argument-hint: "[criteria, e.g. 'industrial services in Texas $10-50M EBITDA']"
---

# Deal Sourcing

End-to-end sourcing pipeline that compounds: every selected company persists in
the tenant-owned sourcing ledger before contact enrichment or outreach begins.

## Usage

```
/source <criteria>
```

If no criteria provided, ask the user for sector, geography, size band (revenue or EBITDA), and any negative filters.

## Execution

First classify the request. If it asks to create, list, update, deactivate, or
review matches for a standing thesis, route directly to the thesis operations
below. Do not load `deal-sourcing` or run the one-off discovery, watchlist,
candidate-persistence, contact-import, or outreach pipeline for a thesis
request. Otherwise, load the `deal-sourcing` skill and run this pipeline:

1. **Discover targets** — call `mcp__ololand__search_company_discovery` with:
   - `query`: the user's sector/product/market thesis
   - `mode: "discover"`
   - `company_scope: "private"` unless the user explicitly includes public targets
   - `filters`: geography, industry/sector, ownership, size, and negative filters
   - `limit: 25`
   Use `mcp__ololand__natural_language_company_search` only when the criteria
   cannot be represented as structured filters.
2. **Create the mandate** — call `mcp__ololand__create_watchlist` with the
   user's original criteria and a descriptive name. Reuse an existing watchlist
   only when its criteria are materially identical.
3. **Persist candidates immediately** — pass the selected discovery result
   objects unchanged to `mcp__ololand__save_sourcing_candidates`, with
   `watchlist_id` set to the ID returned or reused in step 2 and `candidates`
   set to the selected result objects. This captures the source snapshot,
   evidence references, match rationale, and candidate stage before any
   third-party enrichment. Repeated calls are idempotent.
4. **Capture supported contacts** — when a discovery result includes an
   executive with a real email, phone number, or LinkedIn URL, select at most
   one founder/CEO/CFO and pass that returned evidence to
   `mcp__ololand__openclaw_import_contacts` with
   `source_system: "company_discovery"`. OloLand performs tenant-scoped identity
   dedupe and central do-not-contact checks. If discovery did not return usable
   contact evidence, leave the candidate shortlisted and report the gap.
5. **Link the relationship** — call
   `mcp__ololand__update_sourcing_candidate` with the step-2 `watchlist_id`,
   saved candidate `match_id`, resulting `outreach_contact_id`, and
   `sourcing_stage: "enriched"`.
6. **Find a hook** — prefer the candidate's returned `search_snippets`,
   `signal_summary`, and `ma_signal_summary`. If those are insufficient, perform
   a current public-web search for a funding round, hiring spike, leadership
   change, product launch, or expansion. Do not call deal-scoped research tools
   before a Deal exists.
7. **Prepare outreach copy** — write a 60-90 word proposed email in the command
   response using the specific hook. This is reviewable copy, not a Gmail or
   OloLand outreach draft, and it is never sent. Keep the candidate at
   `enriched` (or `shortlisted` when no contact was captured).

This plugin declares only the OloLand MCP server. Do not claim Apollo or Gmail
operations, and do not fabricate contact or draft IDs.

## Output

Report a table:

| Company | Contact evidence | Hook | Candidate stage | Outreach copy |

Plus a summary: N discovered, M saved, D deduped/updated, C contacts captured.

## After Completion

- Suggest `/dd-analyze <company>` for the most promising target.
- Remind the user: the proposed copy was not saved or sent; move it to the
  firm's approved outreach system only after review.

## Standing sourcing mandates (thesis)

A watchlist (steps 2-5 above) is a one-off discovery run's persistence layer.
A **thesis** is a different, longer-lived object: a standing sourcing mandate
(sectors, sub-sectors, geography, financial parameters, deal types,
qualitative criteria) that the signal pipeline continuously matches against,
surfacing hits in the Search Monitor over time. These are sourcing mandates,
**not strategy or SWOT frameworks** — do not describe them that way.

Use this when the user wants to save standing acquisition criteria rather
than run a one-time discovery pass:

- **Create** — call `mcp__ololand__create_thesis` with `thesis_name` and
  whichever of `description`, `fund_name`, `sectors`, `sub_sectors`,
  `geography`, `geography_exclusions`, `financial_parameters`, `deal_types`,
  `qualitative_criteria`, `signal_config` the user specified.
- **List** — call `mcp__ololand__list_theses`, optionally filtered by
  `status` (`active` | `paused` | `closed`), before creating a new one — reuse
  an existing mandate whose criteria materially overlap rather than
  duplicating it.
- **Update** — call `mcp__ololand__update_thesis` with `thesis_id` and only
  the fields that changed; omitted fields are left alone.
- **Deactivate** — call `mcp__ololand__deactivate_thesis` with `thesis_id`
  (default `status="paused"`, reversible — never a hard delete; pass
  `status="closed"` when the user means it's done for good). Reactivate with
  `update_thesis(thesis_id, status="active")`.
- **Review matches** — call `mcp__ololand__list_thesis_matches(thesis_id)` for
  the mandate's current non-dismissed signal matches, highest composite score
  first. Promising matches still go through the discovery pipeline above
  (persist as a sourcing candidate, capture supported contacts) before any
  outreach copy is drafted.

Report the `view_url` each call returns (the Search Monitor tab) rather than
constructing a link.
