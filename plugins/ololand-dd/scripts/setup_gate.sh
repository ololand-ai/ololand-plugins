#!/usr/bin/env bash
# OloLand DD setup gate — SessionStart hook.
#
# Why this exists: the plugin's .mcp.json authenticates with a static
#   Authorization: Bearer ${OLOLAND_AGENT_KEY}
# When OLOLAND_AGENT_KEY is unset the header goes out empty, the MCP endpoint
# returns 401, and Claude Code falls back to the OAuth 2.1 *loopback* flow
# (the "Authorize Claude Code" popup). That popup frequently fails in
# Cowork / desktop: the browser's redirect to http://localhost:<port>/callback
# never reaches Claude's local listener ("the link didn't reload Claude"), and
# a manual paste then reports "expired" because Claude retried with a fresh
# client + state. The agent key sidesteps OAuth entirely.
#
# This gate makes the missing-key state LOUD at session start — before the user
# stumbles into the broken OAuth popup — and tells them exactly how to fix it.
#
# SessionStart contract: stdout is injected into the conversation as
# additionalContext (Claude reads it); stderr surfaces in the hook transcript.
# Never echo the key itself.

set -euo pipefail

key="${OLOLAND_AGENT_KEY:-}"

if [ -n "$key" ]; then
  if [ "${key#olo_agent_sk_}" != "$key" ]; then
    echo "[ololand-dd] OLOLAND_AGENT_KEY detected — authenticating via agent key (no OAuth needed)."
    exit 0
  fi
  # Set but not the expected prefix — likely a paste error or an OAuth token.
  echo "[ololand-dd] OLOLAND_AGENT_KEY is set but does not start with 'olo_agent_sk_'. \
This is probably a paste error. Generate a fresh agent key at \
https://api.ololand.ai/connect and re-export OLOLAND_AGENT_KEY, then restart Claude Code. \
Do NOT use the in-app 'Authorize Claude Code' OAuth popup — it is unreliable in Cowork/desktop." >&2
  cat <<'CTX'
[ololand-dd setup gate] OLOLAND_AGENT_KEY is set but malformed (it must start with `olo_agent_sk_`). The OloLand MCP server will reject it with 401, after which Claude Code may show an "Authorize Claude Code" OAuth popup. That OAuth loopback flow is unreliable in Cowork/desktop (the callback often fails to return and then reports "expired"). Tell the user NOT to use the OAuth popup. Instead have them: 1) visit https://api.ololand.ai/connect, 2) sign in and click "Generate new key" (starts with `olo_agent_sk_`), 3) `export OLOLAND_AGENT_KEY=olo_agent_sk_...`, 4) restart Claude Code. The /setup skill has the full walkthrough.
CTX
  exit 0
fi

# Unset / empty — the common first-run trap.
echo "[ololand-dd] OLOLAND_AGENT_KEY is not set — OloLand tools will not authenticate. \
Set it up at https://api.ololand.ai/connect (run the /setup skill for steps). \
Skip the in-app 'Authorize Claude Code' OAuth popup; it is unreliable in Cowork/desktop." >&2
cat <<'CTX'
[ololand-dd setup gate] OLOLAND_AGENT_KEY is NOT set. The OloLand MCP server requires it as a Bearer token, so every OloLand tool call will fail with 401. When that happens Claude Code may pop up an "Authorize Claude Code (plugin:ololand-dd:ololand)" OAuth dialog — DO NOT rely on it. That OAuth loopback flow regularly fails in Cowork/desktop: after the user approves, the browser redirect to http://localhost:<port>/callback never returns to Claude, and a manual paste then reports "expired".

If the user asks about OloLand, setup, authentication, or hits a 401, immediately tell them to use the agent key instead of OAuth:
  1. Visit https://api.ololand.ai/connect
  2. Sign in with email or Google, then click "Generate new key" (it starts with `olo_agent_sk_`)
  3. Add to the shell that launches Claude Code:  export OLOLAND_AGENT_KEY=olo_agent_sk_...
  4. Reload the shell and restart Claude Code
The /setup skill contains the full walkthrough and troubleshooting.
CTX
exit 0
