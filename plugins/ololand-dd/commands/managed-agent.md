---
description: 'Run one of OloLand''s cloud-hosted deal specialists on a deal — risk mapping, forensic QoE, pre-LOI screening, financing prep, IC memo drafting, or the multi-agent IC coordinator that runs risk + forensic + memo specialists in parallel. Each specialist reads the deal through OloLand''s scoped, audited tool rail and answers with citations; the run is dual-written to OloLand''s audit trail (agent_runs + Claude Platform session id) so the result is provenance-complete. Asynchronous: starts the run, then polls to completion.'
---

# /managed-agent (cloud deal specialists)

Runs one of OloLand's **managed deal specialists** — agents hosted on the Claude
Platform that work a deal through OloLand's scoped, audited tool rail and
return a sourced, citation-bearing answer. Use it when a question deserves a
dedicated specialist pass rather than an inline answer: a full risk read, a
forensic QoE battery, a pre-LOI screen, financing prep, or an IC-grade
synthesis where the coordinator delegates to risk, forensic, and memo
specialists in parallel.

## Usage

```
/managed-agent <deal_id> <specialist> <question or instruction>
/managed-agent list
```

## Arguments

- `deal_id` (required) — the OloLand deal the specialist should work on.
- `specialist` (required) — one of the `template_id`s returned by
  `mcp__ololand__list_managed_agents`. Typical roster:
  - `risk-chat` — maps findings to the risk taxonomy with severity, likelihood, evidence
  - `forensic-chat` — Beneish, Benford, EBITDA bridge, cross-document reconciliation
  - `screen-chat` — pre-LOI go/no-go: premium analysis, accretion/dilution, antitrust HHI
  - `financing-chat` — financing analysis, capital-provider sourcing prep, lender-package prep
  - `ic-memo` — IC memo drafting; can persist a DRAFT IC package
  - `ic-coordinator` — multi-agent IC synthesis (delegates to risk + forensic + memo in parallel)
  - `lead-orchestrator` — general sourced deal Q&A
- `question` (required) — what the specialist should do.

## Execution

This is an asynchronous managed-agent run. Do not expect an immediate answer;
start it, then poll.

1. **`list` mode.** If the user passed `list` (or asked what specialists
   exist), call `mcp__ololand__list_managed_agents` and render each agent's
   `template_id`, description, and whether it is `configured` in this
   environment. Recommend the best fit for what the user is working on, then
   stop.
2. **Start.** Call `mcp__ololand__run_managed_agent` with `deal_id`,
   `template_id`, and `prompt`. It returns a `task_id` (with
   `task_type: "managed_interactive_agent"`).
   - `{"error_code": "not_found"}` — wrong deal id; confirm it with
     `mcp__ololand__list_deals`.
   - `{"error_code": "invalid_template"}` — the specialist name is not
     callable; show the roster from `mcp__ololand__list_managed_agents` and let
     the user pick.
   - `{"error_code": "not_configured"}` — the specialist exists but is not
     provisioned in this environment; relay that and suggest another
     specialist from the `list` output that shows `configured: true`.
   - `{"error": "Company scope required …"}` — the MCP connection is not
     company-scoped; tell the user to reconnect / sign in, do not retry
     blindly.
   - Any other tool-level error fails closed — relay it rather than
     synthesizing an answer.
3. **Poll.** Call `mcp__ololand__check_task_status` with the `task_id` every
   few seconds. While `state` is `STARTED`/`PROGRESS`, relay the progress
   message. The IC coordinator's delegating turns run multi-minute — keep the
   user informed rather than giving up. Keep polling until `state` is
   `SUCCESS` or `FAILURE`.
4. **On `FAILURE`** — report the `error` verbatim. Do not fabricate a
   specialist answer.
5. **On `SUCCESS`** — the `result` object is:
   - `response` — the specialist's answer, already source-cited. This is the
     deliverable; render it unaltered.
   - `run_id` — the OloLand `agent_runs` audit row.
   - `claude_platform_session_id` — the hosted session for operator trace.
   - `tool_calls`, `input_tokens`, `output_tokens` — run telemetry.
   - `citations` — structured citation payloads backing `[N]` markers, when
     present.

## Output

Present the specialist's `response` unaltered, then append:

```
Specialist run — deal: <deal_id>  specialist: <template_id>
Provenance: run_id=<run_id>  session=<claude_platform_session_id>  tool_calls=<tool_calls>
```

## Honest bounds

- The specialist reads the deal only through OloLand's scoped tool rail — it
  answers from the ingested corpus and deterministic engines, and says so when
  evidence is missing. It cannot approve anything: IC package approval, patch
  approval, and version commits are human-only actions in the OloLand app.
- `ic-memo` / `ic-coordinator` may persist an IC package **draft**; approval
  stays in-app.
- `financing-chat` prepares analysis and sourcing materials only; it never
  spends Apollo credits, sends email, or submits lender applications.
- If a run reports no usable evidence, relay that — a specialist run is not a
  substitute for ingesting the data room first (`/new-deal`, document upload).

## Example

```
/managed-agent deal_acme_2026 forensic-chat Run the full QoE battery and flag anything that moves adjusted EBITDA by >5%.
```

Companion: `/conflicts` (unattended cross-document conflict scan), `/verify`
(per-figure corpus verification), `/dd-analyze` (bounded extraction, risk, and
financial-snapshot pipeline; reconciliation is a separate explicit action).
