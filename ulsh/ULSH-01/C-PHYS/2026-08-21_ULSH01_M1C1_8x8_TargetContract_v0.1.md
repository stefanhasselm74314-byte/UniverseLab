# ULSH-01 / M1-C1 — Canonical 8×8 Target Contract v0.1

**Date:** 2026-08-21  
**Work package:** ULSH-01-WP1  
**Classification:** APPEND_ONLY_CANONICAL_WP1_TARGET_FREEZE_NO_SOLVER_EXECUTION  
**Status:** `ULSH01_WP1_CLOSED_CANONICAL_M1C1_8X8_TARGET_FROZEN`  
**Physical evidence effect:** `NONE`  
**Solver authorized:** `false`

## 1. Decision

ULSH-01-WP1 is closed at the level it is defined to govern: the physical-candidate BVP equation set, boundary conditions, regularity conditions, topology, field content and continuous/discrete variable roles are now frozen into one source-bound canonical target.

This is a **mathematical target freeze**, not a background solution and not an execution authorization.

Canonical target digest:

`SHA256:237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823`

The digest is calculated from the UTF-8 canonical JSON representation of `target_semantics` with sorted keys, compact separators and Unicode preserved.

## 2. Frozen field content

Frozen M1/C1 contains:

- 6D bulk: `g_AB`, `phi`, `A_A`;
- codim-1 common cap: `sigma_cap`;
- regional background profiles: `A_s`, `ell_s`, `varphi_s`, `a_chi_s`.

The smooth codim-0 development field `Sigma_FT` and its amplitudes `c_N`, `c_S` are **not part of this target**.

Therefore:

`SIGMA_FT = DEVELOPMENT_ONLY_NOT_RATIFIED_IN_FROZEN_M1_C1`

and the conditional finite-thickness `10×10` construction is not the canonical M1/C1 target.

## 3. Frozen topology and conventions

- Two smooth disk regions `N` and `S`.
- One regular pole per region.
- Both local radial coordinates increase from pole to the common cap.
- Local outward cap normals: `n_N = n_S = +1`.
- Global two-form orientation signs: `epsilon_N=+1`, `epsilon_S=-1`.
- `Delta_chi=2*pi`.
- Regular pole gauges: `a_chi_N(0)=a_chi_S(0)=0`.
- North-pole four-dimensional frame: `A_N(0)=0`.
- Fixed discrete sector per operator instance: `(N_F,N_sigma,m_sigma)`.
- Charge lattice: `q_ref=q_hat/M6`, `q_sigma=m_sigma*q_ref`.

The bundle condition is counted once:

`R_patch = a_chi_N(cap)-a_chi_S(cap)-N_F/q_hat = 0`.

The oriented global flux condition is equivalent to `R_patch` under the frozen gauges and orientation and is not an additional residual.

## 4. Exact M1 functions

With `varphi=phi/M6^2`:

- `U(phi)=0.5*mhat_phi_sq*M6^6*varphi^2`
- `Z_F(phi)=exp(-2*a_F*varphi)`
- `lambda(phi)=lambda_hat*M6^5`
- `Z_sigma(phi)=z_sigma_hat*M6^3`

External model coefficient order:

`(Lambda_hat, mhat_phi_sq, a_F, lambda_hat, z_sigma_hat, q_hat)`.

These coefficients are external to the BVP unknown vector and may not be silently promoted to shooting variables.

## 5. Independent regional bulk system

Define

`rho_F_s = 0.5*q_s^2*exp(-8*A_s+2*a_F*varphi_s)`.

For each `s in {N,S}` the independent equations are:

```text
E_A =
4*A_s_xx + 10*A_s_x^2 - 6*k4*exp(-2*A_s) + Lambda_hat
+ 0.5*varphi_s_x^2 + 0.5*mhat_phi_sq*varphi_s^2 - rho_F_s = 0

E_ell =
ell_s_xx + 3*A_s_xx*ell_s + 6*A_s_x^2*ell_s + 3*A_s_x*ell_s_x
- 3*k4*exp(-2*A_s)*ell_s + Lambda_hat*ell_s
+ ell_s*(0.5*varphi_s_x^2 + 0.5*mhat_phi_sq*varphi_s^2 + rho_F_s) = 0

E_varphi =
ell_s*varphi_s_xx + (4*A_s_x*ell_s + ell_s_x)*varphi_s_x
- ell_s*mhat_phi_sq*varphi_s + 2*a_F*ell_s*rho_F_s = 0

E_gauge =
a_chi_s_x - q_s*ell_s*exp(-4*A_s+2*a_F*varphi_s) = 0
```

The radial Einstein constraint is a propagated QA channel:

