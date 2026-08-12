# UniverseLab AIP-LENS-01-NULL — Weak-Lensing Null-Pilot Protocol v0.1

Date: 2026-08-12  
Status: `PILOT_PROTOCOL_FROZEN_NOT_EXECUTED`  
Parent: `UL-AIP-v0.1`  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`

## 1. Purpose

`AIP-LENS-01-NULL` is the first operationally specified AI-for-Physics pilot in UniverseLab. It is a **null/reference reproduction pilot**, not an HZT-vs-LambdaCDM classifier and not an evidence-producing analysis.

The pilot asks only whether a controlled machine-learning lensing pipeline can reproduce reference weak-lensing inference under a baseline cosmological model with auditable calibration, coverage, provenance and out-of-distribution controls.

Primary reference targets:

- `Omega_m`
- `S8 = sigma8 * sqrt(Omega_m / 0.3)`

Optional diagnostic target:

- `sigma8`

No HZT parameter is an allowed training target in v0.1.

## 2. Scientific firewall

The following implications are forbidden:

`ML accuracy -> physical admissibility`  
`baseline reproduction -> HZT support`  
`synthetic validation -> real-data validation`  
`classifier confidence -> evidence`  
`surrogate output -> solver proof`

Therefore the pilot has:

- no K1-D release effect;
- no K1-E admissibility effect;
- no WP4 release effect;
- no physical-evidence effect;
- no HZT solver, likelihood, parameter or topology modification.

## 3. Input hierarchy

The pilot is split into three strictly ordered stages.

### N0 — protocol and provenance freeze

Required before any model training:

- exact dataset identifiers and licenses;
- exact mock/simulation generator identity and version;
- exact train/validation/test split specification;
- seed registry;
- preprocessing and masking definition;
- target parameter ranges;
- nuisance-parameter treatment;
- reference estimator and reference metrics;
- immutable output schema.

N0 is the only stage authorized by this v0.1 protocol.

### N1 — synthetic/mock null reproduction

May be separately authorized only after N0 passes. It must use baseline-model simulations only and must demonstrate that the ML pipeline can recover held-out baseline parameters without leakage.

### N2 — real-data control application

May be separately authorized only after N1 passes. Real survey data must remain blinded from training, and simulator-to-real transfer must be treated as an independent validation problem.

## 4. Minimum split contract

A future executable contract must freeze independent partitions for:

- training;
- hyperparameter/validation;
- calibration;
- final test;
- OOD stress tests.

The final test partition must be untouched until the analysis configuration is frozen. No sky patch, simulation realization, augmentation lineage or deterministic derivative may cross partition boundaries.

## 5. Baseline observables

Allowed inputs may include one or more of:

- shear maps or catalog-derived map products;
- convergence/kappa maps;
- tomographic bins;
- masks and survey geometry channels;
- controlled noise realizations.

Any use of masks, noise, baryonic prescriptions, intrinsic alignments, photo-z uncertainties or shear-calibration systematics must be explicitly represented in provenance and split integrity.

## 6. Required metrics

At minimum, N1 must report on the frozen final test set:

- bias for each target;
- RMSE or equivalent scale-aware error;
- empirical interval coverage at 68% and 95% if probabilistic outputs are claimed;
- calibration diagnostics;
- residual dependence on nuisance variables;
- performance stratified by parameter-space location;
- OOD rejection/detection performance;
- comparison to a declared non-ML baseline.

A point-estimate network without uncertainty diagnostics cannot pass beyond AIP-G3.

## 7. AIP gate mapping

- `AIP-G0`: scope and non-evidence firewall frozen.
- `AIP-G1`: provenance, licensing and split integrity verified.
- `AIP-G2`: units, geometry conventions, masks, target definitions and physical constraints verified.
- `AIP-G3`: numerical fidelity on held-out baseline simulations verified.
- `AIP-G4`: calibration, coverage and OOD behavior verified.
- `AIP-G5`: authoritative-return test; selected predictions must be checked against the reference simulator/estimator path.
- `AIP-G6`: real-data null/control test with explicit simulator-to-real checks.
- `AIP-G7`: separate review required for any later evidential use.

This protocol freezes only `G0` and the requirements for `G1..G7`; it does not claim those gates have passed.

## 8. Fail-closed conditions

The pilot must stop rather than promote if any of the following occurs:

- train/test leakage or uncertain split lineage;
- undocumented preprocessing;
- missing simulator provenance;
- target leakage through filenames, metadata or generation artifacts;
- calibration/coverage failure;
- material OOD failure without abstention;
- material simulator fingerprint exploitation;
- material degradation on nuisance/systematic stress tests;
- inability to reproduce the declared baseline;
- any attempt to interpret a null-pilot score as HZT evidence.

## 9. First executable target

The first executable successor should be `AIP-LENS-01-NULL-N1`, using a small, reproducible baseline weak-lensing mock set with frozen parameter grid, train/calibration/test split and a deliberately simple reference estimator before any deep architecture is introduced.

The intended progression is:

`simple baseline -> simple ML -> calibrated ML -> OOD/systematics stress -> real-data control`

not

`largest model -> best score`.

## 10. Source context

Methodological context includes the user-supplied MIT/IAIFI material on AI-for-physics, simulation-based inference, symmetry-aware learning, model misspecification and astrophysical applications, plus the earlier weak-lensing ML examples discussed for KiDS-like analyses.

## 11. Frozen status

`AIP-LENS-01-NULL = PILOT_PROTOCOL_FROZEN_NOT_EXECUTED`

`model_training = NO`

`model_execution = NO`

`HZT_comparison = NO`

`WP4 = BLOCKED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`physical_evidence_effect = NONE`
