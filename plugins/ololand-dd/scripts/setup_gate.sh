#!/usr/bin/env bash
# OloLand DD setup gate — SessionStart hook.
#
# As of plugin v1.15.0 the MCP server is declared OAuth-native: .mcp.json
# carries NO static Authorization header, so connecting goes straight to an
# OAuth 2.1 sign-in (one click in Claude Desktop / Cowork). The OloLand auth
# server runs on a single canonical host (api.ololand.ai) and self-heals the
# loopback handoff, so the old "Authorize Claude Code" popup that stranded
# Cowork users is fixed.
#
# Because there is no static header anymore, OLOLAND_AGENT_KEY is NOT consumed
# by the default connection. The key is only for headless / CI hosts where a
# browser sign-in is impossible AND the user has added their own Authorization
# header to the MCP server config (see the /setup skill).
#
# This gate is a lightweight first-run pointer: it tells the model how OloLand
# authenticates so it can guide the user if tools return 401. Never echo the key.
#
# SessionStart contract: stdout is injected into the conversation as
# additionalContext (Claude reads it); stderr surfaces in the hook transcript.

set -euo pipefail

# Resolve the sibling setup script to an absolute path now: the guidance below
# may be run later from a shell where CLAUDE_PLUGIN_ROOT is not exported, so emit
# a concrete path rather than the ${CLAUDE_PLUGIN_ROOT} placeholder. The context
# heredocs stay single-quoted (keeping ${OLOLAND_AGENT_KEY} literal); the
# @@SETUP_SCRIPT@@ token is substituted afterward.
setup_script="$(cd "$(dirname "$0")" && pwd)/setup_headless.sh"

key="${OLOLAND_AGENT_KEY:-}"

if [ -n "$key" ]; then
  # A key is set — headless/CI intent. It is only used if the user added an
  # Authorization header to their MCP config; the default manifest is OAuth.
  cat <<'CTX' | sed "s#@@SETUP_SCRIPT@@#$setup_script#g"
[ololand-dd] OLOLAND_AGENT_KEY is set. Note: the default OloLand MCP server (.mcp.json) is OAuth-native and does NOT read this env var — it is only used in headless/CI setups where the MCP config sends an `Authorization: Bearer ${OLOLAND_AGENT_KEY}` header. If that header isn't wired up yet, run `@@SETUP_SCRIPT@@` to add it in one command (no hand-editing .mcp.json). For interactive use (Claude Desktop / Cowork), just connect the OloLand server and sign in; no key needed. See the /setup skill.
CTX
  exit 0
fi

# No key — the normal interactive case. OAuth one-click is the path.
cat <<'CTX' | sed "s#@@SETUP_SCRIPT@@#$setup_script#g"
[ololand-dd] OloLand authenticates via OAuth (one-click sign-in). When you connect the OloLand MCP server, Claude opens a sign-in page at api.ololand.ai — sign in with email or Google and approve. No agent key or manual setup is required for interactive use.

If OloLand tools return 401 ("authentication required"), the server simply isn't connected yet: tell the user to connect/enable the OloLand MCP server in their client and complete the sign-in. Headless/CI users (no browser) instead generate an agent key at https://api.ololand.ai/connect, `export OLOLAND_AGENT_KEY=<key>`, then run `@@SETUP_SCRIPT@@` to wire it in one command (see the /setup skill).
CTX
exit 0
