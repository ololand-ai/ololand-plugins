#!/usr/bin/env python3
"""Export a separate portable OpenAI upload without changing Claude source."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from zipfile import ZIP_DEFLATED, ZipFile
from urllib.parse import urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True

# These canonical workflows remain available to their original host. An
# OpenAI upload must not relabel a write with another host's provenance.
UNSUPPORTED_COMMANDS = {
    "ololand-dd": {
        "dd-correct": {
            "workflow_id": "ololand-dd/commands/dd-correct.md",
            "skill_id": "ololand-dd-dd-correct",
            "status": "unsupported",
            "reason_code": "cowork_provenance_only",
            "reason": "submit_agent_claim_correction always stamps surface=cowork; an OpenAI correction would have incorrect provenance.",
            "action": "Do not invoke submit_agent_claim_correction from OpenAI. Explain the limitation and retain proposed correction text for human review without claiming it was submitted.",
        },
    },
}
UNSUPPORTED_CORRECTION_NOTICE = "unsupported OpenAI claim-correction workflow (see unsupported-workflows.json)"


def neutral_text(text: str) -> str:
    """Normalize complete provider phrases before their component words."""
    text = text.replace("Project Atlas Claude memo", "Project Atlas memo")
    text = text.replace("Claude Cowork", "your assistant")
    text = text.replace("Claude Code", "your assistant")
    text = text.replace("Claude Desktop", "your assistant")
    text = text.replace("Claude Platform", "OloLand's hosted agent service")
    text = text.replace("Claude\nPlatform", "OloLand's hosted agent service")
    text = text.replace("Claude Dispatch", "supported voice interfaces")
    text = text.replace("Claude Channels", "supported messaging interfaces")
    text = text.replace("claude_platform_session_id", "hosted-session identifier returned by the tool")
    text = text.replace("Cowork", "your assistant")
    text = text.replace("Claude", "the assistant")
    return re.sub(r"\bmcp__ololand__([a-zA-Z0-9_]+)\b", r"\1", text)


def validate_package(package: Path) -> None:
    """Fail closed on accidental local bindings, credentials, or dependencies."""
    for path in package.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlinks are not allowed")
        relative = path.relative_to(package)
        if "hooks" in relative.parts or path.name in {".app.json", "app.json", ".env", ".mcp.json"}:
            raise ValueError(f"Unsupported private/local component: {relative}")
        if path.is_file() and path.suffix in {".md", ".json", ".yaml", ".yml", ".csv", ".txt"}:
            text = path.read_text()
            if re.search(r"olo_agent_sk_[A-Za-z0-9_-]{12,}|Bearer\s+[A-Za-z0-9_-]{20,}", text):
                raise ValueError(f"Credential material is not allowed: {relative}")
            if re.search(r"CLAUDE_PLUGIN_ROOT|\.claude/|\bmcp__ololand__|/cmd-[a-z0-9-]+|\.\./\.\./commands/", text):
                raise ValueError(f"Unportable dependency: {relative}")


SETUP_BODY = """# Connect OloLand

This is an explicit, user-invoked setup workflow. Enable the packaged `ololand`
MCP connection, complete the client's OAuth sign-in, and inspect the tools
actually available to the connected account. If authentication fails, ask the
user to reconnect. Never request, print, or store account credentials in chat.
Do not run local setup scripts or claim a session-start hook has run.
Resolve a requested deal using the connected server; do not assume a sample
deal or entitlement exists. Report connection or permission gaps explicitly.

OpenAI cannot execute this plugin's local lifecycle hooks. The upload supplies
an explicit workflow, not an automatic setup gate. Server-side MCP auditing
remains authoritative. Preserve tool-returned evidence and permission blockers;
IC approval and other human-only gates stay with authorized people in OloLand.
"""

COMPLIANCE_BODY = """# OloLand compliance review and setup

OpenAI cannot execute local lifecycle hooks. This user-invoked workflow is not
equivalent to automatic MNPI blocking, citation enforcement, local NDJSON
provenance writeback, audit mirroring, capacity warnings, or session banners.
Do not claim those hooks are armed or create a passing compliance attestation.

