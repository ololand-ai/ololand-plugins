---
description: List, read, create, or template-populate deal-scoped OloLand workbooks for analysis handoff.
argument-hint: "[list|get|create|templates|generate|excel-model|extraction] <deal_id|workbook_id>"
---

# Workbook

Use this command when the user wants to see analysis workbooks, open workbook cells, create a workbook shell for follow-up analysis, or populate a workbook from a registered Excel template.

## Usage

```
/workbook list <deal_id>
/workbook get <workbook_id>
/workbook create <deal_id> "QoE follow-up model"
/workbook templates [profile_id]                 # registered template profiles, or one profile's mappings
/workbook generate <deal_id> <template_id> [extraction_id]  # DRAFT populated workbook from a template
/workbook excel-model <deal_id> [title]           # persisted/downloadable live-formula LBO model
/workbook extraction <deal_id> <document_id>     # extract canonical indicators from a deal document
/workbook extraction <extraction_id>             # read back a finished extraction
```

## Execution

1. `list` — call `mcp__ololand__list_deal_workbooks(deal_id)`.
2. `get` — call `mcp__ololand__get_workbook(workbook_id, include_cells=true)`.
3. `create` — confirm title and description, then call `mcp__ololand__create_deal_workbook`.
4. `templates` — call `mcp__ololand__list_excel_templates()` for the company's registered template profiles; for one profile's status and learned field mappings, call `mcp__ololand__get_template_profile(profile_id)`.
5. `generate` — call `mcp__ololand__generate_populated_workbook(deal_id, template_id)`, optionally with an `extraction_id`. Returns a `task_id`; poll `mcp__ololand__check_task_status` for the audit manifest and any fields still needing confirmation.
6. `excel-model` — call `mcp__ololand__generate_excel_model(deal_id, model_type="lbo", title=title)` directly. This is distinct from the template-population path: it runs or reuses the persisted deterministic LBO engine, builds a live-formula `.xlsx`, saves it as a deal artifact, and returns the dock-artifact reference that opens with a Download button. `model_type="dcf"` fails closed with `model_type_not_ready`; DCF workbook generation is not ready.
7. `extraction` — call `mcp__ololand__extract_indicators_from_document(deal_id, document_id)` to extract canonical financial indicators (with cell-level citations) from an uploaded document; returns a `task_id`. Poll `mcp__ololand__check_task_status(task_id)` until it completes and reports the `extraction_id`, then read results with `mcp__ololand__get_canonical_extraction(extraction_id)`. If the user already has an extraction id, skip straight to the read.
8. If the user wants to write model cells, explain that workbook cell authoring remains in the app/workbook surface unless a specific MCP cell-write tool exists.

## Output

- **Workbook list**: title, id, archived state, updated time.
- **Workbook detail**: title, description, cells by position/type/title, execution errors.
- **Create result**: workbook id and returned `view_url`.
- **Templates**: profile id, name, status, mapped-field count.
- **Generate result**: task id, then — from task status — the audit manifest and the list of fields needing human confirmation. Label the workbook DRAFT.
- **Excel-model result**: artifact id, title, model type, file size, and returned dock-artifact reference. The workbook is persisted and downloadable; state that DCF workbook generation is not ready.
- **Extraction**: extraction id, classified fields with citation coverage.

## Guardrails

- Do not invent workbook cells from chat. Create a shell and point the user to the app if cell-level authoring is needed.
- **Template-populated workbooks are always DRAFT.** Only a human, via the in-app review UI, can finalize one — never present a generated workbook as finalized, and surface the fields the audit manifest says still need confirmation.
- The `excel-model` workflow is engine-bound and separate from template review. Do not relabel it as a template-populated DRAFT or route it through `generate_populated_workbook`.
- Keep analysis claims cited to documents or extracted knowledge; workbook presence alone is not evidence.
