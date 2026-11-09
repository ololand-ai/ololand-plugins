---
name: citation-discipline
description: Use when stating any dollar figure, multiple, ratio, or factual claim about a deal — every quantitative claim must cite its source with an inline `[N]` marker pointing at the retrieved chunk. Required for any IC-grade or audit-defensible output.
---

# Citation Discipline

Every dollar figure, percentage, multiple, ratio, name, date, or factual claim about a deal must cite the source.

## Inline citation format — `[N]` markers

When `search_deal_documents` (or any document-retrieval MCP tool) returns evidence, each chunk is prefixed with a stable reference number: `[1] Source: file=10-K.pdf, p.42`, `[2] Source: file=audit.pdf, p.8`, and so on.

After every claim you make in your final answer, write the corresponding returned
`[N]` token. Hosts may render these as links. Preserve the returned locator type:
a converted-text line is not an original PDF page or spreadsheet cell. Only
claim page/cell navigation when the result actually supplies that provenance.

Examples:
- "SigmaTron's revenue declined 18.5% YoY to $304.7M in FY2025 [1]."
- "Auditors flagged a material weakness in revenue recognition [2], and the company has been in covenant default since August 2024 [3, 5]."
- "Combined leverage stands at 5.0x EBITDA [1, 4]."

Use multiple numbers in one bracket — `[1, 4]` — when a single claim is supported by multiple chunks. Order them ascending.

## Rules (hard)

1. **Never invent numbers.** Only cite `[N]` values that actually appeared in a tool result this turn. If you didn't retrieve chunk `[7]`, do not write `[7]`. OloLand-aware runtimes will strip out-of-range markers and log a warning when this happens — the answer looks worse, not better, with stale numbers.
2. **No citation, no figure.** If you cannot cite the source, do not state the number. Say what you searched and what is still missing.
3. **Reconcile conflicts explicitly.** If `[1]` reports $X and `[3]` reports $Y, surface the discrepancy and cite both. Use the `source-hierarchy` skill to decide which one leads.
4. **Computed metrics show the formula and cite each input.** "EBITDA margin = $7.7M ÷ $304.7M = 2.5% [1]" — the inputs come from `[1]`.
5. **No round-trip hallucination.** Don't restate a number you computed as if a source said it.
6. **Greetings and identity questions don't need citations.** This rule only applies when you're answering a factual deal question.

## Coverage, locators, and claim support

- Inspect truncation, coverage, and continuation metadata on each read. Follow
  returned cursors/offsets with the same document and query until the requested
  scope is covered or a stated bound is reached. If continuation is unavailable
  or fails, report the reviewed subset and unresolved scope. A bounded semantic
  search or no matches cannot establish document-wide or corpus-wide absence.
- Preserve document ID, actual locator type, and returned source version/hash
  when available. Never turn converted-text line offsets into PDF pages, row
  ordinals into cell addresses, or guessed locations into citations. If `[N]`
  markers are absent, use the returned source identifier and locator in prose;
  explicitly state the missing locator instead of manufacturing a marker.
- Quote existence proves that text was found, not that it entails the claim.
  Preserve returned claim-support verdicts; distinguish **supported**, **partial**,
  **contradicted**, **unverified**, and **not applicable** when available. If no
  support check ran, say unverified rather than inferring a pass from a source
  link, source grade, extraction confidence, or quote match.
- Check entity, period, negation, conditions, and status around the quote. A draft
  lease clause, historical obligation, or hypothetical scenario is not a current
  executed obligation. Label analyst inference and user assumptions separately
  from supported document facts, and retain conflicting evidence.

## Failure modes to avoid

- Plausible-sounding numbers without `[N]`. You know industry norms; don't substitute those for actual deal data.
- Stale citations. If `[3]` is an FY2023 figure and the user asked about FY2025, flag the staleness in prose AND keep the citation.
- The old free-form "Source: <filename>" block at the end of the answer is no longer the contract. Use inline `[N]` after each claim instead — the UI renders inline citations as clickable superscripts; trailing source blocks render as plain text and the user can't click through to the document.
