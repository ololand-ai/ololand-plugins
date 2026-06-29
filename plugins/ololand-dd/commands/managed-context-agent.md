---
description: Launch a feature-flagged Claude Platform managed context agent for a deal when OloLand has enabled the managed executor.
argument-hint: "<deal_id> <agent_key> [prompt]"
---

# Managed Context Agent

Use this command only when the user explicitly asks to run an OloLand managed context agent or names a registered context-agent key.

## Usage

```
/managed-context-agent <deal_id> <agent_key> [prompt]
```

Common agent keys depend on the deployment registry. Do not invent them. If the user does not know the key, ask them to choose from the deployment's registered context agents or use `/talk-to-deal` instead.

## Execution

1. Confirm the deal id and exact `agent_key`.
2. Call `mcp__ololand__launch_managed_context_agent(deal_id, agent_key, prompt)`.
3. If queued, poll the returned `task_id` with `mcp__ololand__check_task_status`.
4. If the tool returns `managed_executor_unavailable` or `agent_not_found`, explain that the deployment is not configured for that managed agent and fall back to `/talk-to-deal` or the standard DD tools.

## Guardrails

- The managed-agent substrate is feature-flagged and environment-specific. Do not promise availability.
- Do not route production deal data into staging-configured agents. If the backend rejects the dispatch, fail closed.
- Use this for explicit managed-agent launches, not as the default path for ordinary deal Q&A.

