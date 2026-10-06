#!/usr/bin/env bash
# Fails if generated Claude/Codex plugin artifacts are missing or stale.
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$repo_root/scripts/generate-plugin-artifacts.py" --check
python3 -B -m unittest discover -s "$repo_root/scripts" -p 'test_export_openai_plugin.py' -v
python3 "$repo_root/scripts/check-mcp-tool-refs.py"
python3 "$repo_root/scripts/check-plugin-size.py"
