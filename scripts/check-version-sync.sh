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
# Restrict README validation to the intended marketplace table. Other plugin
# links elsewhere in the README are documentation and must not count.
section_match = re.search(
    r"(?ms)^## Plugins in this marketplace\s*$\n(.*?)(?=^## |\Z)", text
)
if section_match is None:
    print("missing README section: Plugins in this marketplace")
    raise SystemExit
table_text = section_match.group(1)
# Match the same SemVer subset accepted by generate-plugin-artifacts.py,
# including prerelease and build metadata (for example, 1.2.0-rc.1).
version = r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][0-9A-Za-z.-]+)?"
row_re = re.compile(rf"^\|\s*\[`([a-z0-9-]+)`\]\([^)]*\)\s*\|\s*v({version})\s*\|", re.MULTILINE)
candidate_re = re.compile(r"^\|\s*\[`([a-z0-9-]+)`\]\([^)]*\)\s*\|", re.MULTILINE)
readme_versions = {}
known_names = set(versions)
for match in candidate_re.finditer(table_text):
    name = match.group(1)
    if name in known_names:
        parsed = row_re.match(table_text, match.start())
        if not parsed:
            print(f"unparseable version row: {name} README.md (expected v{version})")
        else:
            readme_versions.setdefault(name, []).append(parsed.group(2))

for name, mp_version in versions.items():
    readme_rows = readme_versions.get(name, [])
    if not readme_rows:
        print(f"missing plugin row: {name} README.md marketplace table")
    elif len(readme_rows) > 1:
        print(f"duplicate plugin rows: {name} README.md marketplace table ({len(readme_rows)})")
    elif readme_rows[0] != mp_version:
        print(f"version drift: {name} README.md=v{readme_rows[0]} marketplace.json={mp_version}")
' "$marketplace_json" "$readme")"

  if [ -n "$readme_drift" ]; then
    echo "$readme_drift" >&2
    drift=1
  fi
fi

cursor_marketplace="$repo_root/.cursor-plugin/marketplace.json"
if [ -f "$cursor_marketplace" ]; then
  cursor_drift="$(python3 -c '
import json, os, sys

claude_path, cursor_path, repo_root = sys.argv[1], sys.argv[2], sys.argv[3]
claude = json.load(open(claude_path))
cursor = json.load(open(cursor_path))
claude_names = [p["name"] for p in claude["plugins"]]
cursor_names = [p["name"] for p in cursor["plugins"]]
if claude_names != cursor_names:
    print(f"plugin list drift: claude={claude_names} cursor={cursor_names}")
for entry in cursor["plugins"]:
    source = os.path.normpath(os.path.join(repo_root, entry["source"]))
    cursor_plugin = os.path.join(source, ".cursor-plugin", "plugin.json")
    claude_plugin = os.path.join(source, ".claude-plugin", "plugin.json")
    if not os.path.isfile(cursor_plugin):
        print(f"missing Cursor manifest: {entry['name']} {cursor_plugin}")
        continue
    cursor_manifest = json.load(open(cursor_plugin))
    if cursor_manifest.get("name") != entry["name"]:
        print(f"name drift: marketplace {entry['name']} cursor plugin.json={cursor_manifest.get('name')}")
    if os.path.isfile(claude_plugin):
        claude_version = json.load(open(claude_plugin))["version"]
        if cursor_manifest.get("version") != claude_version:
            print(f"version drift: {entry['name']} cursor={cursor_manifest.get('version')} claude={claude_version}")
' "$marketplace_json" "$cursor_marketplace" "$repo_root")"
  if [ -n "$cursor_drift" ]; then
    echo "$cursor_drift" >&2
    drift=1
  fi
fi

if [ "$drift" -ne 0 ]; then
  echo "update marketplace.json, each plugin's plugin.json, and the root README's plugin table to agree before committing." >&2
  exit 1
fi