## Explicit setup

When the user requests setup, enable the packaged `ololand` MCP connection and
complete OAuth using the client's connection settings. Inspect available tools
and permissions; do not request credentials in chat. Explain the limits above
and agree which document or deal the user wants reviewed. This workflow does
not install scripts, write local audit ledgers, or monitor future tool calls.

## Explicit review

1. Confirm the user's authorized scope and whether the material may contain
   material non-public information (MNPI). If authorization is unclear, stop
   the affected action and request an authorized human review. A text marker
   does not establish authorization.
2. Review supplied claims, figures, and citations against accessible source
   documents and returned engine evidence. Preserve document/page references,
   discrepancies, unavailable sources, and unverified claims. Never invent
   citations or turn missing evidence into a pass.
3. For a requested deal review, use only available read tools and their current
   schemas to inspect audit provenance, assumption-control/evidence summaries,
   account limits, and approval blockers. Unavailable tools are limitations,
   not evidence of compliance. Do not invent an audit-write endpoint.
4. Report findings, gaps, source references, tool-returned audit/run identifiers,
   and remaining human decisions. Server-side MCP rail auditing remains
   authoritative for calls handled by that server. This review does not audit
   unrelated client actions or create the local hook ledgers.
5. Retain server-enforced controls and human-only IC approval in the OloLand
   app. Never bypass an evidence blocker, approve on a person's behalf, or
   imply this workflow certifies legal or regulatory compliance.
