---
description: Map private companies, review a sourced target brief, inspect data-source access, or prepare a deal-sourcing pipeline.
argument-hint: "[map <criteria>|brief <watchlist_id> [since YYYY-MM-DD]|connections|<criteria>]"
---

# Deal Sourcing

End-to-end sourcing pipeline that compounds: every selected company persists in
the tenant-owned sourcing ledger before contact enrichment or outreach begins.

## Usage

```
/source <criteria>
/source map private ecommerce seller software, trust and fulfillment tools
/source brief <watchlist_id> since 2026-09-21
/source connections
```

If no criteria are provided, ask for capabilities or sector, geography, stage
or size preferences, and exclusions. Early-stage capability searches need not
have revenue or EBITDA data; keep unavailable financials unknown.

## Select the workflow

Route `connections`, `brief`, and `map` before thesis/default sourcing intent.
Requests for a company landscape, database, or research-only shortlist use
`map`; requests to review an existing pipeline or prepare its weekly brief use
`brief`. These modes do not capture contacts, draft outreach, promote deals,
or activate delivery. A recurring-delivery request is a separate scheduling
task, not satisfied by generating a brief.

Execute exactly one branch and return its output. After `connections`, `brief`,
or `map` completes, stop; never fall through to the default sourcing pipeline
or its contact/outreach steps. Only a separate user request can start another
branch.

### Connections — establish what can actually be read

Inventory only tools available in this session. The plugin declares OloLand's
MCP server; it does not install or authenticate Google Drive, Slack, Gmail,
Calendar, Obsidian, or an internal forum connector.

If the host already exposes a source connector, use it for a small read of a
user-selected permitted source. Report the source reference, access outcome,
and intended use. Do not infer working access from the presence of a tool.
When no connector is available, report that gap and use a selected-file import
or the client's connector setup flow. Never request tokens in chat.

Host tools can contribute evidence to this conversation. Their credentials and
permissions do not transfer to OloLand, and an interactive read does not create
a persistent OloLand source or authorize a scheduled job. Before passing
private excerpts to OloLand, establish that this transfer is within the user's
requested scope and use only necessary content with source references. Never
include private notes, strategy, or source excerpts in public-web queries.

For the OloLand application, direct the user to Settings → Connect data sources
(`/integrations`; older versions label it Integrations). The current Google
connection supports Drive import and Home assistant reads. For deal analysis,
import selected documents into that deal's Data Room and verify they appear
and are retrievable. Connecting alone does not sync a vault or import files.
The Gmail connection is send/metadata access, not inbox-content retrieval;
do not claim Calendar or Slack access from the Google connection. Connected
Apps lists agents authorized to access OloLand, not external data sources.

Return a table: source, access path, tested read, persistence, remaining step.

### Map — persist a research universe without outreach

Load the `deal-sourcing` skill's research-only workflow. Run discovery and
durable mandate/candidate persistence (steps 1–3 below) and then stop before
contact capture. Call `mcp__ololand__list_watchlists` first to reuse a materially
identical mandate. Pass actual discovery results unchanged to persistence;
never fabricate discovery IDs or disguise hand-researched rows as returned
objects. If OloLand access is unavailable, provide a clearly labeled local
research artifact and state that it has not been saved to the tenant ledger.

Include capability/category, stage and ownership evidence (or unknown),
source/date, fit hypothesis, uncertainty, actual saved stage, and next research
action. Stage and private status require evidence; absence of a stock ticker
is not proof. Keep evidence completeness separate from strategic fit.

### Brief — read an existing sourcing ledger

1. If the watchlist ID is missing, call `mcp__ololand__list_watchlists` and
   resolve the intended mandate; do not create one as a side effect.
2. Call `mcp__ololand__list_watchlist_matches` with that `watchlist_id`,
   `include_dismissed: true`, `skip: 0`, and `limit: 100`. Page using `skip`
   until `total` is covered, or state the exact reviewed subset if bounded.
   Preserve passed/dismissed dispositions; they are not new recommendations.
3. If a comparison date is supplied, classify new-to-ledger candidates using
   `first_matched_at`. A newer `last_signal_at` or `updated_at` identifies a
   record to inspect, not proof of a material business change. Use dated
   evidence to explain an update. Without a prior brief/baseline, label the
   result an initial snapshot; never invent week-over-week change.
4. Review supporting `evidence_refs` and any permitted public sources. Select
   up to 5–10 relevant, non-passed candidates; use fewer if evidence is weak.
   Distinguish new discoveries, evidenced updates, unchanged watch items,
   and research gaps. Report any reconsideration of a passed company
   separately, with its original reason and new evidence; do not change it.
5. For each item show the company/domain, mandate fit hypothesis, what changed
   (or initial discovery), dated sources, uncertainty, and next action. Return
   the actual `view_url` and covered period. Save/update/promote/contact/send
   tools are out of scope for this read-only mode.

A brief generated here is an on-demand draft. Search Monitor is the sourcing
ledger; existing in-app briefings and environment-controlled digest delivery
have their own cadence. Do not claim a Monday schedule, delivery, or background
source access without an actual configured schedule and execution evidence.
The unrelated marketing weekly briefing is not a tenant sourcing scheduler.

## Default sourcing pipeline — `/source <criteria>` only

This section is not executed for `connections`, `brief`, or `map`. For remaining
requests, first classify the request. If it asks to create, list, update, deactivate, or
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

## Default sourcing output

Report a table:

| Company | Contact evidence | Hook | Candidate stage | Outreach copy |

Plus a summary: N discovered, M saved, D deduped/updated, C contacts captured.

## After default sourcing completion

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
