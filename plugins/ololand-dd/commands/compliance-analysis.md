---
description: Run deal-scoped compliance analysis for OFAC screening, HSR threshold review, and CFIUS risk. Uses OloLand's context-aware compliance workbench.
---

# Compliance Analysis

Run OloLand's compliance workbench for sanctions, antitrust threshold, and national-security risk checks.

## Usage

```
/compliance-analysis <deal_id> [ofac|hsr|cfius|all]
```

## Arguments

- `deal_id` (required) - The deal to analyze.
- `scope` (optional) - `ofac`, `hsr`, `cfius`, or `all`. Default: `all`.

## Execution

1. For `ofac` or `all`, call `run_ofac_screen(deal_id)`. Pass explicit `entities` or `sdn_entries` only if the user supplied them.
2. For `hsr` or `all`, call `run_hsr_analysis(deal_id)`. If the user supplies transaction value, buyer size, target size, or exemptions, pass those inputs through. Dollar inputs are in millions.
3. For `cfius` or `all`, call `run_cfius_risk(deal_id, ...)`. Ask for missing acquirer country, target industry, government ownership, critical technology, critical infrastructure, sensitive data, and government-contract flags when they materially affect the result.
4. Use returned `view_url` values for web app handoff.

## Output

Render:

- **OFAC** - match status, matched entities, confidence, required remediation.
- **HSR** - reportability status, thresholds crossed, exemptions, timing risk.
- **CFIUS** - risk tier, drivers, mitigation path, filing recommendation.
- **Open diligence asks** - missing identities, jurisdictions, NAICS/product categories, ownership, sensitive-data facts.

## Guardrails

- This is workflow support, not legal advice. Tell the user to involve counsel for filings, sanctions escalations, or CFIUS mitigation.
- Do not treat missing acquirer/target details as clean results. Classify missing data as a gap.

## Output URL Conventions

Use the tool-returned `view_url`. Canonical surface:

- Compliance workbench: `https://app.ololand.ai/deals/{deal_id}/analysis/compliance`
