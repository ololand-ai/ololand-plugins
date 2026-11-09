---
description: Search documents in a deal's data room — full-text + semantic search across uploaded PDFs, financials, legal docs — plus literal/structural document navigation (list, read, grep, sections, tables, notes).
---

# Deal Document Search

Search across all documents in a deal's data room using hybrid search (dense + sparse + rerank).

## Usage

```
/deal-search <deal_id> <query>
```

## Arguments

- `deal_id` (required) — The deal to search within.
- `query` (required) — Natural language search query.

## Execution

1. Call `search_deal_documents` with the deal_id and query.
2. Present results with:
   - Document name and actual returned locator (PDF page, spreadsheet cell, structural span, or converted-text line); unknown if absent
   - Relevant excerpt (highlighted match)
   - Relevance score
3. If the query implies a financial figure, cross-reference with `get_financial_snapshot` to check consistency.

## Examples

- `/deal-search deal123 customer concentration risk`
- `/deal-search deal123 revenue recognition policy`
- `/deal-search deal123 change of control provisions`
- `/deal-search deal123 EBITDA adjustments and add-backs`

## Document navigation primitives

Semantic search (above) answers "what's relevant to this meaning." These
tools answer "I know (or can find) exactly where this is" — literal path- and
structure-based access to the same data-room text, complementing
`search_deal_documents` (semantic) and `grep_filing` (SEC-filing chunks).

- **List** — `mcp__ololand__list_deal_files(deal_id)` returns every document's
  data-room path, `file_id`, category, size, and modified time. Call this
  before `read_deal_file` / `grep_deal_files` to see what exists.
- **Read** — `mcp__ololand__read_deal_file(path, deal_id, offset, limit)`
  reads a known document's full text by data-room path, paginated by line
  (frontmatter stripped, `file_id` carried for citation).
- **Grep** — `mcp__ololand__grep_deal_files(pattern, deal_id, glob,
  case_sensitive, max_results)` is literal/regex pattern matching over the
  markdown mirror — use this instead of `search_deal_documents` when the user
  needs an exact string or regex match, not a meaning-based hit. `glob` scopes
  to a folder/type, e.g. `financials/*`.
- **Read a structural section** — `mcp__ololand__read_section(deal_id,
  file_id, section)` reads a named section end-to-end (e.g. "Item 7. MD&A",
  "Note 11", "Risk Factors", "Consolidated Balance Sheet"). Section matching
  is case-insensitive substring; requires `file_id` from `list_deal_files`.
  Documents without structural sections return the full document instead
  (`matched_field="document"`); a near-miss on a structured document returns
  `available_sections` to retry against.
- **Read a structured table** — `mcp__ololand__read_table(deal_id, file_id,
  table_label)` returns a document-graph `TableNode` as typed rows × columns
  with cell-level span IDs — not chunked text, so the row/column structure
  survives. Returns an error if the graph has no matching table; there is no
  chunk-based fallback for this one, deliberately, since chunking would
  destroy exactly the structure this tool exists to preserve.
- **Read a financial-statement note** — `mcp__ololand__read_note(deal_id,
  file_id, note_number)` reads a numbered note in full, including its
  outgoing `cross_references` — follow a Note 11 → Note 8 → Note 18 chain with
  repeated calls, or `list_cross_references` for the whole graph at once.

## Native spreadsheet tables

When the connected `read_table` schema and response support native workbook
evidence, an empty `table_label` discovers `available_tables`; use the returned
stable table ID or exact label to select one. Preserve `source_hash`,
`source_version`, `worksheet`, `range`, `table_id`, and `evidence_kind`. A native
cell address is a valid original locator only for that identified workbook
version. Do not map converted-text offsets to cells.

Keep literal values, formulas, and imported cached values distinct. Native
extraction does not recalculate formulas; `cache_status: "unverified"` or
`"missing"` cannot be described as a verified result. Header bindings are
available only when actually returned; a worksheet used-range alone does not
prove row/column meaning, reporting period, currency, or scale. Resolve an
ambiguous label with the returned choices. `table_not_materialized`,
`unsupported_format`, or `source_unreadable` is a capability/data gap, not proof
of an empty workbook. Existing documents may need an explicitly authorized
reingestion in the app. Do not launch one or a paid analysis from a read request.
On an older server, use only its callable schema and report missing native
workbook provenance rather than claiming this path ran.

## Partial retrieval and absence claims

Inspect returned coverage, truncation, and continuation fields before summarizing
completeness. Continue with the returned cursor/offset and the same query/document
when the current callable schema supports it; do not invent parameters for older
servers. Stop when coverage is complete, a reported failure prevents continuation,
or the agreed bound is reached, and disclose the unread portion. A structural read
may be bounded even when described as full text. A missing table graph or a search
with no matches is a retrieval gap, not proof the source contains no such table,
clause, risk, or figure. Only assert absence within the scope actually reviewed.

For financial comparisons, apply the `financial-valuation` identity rules:
entity, reporting period, basis, currency/units, and source/snapshot must match
or be explicitly labeled as different. Do not overwrite a governed model with
a separately retrieved figure.

Use these when the user names a specific document, section, table, or note —
reach for `search_deal_documents` when they're asking a question and don't
know exactly where the answer lives.
