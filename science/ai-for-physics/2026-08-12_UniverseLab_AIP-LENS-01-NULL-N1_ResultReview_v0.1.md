# UniverseLab AIP-LENS-01-NULL-N1 — Result Review v0.1

Date: 2026-08-12  
Review ID: `AIP-LENS-01-NULL-N1-RESULT-REVIEW`  
Status: `PASS_N1_RESULT_REVIEW_SYNTHETIC_INFRASTRUCTURE_VALIDATED_N2_PROTOCOL_PREPARATION_ELIGIBLE_NO_REAL_DATA_EXECUTION`

## 1. Scope

This review independently checks the preserved canonical `AIP-LENS-01-NULL-N1` main-run artifact for integrity, split binding, final-test metric consistency and compliance with the predeclared N1 synthetic thresholds.

It does **not** perform new model training, real-data inference, HZT comparison, physical solver execution or evidential promotion.

## 2. Canonical execution under review

- workflow run: `31601928296`
- canonical head: `d7476e0e163d4267f36be0256d110937684f59e1`
- run class: `CANONICAL_MAIN`
- conclusion: `success`
- artifact ID: `9143456964`
- artifact ZIP SHA256: `dce854e11dadda1e0650d59ba3722c83c89cc02f94ae5ddcdf704be15a8109ce`
- artifact size: `16326` bytes

The preserved archive contains exactly four expected files: the run log, execution summary, final-test predictions and split manifest.

## 3. Integrity checks

The downloaded archive independently reproduced the published ZIP digest. The run log and `N1_execution_summary.json` are byte-identical. The split manifest canonical digest is

`b5908757ebb78ed62cfc41997e582f62dd75f215cba37fe596547e99f3c41f84`

and matches the binding recorded in the execution summary.

The final-test CSV contains exactly `256` rows and `256` unique IDs.

## 4. Independent final-test recomputation

The preserved final-test CSV was used to recompute ML residual RMSE, mean bias, 68%/95% conformal coverage using the frozen `q68/q95` values, and residual correlations with the declared `noise` and `ia` nuisance variables.

For `Omega_m`:

- RMSE recomputed: `0.026297734741452885`
- RMSE reported: `0.02629773474143493`
- bias recomputed: `0.0026473927098085936`
- bias reported: `0.0026473927098010362`
- coverage 68%: `0.625`
- coverage 95%: `0.9609375`
- residual/noise correlation recomputed: `-0.004900824267487005`
- residual/IA correlation recomputed: `-0.13094066536818655`

For `S8`:

- RMSE recomputed: `0.020612637440226615`
- RMSE reported: `0.020612637440267163`
- bias recomputed: `-0.0019483221431328148`
- bias reported: `-0.0019483221431069665`
- coverage 68%: `0.62109375`
- coverage 95%: `0.92578125`
- residual/noise correlation recomputed: `0.02774842909833454`
- residual/IA correlation recomputed: `0.14366292593639746`

All independently recomputed values match the preserved execution summary within the review tolerance `1e-12`.

## 5. Threshold review

The N1 execution remains a PASS against its predeclared thresholds. The ML estimator is only modestly better than the declared linear baseline:

- `Omega_m`: ML/baseline RMSE ratio `0.9776013645605738`
- `S8`: ML/baseline RMSE ratio `0.9451783585921744`

This is methodologically acceptable for the null pilot; no claim of deep-learning superiority is made or needed.

The reported OOD values also pass their predeclared thresholds (`FPR=0.015625`, `TPR=0.99609375`). However, the preserved canonical artifact does not contain the OOD_STRESS rows, so the OOD rates cannot be independently reconstructed from the archive alone. They remain deterministic-pipeline outputs covered by the canonical regression/CI run. This limitation is explicitly retained rather than silently promoted.

## 6. Gate disposition

`AIP-G0` is preserved.

`AIP-G1` is ratified only for this synthetic execution.

`AIP-G2` is ratified only for schema/unit-contract integrity and is **not** physical simulator validation.

`AIP-G3` and `AIP-G4` are ratified only for the frozen toy synthetic model.

`AIP-G5` is ratified only as a synthetic-truth return check.

`AIP-G6` remains not tested. No real-data execution is authorized by this review.

`AIP-G7` is not reached.

## 7. Decision

The N1 result is accepted as a successful **synthetic infrastructure/null-pilot result**.

The next admissible step is only:

`AIP-LENS-01-NULL-N2-PROTOCOL-FREEZE`

This means N2 protocol preparation may begin, but real-data execution remains blocked until a separate contract freezes the exact survey/release, licensing and provenance, blinding/no-training-on-real-data rule, observables and preprocessing, survey mask and geometry, non-ML reference baseline, simulator-to-real transfer diagnostics, systematics/null tests, immutable result schema and a separate executable authorization.

## 8. Scientific firewall

The following remain forbidden:

`synthetic PASS -> physical weak-lensing validation`

`synthetic PASS -> real-data validation`

`synthetic PASS -> HZT support`

`ML performance -> physical evidence`

Therefore:

- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

No HZT parameter, physical likelihood, solver state, topology or physical parameter is changed by this review.
