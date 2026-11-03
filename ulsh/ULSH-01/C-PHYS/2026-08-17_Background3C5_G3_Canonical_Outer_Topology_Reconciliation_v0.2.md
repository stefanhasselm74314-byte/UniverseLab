# ULSH-01 / C-PHYS — Background3C5 G3 Canonical Outer Topology Reconciliation v0.2

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** CANONICAL_OUTER_MODE_IDENTIFIED / BACKGROUND3C5_TOPOLOGY_EQUIVALENCE_NOT_RATIFIED / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Purpose

Append-only correction to the G3 v0.1 audit after recovery of current merged MD2S/C-PHYS canonical contracts that were not incorporated into the initial outer-target search.

This document distinguishes two questions that must not be conflated:

1. What outer topology is canonical for the governed ULSH-01 / MD2S M1 BVP?
2. Has the one-region finite-thickness Background3C5 candidate in PR #137 been proven topology/operator equivalent to that canonical BVP?

The answer to (1) is now fixed. The answer to (2) remains no.

## 2. Canonical outer topology

The merged `registry/2026-08-03_MD2S_C1_BVPPreflightContract_v0.1.json` freezes a two-region geometry:

- two smooth disk regions `N` and `S`;
- one regular pole in each region;
- both radial coordinates run from their pole to a common codimension-1 cap;
- the full BVP is closed by cap/patch/junction residuals rather than an asymptotic smooth-bulk boundary at infinity.

Its eight continuous global unknowns are

`(phi_N0, Q_N, A_S0, phi_S0, Q_S, rho_N, rho_S, K4)`

with `A_N0=0` and regular pole gauges fixed.

The independent global residual vector is

`R = (R_A, R_L, R_phi, R_patch, R_4d, R_chi, R_scalar, R_gauge)`

with

`R_A = A_N(rho_N)-A_S(rho_S)`,

`R_L = L_N(rho_N)-L_S(rho_S)`,

`R_phi = phi_N(rho_N)-phi_S(rho_S)`,

`R_patch = A_chi,N(rho_N)-A_chi,S(rho_S)-N_F/q0`,

`R_4d = -(3 A_Sigma + L_Sigma) + kappa6^2 (lambda + Y_sigma/2)`,

`R_chi = -4 A_Sigma + kappa6^2 (lambda - Y_sigma/2)`,

`R_scalar = phi_N' + phi_S' + lambda1`,

`R_gauge = exp(-4A)/L (Q_N+Q_S) - q0 z_sigma0 d_chi/L^2`.

The global flux condition is counted once through the two-patch relation; the rr constraints are propagated QA channels, not additional endpoint conditions.

Therefore, for the canonical governed MD2S C1/M1 topology,

`OUTER_MODE = CAP_OR_BRANE_JUNCTION_HANDOFF`.

`SMOOTH_BULK_HANDOFF` is not the canonical full-BVP outer mode.

## 3. Persistence into the later M1 / CP01R3 program

The merged Background-3A assembly correction explicitly preserves the M1 topology-correction contract and freezes

`8N profile/global bulk rows + 8 cap/global boundary rows = 8N+8 residuals`

against `8N+8` unknowns.

The merged CP01R3 protocol then states that, relative to CP01R2, all of the following are unchanged:

- M1 physical parameters;
- topological sector;
- physical ODEs;
- all eight boundary residual equations;
- acceptance thresholds.

CP01R3's BJP-01 projection acts specifically on the frozen junction equations `R_4D=R_chi=0` while preserving the other six boundary residuals and the pole/brane endpoint values.

Thus no merged canonical artifact found in the C1 -> M1 -> CP01R3 chain replaces the two-pole/common-cap topology by an asymptotic one-region smooth-bulk topology.

## 4. Correction to G3 v0.1 counting

G3 v0.1 used the local one-region G2 center family `(varphi_0,g_2,s_|n|)` and inferred that an executable square problem should contain exactly three continuous outer mismatches.

That counting is valid only for a one-sided local subproblem after all data supplied by the second region/cap have already been fixed externally.

It is NOT the canonical count for the full governed ULSH-01 / MD2S BVP.

For the canonical full two-region BVP, the established structural count is instead

`8 continuous global unknowns <-> 8 independent cap/patch/global residuals`.

At fixed `K4`, the older canonical preflight gives seven continuous unknowns against eight residuals, generically codimension one unless exactly one declared model/eigenparameter is promoted or one independent target condition is released by a separately ratified contract.

Therefore the statements

`three center amplitudes -> exactly three global mismatches`

and

`G3_GLOBAL_BVP_COUNT = SQUARE_CONDITIONAL_ONLY` based solely on that three-dimensional map

must not be used as the full ULSH-01 BVP count.

## 5. Finite-thickness Background3C5 reconciliation blocker

PR #137 introduces a coefficient-fixed finite-thickness local candidate with fields

`(A, ell, varphi, s_hat, a_chi)`

and proves useful local results (regular-center structure, coefficient normalization, Maxwell source normalization, constraint propagation).

However, no current merged canonical artifact was found that proves that this one-region finite-thickness formulation:

- replaces the canonical two-region common-cap topology;
- is a derived reduction of the two-region cap BVP;
- supplies the second-region data implicitly;
- replaces the eight canonical cap/patch residuals by a three-mismatch outer map;
- or preserves the exact canonical junction/patch problem after adding the finite-thickness field.

Hence the finite-thickness local operator may not be bound to the official ULSH-01 physical solver merely by choosing `CAP_OR_BRANE_JUNCTION_HANDOFF` in the existing template.

A topology/operator bridge is required first.

## 6. Required bridge before G3 full closure

The next admissible theory artifact must explicitly choose and derive one of the following:

### A. Two-region finite-thickness extension

Extend the coefficient-fixed finite-thickness sector to both `N` and `S` regions and derive the cap equations from the same parent action. Then prove which of the canonical eight residuals remain unchanged and which are modified by finite-thickness stress/current terms.

### B. Proven one-region reduction

Derive a mathematically controlled reduction in which the second region plus cap are replaced by an effective boundary operator. The resulting effective boundary map must be derived from the canonical two-region parent problem, not postulated. Its dimension/count must follow from the eliminated degrees of freedom.

Without A or B, direct physical binding is blocked.

## 7. G3.1 verdict

`CANONICAL_MD2S_OUTER_MODE = CAP_OR_BRANE_JUNCTION_HANDOFF` — **PASS_CANONICAL**

`CANONICAL_FULL_BVP_RESIDUAL_COUNT = 8` — **PASS_STRUCTURAL**

`CANONICAL_FULL_BVP_CONTINUOUS_UNKNOWN_COUNT = 8` — **PASS_STRUCTURAL**

`BACKGROUND3C5_ONE_REGION_TO_CANONICAL_TWO_REGION_EQUIVALENCE = NOT_RATIFIED`

`THREE_MISMATCH_FULL_BVP_INTERPRETATION = SUPERSEDED_FOR_FULL_ULSH01`

`G3_FULL_EXECUTABLE_TARGET = BLOCKED_PENDING_TOPOLOGY_OPERATOR_BRIDGE`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence status is changed by this reconciliation.