#!/usr/bin/env bash
# OloLand headless / CI setup — one command instead of hand-editing .mcp.json.
#
# Idempotently adds the OloLand MCP server to an .mcp.json with a Bearer-token
# Authorization header. By default the header references ${OLOLAND_AGENT_KEY}
# rather than the literal key, so the secret stays in the environment and never
# lands on disk. For headless / CI hosts that cannot do an interactive OAuth
# sign-in. Interactive users (Claude Desktop / Cowork) don't need this — just
# connect the OloLand server and sign in.
#
# Get a key at https://api.ololand.ai/connect (sign in -> Generate new key).
#
# Usage:
#   setup_headless.sh [--config PATH] [--key olo_agent_sk_...] [--inline-key]
#
#   --config PATH  Target MCP config (default: ./.mcp.json).
#   --key KEY      Agent key. Defaults to $OLOLAND_AGENT_KEY. Used to validate
#                  + print the export line; the file references the env var
#                  unless --inline-key is set.
#   --inline-key   Write the literal key into the header instead of the
#                  ${OLOLAND_AGENT_KEY} placeholder. Use only on ephemeral CI
#                  that cannot set an env var, and gitignore the config.

set -euo pipefail

MCP_URL="https://api.ololand.ai/mcp"
SERVER_NAME="ololand"
config="./.mcp.json"
key="${OLOLAND_AGENT_KEY:-}"
inline=0

usage() { sed -n '2,22p' "$0" | sed 's/^#\{0,1\} \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --config) config="${2:?--config needs a path}"; shift 2 ;;
    --config=*) config="${1#*=}"; shift ;;
    --key) key="${2:?--key needs a value}"; shift 2 ;;
    --key=*) key="${1#*=}"; shift ;;
    --inline-key) inline=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown argument: $1 (try --help)" >&2; exit 2 ;;
  esac
done

# Validate the key shape when provided — warn, don't hard-fail (keys may evolve).
if [ -n "$key" ] && ! printf '%s' "$key" | grep -q '^olo_agent_sk_'; then
  echo "warning: key does not start with 'olo_agent_sk_' — is this an OloLand agent key?" >&2
fi

if [ "$inline" -eq 1 ] && [ -z "$key" ]; then
  echo "error: --inline-key needs a key (pass --key or set OLOLAND_AGENT_KEY)" >&2
  exit 2
fi

if [ "$inline" -eq 1 ]; then
  auth="Bearer $key"
else
  auth='Bearer ${OLOLAND_AGENT_KEY}'
fi

# Idempotent JSON merge via python3 — preserves any other servers + top-level keys.
CONFIG_PATH="$config" SERVER_NAME="$SERVER_NAME" MCP_URL="$MCP_URL" AUTH="$auth" python3 - <<'PY'
import json
import os
import sys

path = os.environ["CONFIG_PATH"]
name = os.environ["SERVER_NAME"]

data = {}
if os.path.exists(path):
    with open(path) as fh:
        raw = fh.read()
    if raw.strip():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            sys.exit(f"error: {path} is not valid JSON ({exc}); fix or move it first")
    if not isinstance(data, dict):
        sys.exit(f"error: {path} top-level must be a JSON object")

servers = data.setdefault("mcpServers", {})
if not isinstance(servers, dict):
    sys.exit(f"error: {path} 'mcpServers' must be a JSON object")

servers[name] = {
    "type": "http",
    "url": os.environ["MCP_URL"],
    "headers": {"Authorization": os.environ["AUTH"]},
}

os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
with open(path, "w") as fh:
    json.dump(data, fh, indent=2)
    fh.write("\n")
print(f"wrote OloLand MCP server '{name}' -> {path}")
PY

echo
echo "OloLand MCP server configured in: $config"
if [ "$inline" -eq 1 ]; then
  echo "  The agent key is written inline — add '$config' to .gitignore so the secret is not committed."
else
  echo "  The config references \${OLOLAND_AGENT_KEY}; export it where your MCP host runs:"
  if [ -n "$key" ]; then
    echo "    export OLOLAND_AGENT_KEY=$key"
  else
    echo "    export OLOLAND_AGENT_KEY=olo_agent_sk_...   # get one at https://api.ololand.ai/connect"
  fi
fi
echo
echo "Next: restart / reconnect your MCP host (e.g. Claude Code) and run any OloLand command."
