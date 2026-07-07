#!/usr/bin/env python3
"""Fail when a plugin's on-disk footprint approaches the Cowork minimal-mode threshold.

Cowork silently strips large plugins to "minimal mode" (drops commands/,
agents/, .mcp.json; truncates skills/) — observed tripping at a ~468KB
ololand-dd v1.13.1 footprint. This check fails at 430KiB to leave margin,
per docs in olo5: docs/architecture/audits/2026-07-06-part4-upgrade-proposals.md
(Tier 3, item 9) and the CLAUDE.md "minimal mode" failure-mode entry.

Size = sum of file byte sizes under plugins/<name>/ (deterministic across
filesystems, unlike du block counts).
"""

from __future__ import annotations

import sys
from pathlib import Path

BUDGET_BYTES = 430 * 1024


def plugin_size(plugin_dir: Path) -> int:
    # lstat + symlink exclusion: count what actually ships in the plugin dir,
    # never targets outside it.
    return sum(
        p.lstat().st_size
        for p in plugin_dir.rglob("*")
        if p.is_file() and not p.is_symlink()
    )


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    plugins_dir = repo_root / "plugins"
    failures = []
    plugin_dirs = sorted(
        p for p in plugins_dir.iterdir() if p.is_dir() and (p / "plugin.yaml").is_file()
    )
    for plugin_dir in plugin_dirs:
        size = plugin_size(plugin_dir)
        pct = 100 * size // BUDGET_BYTES
        status = "FAIL" if size > BUDGET_BYTES else "ok"
        print(f"{status:>4}  {size:>8,} bytes  ({pct:>3}% of budget)  {plugin_dir.name}")
        if size > BUDGET_BYTES:
            failures.append(plugin_dir.name)
    if failures:
        print(
            f"\nERROR: plugin(s) over the {BUDGET_BYTES:,}-byte (430KiB) size budget: "
            f"{', '.join(failures)}.\n"
            "Cowork strips oversized plugins to minimal mode (~468KB observed trip). "
            "Shrink the plugin (e.g. codex.generateCommandSkills: false, trim skills) "
            "instead of raising the budget.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
