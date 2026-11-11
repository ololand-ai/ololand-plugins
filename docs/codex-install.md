# Install OloLand Plugins for Codex

Date: 2026-05-12

OloLand's plugins (`ololand-dd`, `ololand-forensic-qoe`, `ololand-compliance-hooks`, `cim-generator`) ship to Codex CLI from the same marketplace repo as Claude Code and Claude Cowork. Same plugins, same MCP server, three surfaces.

## Prerequisites

- **Codex CLI installed.** See [openai/codex](https://github.com/openai/codex) for setup.
- **OloLand account** with access to the intended company/workspace and deals.
- A Codex host that supports the OloLand server's OAuth flow. Installation does not grant OloLand access.

## Steps

### 1. Add the OloLand plugin marketplace

```bash
codex plugin marketplace add ololand-ai/ololand-plugins
```

> The Codex marketplace artifacts live on `main` (the default branch), so no `--ref` flag is needed. If you installed during the pre-GA window with `--ref staging`, remove that marketplace source and re-add it without the flag — the `staging` branch is retired and no longer updated.

### 2. Enable the plugins in `~/.codex/config.toml`

```toml
[plugins."ololand-dd@ololand-plugins"]
enabled = true

[plugins."ololand-compliance-hooks@ololand-plugins"]
enabled = true

[plugins."ololand-forensic-qoe@ololand-plugins"]
enabled = true
```

### 3. Connect through OAuth

If the installed plugin already supplies the `ololand` connector, use that connection rather than registering a duplicate. Otherwise, register the canonical endpoint:

```bash
codex mcp add ololand --url https://api.ololand.ai/mcp
```

Start the host-managed OAuth sign-in:

```bash
codex mcp login ololand
```

Complete sign-in on `https://api.ololand.ai` yourself. Review the account, company/workspace, and requested access before approving. Do not paste credentials into chat or copy them from local files or environment variables. If this host cannot complete OAuth, report that limitation and stop dependent work.

### 4. Verify the connection

```bash
codex mcp list
```

Confirm the server uses `https://api.ololand.ai/mcp` and inspect its authentication state. A listed server alone does not prove that sign-in or deal access works; use the read-only smoke test below after sign-in succeeds.

### 5. Restart Codex

Restart Codex or start a new Codex session so the plugins + MCP server are loaded.

## Smoke test

```bash
codex exec "Use the ololand MCP server to list my deals. Return the count and first deal name."
```

Expected: Codex calls `ololand.list_deals` and returns your OloLand deals.

## What you installed

| Plugin | Purpose |
|---|---|
| **`ololand-dd`** | Institutional due diligence + middle-office assumption controls + IC approval gate. 60 commands. Three sub-agents (dd-analyst, forensic-screener, war-game-strategist). |
| **`ololand-forensic-qoe`** | Nine forensic workflows spanning Beneish, Benford, EBITDA bridge, journal-entry testing, lapping, conflict detection, verification, and sourced covenant/cross-default/MAC/MAE clause analysis. Pre-LOI screen and Full QoE are included in OloLand Pro and above, with no per-deal price. |
| **`ololand-compliance-hooks`** | MNPI guard (PreToolUse), citation enforcer (PostToolUse on memo/CIM/dossier), audit log, tier-capacity warning, evidence-quality warning. Drops into Codex's hooks scaffold the same way it drops into Claude's. |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Server is disabled or disconnected | Host configuration or connection is incomplete | Inspect its status and use the host's supported OAuth connection flow when requested by the user |
| `Unauthorized` / `401` | OAuth sign-in is incomplete or no longer valid | Report the gap; the user can restore the connection with `codex mcp login ololand` |
| `403` or company-scope error | Connected account lacks the requested access | Verify the selected company/workspace and deal permissions; do not substitute credentials or expand access |
| Plugin commands not loading | `config.toml` block missing or not in `~/.codex/config.toml` | Re-add the `[plugins."ololand-*@ololand-plugins"]` entries |
| `Could not fetch marketplace` | Marketplace source pinned to the retired `staging` branch | `codex plugin marketplace remove ololand-plugins && codex plugin marketplace add ololand-ai/ololand-plugins` |

## Related

- [Claude Code install](https://www.ololand.ai/connect/claude?method=cli)
- [Claude Cowork install](https://www.ololand.ai/connect/claude?method=cowork)
- [IC memo workflow](./cowork-ic-memo-workflow.md) — works identically across Codex, Claude Code, and Claude Cowork once installed
