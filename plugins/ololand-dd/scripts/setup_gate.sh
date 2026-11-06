#!/usr/bin/env bash
# Static OAuth setup guidance; no credential, filesystem, or network access.
# Claude SessionStart accepts plain stdout as additional context.
set -euo pipefail
printf '%s\n' '[ololand-dd] OloLand uses host-managed OAuth at https://api.ololand.ai/mcp. To connect, the user opens the OloLand connector in the host settings and completes sign-in on api.ololand.ai. See the setup skill. Do not read credentials from environment variables or files, request secrets in chat, write auth headers, or approve consent for the user. After connecting, verify the intended account/workspace with an authorized read before running an analysis.'
