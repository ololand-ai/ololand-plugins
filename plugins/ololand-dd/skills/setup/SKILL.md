---
name: setup
description: Connect your OloLand account using the host-managed OAuth connection. Use when OloLand tools are unavailable or return an authentication error, or when the user asks to set up the plugin.
---

# OloLand Setup

The bundled connector uses OAuth at **https://api.ololand.ai/mcp**. The host
manages sign-in and the resulting credentials. This plugin does not read keys
from your environment or files, write authentication headers, or provision an
account automatically.

## Connect

1. In the host's plugin settings, open OloLand's **Connectors** tab or the
   equivalent MCP connection settings and choose **Connect** for OloLand.
2. Complete sign-in on **https://api.ololand.ai** using the OloLand account you
   intend to use. Review the requested access and company/workspace context
   shown there before deciding whether to approve.
3. Return to the host. When the OloLand tools are available, use a read such as
   `list_deals` to verify the accessible workspace and deals. Tool visibility
   alone does not prove the intended account or workspace is connected.
4. Run an analysis only when requested and on a deal the user has selected.

The user enters credentials only in OloLand's sign-in page. Do not request
passwords, access tokens, or keys in chat; inspect credential files; or copy
credentials into MCP configuration. Do not approve consent on the user's
behalf. A host without an interactive OAuth connection cannot use this
directory package's authenticated tools.

## Troubleshooting

- **Authentication required / 401:** ask the user to connect or reconnect the
  OloLand connector through the host's settings, then wait for sign-in to finish.
  Retry the requested read once after the user confirms connection.
- **Permission denied / 403:** report the returned access restriction. Verify
  the selected account and workspace through the normal UI; do not change
  grants or assume reconnecting will fix missing permissions.
- **Sign-in does not return to the host:** report the failed connection and
  use [OloLand support](https://github.com/ololand-ai/ololand-plugins/issues).
  Do not fall back to reading local secrets or adding a manual auth header.
- **Tools unavailable in this host:** report the unsupported connection.
  Do not claim a tool ran or that an analysis completed.
- **Rate limit or service error:** preserve the returned message and retry
  guidance. Never create credentials or switch accounts to work around it.

For supported workflows and account prerequisites, see the plugin README.
