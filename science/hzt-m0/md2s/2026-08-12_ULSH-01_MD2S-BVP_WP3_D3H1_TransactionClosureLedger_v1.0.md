# ULSH-01 / MD2S-BVP — WP3-D3H1 Transaction + Result Closure Ledger v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Scope

WP3-D3 identified two release blockers after the CP01R2 physical target was source-bound: D3-B01 (no CP01R2-specific hardened single-use transaction supervisor) and D3-B02 (no CP01R2-specific immutable result closure containing ETRN-01 diagnostics plus the legacy scientific QA set).

WP3-D3H1 implements those two closures **without issuing a release, without creating a grant and without executing CP01R2**. The independent RR1 in this package is the required post-hardening no-execution review.

## D3-B01 closure

The CP01R2 transaction path is now source-bound to the frozen CP01R2 run payload and 7x5 schedule. It preserves the proven H3 transaction invariants: immutable collision preflight before grant spend/backend initialization, exact release/grant/source-bundle binding, atomic single-use spend and permanent replay denial, one-thread fail-closed startup, machine/BLAS/LAPACK attestation, 1800-s stage limits, shared 21600-s total deadline, exact 8-GiB child `RLIMIT_AS`, result-size cap, no solver-network path, nonfinite JSON sanitation, atomic result commit and post-commit recovery as `COMMITTED_INDETERMINATE` when precommit hashes match.

The execution implementation is `...transaction_v1.0.py`; append-only `...transaction_v1.1.py` supplies the corrected static provenance audit while delegating any later authorized execution to the pinned v1.0 implementation.

## D3-B02 closure

The CP01R2 result schema preserves every legacy CP01R1 scientific QA channel and adds four mandatory ETRN-01 channels:

- raw Jacobian rank/condition history;
- scaled/equilibrated rank/condition history;
- trust-radius / rho / accepted-step history;
- deterministic progress-continuation provenance.

Scaling remains linear-solve preconditioning only. Acceptance continues to use the original unscaled physical residuals and the unchanged preregistered QA gates. Candidate profiles, result JSON, execution stdout/stderr and the manifest are hashed; profile hashes are written back into candidate records. The commit marker is written only after atomic rename and parent-directory fsync.

## Progress continuation clarification

The D1 rule says continuation is allowed after >=10% improvement in the original residual when the terminal state is finite, admissible and not timed out. Here `admissible` is bound to the primary physical-domain admissibility predicate. It is deliberately **not** bound to the legacy full final-QA admissibility object that includes boundary-acceptance conditions; requiring a local root there would recreate the CP01R1 continuation failure mode.

## Independent RR1

The independent review verifies eight gates: source/run identity, transaction closure, result closure, continuation semantics, synthetic result-package/nonfinite handling, replay and collision denial, resource/commit ordering, and the no-release/no-grant/no-execution firewall.

Synthetic tests create no physical state and call no solver. They prove only implementation/reproducibility properties.

RR1 disposition:

- `D3-B01 = VERIFIED_CLOSED`
- `D3-B02 = VERIFIED_CLOSED`
- `new_release_blockers = []`
- nonblocking warning H1-W01: Python-process socket denial is not claimed as a kernel network-namespace proof.

## Scientific firewall

No statement in WP3-D3H1 establishes CP01R2 convergence, continuum existence or uniqueness, continuum Jacobian invertibility/Fredholmness, perturbative stability, ghost freedom, physical identification or observational confirmation.

Current governance remains:

- `WP3 = OPEN`
- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `CP01R2 physical_solve_authorized = false`
- `CP01R2 physical_solve_executed = false`

## Next allowed action

`ULSH-01 / WP3-D4 — CP01R2 Single-Use Release Decision — NO EXECUTION`

A D4 decision may determine release eligibility. It may not reinterpret transaction readiness as a physical result.
