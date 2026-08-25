# MD2S B1.4E Primary Package Recovery v1.0

**Date:** 2026-08-26  
**Status:** `PRIMARY_ARTIFACT_RECOVERED_MANIFEST_VALID_SELECTED_INTERNAL_NUMERIC_CHECKS_PASS`

## Recovered package

Historical source report name:

`HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip`

Recovered uploaded filename:

`HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1.zip`

The outer filename lacks the historical `_PACKAGE` suffix. Exact byte identity of the outer historical wrapper is therefore not claimed. The internal root and payload structure match the historical package family and the internal SHA-256 manifest validates every tracked payload file.

Recovered ZIP:

- size: 2,770,104 bytes;
- SHA-256: `31b80fe24dcb45822b2edb8f24bf83ead40bc05d41b5080f9da8fcd528965c1b`;
- total ZIP entries: 16;
- regular files including the manifest: 12;
- manifest-tracked payload files: 11;
- ZIP CRC test: PASS;
- internal manifest: 11/11 valid.

## Historical provenance match

The official export preserves the B1.4E result and exact package link. The recovered package reports the same state:

- phase `MD-2S-B1.4E`;
- `smooth_target_pole_local_repair_constructed`;
- target-space curvature pole removed to a finite C2 polar pole;
- `K_target(0) = -28.598227282884665`;
- factor-16 geometry retained;
- full scalar/radion sector open;
- C-infinity analyticity not proven;
- factor-16 release blocked;
- K1-D not released;
- K1-E not admissible;
- evidential status none.

The package provenance classification is `quarantined_non_evidential_smooth_target_pole_repair`.

## Selected independent consistency checks

The recovered payload permits independent recomputation of multiple archived quantities:

1. patch coefficient shift: `q2_new - q2_old = -27.847724300744908`, exact;
2. target curvature from the cubic target coefficient: `-6*c3 = -28.598227282884665`, exact;
3. cap-potential global minimum: `4 - phi_prime_R^2/(2*mu_cap) = 3.8100903024938315`, exact;
4. `min(P/r^2) = 0.3791193647165695`, matching the archived value;
5. `min(Q/r^2) = 0.37907653343188696`, matching the archived value;
6. scalar residual for `r/Rcap >= 1e-3`: maximum `9.30694129763765e-07`, RMS `8.257094312235935e-08`, exact;
7. all 24 stored partial-spectrum values agree between the CSV and selected-results JSON to maximum absolute difference `5.684341886080802e-14`;
8. the profile endpoint has `A_prime = 1` and `H_L = 1`, preserving the archived cap geometry.

## Reproduction limit

The package contains an inspection script, stored geometry/sigma profiles, partial spectra, contracts, status, report and manifest. It does **not** contain the generation solver needed to regenerate the profiles or Sturm-Liouville spectra from the underlying field equations.

Therefore:

- the profiles and partial spectra are recovered primary archived numerical products;
- selected internal/derived quantities have independent consistency PASS;
- no full solver re-execution is claimed;
- full scalar/radion stability, chi-dependent modes, naturalness and full ghost freedom remain open.

## Replay consequence

The B1.4E and B1.4H prerequisite package gaps are now both closed at the recovered-primary-package level.

The highest remaining recovery target is no longer another named B1.4 package. It is the run-bound source-identical two-sided Bulk/Cap interface export containing:

- `A_prime_bulk`;
- `A_prime_cap`;
- `Lprime_over_L_bulk`;
- `Lprime_over_L_cap`;
- historically bound oriented normals.

The exact historical two-junction replay remains blocked until these data, the full-precision derivative tables, original junction residual logs and complete generation configuration are recovered.

## Governance firewall

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
