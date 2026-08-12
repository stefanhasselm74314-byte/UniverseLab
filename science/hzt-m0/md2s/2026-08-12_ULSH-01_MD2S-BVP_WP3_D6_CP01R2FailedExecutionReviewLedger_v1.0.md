# ULSH-01 / WP3-D6 — CP01R2 Failed Execution Review Ledger v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`  
GitHub Actions run: `31573154936`  
Triggering `main`: `c9ebdb8c2a0ccb892e0d95d4c2d2d8ab48d4715a`

## Review result

`BLOCKED_WP3_D6_CP01R2_RESULT_REVIEW_FINALIZATION_DEFECT_NO_REPLAY`

The D5 fresh recheck and runtime issuance passed. The single-use grant was then irreversibly spent. The physical target ran for approximately 1004.74 seconds after grant spend and failed only after the schedule loop reached the legacy result finalizer. No immutable scientific result package was committed.

The preserved Actions artifact is:

- artifact id: `9132540539`
- ZIP SHA-256: `e34e11495707b4f96070e348148a80c7d045a53fa029f9a02798786dbc4335ba`
- transaction state: `FAILED`
- verification: `NOT_COMMITTED`
- replay: `false`

## Exact failure

The target process returned code 1 with:

`UnboundLocalError: cannot access local variable 'classification' where it is not associated with a value`

The exception occurred in the inherited CP01R1 `_finalize(...)` routine. CP01R2 stores an internal terminal state after every normally completed mesh stage so that a sufficiently improved, admissible non-root state can seed the next mesh. The CP01R1 finalizer had an older invariant: inside the `n96_key in internal_states` branch it assigns `classification` only when `has_n96_root` is true. CP01R2 therefore reached a new valid numerical control state — N=96 state present but not a local root — for which the legacy finalizer left `classification` undefined.

This is a **software/result-closure defect**, not a physical rejection and not a positive candidate result.

## What can and cannot be inferred

Because the traceback is at the post-loop finalization call, the exact frozen control flow proves that all 35 schedule entries had reached either their normal append path or the preregistered StageTimeout append path in memory before finalization began. It also proves that at least one seed had an N=96 terminal state without satisfying the local-root gate.

However, the per-entry matrix was still only in child-process memory. The finalization exception occurred before the raw result was serialized and before the transaction could commit an immutable result package. Therefore the numerical values, candidate count, residual matrix, ETRN histories, rank/condition histories, continuation provenance, and any independent-backend records are **not recoverable from the preserved artifact**.

The only admissible numerical classification is:

`INDETERMINATE_UNPRESERVED_DUE_FINALIZATION_FAILURE`

It is forbidden to relabel this run as either `NO_CANDIDATE` or `CANDIDATE`.

## New release blockers

**D6-B01 — finalizer semantic compatibility.** CP01R2 needs a deterministic finalizer path for all combinations of N=96 state presence and local-root status, including progress states without local roots. Regression fixtures must cover non-root progress, root rejected by QA, root accepted by QA, missing N=96 state, and timeout paths.

**D6-B02 — per-entry durable write-ahead closure.** Every completed/timed-out schedule record and required numerical provenance must be atomically checkpointed before advancing to the next entry. Finalization must consume those persisted records, so a later finalizer/packaging exception cannot erase the executed 35-entry matrix.

Neither blocker permits any change to the physical equations, fixed parameters, topology, seven seeds, five meshes, scientific thresholds, or ETRN-01 method semantics.

## Governance

The D4 single-use execution permission has been consumed by this attempt. The runtime grant nonce `feff4d8455f0589ea72743db57eceb72` is permanently spent and must never be replayed. A workflow rerun is forbidden. A new physical attempt requires D6 hardening, an independent no-execution re-review, and then a **fresh release decision and fresh grant path**.

Current state:

- `WP3 = OPEN_CP01R2_FAILED_EXECUTION_HARDENING_REQUIRED`
- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

## Next allowed action

`ULSH-01 / WP3-D6H1 — CP01R2 Finalization + Durable Per-Entry Write-Ahead Result Hardening — NO EXECUTION`
