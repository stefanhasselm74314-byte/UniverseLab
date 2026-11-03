# ULSH-01 / C-PHYS — Background-3C5 Normalization Bridge Gate v0.1

**Status:** TWO_IDENTITY_BLOCKER / FAIL_CLOSED  
**Evidence effect:** NONE  
**Physical execution:** NOT AUTHORIZED

## 1. Purpose

The recovered sources now fix the dimensionful SCI-001 bulk action, the M1 potential and gauge kinetic function, the finite-thickness layer action, and the metric/Junction conventions. The remaining ambiguity is no longer a general missing-action problem. It is a narrow normalization bridge between two notational layers of the project.

## 2. Bridge A — scalar field normalization

Recovered dimensionful convention:

`[Phi]=M^2`

`L_Phi = -1/2 (d Phi)^2 - V6(Phi)`.

Recovered M1 convention:

`U(phi)=1/2*mhat_phi^2*M6^6*phi^2`

`Z_F(phi)=exp(-2*a_F*phi)`.

The dimensionally natural mapping is

`Phi = M6^2 phi`.

Under this mapping:

`-1/2(dPhi)^2 = -M6^4/2 (dphi)^2`,

and a mass `m_phi^2=mhat_phi^2*M6^2` gives

`1/2 m_phi^2 Phi^2 = 1/2 mhat_phi^2 M6^6 phi^2`.

This is internally dimensionally consistent and uniquely natural under canonical scalar normalization. It is NOT promoted to canonical status merely from dimensional consistency.

**Gate A:** provenance-bound statement of either `Phi=M6^2 phi` or the exact alternative field redefinition plus M1 kinetic prefactor.

## 3. Bridge B — gauge/charge normalization

Recovered SCI-001 Maxwell convention:

`L_F = - Z_F/(4 g6^2) F^2`, with `[g6^2]=M^-2`.

Recovered M1 charge definitions:

`q_ref=qhat/M6`,

`q_sigma=m_sigma*q_ref`.

Recovered finite-thickness layer notation:

`D_A thetaSigma=partial_A thetaSigma-gSigma*A_A`,

`w=n-gSigma*A_chi`.

The exact canonical relation among `g6`, `q_ref`, `q_sigma`, and `gSigma` is not independently present in the currently surfaced source set.

The v0.3 shorthand

`rho_F=Z_F F_rchi^2/(2L^2)`

also does not state whether `1/g6^2` has been absorbed into `Z_F`, into the gauge field normalization, or merely suppressed typographically.

**Gate B:** provenance-bound gauge-field normalization and exact identification of the charge entering `w` relative to the SCI-001 Maxwell normalization.

## 4. Why the gate matters

A constant field rescaling

`A_A -> c A_A`

moves factors between the Maxwell kinetic coefficient and the charge:

`gauge kinetic coefficient -> gauge kinetic coefficient / c^2`,

`charge -> charge / c`.

Therefore two convention choices can describe identical physics while producing numerically different raw `A_chi`, flux, and Jacobian columns. A response-rank computation before freezing this bridge is not reproducibly normalized.

## 5. Admission rule

Background-3C5 executable M1 equations may be promoted only when both are satisfied:

- `BRIDGE_A_SCALAR_NORMALIZATION = PASS`
- `BRIDGE_B_GAUGE_CHARGE_NORMALIZATION = PASS`

Until then:

`BACKGROUND3C5_KERNEL = IMPLEMENTATION_CANDIDATE_ONLY`

`PHYSICAL_BVP_RUN = FORBIDDEN`

`PHYSICAL_RESPONSE_RANK_R = OPEN`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

## 6. Non-admissible shortcuts

The following do NOT close this gate:

- choosing `M6=1` numerically,
- absorbing `g6` into `A_chi` without a register entry,
- identifying `gSigma=q_sigma` by name similarity,
- obtaining a small residual,
- obtaining rank 4 in a synthetic or convention-dependent Jacobian,
- tuning charge parameters to recover a historical benchmark.

Technical solvability is not physical identification.
