---
description: Generate or approve the canonical OloLand IC package, while preserving assumption-control and verifier-gate blockers.
argument-hint: "<deal_id> [status|generate|approve]"
---

# IC Package

Use this command when the user asks to generate the canonical 8-section IC package, inspect package state, or approve a package after readiness checks.

## Usage

```
/ic-package <deal_id> status
/ic-package <deal_id> generate
/ic-package <deal_id> approve
```

## Execution

1. Always call `mcp__ololand__get_ic_package(deal_id)` first.
2. Before approval, run `/ic-approve-readiness` or directly call:
   - `mcp__ololand__get_assumption_control_summary`
   - `mcp__ololand__get_assumption_evidence_pack`
3. `generate` — assemble the best available structured `deal_data` from deal, financial snapshot, valuation, risks, verification status, and assumptions. Then call `mcp__ololand__generate_ic_package`.
4. Poll the returned `task_id` using `mcp__ololand__check_task_status`.
5. `approve` — only after the user explicitly says to approve, call `mcp__ololand__approve_ic_package`.
6. If approval returns `readiness_blocked`, `verifier_blocked`, or `bad_request`, surface the blocker verbatim and recommend the smallest remediation step.

## Output

Render:

- **Package state**: id, version, status, selected sections, approved time.
- **Generation**: task id, status, and polling result.
- **Approval**: approved or blocked, with blocker tier and exact backend message.
- **Evidence snapshot**: unsupported/weak/partial assumption counts when available.
- **URL**: use returned `view_url`.

## Guardrails

- Approval is a controlled workflow, not a drafting shortcut. Never call `approve_ic_package` without explicit user instruction.
- Do not set `override_verifier_block=true` unless the user explicitly gives an override reason. Preserve the reason.
- If assumptions are unresolved or evidence is missing, do not summarize as "ready".

