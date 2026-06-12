---
name: document-editing
description: Use when the user asks to edit, correct, fix, update, or redline text inside a deal's documents — a wrong figure, a stale name, a sentence to amend across the data room. Launches an agentic editing session via edit_deal_documents; every edit lands as a pending_approval patch a HUMAN must approve and commit. Covers launch→poll→read, writing deterministic edit instructions, pinning the working set, the approval flow, and what the verifiers will reject.
---

# Document Editing (human-approved patches)

OloLand can edit deal documents agentically — but it never commits anything
itself. An editing agent mounts the relevant documents, makes the edits, and
each accepted edit becomes a `pending_approval` patch that passes four
deterministic verifiers. A human reviews, approves (or rejects) and commits
patches into a new document version. Full provenance: proposer, rationale,
evidence quote, verifier verdicts, approval note, version lineage.

## The flow (launch → poll → read → approve)

1. **Launch**: `edit_deal_documents(deal_id, instruction, file_ids?)` —
   returns a `task_id` immediately. Costs 10 credits. Sessions take
   seconds to a couple of minutes.
2. **Poll**: `check_task_status(task_id)` until completed.
3. **Read**: `list_patches(deal_id, status="pending_approval")` — patches
   are DB-backed and stay readable after the task id expires. Each patch
   carries op, before/after text, evidence, and verifier verdicts.
4. **Approve & commit (HUMAN step)**: in the web app under
   **Deal → Document Edits** (`/deals/<deal_id>/patches`), or via
   `approve_patch(patch_id, note?)` then
   `commit_version(node_id, patch_ids)` (per-node, approved patches only).
   Never auto-approve on the user's behalf — surface the pending patches
   and let the user decide.

## Writing instructions that land deterministically

- **Quote the exact text to change**: `replace "FY2024 revenue of $12.4M"
  with "FY2024 revenue of $12.6M"` beats `fix the revenue figure`.
- **Pin the working set when you know the file**: pass `file_ids` to skip
  retrieval-based candidate discovery — faster and unambiguous.
- **One logical change per instruction.** The editing agent keeps each
  edit inside one paragraph; cross-paragraph rewrites are rejected.
- **Repeated text** (OCR'd forms, boilerplate): the agent uses
  replace-all semantics — each occurrence becomes its own patch; the
  reviewer can approve them individually.

## What gets rejected (and why that's the product)

- Edits without source evidence (P0 `patch_evidence`).
- Edits where the quoted before-text no longer matches the document
  (P0 `patch_before_text_match` — the document changed underneath).
- Cross-paragraph rewrites and table-structure changes (cells are
  editable; pipes/headers are not).

Rejected attempts persist as audit rows — say so rather than retrying
blindly; re-read the patch list and adjust the instruction.

## What this is NOT

- Not committed automatically — `pending_approval` is the terminal state
  of the agent's work; humans own `approve_patch` + `commit_version`.
- Not available when `AGENT_SDK_DOC_EDITING_ENABLED` is off — the tool
  returns a clear disabled message; relay it, do not retry.
- Not for creating new documents — it edits text of existing deal
  documents (PDFs are edited via their extracted text render).
