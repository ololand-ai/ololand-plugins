#!/usr/bin/env bash
# OloLand Provenance Writeback — PostToolUse hook
# Writes a JSON line to the local provenance ledger after each generative tool
# call (CIM, IC memo, dossier export). The ledger is intentionally local;
# OloLand's MCP rail owns server-side tool-call auditing.
#
# Schema per ledger line:
#   {"ts": ISO8601, "tool": str, "deal_id": str|null, "user": str, "session": str}
#
# This is the local provenance layer Anthropic's empty hooks/ leaves to vendors.

set -euo pipefail

input="$(cat)"

ledger_dir="${HOME}/.ololand/provenance"
mkdir -p "$ledger_dir"
ledger="${ledger_dir}/$(date -u +%Y-%m-%d).ndjson"

ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
tool="$(printf '%s' "$input" | grep -oE '"tool_name"\s*:\s*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || echo unknown)"
deal_id="$(printf '%s' "$input" | grep -oE '"deal_id"\s*:\s*"[^"]*"' | head -1 | sed 's/.*"\([^"]*\)"$/\1/' || echo "")"
user="${USER:-unknown}"
session="${CLAUDE_SESSION_ID:-${TERM_SESSION_ID:-local}}"

printf '{"ts":"%s","tool":"%s","deal_id":"%s","user":"%s","session":"%s"}\n' \
  "$ts" "$tool" "$deal_id" "$user" "$session" >> "$ledger"

exit 0
