# MD2S-R1-L Source-Identical Replay Closure v1.0

**Date:** 2026-08-26  
**Status:** `TARGETS_NARROWED_REPLAY_STILL_BLOCKED`

## Current state

Primary B1.4F/G/K/L package recovery has materially improved the historical MD2S-R1-L record. It does not yet close the source-identical historical two-junction transaction.

Recovered and manifest-valid:

- B1.4F
- B1.4G
- B1.4K
- B1.4L

Selected B1.4K/L numerical claims additionally have independent reproduction PASS records.

## Newly resolved prerequisite package names

The official historical chat-export chronology gives exact package names for two prerequisite phases that are still not recovered as binaries:

1. `HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip`
2. `HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1_PACKAGE.zip`

These replace the previous vague search target “B1.4E/H inputs” with exact historical binary names. Current File Library search surfaces the historical references but not the ZIP payloads. Current UniverseLab code search returns no exact package-name match.

## Why E/H matter

The surviving legacy recovery v5 identifies the source-identical 6D action/potential/coupling set, including B1.4E/H inputs or source-identical equivalents, as a prerequisite for an exact historical replay. Therefore E/H are now the highest-value package-recovery targets.

This is not a claim that E/H alone are sufficient. Even after E/H recovery, the two-junction transaction still requires run-bound two-sided interface data and generation provenance.

## Remaining hard blockers

The exact historical replay still requires:

- `A_prime_bulk`
- `A_prime_cap`
- `Lprime_over_L_bulk`
- `Lprime_over_L_cap`
- historically bound oriented normals
- full-precision two-sided interface/profile derivative tables
- original two-junction solver residual logs
- complete generation solver tolerances/configuration
- the source-identical 6D action/potential/coupling set for all prerequisite runs

No missing field may be filled from later C1/rebuild data and no interpolated value may be relabeled as historical original data.

## Search order

**P0:** recover B1.4E package binary.  
**P0:** recover B1.4H package binary.  
**P1:** recover the run-bound two-sided Bulk/Cap interface export.  
**P2:** recover the original residual/derivative/configuration bundle.

If any package is recovered, validate ZIP CRC, internal manifest, exact package identity, input/output bindings, and its relationship to F/G/K/L before changing evidence status.

## Governance firewall

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
