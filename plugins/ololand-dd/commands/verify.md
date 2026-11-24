---
description: "Check the figures, factual claims and citations in an artifact (CIM paragraph, IC memo, risk narrative, DCF write-up) against a deal's source documents and deterministic engine runs. Works on OloLand-produced artifacts (four atomic-claim verifiers + citation audit + cross-document reconciliation) AND on externally-drafted artifacts — e.g. a memo written in Claude Cowork — via per-claim corpus grading. The 'defend every number, cite every source' button."
---

# /verify

You are running OloLand's verifier stack against an artifact and a deal. This is the user-facing surface for the four atomic-claim verifiers that back the "verifiable outputs" guarantee.

## Required inputs

Ask the user for these if missing:

1. **deal_id** — the OloLand deal whose source documents back the verification.
2. **text** — the artifact text to verify. Accept any of:
   - A paragraph or section pasted inline.
   - A path to a local file (read it with your file tool, then pass the contents).
   - The output of a previous OloLand command (e.g., the IC memo body, a CIM section, a risk narrative).

Optional:
- **include_dcf_arithmetic** (default `true`) — also replay the DCF identity checks against the deal's stored `DCFRun`. Set to `false` if the artifact does not reference a DCF.
- **audit_markers** (default `true` when the artifact contains `[N]` markers) — also run `check_citation_coverage` to audit the `[N]` markers.

## OloLand-produced artifacts

For drafts written outside OloLand, use the external workflow below. For artifacts produced by OloLand, follow these steps.

1. Call `mcp__ololand__run_atomic_verifiers` with `deal_id`, `text`, and `include_dcf_arithmetic`.
2. If the artifact contains any `[N]` markers, also call `mcp__ololand__check_citation_coverage` with the same `deal_id` and `text`. (Detect with a quick regex on the text — `\[\d+\]` excluding `[EK:N]`.)
3. If the user signals this is an IC memo or final report (i.e., wants a full audit, not just a spot-check), also call `mcp__ololand__reconcile_documents` with `deal_id`. This walks the CPA > tax > management > AI source hierarchy across the deal's stored financial observations.

## Externally-drafted artifacts (e.g. written in Claude Cowork)

Use this workflow for an investment memo drafted in ChatGPT, Claude Cowork or another editor. Keep the original memo and the selected deal fixed throughout the review.

1. Inventory every material factual claim in document order, including financial table cells, contract terms and claims embedded in recommendations. Retain its location, entity, period, units, reporting basis and cited page or cell. Track assumptions and investment judgments separately; verify their factual premises and recalculate stated arithmetic when the inputs are available.
2. Call `mcp__ololand__grade_external_artifact` with the original text, `deal_id` and `mode="strict"`. For a memo above the tool's input limit, begin with bounded passages. Use only arguments supported by the connected tool. On `needs_deal`, identify the intended deal. On `needs_corpus`, report the evidence gap. On access denial, stop.
3. Map the returned `figures` and `textual_claims` to the inventory. Keep the claim verdict, reason, source locator and run ID when returned. A timeout has no verdict. A partial, degraded or truncated result can leave omissions even when some rows have verdicts.
4. Continue with just the unassessed claims, in order, in passages of one to three related claims using the same tool and deal. Copy the original wording. Include the heading and definitions needed to interpret each passage. For a table, include the row label, column headers, units, period, footnotes and matching source references. Resolve citation markers to the memo's bibliography. Track repeated context once. If a passage times out, narrow it to a single claim. Record persistent failures as unassessed and move on. If successive single-claim calls remain unavailable, report the remaining inventory as unassessed and give the next claim location for resuming. Respect any explicit call or cost limit.
5. For a disputed result, read the cited source row or clause using the available document tools. Compare the metric, entity, period, units and rounding. Report an independently reproduced calculation or source-supported disagreement alongside the original tool verdict. Keep missing or conflicting evidence visible.
6. Reconcile the claim inventory to the results. Give counts for supported, contradicted, unverified and unassessed claims, and identify the remaining assumptions and judgments. Report unresolved source or citation gaps and the relevant run IDs. Mark whole-memo verification **incomplete** while any material claim is unverified, unassessed or disputed, or any material citation remains unchecked. Report confirmed errors even when coverage is incomplete. A passage-level grade applies only to that passage.

## Output for OloLand-produced artifacts

Render a single human-readable verdict block, in this order:

```
Verifier verdict for <deal_id>:
  Inline numbers:      <supported>/<total> supported  [PASS|FAIL]
  Claim chunks:        <supported>/<total> supported  [PASS|FAIL]
  Citation existence:  <valid>/<total> valid          [PASS|FAIL|N/A]
  DCF arithmetic:      <status>                        [PASS|FAIL|N/A]
  [N] markers:         <in_range> in-range,
                       <out_of_range> out-of-range    [PASS|FAIL|N/A]
  Cross-doc reconcile: <reconciled>/<total> metrics   [optional, IC only]

Overall: <PASS|FAIL>
```

Then list up to 10 unsupported numbers and unsupported claims verbatim (the most damaging review-cycle items). For each unsupported number, quote the `raw` field. For each unsupported claim, quote the sentence.

If the artifact is going into IC or a regulator-facing deliverable and the verdict is FAIL, recommend the user:

1. Re-run `mcp__ololand__search_deal_documents` for any unsupported claim to locate the missing source.
2. Fix the citation with an inline `[N]` marker pointing at the retrieved chunk.
3. If a number cannot be sourced, remove the claim or downgrade it to qualitative language.

## When to use this

- Right before submitting an IC memo, CIM, or board-pack section.
- During a partner review when a number "looks off".
- As a pre-commit check on AI-generated risk narratives before they land in `analyst_corrections`.
- Mid-conversation, after any agent finishes generating a deal-bound artifact — `/verify` it against the same deal.
- On a memo or analysis **drafted in Claude Cowork or another tool** — grade it against the deal's data room to turn unsourced prose into source-linked, IC-defensible claims (uses `grade_external_artifact`).

## When NOT to use this

- For a purely subjective opinion with no checkable factual premise.
- For non-deal artifacts (general M&A commentary, market color, methodology notes).
- Pre-ingestion — verifiers need a populated deal corpus to retrieve chunks against. If `citations_available` is 0, ingest documents first.

Companion skill: `verifier-stack` (auto-loads with this command and explains the methodology and the limits of each verifier).
