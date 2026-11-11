---
description: Request, inspect, and track a human reviewer's check of a deal's forensic screen. The reviewer's sign-off is evidence attached to the IC package with its lineage, not an audit, attestation, or signed opinion.
---

# Verification Marketplace

Use this command when the user asks for a human reviewer, verified forensic screen, external reviewer status, or IC appendix provenance.

## Usage

```
/verification-marketplace <deal_id> [status|list|request]
```

## Arguments

- `deal_id` (required) - The deal whose forensic screen verification state should be reviewed.
- `action` (optional) - `status` (default), `list`, or `request`.

## Execution

1. Call `get_deal_verification_status(deal_id)` first. This returns the active request, latest signed sign-off if one exists, reviewer credential metadata, and web URLs.
2. If action is `list`, call `list_deal_verification_requests(deal_id)` and render each request with `status`, `priority`, `requested_at`, `assigned_at`, `completed_at`, `source_artifact_id`, and `forensic_job_id`.
3. If action is `request`, confirm the user wants to queue a Phase-1 concierge review. Then call `request_verified_forensic_screen` with the `deal_id` and any known `purchase_id`, `forensic_job_id`, `source_artifact_id`, and `findings_scope`.
4. If a signed artifact exists, surface its signed artifact ID and IC-package appendix lineage. Treat this as control evidence, not generic services copy.

## Output

Render:

- **Verification state** - no request / queued / assigned / in review / signed / rejected / canceled.
- **Reviewer** - reviewer name, credential, firm, and conflict status when available.
- **SLA** - requested/assigned/completed timestamps and any SLA deadline returned by the tool.
- **Signed artifact lineage** - parent forensic artifact -> signed verification artifact -> IC appendix.
- **Next action** - queue request, wait for assignment, review signed statement, or attach to IC package.

## Guardrails

- Do not imply automatic payment, escrow, or instant fulfillment. Phase 1 is a manual concierge marketplace with explicit fee/spread accounting.
- A reviewer's sign-off is review evidence. Do not describe it as an audit, an attestation, a CPA opinion, or an expert-signed opinion.
- Do not bypass conflict checks. If the tool reports a conflict or blocked assignment, surface that as a blocker.
- If the user wants to approve IC, pair this command with `/ic-approve-readiness`; human verification is additional evidence, not a substitute for resolving assumption-control blockers.

## Output URL Conventions

Use tool-returned `view_url` values when present. Canonical surfaces:

- Forensic analysis: `https://app.ololand.ai/deals/{deal_id}/analysis/financial/forensic`
- IC package: `https://app.ololand.ai/deals/{deal_id}/ic-package`