"""


def portable_adapter(source: Path, metadata: dict) -> str | None:
    """Require a reviewed adapter for the exact local hook source."""
    if not (source / "hooks").exists():
        return None
    adapter = metadata.get("openai", {}).get("portable", {}).get("hooksAdapter", {})
    allowed = {
        "ololand-dd": "explicit-dd-setup-v1",
        "ololand-compliance-hooks": "explicit-compliance-review-v1",
    }
    if not adapter.get("id") or adapter.get("id") != allowed.get(metadata["name"]):
        raise ValueError("Local hooks require a recognized explicit portable hooks adapter")
    hook = source / "hooks" / "hooks.json"
    if not hook.is_file() or hashlib.sha256(hook.read_bytes()).hexdigest() != adapter.get("sourceSha256"):
        raise ValueError("Portable hooks adapter must be reviewed against the current hooks source")
    return adapter["id"]


def portable_roles(source: Path, metadata: dict) -> list[tuple[Path, dict, str]]:
    """Require explicit reviewed portability for every local agent definition."""
    definitions = sorted((source / "agents").glob("*.md"))
    configured = metadata.get("openai", {}).get("portable", {}).get("agentRoles", {})
    if set(configured) != {path.stem for path in definitions}:
        raise ValueError("Every local agent role requires an explicit portable mapping")
    supported = {("ololand-dd", role) for role in
                 ("dd-analyst", "forensic-screener", "war-game-strategist")}
    roles = []
    for path in definitions:
        declaration = configured[path.stem]
        if ((metadata["name"], path.stem) not in supported or
                declaration.get("adapter") != "explicit-role-workflow-v1"):
            raise ValueError("Unknown portable agent role adapter")
        if (path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != declaration.get("sourceSha256")):
            raise ValueError("Portable agent role adapter must be reviewed against the current source")
        front, body = path.read_text().split("---\n", 2)[1:]
        fields = yaml.safe_load(front)
        if fields.get("name") != path.stem:
            raise ValueError("Portable agent role identity must match its source file")
        fields = {"name": f"{metadata['name']}-role-{path.stem}",
                  "description": "Use when the user requests the " + path.stem + " role or equivalent workflow. " + fields["description"]}
        execution = (
            "## Portable role execution\n\n"
            "This is an explicit role workflow skill, not an automatically registered local agent. "
            "When the host lacks authorized delegation, execute the steps sequentially yourself. "
            "Do not claim subagents, parallel work, or independent reviews ran when they did not. "
            "If authorized delegation is available, scope each delegated read task and retain control "
            "of tool writes and simulation limits. Routing to this role alone does not authorize "
            "writes or simulations; preserve the execution authority and human approval gates below. "
            "Use only current connected tool schemas and report returned evidence, identities, and gaps.\n\n"
        )
        if path.stem == "forensic-screener":
            start = body.find("### Compliance Hooks")
            end = body.find("\n## Workflow", start)
            if start < 0 or end < 0:
                raise ValueError("Forensic role portable citation boundary missing")
            body = body[:start] + (
                "### Citation and evidence review\n\n"
                "OpenAI cannot execute local lifecycle hooks. Cite every numeric claim with "
                "actual source references; review missing citations explicitly. This skill does "
                "not automatically warn or deny unrelated tool actions. Server-side MCP auditing "
                "and human approval gates remain in OloLand.\n"
            ) + body[end:]
            body = body.replace("The compliance hooks will warn on unsourced numbers.",
                                "Flag unsourced numbers as unverified during this explicit review.")
            execution += (
                "Statistical flags are investigation prompts, not proof of fraud. Classify every "
                "unrun, insufficient-data, unreliable, unsupported, or unavailable primitive as "
                "a gap. Do not promise a complete seven-primitive battery, defensible EBITDA, "
                "precedent counts, fixed cost, or completion timing without returned evidence.\n\n"
            )
        # Promotional narrative is not executable role behavior or live evidence.
        body = body.split("\n## Why this exists", 1)[0]
        roles.append((Path("role-" + path.stem), fields, execution + body))
    return roles


def export(name: str, output: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "generator", ROOT / "scripts/generate-plugin-artifacts.py"
    )
    generator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(generator)
    source = ROOT / "plugins" / name
    metadata = generator.load_yaml(source / "plugin.yaml")
    if metadata["name"] != name:
        raise ValueError("Plugin identity must match its directory")
    adapter = portable_adapter(source, metadata)
    codex = generator.codex_manifest(source, metadata)
    interface = dict(codex["interface"])
    interface.update(metadata.get("openai", {}).get("interface", {}))
    for key in ("displayName", "shortDescription"):
        if not 0 < len(interface[key]) <= 30:
            raise ValueError(f"{key} must contain 1-30 characters")
    for key in ("websiteURL", "supportURL", "privacyPolicyURL", "termsOfServiceURL"):
        if not isinstance(interface.get(key), str) or not interface[key].startswith("https://"):
            raise ValueError(f"{key} must be an explicit HTTPS listing URL")
    extension = {key: value for key, value in codex.get("extensions", {}).get("com.openai", {}).items()
                 if key not in ("interface", "portable")}
    extension["interface"] = interface
    manifest = generator.base_manifest(metadata)
    manifest["homepage"] = interface["websiteURL"]
    manifest["keywords"] = [tag for tag in manifest["keywords"] if tag not in {"claude-cowork", "anthropic-augment"}]
    manifest["description"] = neutral_text(interface["longDescription"])
    manifest["$schema"] = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    manifest["extensions"] = {"com.openai": extension}
    mcp_path = source / ".mcp.json"
    mcp = (json.loads(mcp_path.read_text()) if mcp_path.is_file() else
           {"mcpServers": metadata.get("openai", {}).get("portable", {}).get("mcpServers", {})})
    if set(mcp) - {"mcpServers", "$schema"}:
        raise ValueError("Public MCP files may contain only servers and schema")
    if not mcp.get("mcpServers"):
        raise ValueError("Portable workflows must declare their MCP dependencies")
    mcp["$schema"] = "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json"
    dependencies = []
    for server_name, server in mcp["mcpServers"].items():
        if set(server) - {"type", "url"}:
            raise ValueError("Public MCP connections may contain only transport and URL; no credentials or local configuration")
        endpoint = urlsplit(server["url"])
        if endpoint.scheme != "https" or not endpoint.netloc or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
            raise ValueError("Public MCP endpoint must use HTTPS")
        server["type"] = "streamable-http"
        dependencies.append({
            "type": "mcp", "value": server_name,
            "description": f"Connected {metadata['displayName']} tools",
            "transport": "streamable_http", "url": server["url"],
        })
    skills = []
    references = {}
    unsupported = UNSUPPORTED_COMMANDS.get(name, {})
    exclusions = []
    for skill in sorted((source / "skills").iterdir()):
        if not skill.is_dir() or not (skill / "SKILL.md").exists():
            continue
        # Commands are always rendered from canonical source, independent of
        # the local Codex wrapper-generation setting.
        if skill.name.startswith("cmd-") and (source / "commands" / (skill.name[4:] + ".md")).is_file():
            continue
        text = (skill / "SKILL.md").read_text()
        front, body = text.split("---\n", 2)[1:]
        fields = yaml.safe_load(front)
        skills.append((skill, fields, body))
        if skill.name.startswith("cmd-"):
            references[f"/{skill.name}"] = fields["name"]
            references[f"/{skill.name.removeprefix('cmd-')}"] = fields["name"]
    for command in sorted((source / "commands").glob("*.md")):
        if command.stem in unsupported:
            exclusions.append(unsupported[command.stem])
            for reference in (f"/cmd-{command.stem}", f"/{command.stem}", f"/{name}:{command.stem}", f"../../commands/{command.name}"):
                references[reference] = UNSUPPORTED_CORRECTION_NOTICE
            continue
        text = generator.command_skill_text(metadata, command)
        front, body = text.split("---\n", 2)[1:]
        fields = yaml.safe_load(front)
        skills.append((Path("cmd-" + command.stem), fields, body))
        for reference in (f"/cmd-{command.stem}", f"/{command.stem}", f"/{name}:{command.stem}", f"../../commands/{command.name}"):
            references[reference] = fields["name"]
    for role, fields, body in portable_roles(source, metadata):
        skills.append((role, fields, body))
        role_name = role.name.removeprefix("role-")
        for reference in ("@" + role_name, f"../../agents/{role_name}.md", f"agents/{role_name}.md"):
            references[reference] = fields["name"]
    required_adapter_skill = {
        "explicit-dd-setup-v1": "setup",
        "explicit-compliance-review-v1": "compliance-hooks-setup",
    }.get(adapter)
    if required_adapter_skill and required_adapter_skill not in {skill.name for skill, _, _ in skills}:
        raise ValueError("Portable hooks adapter is missing its explicit setup/review skill")
    command_pattern = (
        # Command syntax starts a token in prose/code, not a URL segment
        # after a placeholder or a Markdown link destination. A following
        # slash also identifies a path rather than a complete command.
        re.compile(r"(?<![^\s`])(?:" + "|".join(
            re.escape(key) for key in sorted(references, key=len, reverse=True)
        ) + r")(?![\w/-])")
        if references else None
    )
    with tempfile.TemporaryDirectory(prefix="ololand-openai-") as temp:
        package = Path(temp) / name
        package.mkdir()
        for skill, fields, body in skills:
            if fields["name"] in {item["skill_id"] for item in exclusions}:
                continue
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"]):
                raise ValueError("Portable skill names must be safe kebab-case paths")
            destination = package / "skills" / fields["name"]
            if destination.exists():
                raise ValueError("Duplicate skill name")
            if skill.is_dir():
                if skill.is_symlink() or any(path.is_symlink() for path in skill.rglob("*")):
                    raise ValueError("Symlinks are not allowed")
                shutil.copytree(skill, destination)
            else:
                destination.mkdir(parents=True)
            if adapter == "explicit-dd-setup-v1" and skill.name == "setup":
                body = SETUP_BODY
                fields["description"] = "Connect OloLand and review available deal tools when the user requests setup or has a connection error."
            elif adapter == "explicit-compliance-review-v1" and skill.name == "compliance-hooks-setup":
                body = COMPLIANCE_BODY
                fields["description"] = "Use when the user requests OloLand compliance review or setup: review citations, provenance, MNPI authorization, and human approval gaps."
            # Keep provider-specific implementation in the original source.
            body = body.replace("<!-- Generated by scripts/generate-plugin-artifacts.py; do not edit. -->\n", "")
            body = body.replace("# Codex wrapper for /", "# Workflow for /")
            body = body.replace("or the equivalent workflow in Codex", "or the equivalent workflow")
            body = neutral_text(body)
            fields["description"] = neutral_text(fields["description"])
            if exclusions:
                # Informational tool links in memory/audit skills must not route
                # back to the excluded write through a different workflow.
                body = body.replace("submit_agent_claim_correction", UNSUPPORTED_CORRECTION_NOTICE)
                fields["description"] = fields["description"].replace("submit_agent_claim_correction", UNSUPPORTED_CORRECTION_NOTICE)
            if name == "ololand-dd" and skill.name == "welcome":
                fields["description"] = "Orient the user to available OloLand tools when requested after connection."
                body = body.replace("44 tools for institutional-grade due diligence", "available tools for due diligence")
                body = body.replace("A sample deal (Paragon Flight School) is loaded in your workspace.", "Resolve Paragon Flight School through available tools if the user wants to explore a sample; do not assume it exists in this workspace.")
            body = body.replace("the assistant will render it inline as an interactive iframe. No further action is required from you; acknowledge briefly and stop.",
                                "show the interactive view only if the client supports it. Otherwise explain that display limitation and summarize only data actually returned by the tool.")
            if name == "ololand-forensic-qoe" and skill.name == "forensic-qoe":
                body = body.replace(
                    "This output shape is what the `/cmd-forensic-screen` and `/cmd-dd-analyze` commands aggregate into a Pre-LOI Screen and full Forensic QoE respectively.",
                    "Use the packaged `ololand-forensic-qoe-forensic-screen` workflow to summarize only results actually returned by the service. This upload does not include the general due-diligence workflow; request that separate plugin if needed.",
                )
            if command_pattern:
                body = command_pattern.sub(lambda match: references[match.group()], body)
                fields["description"] = command_pattern.sub(
                    lambda match: references[match.group()], fields["description"]
                )
            if re.search(r"/cmd-[a-z0-9-]+", body + fields["description"]):
                raise ValueError(f"Unpackaged command reference in {skill.name}")
            if "../../commands/" in body or "CLAUDE_PLUGIN_ROOT" in body:
                raise ValueError(f"Unpackaged local dependency in {skill.name}")
            if name == "ololand-forensic-qoe" and skill.name == "cmd-forensic-screen":
                start = body.find("## When the user wants the PDF deliverable")
                end = body.find("\n## When the user wants human verification", start)
                if start < 0 or end < 0:
                    raise ValueError("PDF workflow boundary missing")
                body = body[:start] + (
                    "## When the user wants the PDF deliverable\n\n"
                    "PDF generation is a separate metered action. The service's published MCP "
                    "pricing identifies `generate_forensic_screen_pdf` as **50 service credits**. "
                    "Confirm the current cost, available quota, and account entitlement in OloLand "
                    "before execution; if they cannot be verified, stop and request that verification.\n\n"
                    "1. Check whether `generate_forensic_screen_pdf` is actually available to the "
                    "connected account. If unavailable, explain the access limitation.\n"
                    "2. Disclose the verified cost and obtain the user's explicit confirmation "
                    "to generate the report and consume those service credits. A request for a "
                    "PDF alone does not confirm an undisclosed charge. Do not initiate a purchase "
                    "or payment to obtain credits.\n"
                    "3. Only after that confirmation, invoke the tool using its current schema "
                    "and the resolved deal ID. Use a status tool only if the connected server "
                    "actually exposes it and the result supplies the required job identifier.\n"
                    "4. Report only the status, sections, and download URL returned by the service. "
                    "Do not promise fixed report sections or completion timing.\n"
                ) + body[end:]
            # Drop obsolete pricing and latency promises from the upload copy.
            fields["description"] = re.sub(r" The \$99 / 72-hour SLA.*$", "", fields["description"])
            body = re.sub(r"Returns the full screen in 60-90 seconds[^\n]*", "Report only the completion status and findings actually returned by the service.", body)
            body += "\n\n## OpenAI execution requirements\n\n"
            body += (
                "Use the connected MCP server's current tool schemas. Do not invent tool arguments, "
                "job-status endpoints, inputs, or outputs. If a referenced tool is unavailable, "
                "explain the limitation and request the needed connection or data. Invoke writes "
                "only when the user has requested the corresponding action. Do not initiate purchases "
                "or payments. "
                "An unrun, unsupported, or unavailable procedure is a gap, never a passing result.\n\n"
            )
            if name == "ololand-forensic-qoe":
                body += (
                    "Statistical flags are investigation prompts, not proof of fraud. "
                    "The conversation-level forensic tools and the self-serve PDF report have different "
                    "coverage. The current self-serve Full QoE report supports eligible transaction-level "
                    "Benford, lapping, and journal-entry tests. It does not currently include Beneish, "
                    "EBITDA bridge, full cross-document reconciliation, working-capital normalization, "
                    "or revenue-quality deep dives. Do not promise these sections in a PDF or a signed "
                    "CPA opinion. Preserve the limits returned by each tool.\n"
                )
            if adapter:
                body += ("\nOpenAI cannot execute local lifecycle hooks. Use the packaged explicit setup/review workflow when requested. "
                         "Server-side MCP auditing remains authoritative; preserve evidence blockers and human-only approval gates.\n")
            if exclusions:
                body += ("\nClaim-correction submission is unsupported in this OpenAI upload because the current handler records surface=cowork. "
                         "Do not invoke submit_agent_claim_correction from OpenAI. Explain the limitation and retain proposed correction text "
                         "for human review without claiming submission. See unsupported-workflows.json for the excluded canonical workflow.\n")
            (destination / "SKILL.md").write_text(
                "---\n" + yaml.safe_dump(fields, sort_keys=False).rstrip() + "\n---\n" + body
            )
            agents = destination / "agents"
            agents.mkdir(exist_ok=True)
            (agents / "openai.yaml").write_text(yaml.safe_dump({
                "interface": {
                    "display_name": fields["name"].removeprefix(name + "-").replace("-", " ").title(),
                    "short_description": fields["description"][:200],
                },
                "dependencies": {"tools": dependencies},
            }, sort_keys=False))
        if (source / "assets").exists():
            if (source / "assets").is_symlink() or any(path.is_symlink() for path in (source / "assets").rglob("*")):
                raise ValueError("Symlinks are not allowed")
            shutil.copytree(source / "assets", package / "assets")
        fixtures = ROOT / "docs" / "openai-review-fixtures"
        if name == "ololand-forensic-qoe" and fixtures.is_dir():
            shutil.copytree(fixtures, package / "review-fixtures")
        if adapter:
            (package / "PORTABILITY.md").write_text(
                "OpenAI cannot execute local lifecycle hooks. This upload provides explicit user-invoked "
                "setup/review workflows, not equivalent automatic enforcement or local audit ledgers. "
                "Server-side MCP rail auditing remains authoritative; human approval gates remain in OloLand.\n"
            )
        if exclusions:
            (package / "unsupported-workflows.json").write_text(json.dumps({
                "format_version": 1, "workflows": exclusions,
            }, indent=2) + "\n")
        (package / "mcp.json").write_text(json.dumps(mcp, indent=2) + "\n")
        (package / "plugin.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        shutil.copy2(ROOT / "LICENSE", package / "LICENSE")
        for key in ("logo", "composerIcon"):
            asset = package / interface[key]
            if not asset.is_file() or not asset.resolve().is_relative_to(package.resolve()):
                raise ValueError(f"Missing or unsafe {key}")
        validate_package(package)
        output.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(output, "w", ZIP_DEFLATED) as archive:
            for path in sorted(package.rglob("*")):
                if path.is_symlink():
                    raise ValueError("Symlinks are not allowed")
                if path.is_file():
                    archive.write(path, path.relative_to(package.parent))
    print(output.resolve())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.name):
        parser.error("Use a kebab-case plugin name")
    export(args.name, args.output)
