# ULSH-01 / C-PHYS — Background3C5 Operator Variable Consistency Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** FAIL_CLOSED_OPERATOR_IDENTITY_MISMATCH  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This audit compares the implementation-only module

`2026-08-15_hzt_background3c5_finite_thickness_operator_v0.1.py`

against the currently authoritative Background3C5 equation freeze and normalization closure.

No numerical fit, convergence result or runtime success is relevant to this identity audit.

## 2. Authoritative geometric variables

The frozen C-PHYS metric is

`ds6^2 = exp(2A(r)) gbar_mn dx^m dx^n + dr^2 + L(r)^2 dchi^2`,

with

`B_geo = L'/L`,

and regular-axis conditions

`L(0)=0`, `L'(0)=1`, `A'(0)=0`, `phi'(0)=0`.

Thus near a regular axis

`L(r)=r+O(r^3)`

and

`B_geo(r)=1/r+O(r)`.

The frozen equations use `L`, `L'/L`, and `L''/L` in this meaning.

## 3. Mismatch A — B semantics

The implementation-only v0.1 profile contains a field named `B` and evaluates terms such as

`exp(-2 B)`, `B'`, and `3 A' + B' - C'`.

Those operations are compatible with a logarithmic metric warp coordinate, e.g. `B_log = ln L`, but they are not compatible with the frozen definition `B_geo=L'/L`.

At the regular axis:

- frozen `B_geo ~ 1/r`,
- logarithmic `B_log ~ ln r`.

They are distinct variables with distinct dimensions and asymptotics.

**Verdict:** `B_VARIABLE_IDENTITY = FAIL`.

## 4. Mismatch B — extra C warp variable

The frozen metric gauge has radial line element `dr^2`; no independent radial lapse/warp field `C(r)` occurs in the authoritative metric ansatz.

The implementation-only v0.1 introduces `C`, `C'`, and multiple `exp(±2C)` factors without a provenance-bound coordinate transformation from the frozen proper-radial gauge.

A coordinate reparameterization could in principle introduce a radial lapse, but such a transformation has not been frozen or proven equivalent here.

**Verdict:** `C_VARIABLE_IDENTITY = UNPROVEN_AND_NOT_BINDABLE`.

## 5. Mismatch C — Maxwell sector

The authoritative finite-thickness Maxwell sector is the internal angular gauge field

`A_chi(r)`, `F_rchi=A_chi'`,

with

`d/dr [ exp(4A) (Z_F/g6^2) A_chi'/L ] = - exp(4A) gSigma s^2 w/L`,

`w=n-gSigma A_chi`.

The implementation-only v0.1 instead reconstructs a quantity named

`At_prime = Q exp(-3A-B+C-gamma)/Z_F`

and defines an electric invariant from it.

No frozen map identifies that `Q/At_prime` sector with the internal `A_chi/F_rchi` sector.

**Verdict:** `MAXWELL_OPERATOR_IDENTITY = FAIL`.

## 6. Consequence

The v0.1 implementation may contain reusable software patterns, but it is not an executable representation of the currently frozen Background3C5 parent equations.

Therefore:

`BACKGROUND3C5_FINITE_THICKNESS_OPERATOR_v0.1 = QUARANTINED_IDENTITY_MISMATCH`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`CENTER_SERIES_MAY_NOT_BE_DERIVED_FROM_OPERATOR_v0.1 = TRUE`

`RANK_R_CLAIM_ALLOWED = FALSE`

This is a software/theory binding failure, not evidence against existence of a solution of the frozen equations.

## 7. Correct next representation

G2 center regularity must be derived directly in the authoritative variables

`(A, L, phi, s, A_chi)`

with fixed discrete winding/flux labels and proper-radial gauge.

Only after that derivation is frozen may a replacement executable kernel be built around a regular center variable such as

`ell(r)=L(r)/r`

rather than numerically evolving `L'/L` through its explicit `1/r` singularity.

## 8. Status

**Result:** falsified/blockiert for direct operator binding.  
**Theory status:** unchanged.  
**Next gate:** G2 regular-center series in authoritative variables.
