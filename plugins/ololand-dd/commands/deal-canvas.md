---
description: Create or update charts, KPI rows, tables, and infographics on the deal canvas — every value bound to an engine or a citation, never invented.
argument-hint: "<deal_id> [chart|kpi|table|infographic|update] ..."
---

# Deal Canvas

Use this command when the user asks for a chart, graph, KPI summary, table,
or infographic **on the deal canvas** — a persisted, dock-visible artifact,
not a one-off markdown table in chat.

## Usage

```
/deal-canvas <deal_id> chart <chart_type> "<title>" <x_axis_key> <series...>
/deal-canvas <deal_id> kpi "<title>" <items...>
/deal-canvas <deal_id> table "<title>" <columns...> <items...>
/deal-canvas <deal_id> infographic "<title>" <sections...>
/deal-canvas <deal_id> update <tile_id> <changed fields...>
```

## The binding contract (applies to every kind)

Every numeric series, item, or column must be bound one of two ways — there
is no free-text numeric value on this surface:

- **Engine-bound** — `{"mode": "engine", "metric": <engine metric>}` and
  OloLand fills the value from its own engines (financial snapshot / DCF /
  LBO). Never set `unit`/`scale` on an engine-bound value; they're ignored if
  present.
- **Cited** — `{"mode": "cited", "citations": [{"document_id": <file in this
  deal>, "page": <n>}]}` with the row values passed in `data` (charts) or
  inline on the item/column (KPI/table/infographic). Every cited series must
  carry at least one citation that resolves to a file in **this** deal, or
  the call is refused with `error_code="uncited_series"`. For KPI rows,
  tables, and infographics specifically, a cited entry also requires an
  explicit `unit` (`usd` | `percent` | `ratio` | `count`) and, when
  `unit="usd"`, an explicit `scale` (`actual` | `thousands` | `millions` |
  `billions`) — OloLand converts to canonical absolute USD before storing.
  Missing or invalid unit/scale is refused the same way, never defaulted.

## Execution

1. **chart** — call `mcp__ololand__create_deal_chart(deal_id, chart_type,
   title, x_axis_key, series, data, filters, insights)`. `chart_type` is one
   of `line`, `bar`, `area`, `scatter`, `pie`, `composed`. `data` carries the
   rows for cited series only (ignored for engine series). Re-issuing an
   identical chart returns the existing tile (`deduped: true`) instead of
   minting a duplicate — don't apologize for or hide a dedupe response, just
   report the existing tile.
2. **kpi / table / infographic** — call `mcp__ololand__create_deal_artifact(
   deal_id, kind, title, items, columns, x_axis_key, data, sections,
   insights)` with `kind` set to `kpi_row`, `table`, or `infographic`. Use
   `kind="infographic"` with 1-12 ordered `sections` for composite requests
   that combine several of the above. Never author raw HTML or sandbox files
   for this surface — the artifact system renders it.
3. **update** — for any follow-up like "make it a bar chart" or "add EBITDA
   margin," call `mcp__ololand__update_deal_artifact(deal_id, tile_id, ...)`
   with the `tile_id` the create call returned, **restating the full
   binding** (`series`/`items`/`columns`/`sections`) — every value is
   re-verified against engines/citations exactly as on creation, so a partial
   restatement drops whatever isn't repeated. The prior spec is kept as a
   restorable version, so this is safe to iterate on.

## Output

Report the tile/artifact reference and kind, whether it was newly created,
updated, or deduped, and — for cited series — which document(s)/page(s) back
each value. If a call comes back `uncited_series`, tell the user exactly
which item is missing its citation, unit, or scale rather than retrying with
a guessed value.

## Guardrails

- **No invented numbers.** Every value is engine-bound or cited to a document
  in this deal — never a value typed from memory or estimated in chat.
- **Update in place, don't duplicate.** A follow-up edit to an existing tile
  goes through `update_deal_artifact` with its `tile_id`, not a fresh
  `create_deal_chart`/`create_deal_artifact` call.
- Cell-level workbook authoring is a different surface — see `/workbook` for
  Excel-style analysis workbooks; this command is for canvas-visible
  charts/KPIs/tables/infographics only.
