# ULSH-01 / C-PHYS — Background-3C5 Equation Freeze Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** PARTIAL_FREEZE_ONLY / PHYSICAL_EXECUTION_BLOCKED  
**Governance:** K1-D = NOT_RELEASED; K1-E = NOT_ADMISSIBLE; evidence_effect = NONE

## 1. Scope

This artifact records the maximum equation set that can be frozen without inventing missing 6D coefficients or conventions. It is an authorization artifact, not a physical result.

## 2. Frozen ansatz and fields

Metric:

`ds_6^2 = exp(2 A(r)) gbar_{mu nu} dx^mu dx^nu + dr^2 + L(r)^2 dchi^2`

with `gbar_{mu nu}` maximally symmetric and `gbar R_{mu nu} = 3 K4 gbar_{mu nu}`.

Finite-thickness layer:

`Sigma = s(r)/sqrt(2) * exp(i n chi)`

`w(r) = n - gSigma A_chi(r)`

Dynamical radial profiles:

`A(r), L(r), phi(r), s(r), A_chi(r)`.

Discrete branch labels:

`n in Z`, `N in Z`.

They MUST remain fixed during the continuous response-rank scan.

## 3. Frozen finite-thickness parent sector

The local layer action is frozen as

`S_layer = - integral d^6X sqrt(-g) [ 1/2 (partial s)^2 + 1/2 s^2 (D thetaSigma)^2 + V_Sigma(s,phi) ]`

with

`D_A thetaSigma = partial_A thetaSigma - gSigma A_A`,

`V_Sigma(s,phi) = Lambda_layer(phi) + 1/2 mSigma^2(phi) s^2 + lambdaSigma/4 s^4`,

`mSigma^2(phi) = mSigma0^2 + etaSigma (phi - phi_*)`.

The layer thickness is derived from the solved `s(r)` profile and is NOT an independent control.

## 4. Frozen local energy channels

`E_r = 1/2 s'^2`

`E_chi = 1/2 s^2 w^2 / L^2`

`rho_F = Z_F F_{r chi}^2 / (2 L^2)`

Stress components:

`T^mu_mu = -E_r - E_chi - V_Sigma - rho_F`

`T^r_r = +E_r - E_chi - V_Sigma + rho_F`

`T^chi_chi = -E_r + E_chi - V_Sigma + rho_F`

The local stress-basis rank is exactly 3. This is a structural result only.

## 5. Frozen layer amplitude equation

For the radial ansatz:

`s'' + (4 A' + L'/L) s' - (w^2/L^2) s - partial_s V_Sigma = 0`.

For the explicit potential family:

`partial_s V_Sigma = mSigma^2(phi) s + lambdaSigma s^3`.

Therefore:

`s'' + (4 A' + L'/L) s' - (w^2/L^2) s - mSigma^2(phi) s - lambdaSigma s^3 = 0`.

## 6. Maxwell sector — structure frozen, normalization NOT frozen

The finite-thickness parent sector requires a local winding current in the chi component,

`nabla_A F^{A chi} proportional_to - gSigma s^2 w / L^2`.

The exact prefactor and sign in solver-normalized form depend on the missing canonical `Z_F` / gauge convention register and the exact bulk Maxwell normalization. Therefore the executable Maxwell ODE MUST remain blocked until that register is provenance-bound.

## 7. Stabilizer equation — NOT frozen

The exact `phi(r)` equation cannot yet be frozen because the complete canonical bulk scalar action, kinetic normalization and full `V(phi)` definition have not been recovered in the present source set.

The layer contribution is structurally fixed through

`partial_phi V_Sigma = partial_phi Lambda_layer(phi) + 1/2 partial_phi mSigma^2(phi) s^2`,

with `partial_phi mSigma^2 = etaSigma`, but this is insufficient to reconstruct the full stabilizer equation.

## 8. Einstein equations — geometry fixed, source normalization NOT frozen

The metric ansatz and local layer stress directions are fixed. However the exact executable Einstein system cannot be frozen until all of the following are provenance-bound from the canonical SCI-001 bulk action:

1. Einstein-Hilbert normalization (`M6^4/2`, `1/(2 kappa6^2)`, or equivalent canonical convention),
2. cosmological-term placement and sign,
3. stabilizer kinetic normalization,
4. stabilizer potential normalization,
5. Maxwell normalization and `Z_F` convention,
6. relation `M6^4 <-> kappa6^{-2}` used by the canonical register.

No coefficient is to be guessed from standard textbook conventions.

## 9. Boundary and regularity conditions frozen

At the smooth center:

`L(0)=0`

`L'(0)=1`

`A'(0)=0`

`phi'(0)=0`

and for `n != 0`:

`s(0)=0`.

Outside the layer zone:

`s(r) -> 0` when `mSigma^2(phi)>0`.

Gauge regularity and global flux quantization must hold simultaneously. The flux integer `N` is fixed during a continuous Jacobian scan.

## 10. Junction system frozen

At a regulated ring interface define

`A_Sigma = sum_s n_s^r A'_s`

`L_Sigma = sum_s n_s^r (L'_s/L_s)`.

For a winding-supported surface source:

`M6^4 (-3 A_Sigma - L_Sigma) = -lambda - 1/2 Y_sigma`

`M6^4 (-4 A_Sigma) = -lambda + 1/2 Y_sigma`

hence

`Y_sigma = M6^4 (L_Sigma - A_Sigma)`.

Pure tension requires `A_Sigma = L_Sigma`.

These equations are interface relations and do not close the bulk BVP by themselves.

## 11. Continuous controls frozen for the response-rank program

At fixed `(n,N)`:

`c = (Lambda6/Lambda_ref, Lambda_layer/Lambda_ref, mSigma^2/mref^2, gSigma, lambdaSigma)`.

Target response vector:

`y = (delta_beta/beta, delta_Xi, delta_U_umb, delta_m0^2 Rcap^2)`.

The structural incidence rank is 4, but this does NOT imply global physical response rank 4.

## 12. Equation-freeze verdict

### FROZEN

- metric ansatz and field content,
- finite-thickness scalar parent sector,
- winding definition and discrete-branch treatment,
- local energy/stress decomposition,
- layer amplitude ODE,
- center and outer regularity structure,
- two metric junction equations,
- response controls and outputs,
- prohibition on free layer-thickness and free radion-boundary-mass proxies.

### NOT FROZEN / HARD BLOCKERS

- complete canonical SCI-001 bulk action,
- exact Einstein-equation coefficients,
- exact stabilizer ODE,
- exact Maxwell ODE normalization/sign in the canonical `Z_F` convention,
- full dimensional normalization map,
- provenance-bound canonical equation register.

## 13. Authorization status

`BACKGROUND3C5_EQUATION_FREEZE = PARTIAL`

`BACKGROUND3C5_PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`REASON = CANONICAL_BULK_ACTION_AND_ZF_GAUGE_REGISTER_NOT_PROVENANCE_BOUND`

The next admissible action is recovery or reconstruction-from-authoritative-source of the canonical SCI-001 v0.1 bulk action and convention register, followed by an independent symbolic variation and dimensions/sign audit. Only then may `background3c5_kernel_v1_0.py` be promoted from contract to physical implementation.
