#!/usr/bin/env bash
# OloLand MNPI Guard — PreToolUse hook
# Reads tool invocation JSON on stdin. Blocks (exit 2) if the tool input
# contains MNPI-suggestive keywords without an explicit allow-marker.
#
# Allow-marker: `# mnpi:cleared` anywhere in tool_input.command or tool_input.content.
# Blocks: ticker-prefixed earnings figures, "material non-public", insider window references.
#
# Block contract (Claude Code hooks, PreToolUse): exit 2 with the reason on
# STDERR and nothing on stdout. On exit 2 Claude Code shows Claude the stderr
# text as the denial reason. Exit 2 is used rather than exit 0 plus
# hookSpecificOutput JSON because it fails closed: a guard that exits 0 with
# malformed JSON lets the tool call through. Do not print JSON on stdout here;
# the earlier top-level {"decision": "deny"} shape is not a valid PreToolUse
# value, so Claude Code discarded it and Claude saw an empty reason.

set -euo pipefail

input="$(cat)"

# Single-pass keyword scan — case-insensitive, fast, no jq dependency required.
# We err on the side of letting through and logging — buy-side DD often quotes
# public earnings legitimately. The block list is intentionally narrow.
patterns='material non-public|insider trading window|MNPI|blackout period|earnings under embargo'

if printf '%s' "$input" | grep -qiE "$patterns"; then
  if printf '%s' "$input" | grep -q '# mnpi:cleared'; then
    # Explicit clearance marker present; allow.
    exit 0
  fi
  echo "OloLand MNPI Guard: tool input references material non-public information patterns without a # mnpi:cleared marker. Add the marker after compliance review, or rephrase to use only public sources." >&2
  exit 2
fi

exit 0
