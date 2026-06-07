---
name: setup
description: Connect your OloLand account to Claude Code. Use when OloLand tools return an authentication error, when the OloLand MCP server won't connect, or when the user mentions "setup", "connect", or "configure".
---

# OloLand Setup

OloLand authenticates via **OAuth (one-click sign-in)** — there is no key to
copy for normal use. The plugin's MCP server is OAuth-native: connecting it
opens a sign-in page at **api.ololand.ai**, you approve, and you're done.

## Connect (interactive — Claude Desktop / Cowork / Claude Code)

1. Enable / connect the **ololand** MCP server in your client's connectors or
   plugin settings.
2. Claude opens the OloLand sign-in page at **https://api.ololand.ai** — sign
   in with email or Google and click **Approve**.
3. That's it. Try any OloLand command:
   - `/dd-analyze` — Run full due diligence on a deal
   - `/similar-deals` — Find comparable transactions

If you see OloLand tools in your tools list, you're connected.

> The sign-in runs on a single canonical host and self-heals the browser
> handoff, so it works in Cowork and Desktop. If a sign-in window doesn't
> return on the first try, just reconnect the server and approve again.

## Headless / CI (no browser)

Automated environments can't do an interactive sign-in, so they use a
long-lived **agent key** as a Bearer token instead:

1. Visit **https://api.ololand.ai/connect**, sign in, and click **Generate
   new key** (starts with `olo_agent_sk_`).
2. Export it in the environment that launches your MCP host:
   ```bash
   export OLOLAND_AGENT_KEY=olo_agent_sk_...
   ```
3. Point your MCP host at the OloLand server **with an Authorization header**
   (the published plugin manifest is OAuth-native and does not send one, so
   add it in your own config):
   ```json
   {
     "mcpServers": {
       "ololand": {
         "type": "http",
         "url": "https://api.ololand.ai/mcp",
         "headers": { "Authorization": "Bearer ${OLOLAND_AGENT_KEY}" }
       }
     }
   }
   ```

The agent key works in every MCP host and never expires until you revoke it.

## Troubleshooting

- **"Authentication required" / 401**: the OloLand server isn't connected yet.
  Reconnect it and complete the OAuth sign-in (interactive), or check your
  `OLOLAND_AGENT_KEY` + Authorization header (headless).
- **Sign-in window didn't return**: reconnect the server and approve again —
  the handoff is self-healing and the second attempt typically completes. If
  it still stalls, generate an agent key (see Headless / CI) and use that.
- **"Rate limit exceeded"**: Free tier allows 10 requests/minute. Contact
  sales@ololand.ai to upgrade.
- **MCP server unreachable**: check https://status.ololand.ai or try again in
  60 seconds (Cloud Run cold start).
