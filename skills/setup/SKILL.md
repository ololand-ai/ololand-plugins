---
name: ololand-setup
description: Use when the user needs to connect their OloLand account to the Claude Code plugin, when OLOLAND_AGENT_KEY is not set, when any /dd-* command fails with authentication error, or when the user mentions "setup", "connect", "configure", "API key", or "get started" with OloLand.
---

# OloLand Plugin Setup

The OloLand plugin needs an agent key to connect to your account.

## Setup Steps

1. Tell the user: "The OloLand plugin needs to connect to your account. I'll open the setup page."

2. Direct the user to open **https://ololand.ai/connect** in their browser. If the Bash tool is available, offer to open it:
   ```
   open https://ololand.ai/connect
   ```

3. On that page, the user will sign in (or create an account) and receive an agent key starting with `olo_agent_sk_`.

4. Ask the user to paste the key. Once they provide it, instruct them to set it in their environment:
   ```
   export OLOLAND_AGENT_KEY=<their_key>
   ```

5. Verify the connection by calling the `list_deals` MCP tool. If it returns successfully, the connection is working.

6. Based on the result:
   - **If deals exist**: "Connected! You have {count} deals. Try `/dd-analyze {first_deal_id}` to run due diligence, or `/talk-to-deal {first_deal_id} What are the top risks?` for a quick summary."
   - **If no deals**: "Connected! Create your first deal at https://app.ololand.ai, upload documents to the data room, then come back and run `/dd-analyze`."

## Troubleshooting

- If the key doesn't work, ask the user to verify it starts with `olo_agent_sk_`
- If the MCP server is unreachable, check that the user's network allows HTTPS connections to `ma-workbench-api-303576587005.us-central1.run.app`
- The key is shown only once on the connect page. If lost, the user can generate a new one at https://app.ololand.ai under Settings > API Keys.