```text
C_rr =
ell_s*(-6*k4*exp(-2*A_s)+6*A_s_x^2+Lambda_hat)
+4*A_s_x*ell_s_x
-ell_s*(0.5*varphi_s_x^2-0.5*mhat_phi_sq*varphi_s^2+rho_F_s)
```

with the frozen identity

`C_rr_x + 4*A_x*C_rr = ell_x*E_A + 4*A_x*E_ell - varphi_x*E_varphi`.

It is **not** an extra nonlinear or endpoint residual.

## 6. Pole regularity

North pole:

`A_N(0)=0`, `A_N_x(0)=0`, `ell_N(0)=0`, `ell_N_x(0)=1`, `varphi_N_x(0)=0`, `a_chi_N(0)=0`.

South pole:

`A_S_x(0)=0`, `ell_S(0)=0`, `ell_S_x(0)=1`, `varphi_S_x(0)=0`, `a_chi_S(0)=0`.

Free pole data carried by the augmented vector are `varphi_N_0`, `A_S_0`, `varphi_S_0`. Conical pole defects are forbidden.

The frozen pole-regular chart uses `tau=(x_s/rho_s)^2 in [0,1]` and the affine parity forms from Operator-2B.

## 7. Canonical 8×8 boundary-value problem

Continuous augmented unknown vector:

```text
(varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4)
```

Independent boundary residual order:

```text
(R_A, R_ell, R_varphi, R_patch, R_4d, R_chi, R_scalar, R_gauge_local)
```

Continuity:

```text
R_A       = A_N(cap)-A_S(cap) = 0
R_ell     = ell_N(cap)-ell_S(cap) = 0
R_varphi  = varphi_N(cap)-varphi_S(cap) = 0
```

Cap quantities retain the frozen M1 notation:

```text
A_hat_Sigma = sum_s n_s*A_s_x(cap)
L_hat_Sigma = sum_s n_s*ell_s_x(cap)/ell_Sigma
d_chi       = N_sigma-m_sigma*q_hat*a_chi_Sigma
Y_hat_sigma = z_sigma_hat*d_chi^2/ell_Sigma^2
```

with `n_N=n_S=+1` and `ell_Sigma=ell_N(cap)=ell_S(cap)`.

Junction residuals:

```text
R_4d =
-3*A_hat_Sigma-L_hat_Sigma+lambda_hat+0.5*Y_hat_sigma = 0

R_chi =
-4*A_hat_Sigma+lambda_hat-0.5*Y_hat_sigma = 0

R_scalar =
varphi_N_x(cap)+varphi_S_x(cap) = 0

R_gauge_local =
sum_s[q_s*exp(-4*A_s(cap))/ell_Sigma]
-m_sigma*q_hat*z_sigma_hat*d_chi/ell_Sigma^2 = 0
```

The mathematical target intentionally preserves the source notation `a_chi_Sigma` in the gauge-invariant cap combination. WP2 must bind an explicit patch representation consistently with `R_patch`; that implementation choice may not change `d_chi` or the target semantics.

Structural result:

`8 continuous augmented unknowns ↔ 8 independent boundary/global residuals`.

For the frozen collocation assembly this becomes:

`8*N + 8 unknowns ↔ 8*N + 8 residuals`.

## 8. What WP1 closure does not prove

The following remain explicitly open:

- non-emptiness of `G^-1(0)`;
- physical background existence;
- uniqueness;
- Fredholm property;
- continuum BVP Jacobian rank;
- conditioning;
- perturbative stability;
- ghost freedom;
- physical response rank.

Hence:

```text
BACKGROUND_SOLVER_EXECUTION = NOT_AUTHORIZED
physical_background = NOT_ESTABLISHED
R1.1 = BLOCKED
R1.2 = BLOCKED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
physical_evidence_effect = NONE
```

WP1 closure does not authorize CP01R1 or an `a_F=1/4` target solve.

## 9. Implementation handoff

The next safe step is:

`RECONCILE_WP2_WP3_ASSETS_TO_EXACT_8X8_TARGET_DIGEST_IMPLEMENTATION_AND_QA_ONLY`

Every retained WP2/WP3 asset must either:

1. bind exactly to `SHA256:237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823`, or
2. be labeled development-only / incompatible / superseded for the canonical M1/C1 target.

No physical backend import, Jacobian evaluation, 41-job physical run or WP4 authorization follows automatically.

## 10. Source-bound authority

The machine-readable companion file records the exact repository paths and Git blob SHAs for the parent action, global convention freeze, M1 function freeze, Operator-2A, regularity preflight, Operator-2B, C1 BVP preflight, topology correction, assembly correction and the 2026-08-21 field-content provenance recovery.
