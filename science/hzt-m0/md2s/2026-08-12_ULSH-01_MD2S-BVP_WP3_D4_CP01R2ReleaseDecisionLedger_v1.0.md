# ULSH-01 / WP3-D4 — CP01R2 Single-Use Release Decision Ledger v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Solver: `ULSH-01 / MD2S-BVP`  
Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Decision

**Status:** `PASS_WP3_D4_CP01R2_SINGLE_USE_RELEASE_AUTHORIZED_NO_EXECUTION`

**Decision ID:** `ULSH-01-WP3-D4-CP01R2-RELEASE-DEC-20260812-A`

WP3-D4 authorizes only the future issuance of one CP01R2 physical-solve authorization plus one fresh, single-use execution grant bound exactly to this decision. D4 itself does not create either runtime artifact and does not execute the physical solver.

The decision is based on the independently reviewed CP01R2 protocol, the immutable D3 run-input freeze, the D3 physical-binding review, the D3H1 transaction/result hardening, and the independent D3H1-RR1 review. RR1 verified `D3-B01` and `D3-B02` closed and reported no new release blockers.

## Frozen transaction identity

- `run_id = HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`
- `run_payload_sha256 = e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36`
- `schedule_sha256 = 929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b`
- `dependency_lock_sha256 = 4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f`
- baseline reviewed `main = 39c285f893c0c119fc5bc16d1966a5d9e7d7d2b9`

The future grant remains limited to 3600 seconds from issuance, uses a fresh 128–256-bit lowercase hexadecimal nonce, is permanently non-replayable after atomic spend, and cannot change parameters, topology, meshes, seeds, numerical thresholds, method, ordering, or failure ladder.

## No-execution firewall

At D4 completion:

- physical release **decision**: positive and single-use scoped;
- physical release authorization artifact: **absent**;
- single-use execution grant: **absent**;
- physical solve authorized by a runtime artifact: **false**;
- physical solver calls in D4: **0**;
- physical solve executed: **false**;
- physical evidence effect: **NONE**.

A release decision is governance permission to issue a future runtime authorization. It is not itself an executable grant and is not a physical result.

## Scientific interpretation

D4 establishes that the already frozen CP01R2 implementation/reproducibility path has cleared the required release-governance review. It does **not** establish convergence, existence or uniqueness of a continuum solution, continuum Jacobian invertibility/Fredholm properties, perturbative stability, ghost freedom, physical identification, or observational confirmation.

Scaled residuals, scaled conditioning, trust-region diagnostics and progress-continuation remain numerical diagnostics only. Candidate acceptance remains controlled exclusively by the frozen physical/raw acceptance criteria.

## Governance after D4

- `WP3 = RELEASE_DECIDED_SINGLE_USE_CP01R2_EXECUTION_PENDING`
- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

## Next allowed action

`ULSH-01_WP3_D5_CP01R2_SINGLE_USE_RELEASE_ARTIFACT_AND_FRESH_GRANT_ISSUANCE_THEN_IMMEDIATE_EXECUTION`

The release authorization and fresh grant must be issued only immediately before the single execution attempt so that grant validity is not consumed by an intervening review delay. Any spent grant is permanently non-replayable; any failure or indeterminate crash requires a fresh governance decision/grant path rather than silent retry.
