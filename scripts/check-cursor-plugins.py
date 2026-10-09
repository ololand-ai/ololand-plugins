#!/usr/bin/env python3
"""Validate Cursor / Grok Bot plugin manifests, marketplace, and referenced files.

Checks that every `.cursor-plugin/plugin.json` parses, stays within the published
Cursor plugin schema, every referenced path exists, MCP configs contain no
literal secrets, and every skill has `name` + `description` frontmatter.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "PyYAML is required. Run: python3 -m pip install -r scripts/requirements.txt"
    ) from exc


REPO_ROOT = Path(__file__).resolve().parents[1]
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:[-+][0-9A-Za-z.-]+)?$"
)
PLUGIN_NAME_RE = re.compile(r"^[a-z0-9]([a-z0-9.-]*[a-z0-9])?$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLACEHOLDER_RE = re.compile(r"\$\{[A-Z][A-Z0-9_]*\}")
LITERAL_SECRET_RE = re.compile(
    r"(olo_agent_sk_[A-Za-z0-9_-]{8,}|sk-[A-Za-z0-9]{16,}|Bearer\s+[A-Za-z0-9._-]{16,})",
    re.IGNORECASE,
)
SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|access[_-]?token|secret|password|authorization|bearer)",
    re.IGNORECASE,
)

PLUGIN_ALLOWED_FIELDS = {
    "name",
    "displayName",
    "description",
    "version",
    "minClientVersions",
    "author",
    "publisher",
    "homepage",
    "repository",
    "license",
    "logo",
    "keywords",
    "category",
    "tags",
    "commands",
    "agents",
    "skills",
    "rules",
    "hooks",
    "variables",
    "mcpServers",
}
MARKETPLACE_ALLOWED_FIELDS = {"name", "owner", "metadata", "plugins"}
MARKETPLACE_PLUGIN_ALLOWED = {"name", "source", "description", "minClientVersions"}
AUTHOR_ALLOWED = {"name", "email"}
OWNER_ALLOWED = {"name", "email"}
COMPONENT_FIELDS = ("skills", "commands", "agents", "rules", "hooks", "logo", "mcpServers")


class Findings:
    def __init__(self) -> None:
        self.errors: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def ok(self) -> bool:
        return not self.errors


def load_json(path: Path, findings: Findings) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        findings.error(f"{rel(path)}: file is missing")
    except json.JSONDecodeError as exc:
        findings.error(f"{rel(path)}: invalid JSON ({exc})")
    return None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def parse_frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    metadata = yaml.safe_load(parts[1]) or {}
    return metadata if isinstance(metadata, dict) else None


def is_safe_relative(value: str) -> bool:
    if not value or value.startswith("/") or value.startswith("${"):
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def collect_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        found: list[str] = []
        for item in value:
            found.extend(collect_strings(item))
        return found
    if isinstance(value, dict):
        found: list[str] = []
        for item in value.values():
            found.extend(collect_strings(item))
        return found
    return []


def check_no_literal_secrets(value: Any, path_label: str, findings: Findings) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if SECRET_KEY_RE.search(str(key)) and isinstance(item, str):
                if item and not PLACEHOLDER_RE.search(item):
                    findings.error(
                        f"{path_label}: {key} must use a ${{VAR}} placeholder, not a literal value"
                    )
            check_no_literal_secrets(item, path_label, findings)
        return
    if isinstance(value, list):
        for item in value:
            check_no_literal_secrets(item, path_label, findings)
        return
    if isinstance(value, str) and LITERAL_SECRET_RE.search(value) and not PLACEHOLDER_RE.search(value):
        findings.error(f"{path_label}: literal credential or token is not allowed")


def resolve_manifest_path(plugin_root: Path, raw: str) -> Path:
    return (plugin_root / raw).resolve()


def check_path_inside(plugin_root: Path, raw: str, field: str, findings: Findings) -> Path | None:
    label = f"{rel(plugin_root / '.cursor-plugin' / 'plugin.json')}: {field}"
    if not is_safe_relative(raw):
        findings.error(f"{label} path {raw!r} must be relative and must not contain '..'")
        return None
    path = resolve_manifest_path(plugin_root, raw)
    try:
        path.relative_to(plugin_root.resolve())
    except ValueError:
        findings.error(f"{label} path {raw!r} escapes the plugin directory")
        return None
    if not path.exists():
        findings.error(f"{label} path {raw!r} does not exist")
        return None
    return path


def check_skills(plugin_root: Path, skills_value: Any, findings: Findings) -> None:
    paths = skills_value if isinstance(skills_value, list) else [skills_value]
    for raw in paths:
        if not isinstance(raw, str):
            findings.error(f"{rel(plugin_root)}: skills entries must be strings")
            continue
        skills_dir = check_path_inside(plugin_root, raw, "skills", findings)
        if skills_dir is None:
            continue
        if not skills_dir.is_dir():
            findings.error(f"{rel(plugin_root)}: skills path {raw!r} is not a directory")
            continue
        skill_files = sorted(skills_dir.glob("*/SKILL.md"))
        if not skill_files:
            findings.error(f"{rel(plugin_root)}: skills path {raw!r} has no <skill>/SKILL.md files")
            continue
        for skill_md in skill_files:
            metadata = parse_frontmatter(skill_md)
            if metadata is None:
                findings.error(f"{rel(skill_md)}: missing YAML frontmatter")
                continue
            name = metadata.get("name")
            description = metadata.get("description")
            if not isinstance(name, str) or not name.strip():
                findings.error(f"{rel(skill_md)}: frontmatter name is required")
            elif not SKILL_NAME_RE.match(name):
                findings.error(f"{rel(skill_md)}: frontmatter name {name!r} must be kebab-case")
            if not isinstance(description, str) or not description.strip():
                findings.error(f"{rel(skill_md)}: frontmatter description is required")


def check_markdown_dir(
    plugin_root: Path, raw: str, field: str, findings: Findings, required: tuple[str, ...]
) -> None:
    directory = check_path_inside(plugin_root, raw, field, findings)
    if directory is None:
        return
    if directory.is_file():
        files = [directory]
    elif directory.is_dir():
        files = sorted(
            p
            for p in directory.iterdir()
            if p.is_file() and p.suffix in {".md", ".mdc", ".markdown", ".txt"}
        )
        if not files:
            findings.error(f"{rel(plugin_root)}: {field} path {raw!r} has no markdown files")
            return
    else:
        findings.error(f"{rel(plugin_root)}: {field} path {raw!r} is not a file or directory")
        return
    for path in files:
        metadata = parse_frontmatter(path)
        if metadata is None:
            if field == "commands":
                findings.error(f"{rel(path)}: command is missing YAML frontmatter")
            continue
        for key in required:
            value = metadata.get(key)
            if not isinstance(value, str) or not value.strip():
                findings.error(f"{rel(path)}: {field} frontmatter {key} is required")


def check_mcp_file(path: Path, findings: Findings) -> None:
    data = load_json(path, findings)
    if not isinstance(data, dict):
        if data is not None:
            findings.error(f"{rel(path)}: MCP config must be a JSON object")
        return
    servers = data.get("mcpServers")
    if not isinstance(servers, dict) or not servers:
        findings.error(f"{rel(path)}: mcpServers must be a non-empty object")
        return
    check_no_literal_secrets(data, rel(path), findings)
    for name, server in servers.items():
        if not isinstance(server, dict):
            findings.error(f"{rel(path)}: server {name!r} must be an object")
            continue
        url = server.get("url")
        command = server.get("command")
        if not url and not command:
            findings.error(f"{rel(path)}: server {name!r} needs url or command")
        if isinstance(url, str) and url.startswith("http://"):
            findings.error(f"{rel(path)}: server {name!r} must use HTTPS")


def check_plugin_manifest(plugin_root: Path, expected_name: str, findings: Findings) -> dict[str, Any] | None:
    manifest_path = plugin_root / ".cursor-plugin" / "plugin.json"
    manifest = load_json(manifest_path, findings)
    if not isinstance(manifest, dict):
        return None

    extra = set(manifest) - PLUGIN_ALLOWED_FIELDS
    if extra:
        findings.error(f"{rel(manifest_path)}: unsupported fields {sorted(extra)}")

    name = manifest.get("name")
    if name != expected_name:
        findings.error(f"{rel(manifest_path)}: name {name!r} does not match {expected_name!r}")
    if not isinstance(name, str) or not PLUGIN_NAME_RE.match(name):
        findings.error(f"{rel(manifest_path)}: name must be kebab-case")

    for field in ("displayName", "description", "license", "repository"):
        if not isinstance(manifest.get(field), str) or not str(manifest.get(field)).strip():
            findings.error(f"{rel(manifest_path)}: {field} is required")

    version = manifest.get("version")
    if not isinstance(version, str) or not SEMVER_RE.match(version):
        findings.error(f"{rel(manifest_path)}: version must be semver")

    author = manifest.get("author")
    if not isinstance(author, dict) or not author.get("name"):
        findings.error(f"{rel(manifest_path)}: author.name is required")
    elif set(author) - AUTHOR_ALLOWED:
        findings.error(
            f"{rel(manifest_path)}: author only allows name and email, not {sorted(set(author) - AUTHOR_ALLOWED)}"
        )

    for field in COMPONENT_FIELDS:
        value = manifest.get(field)
        if value is None:
            continue
        if field == "hooks" and isinstance(value, dict):
            continue
        paths = value if isinstance(value, list) else [value]
        if field == "skills":
            check_skills(plugin_root, value, findings)
            continue
        for raw in paths:
            if not isinstance(raw, str):
                findings.error(f"{rel(manifest_path)}: {field} entries must be strings")
                continue
            if field == "commands":
                check_markdown_dir(plugin_root, raw, field, findings, ("description",))
            elif field == "agents":
                check_markdown_dir(plugin_root, raw, field, findings, ("name", "description"))
            elif field == "mcpServers":
                mcp_path = check_path_inside(plugin_root, raw, field, findings)
                if mcp_path is not None:
                    check_mcp_file(mcp_path, findings)
            else:
                check_path_inside(plugin_root, raw, field, findings)

    if (plugin_root / "hooks" / "hooks.json").is_file() and "hooks" not in manifest:
        findings.error(
            f"{rel(manifest_path)}: Claude hooks.json is present; set hooks so Cursor does not auto-discover the Claude file"
        )

    return manifest


def check_marketplace(findings: Findings) -> list[dict[str, Any]]:
    path = REPO_ROOT / ".cursor-plugin" / "marketplace.json"
    marketplace = load_json(path, findings)
    if not isinstance(marketplace, dict):
        return []

    extra = set(marketplace) - MARKETPLACE_ALLOWED_FIELDS
    if extra:
        findings.error(f"{rel(path)}: unsupported fields {sorted(extra)}")
    if not isinstance(marketplace.get("name"), str) or not marketplace["name"]:
        findings.error(f"{rel(path)}: name is required")

    owner = marketplace.get("owner")
    if not isinstance(owner, dict) or not owner.get("name"):
        findings.error(f"{rel(path)}: owner.name is required")
    elif set(owner) - OWNER_ALLOWED:
        findings.error(
            f"{rel(path)}: owner only allows name and email, not {sorted(set(owner) - OWNER_ALLOWED)}"
        )

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        findings.error(f"{rel(path)}: plugins must be a non-empty array")
        return []

    seen: set[str] = set()
    for index, entry in enumerate(plugins):
        label = f"{rel(path)} plugins[{index}]"
        if not isinstance(entry, dict):
            findings.error(f"{label}: must be an object")
            continue
        extra_entry = set(entry) - MARKETPLACE_PLUGIN_ALLOWED
        if extra_entry:
            findings.error(f"{label}: unsupported fields {sorted(extra_entry)}")
        name = entry.get("name")
        source = entry.get("source")
        if not isinstance(name, str) or not PLUGIN_NAME_RE.match(name):
            findings.error(f"{label}: invalid name")
            continue
        if name in seen:
            findings.error(f"{label}: duplicate plugin {name}")
        seen.add(name)
        if not isinstance(source, str) or not is_safe_relative(source):
            findings.error(f"{label}: source must be a relative path without '..'")
            continue
        plugin_root = (REPO_ROOT / source).resolve()
        try:
            plugin_root.relative_to(REPO_ROOT.resolve())
        except ValueError:
            findings.error(f"{label}: source {source!r} escapes the repository")
            continue
        if not plugin_root.is_dir():
            findings.error(f"{label}: source directory {source!r} does not exist")
            continue
        manifest = check_plugin_manifest(plugin_root, name, findings)
        yaml_path = plugin_root / "plugin.yaml"
        if yaml_path.is_file() and manifest:
            metadata = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            if isinstance(metadata, dict) and str(metadata.get("version")) != manifest.get("version"):
                findings.error(
                    f"{rel(plugin_root / '.cursor-plugin' / 'plugin.json')}: version "
                    f"{manifest.get('version')} does not match plugin.yaml {metadata.get('version')}"
                )
    return plugins


def validate(repo_root: Path | None = None) -> list[str]:
    global REPO_ROOT
    if repo_root is not None:
        REPO_ROOT = repo_root
    findings = Findings()
    check_marketplace(findings)
    return findings.errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Cursor / Grok Bot plugin validation failed:", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print("ok: Cursor / Grok Bot plugin manifests and skills are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
