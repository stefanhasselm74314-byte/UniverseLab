# ULSH-01 / WP3-D6H1 — CP01R2 Finalization + Durable Write-Ahead Hardening v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Solver: `ULSH-01 / MD2S-BVP`  
Run family: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Status

`PASS_D6H1_IMPLEMENTED_NO_EXECUTION_PENDING_INDEPENDENT_REVIEW`

WP3-D6H1 is an append-only software/reproducibility hardening step after the spent, non-replayable CP01R2 attempt in GitHub Actions run `31573154936`. It does not rerun that attempt, does not issue a new authorization/grant and does not change any physical or numerical acceptance input.

## D6-B01 closure implementation

CP01R2 legitimately stores terminal progress states that are not local roots. The inherited CP01R1 finalizer assumed that an N=96 state implied a local root and could therefore leave `classification` unassigned.

The hardened target defines a total CP01R2 N=96 classification vocabulary:

- `N96_TIMEOUT_NO_RETRY`
- `N96_SKIPPED_AFTER_TIMEOUT_NO_RETRY`
- `NO_N96_TERMINAL_STATE`
- `N96_TERMINAL_STATE_NO_LOCAL_ROOT`
- `N96_LOCAL_ROOT_PRESENT_PENDING_QA`
- `N96_LOCAL_ROOT_REJECTED_BY_QA`
- `N96_LOCAL_ROOT_ACCEPTED_DIAGNOSTIC_CANDIDATE`

Only an N=96 terminal state that exists **without** the frozen local-root gate is omitted from the compatibility view passed to the inherited CP01R1 candidate finalizer. The real terminal state remains durably checkpointed. A true local root is never removed or weakened, and all original raw acceptance thresholds remain authoritative.

## D6-B02 closure implementation

Before the schedule can advance, every completed, timed-out or skipped entry is written as a strict-JSON checkpoint using:

1. exact frozen ordinal / entry / seed / node identity;
2. nonfinite diagnostic projection to `null` with exact path/kind/reason provenance;
3. terminal state vector for completed stages;
4. exclusive checkpoint creation;
5. file `fsync`;
6. atomic rename;
7. directory `fsync`;
8. SHA-256 previous-checkpoint chain;
9. atomic `state.json` chain-head pointer.

A gap, duplicate, schedule mismatch or hash-chain mismatch fails closed.

After the 35-entry loop, the finalization input matrix is rebuilt from the durable checkpoint records. Terminal state vectors are reloaded from the checkpoints and residual details are recomputed from those persisted states. The transient in-memory `entries` list is therefore no longer the authoritative post-loop input.

The hardened transaction wrapper additionally writes `checkpoint-recovery.json` into the spent-grant directory whether the child target exits successfully or fails. Thus a future finalizer/package failure cannot erase the already durable numerical prefix.

## Scientific firewall

No physical equation, parameter, topology, seed, mesh, ETRN-01 rule, progress-continuation rule, raw residual threshold, independent-backend requirement or higher-precision audit is changed.

A checkpoint proves only that a numerical schedule record was durably preserved. It is not candidate acceptance, continuum existence, uniqueness, Fredholmness, ghost freedom, K1-D release, K1-E admissibility or physical confirmation.

The failed D5 numerical outcome remains:

`INDETERMINATE_UNPRESERVED_DUE_FINALIZATION_FAILURE`

Nothing in D6H1 retroactively upgrades that failed attempt.

## Governance

- old D5 grant: `SPENT / NON-REPLAYABLE`
- D6-B01: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW`
- D6-B02: `IMPLEMENTED_PENDING_INDEPENDENT_REVIEW`
- future D6H1 release authorization: `ABSENT`
- future D6H1 single-use grant: `ABSENT`
- physical execution in D6H1: `NO`
- `WP3 = OPEN_CP01R2_D6H1_HARDENING_PENDING_INDEPENDENT_REVIEW`
- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

## Next allowed action

If and only if an independent no-execution review verifies both blocker closures and introduces no new release blocker:

`ULSH-01 / WP3-D6R1 — CP01R2 fresh release decision — NO EXECUTION`

A new physical attempt requires a fresh release decision and a new single-use grant. The spent D5 grant and workflow run must never be replayed.
