---
description: Pre-flight check before IC package approval. Reads the IC gate evaluator's typed blocker list (unsourced figure, source conflict, open assumption, stale dependent, unsigned workstream, open closing condition, missing readiness input) when the server returns it, plus both assumption blocker tiers and weak-evidence warnings.
---

# IC Approve Readiness

Since the gate evaluator extraction (backend `services/ic_gate_service.py`,
2026-11), approval, memo export and this pre-flight read ONE evaluator. The
control summary carries its projection as `ic_gate`:

```
ic_gate: {
  status: "ready" | "blocked" | "incomplete",
  blocker_count, override_permitted_count,
  by_kind: {<kind>: n},
  blockers: [{kind, code, label, message, evidence: {type, id, ...}, override_permitted}],
  warnings: [...],
  stages: {assumption_controls | memo_verifier | source_conflicts | underwriting_readiness:
           {status: "passed" | "blocked" | "not_evaluated" | "degraded", reason?}},
  kinds: [...]
}
```

`kind` is one of `unsourced_figure`, `source_conflict`, `open_assumption`,
`stale_dependent`, `unsigned_workstream`, `open_closing_condition`,
`missing_readiness_input`. Only `unsourced_figure` and `source_conflict` may
be approved past with a recorded reason (`override_permitted: true`); every
other kind needs the underlying state fixed. `incomplete` means a stage did
not run — the memo figure-vs-source stage runs at approval and export, not on
this read, so it reads `not_evaluated` here — and `ready` is therefore a
lower bound, never an approval.

Older servers return no `ic_gate`; fall back to the two assumption tiers below.

IC package approval is gated by two independent blocker tiers:

1. **Open blocking assumptions** — high or critical tracked assumptions still in an unresolved state.
2. **Unsupported high-priority assumptions** — high or critical tracked assumptions whose evidence_strength is `none` (no provenance attached at all).

A separate **weak-evidence warning** surface flags high/critical assumptions whose evidence_strength is `weak` or `partial`. These do NOT block approval, but the IC viewer surfaces them so the analyst knows what to defend.

This command runs the pre-flight check before the analyst attempts to approve.

## Usage

```
/ic-approve-readiness <deal_id>
```

## Arguments

- `deal_id` (required) — The deal whose IC package readiness to assess.

## Execution

1. Call `get_assumption_control_summary` with the `deal_id`. If the response carries `ic_gate`, it is the authoritative blocker list for this read: render its `status`, then one row per blocker grouped by `kind` (label, `evidence` pointer, whether an override is permitted), then the per-stage status including every `not_evaluated` stage and its reason. Do not add blockers the server did not return, and do not drop any it did.
2. Call `get_assumption_evidence_pack` to retrieve `quality_flags` for the deal.
3. Call `get_ic_package(deal_id)` to retrieve the latest IC package and its `approval_evidence_snapshot`. If the response has `package: null`, no IC package exists yet — note this and continue with just the assumption-level analysis. An approved package's snapshot carries `ic_gate.blockers` and `ic_gate.overrides` — the blockers that stood at approval and the recorded overrides that cleared them; report both when present.
4. Categorize (the fallback detail when `ic_gate` is absent, and the assumption-level drill-down beside it when present):
   - **Tier-1 blockers** (resolution required): from `control_summary.blocking_assumptions` — high/critical, status not in {verified, mitigated, invalidated, accepted}.
   - **Tier-2 blockers** (provenance required): from `quality_flags` — high/critical tracked assumptions with `evidence_strength == "none"`.
   - **Warnings** (review recommended, not blocking): from `quality_flags` — high/critical tracked assumptions with `evidence_strength` in {weak, partial}. Cross-reference these against `approval_evidence_snapshot.warnings` if a package exists.
