---
description: Close the institutional-learning flywheel for a deal — record what the model predicted, then the realized post-close actuals (exit EV, IRR, MOIC), and score every prediction against what actually happened. This is the write side of the loop that /calibrate-vs-history and /similar-deals read from.
---

# Record Outcome

Most AI tools forget every deal the moment the session ends. OloLand's flywheel does the opposite: it captures what the model predicted, then — once the deal closes and 12+ months of realized data exist — scores those predictions against reality. That accuracy history is what lets `/calibrate-vs-history` say *"your firm overestimates revenue growth by 7pp in deals like this."*

That read side only works if the **write side** is fed. This command is the write side. It does two things:

1. **Mints predictions** (if the deal doesn't have them yet) by running the deterministic engines and a forecast run — so there is something concrete to grade later.
2. **Records realized actuals** and closes the loop — stamping an accuracy score on each `enterprise_value` / `irr` / `moic` prediction.

## Usage

```
/record-outcome <deal_id>
```

Two distinct moments call for it:

- **At underwriting / IC** — mint the predictions so the deal is on the books to be graded later. (Steps 1-3 below; skip the actuals.)
- **Post-close (12+ months out)** — record the realized exit and close the loop. (Steps 4-5 below.)

## Arguments

- `<deal_id>` (required) — the deal to mint predictions for and/or record actuals against.

## Execution

The instructions below are for the model executing this command.

> **Decide the path first — and run only one.** This command has two mutually exclusive paths: **A. mint predictions** (IC / underwriting time) and **B. record actuals** (post-close). Work out which moment the user is in and run *only* that path. **Never run A then B in the same pass.**
>
> **Why (look-ahead guardrail — this is load-bearing):** a prediction is only meaningful if it was made *before* the outcome was known. If you mint a forecast at post-close — from a snapshot that already reflects how the deal turned out — and then score it against the known actuals, you fabricate an artificially-accurate "IC-time" prediction and poison the calibration / similar-deal corpus that `/calibrate-vs-history` depends on. So: only mint (A) when the outcome is genuinely unknown. In the post-close path (B) you **do not mint** — if no IC-time predictions exist, that deal simply doesn't get a graded score, and that is the correct, honest result (see step 5). Note that `record_deal_actuals` may return a backend hint like *"run create_forecast_run first"* when 0 predictions close — **do not follow that hint post-close**; it is only valid at IC time.

> **Units are load-bearing — do not get this wrong.** The realized-actuals tool stores values in canonical units, and a unit mismatch silently corrupts the accuracy score (this exact class of bug was the reason the flywheel scored nothing for months). Always pass:
> - `actual_exit_ev` — **absolute USD**. `450000000` for $450M, NOT `450` and NOT `450000`.
> - `actual_irr` — a **decimal**. `0.28` means 28%, NOT `28`.
> - `actual_moic` — a **multiple**. `3.2` means 3.2×, NOT `320`.
> Confirm the magnitude of **only the metrics the user actually provided** back to them before recording — never echo a placeholder for a metric they didn't give (e.g. "recording a $450,000,000 exit — correct?", or "recording 0.28 IRR / 3.2× MOIC — correct?"). `record_deal_actuals` takes at least one of the three; don't invent the others.

### A. Mint predictions — IC / underwriting time ONLY (outcome not yet known)

Run this path only while the deal is live and its outcome is genuinely unknown. **Do not run it to "backfill" a deal that has already closed** — see the look-ahead guardrail above.

1. **Run the deterministic models.** Call `run_deal_model(deal_id)` (defaults to `stages=["dcf","lbo"]`, `scenario_name="base"`). This persists a DCFRun + LBORun from the deal's existing financial snapshot — the DCF backs the `enterprise_value` prediction, the LBO backs `irr` / `moic`. No assumptions are required; the engines read the snapshot. If it returns `"Deal model pipeline returned no snapshot."`, the deal has no financial snapshot yet — tell the user to run `/dd-analyze` or `/valuation` first, then retry.

2. **Mint the forecast.** Call `create_forecast_run(deal_id)` (defaults: `trigger="manual"`, `prediction_horizon_days=365`). This reads the runs from step 1 and writes typed `DealPrediction` rows: `enterprise_value` (absolute USD), `irr` (decimal), `moic` (multiple). Report `predictions_created` and `prediction_types` back to the user.

3. **Stop here if the deal hasn't closed.** Predictions are now on the books. They'll be graded when actuals land. Tell the user the deal is being tracked and that `/record-outcome <deal_id>` should be run again post-close.

### B. Record actuals and close the loop — post-close (do NOT mint here)

This path records what actually happened and grades whatever IC-time predictions already exist. It must **not** call `run_deal_model` or `create_forecast_run` — minting at this point is look-ahead bias (see the guardrail above). Go straight to step 4.

4. **Initialize the outcome row (once).** Call `record_deal_outcome(deal_id, outcome_status)` where `outcome_status` is one of: `active`, `closed`, `passed`, `exited`, `merged`, `written_off`. The command only takes `<deal_id>`, so derive the status: if the user named it, use that; if they're recording exit actuals (EV/IRR/MOIC), default to `exited` (or `merged` if the deal closed via merger); otherwise ask which applies. If it returns `"Outcome tracking already exists for deal ..."` with an `existing_outcome_id`, that's fine — proceed to step 5 (the row already exists).

5. **Record the realized actuals.** Call `record_deal_actuals(deal_id, ...)` with at least one of `actual_exit_ev` / `actual_irr` / `actual_moic` (the tool rejects a call with none). Optional context: `exit_revenue`, `exit_ebitda`, `total_risk_impact`, `lessons_learned`, `outcome_status`. Re-read the **Units** box above before passing values. The response reports `predictions_closed` plus `ev_prediction_accuracy` / `irr_prediction_accuracy` / `risk_prediction_accuracy`.

   - **If `predictions_closed > 0`** — relay the accuracy scores: they are the grade the model earned on this deal, and they now feed `/calibrate-vs-history`.
   - **If `predictions_closed == 0`** — the deal had no IC-time predictions on file. The outcome is still recorded (it feeds outcome tracking and `/similar-deals`), but there was nothing to grade. Tell the user this plainly. **Do NOT** now run `run_deal_model` / `create_forecast_run` to "create something to score" — that would mint a forecast from post-close data and grade it against the known result (look-ahead bias). For future deals, the fix is to run `/record-outcome` at IC time *before* the outcome is known.

## What this unlocks

Once a cohort of deals has closed-and-observed outcomes on file, the read side lights up:

- `/calibrate-vs-history <deal_id>` — applies your firm's historical bias to the live deal's projections.
- `/similar-deals <deal_id>` — cross-deal pattern match weighted by realized outcome accuracy.
- `/playbook-recall` — what worked / didn't / was missed in similar past deals.

Each closed outcome makes all three sharper. Nothing else in the toolchain can answer *"are we systematically too optimistic about deals like this?"* — only the firm's own graded outcomes can.

## Notes

- `record_deal_actuals` is **free** (zero-credit) — recording outcomes must never be gated by a credit balance.
- The closure is best-effort and idempotent: re-recording actuals re-scores the same predictions; it won't double-count.
- EV / IRR / MOIC are the canonical graded predictions. Risk-realization accuracy is computed from `total_risk_impact` against the deal's flagged risks.

## Related commands

- `/calibrate-vs-history` — the payoff: historical-bias-corrected projections.
- `/similar-deals` — outcome-weighted cross-deal pattern match.
- `/dd-analyze`, `/valuation` — produce the financial snapshot the models read.
