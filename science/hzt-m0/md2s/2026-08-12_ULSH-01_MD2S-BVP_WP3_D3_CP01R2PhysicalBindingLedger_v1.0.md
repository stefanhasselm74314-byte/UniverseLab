# ULSH-01 / WP3-D3 — CP01R2 Physical Target Binding + Release-Readiness Review v1.0

**Date:** 2026-08-12  
**Architecture:** HPVS → HZT-M0 → HZT-Full  
**Solver:** ULSH-01 / MD2S-BVP  
**Run:** `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Purpose

WP3-D3 binds the independently reviewed ETRN-01 method to the exact frozen M1 physical source surfaces while preserving the CP01R1 physical sector and all scientific acceptance gates. This package is strictly **NO EXECUTION**.

Because the numerical method changed after the negative CP01R1 outcome, CP01R2 receives a fresh immutable run identity and frozen payload. The physical parameters, topology, alpha_H, seven seeds, node counts, physical residual assembly and scientific QA thresholds remain unchanged.

## Binding result

The source-contract mapping is complete for:

- primary M1 model/sector construction;
- exact collocation residual and boundary residual assembly;
- complex-step Jacobian;
- admissibility gate;
- exact seven-seed adapter;
- deterministic Lobatto prolongation semantics;
- ETRN-01 scaled linear-solve geometry with original-residual acceptance firewall;
- independent x-space shooting backend dispatch after a primary local-root gate;
- unchanged residual, constraint, convergence, spectral, condition and >=80-bit QA requirements.

No physical backend is imported by the D3 audit, no physical residual is evaluated, and no nonlinear solver call occurs.

## Release-readiness result

Physical target binding passes, but **release readiness is blocked** by two remaining transaction-level items.

**D3-B01 — CP01R2 transaction supervisor binding.** The proven H3 transaction supervisor is still CP01R1-specific. CP01R2 needs its own append-only source-bound transaction supervisor preserving single-use grant spend, fail-closed thread/network/resource policy, per-stage and total deadlines, result-size budget, machine attestation, JSON-safe nonfinite handling, atomic immutable commit, COMMITTING_RESULT recovery and replay denial.

**D3-B02 — CP01R2 result-package closure.** The result schema/package must explicitly capture the new ETRN-01 raw/scaled rank-condition diagnostics, trust-radius/rho history and progress-continuation provenance while retaining every legacy scientific QA artifact required by CP01R1.

These are implementation/reproducibility blockers, not evidence about the physical M1 BVP.

## Governance

- WP3: `OPEN_CP01R2_PHYSICAL_TARGET_BOUND_RELEASE_READINESS_BLOCKED_BY_TRANSACTION_CLOSURE`
- WP4: `BLOCKED`
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical solve authorized: `false`
- physical solve executed: `false`
- physical evidence effect: `NONE`

## Next allowed action

`ULSH-01 / WP3-D3H1 — CP01R2 transaction supervisor + immutable result closure hardening, NO EXECUTION.`

No CP01R2 release authorization or single-use execution grant may be issued until D3-B01 and D3-B02 are independently verified closed.
