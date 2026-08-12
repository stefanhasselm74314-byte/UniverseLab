# UniverseLab AIP-LENS-01-NULL-N1 — Deterministic Synthetic Execution Protocol v0.1

Date: 2026-08-12  
Status: `AUTHORIZED_FOR_DETERMINISTIC_SYNTHETIC_EXECUTION`  
Parent: `AIP-LENS-01-NULL / N0`  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`

## 1. Scope

N1 is the first executable stage of the UniverseLab AI-for-Physics weak-lensing null pilot. It is deliberately small and deterministic. Its purpose is to test whether the full ML governance path actually works end to end: independent partitions, baseline comparison, learned model, calibration, coverage, nuisance diagnostics, OOD rejection, immutable outputs and reproducibility.

This is **not** a physical weak-lensing simulation. The generator is explicitly classified as:

`DECLARED_TOY_SYNTHETIC_WEAK_LENSING_INSPIRED_SUMMARY_MODEL`

It is not N-body, ray tracing, KiDS, DES, HSC, Euclid, LSST or HZT simulation. A PASS can validate only the N1 synthetic pipeline and its declared numerical thresholds.

## 2. Targets and synthetic observables

Required targets are

`Omega_m`

and

`S8 = sigma8 * sqrt(Omega_m / 0.3)`.

`sigma8` is retained only as a diagnostic generator parameter. No HZT parameter is an allowed target.

Each realization contains twelve input channels: six tomographic-like lensing-amplitude summaries, four derived shape/ratio summaries, and two explicitly declared nuisance channels (`noise`, `ia`). The six primary channels are smooth nonlinear functions of `Omega_m`, `sigma8`, redshift-like bin index and `ia`, with deterministic seeded Gaussian noise.

The construction is weak-lensing-inspired only. It has no claim to reproduce a survey covariance, nonlinear structure formation, baryonic feedback, intrinsic-alignment realism, map geometry, mask coupling or actual shear calibration.

## 3. Frozen partitions

The exact partitions are:

| Partition | N | Seed |
|---|---:|---:|
| TRAIN | 512 | 11001 |
| VALIDATION | 128 | 11002 |
| CALIBRATION | 128 | 11003 |
| FINAL_TEST | 256 | 11004 |
| OOD_STRESS | 256 | 11005 |

IDs are partition-qualified and lineage collisions are forbidden.

In-distribution generation uses `Omega_m in [0.22,0.38]`, `sigma8 in [0.68,0.90]`, `noise in [0.02,0.06]`, and `ia in [-0.25,0.25]`.

OOD stress generation uses deliberately displaced low/high cosmology branches plus larger noise and IA ranges. OOD status is never inferred from hidden target metadata during evaluation; the detector uses input feature-space deviations only.

## 4. Estimators

The declared non-ML baseline is linear ridge regression on the first six standardized summary channels with `lambda = 1e-6`.

The simple learned model is quadratic feature ridge regression with `lambda = 0.5`. It uses standardized features, their squares and a fixed subset of pairwise interactions. It is intentionally not a deep network and requires no external ML framework.

Uncertainty intervals are split-conformal absolute-residual intervals calibrated only on `CALIBRATION`. The claimed nominal coverages are 68% and 95%.

OOD detection is `max(abs(training-standardized feature z-score))`; its threshold is the 99th percentile of the `VALIDATION` score distribution.

## 5. Predeclared pass thresholds

Before execution, N1 freezes these thresholds:

- absolute bias <= 0.010 for both targets;
- RMSE <= 0.040 for both targets;
- learned-model RMSE must not exceed the declared baseline RMSE;
- 68% empirical coverage must lie in [0.55, 0.82];
- 95% empirical coverage must lie in [0.88, 1.00];
- absolute residual correlation with each declared nuisance <= 0.20;
- OOD validation false-positive rate <= 0.05;
- OOD stress true-positive rate >= 0.90;
- worst quartile-stratified RMSE / global RMSE <= 2.0.

Changing a threshold after opening `FINAL_TEST` creates a new protocol version and invalidates promotion from the old execution.

## 6. Run classes

Pull requests run `PR_REHEARSAL`. This is a full deterministic execution used to validate implementation and reproducibility but is not the canonical result for N1 review.

A push of the identical merged source/contract to `main` runs `CANONICAL_MAIN`. Only that run may be used by the subsequent N1 result-review step.

Reruns are allowed when source and contract are unchanged because N1 is deterministic methods validation, not a single-use physical-solver authorization.

## 7. Output package

Every execution emits:

- `N1_execution_summary.json`;
- `split_manifest.json`;
- `final_test_predictions.csv`.

The summary binds the execution contract, parent N0 contract, exact split content hashes, learned-weight digests, metrics, thresholds, failure list and gate claims.

## 8. Gate interpretation

A successful N1 execution may support only the following limited claims:

`AIP-G1`: provenance/split integrity for this synthetic execution.  
`AIP-G2`: schema/target/unit contract only; not physical simulator validation.  
`AIP-G3`: declared held-out numerical thresholds.  
`AIP-G4`: declared calibration/coverage/OOD thresholds.  
`AIP-G5`: return against known synthetic truth only.

`AIP-G6` cannot pass because no real survey data are used. `AIP-G7` always requires a separate review.

## 9. Scientific firewall

The following implications remain forbidden:

`synthetic PASS -> real weak-lensing validation`

`synthetic PASS -> HZT support`

`ML score -> physical evidence`

`ML score -> K1-D release`

`ML score -> K1-E admissibility`

`ML score -> WP4 release`

Therefore after N1 execution:

`WP4 = BLOCKED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`physical_evidence_effect = NONE`

## 10. Next admissible step

If the canonical main execution completes and the artifact is preserved, the only next admissible step is:

`AIP-LENS-01-NULL-N1-RESULT-REVIEW_NO_REAL_DATA_EXECUTION`

N2 real-data execution remains blocked until that separate review explicitly accepts the N1 result package.
