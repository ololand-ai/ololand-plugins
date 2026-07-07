---
name: cim-generation
description: Use when the user asks to create, generate, or draft a Confidential Information Memorandum (CIM), sell-side memorandum, seller marketing document, or information package for a deal — runs OloLand's 14-section CIM generator instead of drafting one from prose.
---

# CIM Generation Skill

When the user asks for a CIM or sell-side marketing document for a deal, use the deterministic OloLand generator rather than drafting the document yourself from context. The platform assembles sections from reconciled financial snapshots, risk/opportunity insights, and market research so every exhibit is traceable — writing one from scratch in-context would lose that provenance.

## Trigger phrases

- "generate a CIM" / "create a CIM" / "draft a CIM" / "prepare a CIM"
- "confidential information memorandum"
- "seller memorandum" / "sell-side memo"
- "information package" / "offering memorandum"
- "marketing document for the target"
- "CIM for this deal"

## Execution

1. Identify the `deal_id` from the conversation context (current deal, recent mentions, or ask the user).
2. Follow `/cim-generate` (this plugin's command): call `generate_cim(deal_id)`, poll `check_task_status(task_id)`, then report `cim_id`, section count, and the deal workspace link where the user can view, edit, and export the finished document.
3. If the user only wants specific sections, pass them through as the `sections` argument rather than generating all 14.
4. Do not write CIM content directly in the conversation — the tool call is the source of truth, and the finished document lives on the deal, not in chat history.
