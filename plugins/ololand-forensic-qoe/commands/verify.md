---
description: 'Verify every dollar and percentage figure in an externally-drafted artifact (an IC memo, analysis, or answer — e.g. one drafted in Claude Cowork) against the sources YOU cite, with no OloLand deal and no ingestion. Per-figure PASS / FAIL / UNVERIFIED with cited-chunk number reconciliation, an NLI derivation check, an independent grader, and a content-hashed provenance pack. The corpus-free "defend every number, cite every source" button for output produced anywhere.'
---

# /verify (corpus-free)

Runs OloLand's verification layer over an artifact you drafted **anywhere** — including in Claude Cowork or another tool — checked against **your own cited sources**, with no OloLand deal and no ingestion. It is the additive "audit my output" surface: install alongside your existing workflow, point it at a memo plus the passages you cited, and get back a per-figure verdict you can defend at IC.

This is distinct from the deal-scoped verifier in `ololand-dd` (`/verify` there reconciles against an **ingested** OloLand deal corpus). This command brings its own evidence — nothing needs to be ingested first.

## Usage

```
/verify
```

Then provide the artifact and its cited sources (see Inputs). There is no `deal_id`.

## Inputs

Ask the user for these if missing:

1. **artifact_text** (required) — the drafted memo / analysis / answer to verify. Accept any of: text pasted inline, a path to a local file (read it with your file tool and pass the contents), or the body of something the user generated elsewhere (e.g. a Cowork IC memo).
2. **evidence** (required) — the sources the artifact cites, as a list of objects `{text, file_name?, page?}`. Ask the user to paste the relevant passage(s) from each cited source. **Ordering is the citation mapping:** the 1st evidence entry is `[1]`, the 2nd is `[2]`, and so on — so the artifact's `[N]` markers resolve positionally against this list. Each entry's `text` is the chunk the figures cited by that marker are checked against.

Optional:

- **rubric** — override the grader rubric (defaults to the institutional DD rubric).
- **mode** (default `strict`) — `strict` fails **closed**: if a provider call (grader / NLI) fails or times out, the affected figures come back `UNVERIFIED_PROVIDER_DEGRADED`, never a silent pass. `advisory` lets such cases pass through.

## Execution

1. Collect `artifact_text` and build the `evidence` list from the user's cited passages (preserve order = `[N]` order).
2. Call `mcp__ololand__grade_external_artifact` with `artifact_text`, `evidence`, `mode` (and `rubric` if supplied).
3. Render the returned verdict (see Output). Do not re-compute or second-guess the per-figure statuses — they come from the deterministic engines, the NLI check, and the independent grader.

## What it checks (per figure)

- **Cited-chunk number reconciliation** — each `$` / `%` figure must reconcile (5% rel / 0.5pt abs) against the chunk **it cites**, not merely against any supplied evidence. A `38%` cited to a source that says `11%` fails even if another source contains `38%`.
- **Citation resolves** — the cited marker maps to a real supplied chunk.
- **NLI derivation** — the cited source must *entail* the claim (entail / neutral / contradict), so a citation pasted onto a guessed number is caught — not just a digit match.
- **Independent grader** — a Gemini grader (a genuinely different model from the one that drafted the artifact) judges figure support and attribution.
- **Blocking deterministic gate** — out-of-range citation markers and material claims made with zero supporting evidence force a non-pass.
- **Fail-closed** (strict mode) — provider degradation surfaces `UNVERIFIED`, never a green pass.

## Output structure

Render a single verdict block:

```
/verify verdict — overall: <PASS | FAIL | UNVERIFIED>   (mode: <strict|advisory>)

Per figure:
  <value>  cited [<file>, p.<n>]   <PASS|FAIL|UNVERIFIED>
     reason: <one line>
     checks: number_matches=<bool>  nli=<entail|neutral|contradict|—>

Coverage: <marker_count> citations, <uncited_material_claims> uncited material claim(s)
Grader (<model>): <passed|failed|—>  <rationale>
Degraded: <list, if any provider could not be reached>

Provenance: run_id=<…>  sha256=<…>
```

Then list every `FAIL` and `UNVERIFIED` figure verbatim (value + cited file/page + reason) — those are the deal-killing review items. For each `FAIL`, recommend the user fix the citation (point it at the source that actually supports the figure) or remove/qualify the claim. Surface the `provenance.run_id` + `content_sha256` as the artifact the user can hand to an IC chair or LP.

## When to use this

- Before an IC memo, analysis, or board section drafted **outside** OloLand (e.g. in Cowork) goes to committee — verify it against your own sources without re-ingesting anything.
- To spot-check a single number that "looks off" in any drafted text, given the passage it came from.
- As a pre-send gate on AI-generated financial prose produced in any tool.

## When NOT to use this

- When you already have the deal **ingested in OloLand** — the deal-scoped `/verify` in `ololand-dd` is richer (cross-document reconciliation across the CPA > tax > management > AI hierarchy, DCF identity replay) because it retrieves against the full corpus, not just the passages you paste.
- For prose with no `$` / `%` figures and no citations — there is nothing to check.

## Honest bounds

- Deterministic number reconciliation covers **dollar and percentage** figures. Multiples (`8.5x`), ratios, and bare counts are not deterministically reconciled — they rely on the grader. Do not represent the result as "every number verified"; it verifies the `$` / `%` figures deterministically + by NLI, and grades the rest.
- Verification only sees the evidence **you supply**. If you paste a truncated snippet, the checks cover that snippet — paste the passage that actually contains the cited figure.

Companion: this is the corpus-free counterpart to `ololand-dd`'s deal-scoped `verifier-stack`; same "defend every number" guarantee, bring-your-own-evidence.