5. Render:

   - **Assessment**: backend-returned state and coverage. An empty ledger is **NOT ASSESSED**, not evidence that diligence is complete; missing state on an older server is **UNKNOWN**. Report partial or degraded evidence lookup separately from policy blockers.
   - **IC gate** (when `ic_gate` is returned): `status` verbatim, `blocker_count` with `by_kind`, each blocker as `kind` — `label` — evidence pointer — "override with reason permitted" or "fix required", and the stage table. Say which stages did not run. Never upgrade `incomplete` to ready, and never call `ready` approved.
   - **Tracked-control gate**: BLOCKED only for returned applicable blockers; otherwise “no known tracked-control blockers.” `ic_blocked=false` does not establish source support, completeness, model eligibility, or approval.
   - **Artifact eligibility**: report the package/publication status and returned missing prerequisites. If no package exists, report **NOT STARTED** for package preparation; do not describe the deal as ready.
   - **Human approval**: report only the persisted approval state. This read does not approve an IC package.
   - **Tier-1 blockers** (one row per blocker): `assumption_id`, `statement`, `status`, `priority`, recommended resolution
   - **Tier-2 blockers** (unsupported high-priority): `assumption_id`, `statement`, `missing_links`, recommended source to attach
   - **Warnings** (weak/partial evidence): `assumption_id`, `statement`, `evidence_strength`, why this is weak, what to add to strengthen it
   - **Counts**: `total`, `open`, `blocking`, by `evidence_strength`
   - **Package state** (if a package exists): `version`, `status`, `approved_at`, and `approval_evidence_snapshot.summary` — the snapshot that was captured at the last approval attempt or will be captured next.

## Readiness boundaries

When returned, use `assessment_status` with `assessment_scope` and
`degraded_checks`; this is tracked-assumption coverage, not whole-deal completion.
Use `publication_readiness.capabilities` for each returned capability's `status`,
`allowed`, reason, and next action. Eligibility for financial display, valuation,
returns, or memo export does not imply eligibility for IC approval. Preserve
`approval_status: "unknown"` unless a separate authoritative package read proves
human approval. These fields are optional on older servers: missing means unknown.

Read the returned assessment/coverage, `source_support_validation`, quality flags,
and package state independently. `source_support_validation: "not_performed"`
means support has not been checked, even if every tracked assumption is closed.
A source link or a passing quote-existence check does not prove the linked
statement. Never fill absent counts, statuses, or validation results with zeros
or passes. A failed lookup is **degraded/unknown**, not a clean bill of health
and not a newly invented policy blocker; preserve the existing fail-soft policy.
Only the authoritative approval surface decides eligibility and human approval.
Do not run analysis, generate a package, or modify controls during this check.

## Why two tiers

The first tier (open blocking assumptions) catches "we still need to verify this." The second tier (unsupported high-priority) catches "we marked this assumption critical but never attached an evidence link" — a different failure mode where the workflow state is closed but the underlying provenance is empty. Both surface here so the analyst sees exactly what stands between the deal and an approved IC.

## Example

```
/ic-approve-readiness deal_acme_2026
```

With `ic_gate` returned: "IC gate: BLOCKED (3 blockers; 1 may be overridden with a reason). open_assumption — 'FY27 22% growth requires geo expansion' (assumption a-17, unresolved) — fix required. open_assumption — 'WC normalization $4M' (assumption a-22, unsupported evidence) — fix required. missing_readiness_input — 'No risk register for this deal' (lint check missing_risk_snapshot) — fix required. Stages: assumption controls blocked; memo verifier not evaluated (runs at approval and export); source conflicts passed; underwriting readiness blocked."

Fallback (no `ic_gate`): "BLOCKED. Tier-1 (2): 'FY27 22% growth requires geo expansion' (unverified, critical) — schedule commercial DD; 'WC normalization $4M' (unverified, high) — pull A/R aging. Tier-2 (1): 'Customer concentration <30% by closing' (status=unverified, evidence_strength=none) — no provenance attached; link the customer-revenue table or mark it accepted with a memo. Warnings (1): 'EBITDA margin sustainable at 22%' (status=verified, evidence_strength=partial) — only one quarter of margin data; consider strengthening with comparables or normalization analysis."

## Related commands

- `/assumption-controls` — interactive review and status transitions for assumption controls
- `/dd-analyze` — populate bounded extraction, risk, and financial-snapshot inputs before IC synthesis; use a separate explicit reconciliation action when needed

## Output URL Conventions (STRICT)

Domain is `app.ololand.ai`. Surfaces:
- IC package: `https://app.ololand.ai/deals/{deal_id}/ic-package`
- Assumption controls: `https://app.ololand.ai/deals/{deal_id}/analysis/assumptions`
