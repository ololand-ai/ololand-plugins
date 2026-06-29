#!/usr/bin/env python3
"""Check OloLand MCP tool references in plugin docs against backend tools.

By default this script looks for the sibling app repo at
../olo5/backend/mcp_server.py. In standalone marketplace CI, where the app repo
is not checked out, it skips cleanly. Set OLOLAND_MCP_SERVER_PATH or pass
--backend to enforce against a specific backend checkout.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKEND = REPO_ROOT.parent / "olo5" / "backend" / "mcp_server.py"

MCP_TOOL_DEF_RE = re.compile(
    r"@mcp\.tool\([^)]*\)\s*\ndef\s+([a-zA-Z_][a-zA-Z0-9_]*)\(",
    re.MULTILINE,
)
OLOLAND_QUALIFIED_RE = re.compile(r"mcp__ololand__([a-zA-Z_][a-zA-Z0-9_]*)")
BACKTICK_TOOL_RE = re.compile(r"`([a-z][a-z0-9_]{2,})`")

DOC_PATHS = [
    REPO_ROOT / "README.md",
    *sorted((REPO_ROOT / "plugins").glob("*/README.md")),
    *sorted((REPO_ROOT / "plugins").glob("*/commands/*.md")),
    *sorted((REPO_ROOT / "plugins").glob("*/agents/*.md")),
]

IGNORED_BACKTICKS = {
    "agent_key",
    "agent_runs",
    "agent_spans",
    "annual_platform_cost_cents",
    "artifact_text",
    "company_id",
    "company_scope",
    "created_at",
    "deal_data",
    "deal_id",
    "display_mode",
    "end_date",
    "external_qoe_high_cents",
    "external_qoe_low_cents",
    "findings_scope",
    "forensic_job_id",
    "is_active",
    "match_id",
    "mcp_allowed_deal_id",
    "metadata",
    "override_reason",
    "package_id",
    "purchase_id",
    "source_artifact_id",
    "start_date",
    "task_id",
    "user_id",
    "view_url",
    "watchlist_id",
    "workflow_key",
}


def load_backend_tools(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    return set(MCP_TOOL_DEF_RE.findall(text))


def markdown_section(text: str, heading: str) -> str:
    marker = f"\n{heading}"
    start = text.find(marker)
    if start < 0 and text.startswith(heading):
        start = 0
    if start < 0:
        return ""
    body_start = text.find("\n", start + 1)
    if body_start < 0:
        return ""
    next_heading = text.find("\n## ", body_start + 1)
    if next_heading < 0:
        next_heading = len(text)
    return text[body_start:next_heading]


def bare_tool_refs(path: Path, text: str) -> set[str]:
    """Return bare backticked tool references from MCP inventory sections."""
    rel = path.relative_to(REPO_ROOT)
    refs: set[str] = set()
    if rel.as_posix() == "plugins/ololand-dd/README.md":
        section = markdown_section(text, "## MCP Tools (100+)")
        refs.update(BACKTICK_TOOL_RE.findall(section))
    if "agents" in rel.parts:
        section = markdown_section(text, "## Available MCP Tools")
        for line in section.splitlines():
            if not line.lstrip().startswith("- `"):
                continue
            match = BACKTICK_TOOL_RE.search(line)
            if match:
                refs.add(match.group(1))
    return refs


def referenced_tools(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    refs = set(OLOLAND_QUALIFIED_RE.findall(text))
    for name in bare_tool_refs(path, text):
        if name in IGNORED_BACKTICKS:
            continue
        if name.startswith("mcp__ololand__"):
            continue
        if "_" not in name:
            continue
        refs.add(name)
    return refs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", type=Path, default=None)
    args = parser.parse_args()

    backend = args.backend
    if backend is None:
        import os

        backend = Path(os.environ.get("OLOLAND_MCP_SERVER_PATH", DEFAULT_BACKEND))
    if not backend.exists():
        print(f"skip: backend MCP server not found at {backend}")
        return 0

    backend_tools = load_backend_tools(backend)
    missing: list[tuple[str, str]] = []
    for path in DOC_PATHS:
        if not path.exists():
            continue
        for tool_name in sorted(referenced_tools(path)):
            if tool_name not in backend_tools:
                missing.append((str(path.relative_to(REPO_ROOT)), tool_name))

    if missing:
        print("OloLand MCP tool references missing from backend:", file=sys.stderr)
        for rel_path, tool_name in missing:
            print(f"  {rel_path}: {tool_name}", file=sys.stderr)
        return 1

    print(f"ok: {len(backend_tools)} backend MCP tools checked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
