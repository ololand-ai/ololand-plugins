---
description: Review Benford first-digit conformity in supplied transactions or a deal's forensic results, preserving returned statistics and evidence gaps.
---

# Benford's Law

Benford's Law describes a logarithmic first-digit distribution in suitable naturally-occurring datasets. Deviations are investigation prompts, not proof of fabricated transactions or fraud; conformity does not establish that transactions are legitimate.

## Usage

```
/benford <deal_id>
/benford <supplied transaction list or GL file>
```

## Arguments

- Supply either a `deal_id` for the deal-scoped forensic workflow or a transaction list/GL file for the standalone tool. `run_benford` accepts `transactions`, not a deal or dataset identifier; each transaction dictionary needs an `amount` field.
- Preserve signed transaction amounts. Negative amounts are evaluated by absolute magnitude; zero and unusable values are ignored. Do not drop valid credits/reversals merely because their amounts are negative.
- Use the returned usable `sample_size`, `minimum_required`, and `status`; a file's raw row count is not the tested population or a guarantee of statistical reliability.

## Execution

1. If the user supplied a transaction list or GL file, parse it into transaction dictionaries using the current tool schema and call `run_benford(transactions)`. The standalone tool analyzes only that supplied payload; it does not fetch the deal's data room. If the user supplied only `deal_id`, call `analyze_forensic_qoe(deal_id)` and extract the returned Benford section. Do not pass a `primitives` argument or invent a transaction-fetch endpoint.
2. Inspect the returned `status` and usable sample size before interpretation. `insufficient_sample`, unavailable, unreliable, or uncomputed results are explicit gaps, not conformity or passing tests. Do not report placeholder zero distributions from an insufficient-sample response as measured results.
3. For computed results, report the returned observed/expected first-digit distributions, `chi_square`, Mean Absolute Deviation (`mad`), `conformity`, and `most_deviant_digit` when present. Preserve the response's scope and limitations.
4. The current standalone `run_benford` response does not return `p_value`, account-level flags, or ranked contributing transactions. Do not invent or back-calculate these and attribute them to the service. Account-specific findings or transaction follow-ups require separate actual source evidence.

## Interpretation

Use the returned `conformity` classification and methodology rather than applying a different threshold table. Report suitability and data gaps separately: a computed conformity result alone does not establish a suitable population, rule out fraud, or identify manipulated accounts.

## Output

For the tested population, only when computation is confirmed:

- Usable sample size, required minimum, status, and population/source description
- Returned observed vs. expected first-digit distributions (table or chart)
- Returned χ² statistic, MAD, conformity, and most-deviant digit when present
- Input limitations and evidence-backed follow-up questions; identify specific journal entries only when actual retrieved evidence supports them

Do not report a p-value: the current standalone response does not supply one. If the test could not run, show the returned gap and the needed input instead of numerical conclusions.

## Why this matters

First-digit analysis can help prioritize transaction review when the population is suitable. Corroborate deviations with source records and other evidence; neither deviation nor conformity establishes whether manipulation occurred.

## Example

```
/benford deal_acme_2026
```
