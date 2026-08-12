# UniverseLab AIP-LENS-01-NULL-N2 — Protocol Freeze v0.1

Date: 2026-08-12  
Protocol: `AIP-LENS-01-NULL-N2-PROTOCOL-FREEZE`  
Status: `FROZEN_REAL_DATA_TARGET_IDENTIFIED_EXECUTION_BLOCKED_PENDING_PHYSICAL_SIMULATOR_FEATURE_BRIDGE_AND_SEPARATE_AUTHORIZATION`

## Scope

This document freezes the real-data control target for the next weak-lensing AI-for-Physics stage. It does **not** download or inspect the real data, does not train a new model, does not perform real-data inference, and does not authorize any real-data execution.

The control target is the public KiDS-1000 cosmic-shear cosmology release from KiDS-DR4 associated with Asgari et al., *A&A* 645, A104 (2021), arXiv:2007.15633v2, DOI 10.1051/0004-6361/202039070. The official release page identifies the fiducial statistic as COSEBIs and distributes the data vector, covariance, source-redshift distributions, redshift-distribution covariance, Multinest chains and KCAP/CosmoSIS configuration material in `KiDS1000_cosmic_shear_data_release.tgz`.

Official sources:

- https://kids.strw.leidenuniv.nl/DR4/KiDS-1000_cosmicshear.php
- https://kids.strw.leidenuniv.nl/DR4/lensing.php
- https://arxiv.org/abs/2007.15633

## Why N2 cannot execute yet

N1 deliberately used a declared toy weak-lensing-inspired summary generator. Its 12-feature representation is not a physically defined transformation of KiDS shear measurements, COSEBIs, band powers or two-point correlation functions. Therefore the frozen N1 weights must **not** be applied directly to KiDS real data.

The required next technical stage is `AIP-LENS-01-NULL-N2-BRIDGE`. It must establish a physics-based weak-lensing forward model, or a separately validated surrogate of one, that produces the same observable semantics used for the real-data control. It must also carry survey geometry/masks, shape noise, redshift uncertainty, intrinsic alignments and declared small-scale/baryonic handling.

This is a hard scientific firewall:

`synthetic feature similarity != physical observable equivalence`.

## Frozen real-data control

The primary real-data statistic is the KiDS-1000 fiducial COSEBIs data product. The control targets remain `S8` and `Omega_m`, with

`S8 = sigma8 * sqrt(Omega_m / 0.3)`.

The non-ML reference is the released KiDS-1000 fiducial COSEBIs analysis implemented through the distributed KCAP/CosmoSIS configuration. The published `S8 = 0.759 +0.024/-0.021` value is reserved for post-execution comparison only; it is not an ML training or calibration target.

Because the result is already public, N2 is explicitly classified as a **published reproduction/control exercise**, not as a discovery-blind test. Strict human-level blinding is impossible. Procedural leakage controls therefore forbid use of the released posterior chains, best-fit values, real-data residuals or real-data outputs for model selection, threshold selection or hyperparameter tuning before a frozen prediction is sealed.

## Data-use and provenance rule

The official KiDS weak-lensing page welcomes independent analyses but requires the KiDS acknowledgement and relevant KiDS-1000 citations in resulting publications. This protocol records that reuse condition without asserting a broader formal open-data license than the official page states.

Before any future execution, the downloaded package must be locally hashed and that SHA256 must enter the immutable execution/result manifest.

## Required N2-BRIDGE checks

Before real-data execution can even be considered, the bridge must pass all of the following: same observable semantics in simulation and data; survey geometry/mask treatment; shape-noise model; photometric-redshift uncertainty propagation; intrinsic-alignment nuisance treatment; explicit baryonic/systematic treatment or declared scale cuts; calibration and coverage on independent simulations; simulation-to-real domain-shift diagnostics; and a predeclared OOD/abstention rule.

Required real-data null/systematic controls include the released B-mode/null checks where applicable, tomographic-bin stability, statistic/scale stability, redshift-distribution perturbations, intrinsic-alignment sensitivity, covariance consistency, simulation-to-real feature-distribution checks, OOD abstention, and reproduction of the non-ML reference baseline.

Any unexplained material failure blocks interpretation and promotion.

## Gate state

`AIP-G0` is preserved. `AIP-G1` through `AIP-G5` retain only their N1 synthetic/toy scope. `AIP-G2` has **not** yet passed physical-simulator validation. `AIP-G6` remains **NOT TESTED** because no real-data execution has occurred. `AIP-G7` is not reached.

The next candidate is therefore:

`AIP-LENS-01-NULL-N2-BRIDGE`

followed, only if that bridge passes an independent review, by a separate:

`AIP-LENS-01-NULL-N2-EXECUTION-AUTHORIZATION`.

## Governance firewall

No HZT comparison is performed. No HZT parameter is used. No physical solver, likelihood, physical parameter set or topology is modified. `WP4` remains `BLOCKED`; `K1-D` remains `NOT_RELEASED`; `K1-E` remains `NOT_ADMISSIBLE`; physical-evidence effect remains `NONE`.

A future successful KiDS reproduction would validate only the declared real-data control pipeline within its frozen scope. It would not constitute HZT support, HZT evidence, modified-gravity evidence or a release of any HZT scientific gate.
