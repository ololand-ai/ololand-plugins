---
description: Export an OloLand deal dossier as an OKF bundle for downstream system handoff.
argument-hint: "<deal_id>"
---

# OKF Export

Use this command when the user asks for an OKF bundle, portable deal dossier, or machine-readable export of a deal's OloLand record.

## Usage

```
/okf-export <deal_id>
```

## Execution

1. Confirm the deal id.
2. Call `mcp__ololand__export_deal_okf_bundle(deal_id)`.
3. If the response includes artifact or download metadata, render it exactly and preserve provenance fields.
4. If the user wants a regulator/compliance package instead, route to `/regulator-export`; OKF is a deal-record handoff, not the compliance-framework export.

## Output

- Bundle id/path or artifact id.
- Included sections/data classes.
- Any warnings about missing deal data.
- Returned URL or retrieval instructions.

## Guardrails

- Do not describe OKF as a signed IC artifact.
- Do not strip provenance, source ids, or methodology fields from the exported bundle summary.

