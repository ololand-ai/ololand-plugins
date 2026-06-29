---
description: List, read, or create deal-scoped OloLand workbooks for analysis handoff.
argument-hint: "<deal_id|workbook_id> [list|get|create]"
---

# Workbook

Use this command when the user wants to see analysis workbooks, open workbook cells, or create a workbook shell for follow-up analysis.

## Usage

```
/workbook list <deal_id>
/workbook get <workbook_id>
/workbook create <deal_id> "QoE follow-up model"
```

## Execution

1. `list` — call `mcp__ololand__list_deal_workbooks(deal_id)`.
2. `get` — call `mcp__ololand__get_workbook(workbook_id, include_cells=true)`.
3. `create` — confirm title and description, then call `mcp__ololand__create_deal_workbook`.
4. If the user wants to write model cells, explain that workbook cell authoring remains in the app/workbook surface unless a specific MCP cell-write tool exists.

## Output

- **Workbook list**: title, id, archived state, updated time.
- **Workbook detail**: title, description, cells by position/type/title, execution errors.
- **Create result**: workbook id and returned `view_url`.

## Guardrails

- Do not invent workbook cells from chat. Create a shell and point the user to the app if cell-level authoring is needed.
- Keep analysis claims cited to documents or extracted knowledge; workbook presence alone is not evidence.

