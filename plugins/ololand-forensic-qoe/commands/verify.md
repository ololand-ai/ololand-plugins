---
description: "Verify every dollar and percentage figure in an externally-drafted artifact (an IC memo, analysis, or answer — e.g. one drafted in Claude Cowork) against an OloLand deal's INGESTED data room. For each figure, evidence is retrieved per-claim from the corpus (not pasted by you) — so it confirms a number against the real source, or flags a source elsewhere in the data room that contradicts it, including evidence the author never cited. Per-figure PASS / FAIL / UNVERIFIED with corpus number reconciliation, an NLI derivation check, an independent grader, and a content-hashed provenance pack. No deal yet? It walks you through creating one."
---

# /verify (deal-scoped, corpus-based)

Runs OloLand's verification layer over an artifact you drafted **anywhere** — including in Claude Cowork or another tool — checked against an **OloLand deal's ingested data room**. For each figure it retrieves the supporting evidence from the corpus itself, so it catches numbers the author cited to the wrong source, or that the data room contradicts. Get back a per-figure verdict + a content-hashed provenance pack you can defend at IC.

It requires a deal with an ingested corpus. If you don't have one, this command walks you through creating it (`create_deal` + upload your documents) — that is the path from a Cowork draft to a verifiable OloLand deal.

## Usage

```
/verify
```

Then provide the artifact and the deal to verify it against (see Inputs).

## Inputs

Ask the user for these if missing:

1. **artifact_text** (required) — the drafted memo / analysis / answer to verify. Accept any of: text pasted inline, a path to a local file (read it with your file tool and pass the contents), or the body of something the user generated elsewhere (e.g. a Cowork IC memo).
2. **deal_id** (optional, required for verification) — the OloLand deal whose **ingested** data room backs the verification. If the user has no deal, do NOT block or repeatedly ask for one — proceed to the funnel (see Execution step 1) so they get the `create_deal` path.

Optional:

- **rubric** — override the grader rubric (defaults to the institutional DD rubric).
- **mode** (default `strict`) — `strict` fails **closed**: if a provider call (grader / NLI) fails or times out, the affected figures come back `UNVERIFIED`, never a silent pass. `advisory` lets such cases pass through.

## Execution

1. **No deal yet?** If the user has no `deal_id`, call `mcp__ololand__grade_external_artifact` with just the `artifact_text` — it returns `status: "needs_deal"`. Relay its guidance: create a deal and upload the data room with `mcp__ololand__create_deal`, then re-run `/verify` with the returned `deal_id`. (This is the intended onboarding path — do not fall back to pasting evidence.)
2. **Verify.** Call `mcp__ololand__grade_external_artifact` with `artifact_text`, `deal_id`, `mode` (and `rubric` if supplied).
3. **Handle the status field:**
   - `ok` — render the verdict (see Output).
   - `needs_corpus` — the deal exists but has no ingested documents. Tell the user to upload the data room (ingest), then re-run.
   - `search_error` — a retryable corpus-search failure (not a missing corpus); tell the user to retry.
4. Do not re-compute or second-guess the per-figure statuses — they come from the deterministic engines, the NLI check, and the independent grader.

## What it checks (per figure)

- **Corpus number reconciliation** — each `$` / `%` figure must reconcile (5% rel / 0.5pt abs) against the chunks **retrieved for that figure from the deal corpus**. A `38%` whose data-room source says `11%` fails.
- **NLI derivation** — the retrieved source must *entail* the claim (entail / neutral / contradict), so a guessed number that happens to appear is caught — not just a digit match.
- **Independent grader** — a Gemini grader (a genuinely different model from the one that drafted the artifact) judges figure support and attribution.
- **Fail-closed** (strict mode) — provider degradation surfaces `UNVERIFIED`, never a green pass; a figure with no supporting corpus evidence is `UNVERIFIED` (we report we could not confirm it, we do not silently pass it).

## Output structure

Render a single verdict block:

```
/verify verdict — overall: <PASS | FAIL | UNVERIFIED>   (deal: <deal_id>, mode: <strict|advisory>)

Per figure:
  <value>  source [<file>, p.<n>]   <PASS|FAIL|UNVERIFIED>
     reason: <one line>
     checks: number_matches=<bool>  nli=<entail|neutral|contradict|—>

Coverage: <marker_count> corpus chunks used
Grader (<model>): <passed|failed|—>  <rationale>
Degraded: <list, if any provider could not be reached>

Provenance: run_id=<…>  sha256=<…>
```

Then list every `FAIL` and `UNVERIFIED` figure verbatim (value + source file/page + reason) — those are the deal-killing review items. For each `FAIL`, recommend the user check the figure against the data room (the corpus source that should support it) or remove/qualify the claim. Surface the `provenance.run_id` + `content_sha256` as the artifact the user can hand to an IC chair or LP.

## When to use this

- Before an IC memo, analysis, or board section drafted **outside** OloLand (e.g. in Cowork) goes to committee — verify it against the deal's ingested data room.
- To spot-check a single number that "looks off" in any drafted text, against the corpus.
- As a pre-send gate on AI-generated financial prose produced in any tool.

## When NOT to use this

- For prose with no `$` / `%` figures — there is nothing to reconcile.
- When you have no deal and no intention of ingesting one — verification is grounded in the corpus; without it there is nothing to verify against (the command will return `needs_deal`).

## Honest bounds

- This is **precision over the corpus**: it checks that the figures the memo *states* are supported by the data room. It does **not** yet flag material risks the memo *omitted* (a recall / completeness pass is a separate, forthcoming capability). A `PASS` means the stated figures reconcile — not that the memo is complete.
- Deterministic number reconciliation covers **dollar and percentage** figures. Multiples (`8.5x`), ratios, and bare counts are not deterministically reconciled — they rely on the grader. Do not represent the result as "every number verified".

Companion: the deal-scoped `verifier-stack` in `ololand-dd` runs the four atomic-claim verifiers + cross-document reconciliation against the same ingested corpus.
