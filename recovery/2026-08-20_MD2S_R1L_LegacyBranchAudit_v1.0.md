# MD2S-R1-L Legacy Branch Audit v1.0

Status: `FORENSIC_BRANCH_AUDIT_COMPLETE_WITH_LIMITS`

Physical gate effect: `NONE`

## 1. Corrected identifier finding

The exact string `MD2S-R1-L` **is present** in the surviving repository corpus. It appears in:

`science/hzt-m0/md2s/R1_SOURCE_RECONSTRUCTION_LEDGER_v0.1.json`

as the ID of the `legacy_reproduction` track.

Its declared goal is to reproduce the historical A0 and B1.4N calculations with their original equations and conventions **if those sources can be recovered**.

Therefore the correct interpretation is:

- `MD2S-R1-L = RECOVERED_AS_LEGACY_REPRODUCTION_TRACK_ID`
- `ORIGINAL_HISTORICAL_SOLVER_ARTIFACT_ID = NOT_RECOVERED`

This corrects the broader wording that the exact identifier itself had not been found. The surviving track label is governance/reconstruction metadata, not proof that an original historical solver package named `MD2S-R1-L` survived.

## 2. Branch inventory

The audit covered the 13 legacy `agent/md2s-*` branches returned by the repository branch search:

- `agent/md2s-bulk-localized-junction-v0-1`
- `agent/md2s-c1-bvp-rank-preflight-v0-1`
- `agent/md2s-c1-dimensionless-jacobian-v0-1`
- `agent/md2s-c1-independent-backend-continuation-v0-1`
- `agent/md2s-checkpoint-2026-08-03`
- `agent/md2s-checkpoint-v1-2`
- `agent/md2s-checkpoint-v1-3`
- `agent/md2s-checkpoint-v1-4`
- `agent/md2s-checkpoint-v1-5`
- `agent/md2s-checkpoint-v1-6`
- `agent/md2s-oriented-junction-ledger-v0-1`
- `agent/md2s-parameter-flux-dependency-v0-1`
- `agent/md2s-radial-equation-ledger-v0-1`

For all 13, the branch-vs-main delta file inventory was enumerated. Content review then targeted the high-value science ledgers, reconstruction ledger and checkpoints most likely to contain boundary or solver provenance. This audit does **not** claim byte-level inspection of every file on every branch.

## 3. Junction branches

The oriented and bulk/localized junction ledgers are rebuild-track derivations. They explicitly state that true one-sided derivatives are required and that numerical one-sided boundary values are still missing.

They therefore provide equation structure, normal-orientation rules and residual definitions, but **not** the lost historical two-sided interface export.

## 4. Radial and parameter branches

The radial-equation and parameter/flux branches derive a new conditional current-canon structure. They explicitly avoid identifying their equations or conventions with the historical A0 solver without an equation-level identity proof.

No historical raw Cap/Bulk solver export is supplied there.

## 5. C1 branches

The C1 branches contain genuine analytic and numerical results, but for a **newly defined candidate model**. Their own records state:

`Historical A0 identity = NOT_CLAIMED`.

The exact C1 analytic anchor has, at `x = pi/2`, values such as

- `ell = 1`
- `ell_x = 0`
- `A_x = 0`
- `varphi_x = 0`

and the independent backend produces converged diagnostic Jacobian results.

These are real C1 analytic/numerical data. They are classified here as:

`C1_ANALYTIC_OR_DIAGNOSTIC_DATA_NOT_HISTORICAL_MD2S_R1L_DATA`.

They may **not** be used to fill the missing historical `A'_bulk`, `A'_cap`, `(L'/L)_bulk` or `(L'/L)_cap` values.

## 6. Source-reconstruction ledger

The surviving source-reconstruction ledger gives the strongest direct classification:

- A0 benchmark block: `REPORTED_NUMERICAL_BENCHMARKS`, regression target only.
- A0 analytic closure/numerical reproduction: reported, but not independently reproducible.
- B1.4N negative result: reported, not independently reproducible.
- exact historical radial ODE set and Hamiltonian/dependency map: `MISSING_PRIMARY_TECHNICAL_SOURCE`.
- exact historical cap/localized action and oriented junction conventions: `MISSING_PRIMARY_TECHNICAL_SOURCE`.
- definitions/integration conventions for `V_W`, `R_circle`, `Xi_cap`, `lambda_eff`: partial/missing.

The same ledger says the directly inspected older `Zip_analysis_pack.zip` ended on 2025-12-17 and contained no MD-2S/B1.4N/B1.4O or registered A0 benchmark message-text occurrence, so it predates the 2026 MD-2S calculation.

## 7. Current historical-data verdict

Still not recovered as primary historical solver data:

- `A'_bulk`
- `A'_cap`
- `(L'/L)_bulk`
- `(L'/L)_cap`
- run-bound oriented normals
- historical solver artifact
- derivative tables
- residual logs
- B1.4K primary solver/output provenance
- B1.4L primary solver/output provenance

Thus:

`EXACT_HISTORICAL_TWO_JUNCTION_REPLAY = NOT_REPRODUCIBLE_FROM_SURVIVING_ARCHIVE`.

## 8. Governance firewall

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`

## 9. Next forensic target

The best remaining recovery target is no longer another derived MD2S branch. It is any still-unmatched export binary or original long MD-2S chat/PDF source that post-dates 2025-12-17 and could contain the missing historical equations, one-sided interface export, B1.4K/B1.4L primary output or residual provenance.
