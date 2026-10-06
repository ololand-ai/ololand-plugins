# Plugin Publishing

This repository is a dual-target plugin marketplace. Maintainers edit canonical
YAML metadata and plugin implementation files, then generate Claude and Codex
artifacts from the same source of truth.

## Source Of Truth

Edit these files by hand:

- `marketplace.yaml`
- `plugins/*/plugin.yaml`
- `plugins/*/skills/**`
- `plugins/*/commands/**`
- `plugins/*/agents/**`
- `plugins/*/hooks/**`
- `plugins/*/.mcp.json`

Do not hand-edit generated artifacts:

- `.claude-plugin/marketplace.json`
- `.agents/plugins/marketplace.json`
- `plugins/*/.claude-plugin/plugin.json`
- `plugins/*/.codex-plugin/plugin.json`
- `plugins/*/skills/cmd-<command-name>/SKILL.md` files whose body says they were
  generated from Claude slash commands

## Generate Artifacts

Install the generator dependency once:

```bash
python3 -m pip install -r scripts/requirements.txt
```

Regenerate all plugin artifacts:

```bash
python3 scripts/generate-plugin-artifacts.py
```

Check that generated artifacts are current:

```bash
./scripts/check-plugin-artifacts.sh
```

## Release Process

1. Create a release branch from `main`.
2. Update the relevant `plugins/<plugin>/plugin.yaml` version and metadata.
3. Update skills, commands, agents, hooks, or MCP config as needed.
4. Run `python3 scripts/generate-plugin-artifacts.py`.
5. Run `./scripts/check-plugin-artifacts.sh` and `./scripts/check-version-sync.sh`.
6. Open a PR including both source changes and generated artifacts.
7. Merge after GitHub Actions passes.
8. Tag the release, using either a plugin tag or marketplace tag:

```bash
git tag ololand-dd-v1.6.2
git push origin ololand-dd-v1.6.2
```

or:

```bash
git tag marketplace-v2026.05.12
git push origin marketplace-v2026.05.12
```

Pushing either tag pattern runs `.github/workflows/release.yml`, verifies the
generated artifacts again, and creates a GitHub Release with generated notes.

## Codex Compatibility

The generator writes Codex-compatible manifests at
`plugins/*/.codex-plugin/plugin.json` and a Codex marketplace at
`.agents/plugins/marketplace.json`.

Codex-specific plugin presentation metadata comes from each plugin's
`plugin.yaml` fields:

- `displayName`
- `shortDescription`
- `capabilities`
- `defaultPrompt`
- `interface`

The generator automatically includes Codex component paths when they exist:

- `skills` when `skills/*/SKILL.md` exists
- `hooks` when `hooks/hooks.json` exists
- `mcpServers` when `.mcp.json` exists
- `apps` when `.app.json` exists

Claude slash commands under `commands/*.md` are converted into generated Codex
skill wrappers under `skills/cmd-<command-name>/SKILL.md`. If a hand-written
skill already exists at that path, the generator fails instead of overwriting
it. Set `codex.generateCommandSkills: false` in a plugin's `plugin.yaml` to opt
out.

Claude sub-agent definitions remain in their existing folders. If Codex needs
equivalent behavior, add native Codex skills under `skills/` and regenerate
artifacts.

## Portable OpenAI Draft Uploads

Keep local Claude/Codex sources and private `.app.json` bindings in place.
Export a separate public ZIP for each plugin; the exporter does not modify
the source or include local hooks, scripts, or private application bindings:

```bash
python3 scripts/export-openai-plugin.py ololand-dd --output ../artifacts/ololand-dd-openai-draft.zip
python3 scripts/export-openai-plugin.py ololand-forensic-qoe --output ../artifacts/ololand-forensic-qoe-openai-draft.zip
python3 scripts/export-openai-plugin.py ololand-compliance-hooks --output ../artifacts/ololand-compliance-hooks-openai-draft.zip
python3 scripts/export-openai-plugin.py cim-generator --output ../artifacts/cim-generator-openai-draft.zip
python3 -m unittest discover -s scripts -p 'test_export_openai_plugin.py' -v
```

Each upload includes a workflow skill for every compatible `commands/*.md`, even when
`codex.generateCommandSkills` is false. Commands are rendered from canonical
Markdown directly into the temporary export; generated local wrappers are not
required. References to local commands are translated to packaged workflow
names. Forensic review fixtures and existing draft cases remain scoped to the
Forensic package, along with its PDF cost-confirmation and coverage limits.

