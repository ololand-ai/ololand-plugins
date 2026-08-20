#!/usr/bin/env bash
# Fails if any plugin's plugin.json version disagrees with the marketplace.json
# entry for that plugin, or if the root README's "Plugins in this marketplace"
# table disagrees with marketplace.json. Source of truth: each plugin's
# plugin.json.
#
# Iterates every plugin listed in .claude-plugin/marketplace.json. Resolves
# the plugin path from the entry's "source" field (joined with optional
# metadata.pluginRoot for backwards compatibility with the older format).

set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
marketplace_json="$repo_root/.claude-plugin/marketplace.json"

if [ ! -f "$marketplace_json" ]; then
  echo "fatal: marketplace.json not found at $marketplace_json" >&2
  exit 1
fi

drift=0
plugin_count=$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))['plugins']))" "$marketplace_json")

for i in $(seq 0 $((plugin_count - 1))); do
  read -r name source mp_version <<< "$(python3 -c '
import json, os, sys
mp = json.load(open(sys.argv[1]))
plugin_root = mp.get("metadata", {}).get("pluginRoot", ".")
entry = mp["plugins"][int(sys.argv[2])]
joined = os.path.normpath(os.path.join(plugin_root, entry["source"]))
print(entry["name"], joined, entry.get("version", ""))
' "$marketplace_json" "$i")"

  plugin_json="$repo_root/$source/.claude-plugin/plugin.json"
  if [ ! -f "$plugin_json" ]; then
    echo "fatal: $name lists source $source but $plugin_json does not exist" >&2
    drift=1
    continue
  fi

  pkg_version=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['version'])" "$plugin_json")

  if [ "$pkg_version" != "$mp_version" ]; then
    echo "version drift: $name plugin.json=$pkg_version marketplace.json=$mp_version" >&2
    drift=1
  fi
done

readme="$repo_root/README.md"
if [ -f "$readme" ]; then
  readme_drift="$(python3 -c '
import json, re, sys

marketplace_json, readme_path = sys.argv[1], sys.argv[2]
mp = json.load(open(marketplace_json))
versions = {p["name"]: p["version"] for p in mp["plugins"]}

text = open(readme_path, encoding="utf-8").read()
# Match table rows like: | [`ololand-dd`](./plugins/ololand-dd) | v1.23.0 | ... |
row_re = re.compile(r"^\|\s*\[`([a-z0-9-]+)`\]\([^)]*\)\s*\|\s*v([0-9][0-9.]*)\s*\|", re.MULTILINE)
readme_versions = dict(row_re.findall(text))

for name, mp_version in versions.items():
    readme_version = readme_versions.get(name)
    # A plugin need not appear in the README table; only check the ones that do.
    if readme_version is not None and readme_version != mp_version:
        print(f"version drift: {name} README.md=v{readme_version} marketplace.json={mp_version}")
' "$marketplace_json" "$readme")"

  if [ -n "$readme_drift" ]; then
    echo "$readme_drift" >&2
    drift=1
  fi
fi

if [ "$drift" -ne 0 ]; then
  echo "update marketplace.json, each plugin's plugin.json, and the root README's plugin table to agree before committing." >&2
  exit 1
fi
