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
   - Document name and page number
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

Use these when the user names a specific document, section, table, or note —
reach for `search_deal_documents` when they're asking a question and don't
know exactly where the answer lives.