Incompatible workflows are disclosed in the exported
`unsupported-workflows.json` with canonical workflow ID, omitted skill ID,
status, reason, and permitted next action. The OpenAI DD upload excludes
`ololand-dd/commands/dd-correct.md` (`ololand-dd-dd-correct`): its current
`submit_agent_claim_correction` handler always records `surface=cowork`, so an
OpenAI invocation would have incorrect provenance. The canonical command and
any local wrappers remain unchanged. Exported cross-references explain the
unsupported workflow, and DD skills explicitly prohibit invoking that handler
from OpenAI or claiming a correction was submitted. This upload contains 52 of
the 53 DD command workflows; the exclusion is not a completed or portable write.

Every local `agents/*.md` role also requires an explicit entry in
`openai.portable.agentRoles`, with `adapter: explicit-role-workflow-v1` and the
SHA-256 `sourceSha256` of that role's Markdown source. The reviewed DD analyst,
forensic screener, and war-game strategist roles export as distinct role skills.
They preserve bounded execution authority, evidence controls, and human gates.
When the host lacks authorized delegation, the assistant follows the role's
steps sequentially and must not claim independent agents ran. Local model
selectors are not copied. Missing, unknown, changed, or new unmapped roles fail
closed rather than silently disappearing from an upload.

OpenAI listing overrides belong in `openai.interface` in canonical YAML. Supply
`shortDescription` (at most 30 characters), a supported display name, accurate
`longDescription`, HTTPS website/support/privacy/terms URLs, and real package
paths for `logo` and `composerIcon`. All four packages reuse the existing
OloLand icon. Metadata under `openai.portable` describes export adapters and
is not published as an OpenAI manifest extension.
Override `defaultPrompt` here when the original host's starter actions are
unavailable in OpenAI. Compliance starters request explicit review, connection
setup, and read-only evidence review; the original local-hook starters remain
unchanged in canonical host metadata.

A source with `hooks/` must declare a recognized
`openai.portable.hooksAdapter` with its adapter `id` and the SHA-256
`sourceSha256` of `hooks/hooks.json`, plus `sourceFilesSha256`, a complete map of
plugin-relative paths to hashes for that manifest and every file in the local
`scripts/` tree. This covers direct implementations and local helper scripts:
DD includes both `setup_gate.sh` and its referenced `setup_headless.sh`;
Compliance includes all seven implementation scripts. DD uses `explicit-dd-setup-v1`;
Compliance uses `explicit-compliance-review-v1`. Missing/unknown adapters or a
changed manifest, changed/added implementation, incomplete map, or missing hook
tree fails closed. Symlinked manifests, scripts, directories, and command
sources are rejected before their redirected contents are read. The hook
manifest parser accepts only reviewed local bash invocations and the exact
existing guarded banner/setup forms; outside/traversal/dynamic paths, injected
shell commands, and unknown invocation forms are rejected without execution.
Review the changed source and its portable
limitations before updating that declaration; do not simply refresh the hash
to bypass the check. The hashes verify reviewed bytes, not the security or
behavioral equivalence of arbitrary shell code. Security review remains
necessary when implementation or dependencies change. A source without `.mcp.json` can declare its public HTTPS
connection under `openai.portable.mcpServers`; Compliance does so explicitly.

OpenAI cannot execute local lifecycle hooks. The DD adapter provides explicit
connection setup. The Compliance adapter provides **user-invoked** setup and
document/deal review. It cannot automatically block arbitrary client or other
application tools, enforce citations across sessions, mirror local audit logs,
write local provenance ledgers, or claim the local hooks are armed. These
workflows are not equivalent to automatic hook enforcement. Server-side MCP
rail auditing remains authoritative for calls handled by that server; evidence
blockers and human-only approval gates remain in OloLand.

The offline tests inspect the actual archives, account for every command as
packaged or explicitly unsupported, confirm portable MCP dependencies, verify binding/credential exclusion,
exercise fail-closed adapters, check source preservation, and validate each
listing's five positive and three negative draft cases and required string
fields. DD's cases cover baseline reads, an explicit model candidate, the Full
DD role, IC readiness/human handoff, and source-backed draft verification.
CIM's cases cover complete and selected reads, missing/in-progress states, and
explicit generation. Compliance's cases cover supplied-material review,
citations, MNPI authorization scope, assumption evidence, and reconnection;
manual review cases do not falsely require or claim an MCP invocation.
Descriptions identify reviewer data/access prerequisites. They do not
execute live reviewer scenarios or establish portal readiness. Keep these ZIPs
as drafts until authorized live review, reviewer access, authentic demo
recordings, and submission prerequisites are completed. Do not invent demo
URLs or mark unrun review cases as passed.
Omit publication country selections until the actual authorized choices are
known. Preserve previously settled selections: Forensic retains its existing
`countries: []` declaration for all supported countries. DD, CIM, and Compliance
omit the field because their publication selections have not been provided.

`check-plugin-artifacts.sh` runs the exporter unittest suite after checking
generated metadata. Both pull-request artifact CI and tagged release CI use
that shared script, so an exporter regression blocks either path. The suite
also checks that its failure propagates through the script.
