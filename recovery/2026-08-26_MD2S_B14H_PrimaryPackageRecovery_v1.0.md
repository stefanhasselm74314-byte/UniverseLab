# MD2S B1.4H Primary Package Recovery v1.0

**Date:** 2026-08-26  
**Status:** `PRIMARY_ARTIFACT_RECOVERED_MANIFEST_VALID_SELECTED_INTERNAL_NUMERIC_CHECKS_PASS`

## Recovered package

Historical source report name:

`HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1_PACKAGE.zip`

Recovered uploaded filename:

`HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1.zip`

The outer filename lacks the historical `_PACKAGE` suffix. Therefore exact outer-wrapper byte identity is not claimed. The internal root and payload structure match the historical package path family, and the internal SHA-256 manifest validates every payload file.

Recovered ZIP:

- size: 55,066 bytes;
- SHA-256: `a73210f41362a00b69e169e424da9b8cdba790f0573a1d651cdfeb5d01837f7d`;
- total ZIP entries: 19;
- payload files: 14;
- ZIP CRC test: PASS;
- internal manifest entries: 14;
- manifest-valid entries: 14/14.

## Historical provenance match

The recovered package reports `MD-2S-B1.4H` and the same historical benchmark state preserved in the official export:

- critical `kappa_R = 0.3927482460297915`;
- benchmark `kappa_R = 0.5`;
- benchmark lowest `m^2 R_cap^2 = 0.5527569446937802`;
- factor-16 geometry retained;
- axisymmetric coupled scalar stability conditional at benchmark;
- factor-16 release BLOCKED;
- K1-D NOT RELEASED;
- K1-E NOT ADMISSIBLE;
- evidential status NONE.

The package provenance identifies B1.4G as its source package and classifies itself as `quarantined_non_evidential_boundary_radion_stabilization_design`.

## Selected independent checks

The recovered payload permits independent consistency recomputation of selected quantities:

1. the five benchmark spectrum values in `benchmark_spectrum_kappaR_0p5.csv` match `SELECTED_RESULTS.json` exactly;
2. the regulator spread recomputes to `3.0755086815714705e-05`, exactly matching the archived selected result;
3. the relative margin `(0.5-kappa_crit)/kappa_crit` recomputes to `0.2730801602665159`, exactly matching the archive;
4. the eigenvalues of the archived canonical total cap Hessian recompute to approximately `0.7511587393033659` and `1.1987060298329937`, matching the archived values;
5. the stiffness scan contains an explicit ZERO_THRESHOLD row at the archived critical stiffness.

These checks establish internal numerical consistency of the recovered primary package.

## Important reproduction limit

The package contains an inspection script, stored scan/spectrum/profile data, contracts, status, report and manifest. It does **not** contain the determinant-shooting/generation solver needed to regenerate the archived spectrum from the field equations.

Therefore:

- the archived benchmark spectrum is a recovered primary numerical result;
- selected derived/internal quantities have independent reproduction PASS;
- the spectrum itself is **not** claimed as independently solver-reexecuted from this package alone;
- the negative determinant scan remains a numerical archived scan, not an analytic global node-count theorem.

## Replay consequence

B1.4H is no longer a missing prerequisite package. The highest remaining package-recovery target is now:

`HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip`

The source-identical historical two-junction replay remains blocked by the missing run-bound two-sided Bulk/Cap interface quantities, oriented normals, full-precision derivative tables, original junction residual logs and complete generation solver configuration.

## Governance firewall

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
