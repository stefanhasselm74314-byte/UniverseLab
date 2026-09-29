# ULSH-01 / C-PHYS — Background3C5 G4 Constraint Propagation Closure v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** G4_ANALYTIC_BIANCHI_NOETHER_IDENTITY_CLOSED / SOFTWARE_QA_PENDING  
**Physical evidence effect:** NONE  
**Physical execution:** NOT AUTHORIZED  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This closure concerns only the local radial constraint-propagation identity of the coefficient-fixed finite-thickness operator candidate v0.3. It does not establish global BVP existence, uniqueness, convergence, branch continuity or response rank.

The canonical local residuals are

- `E_A` : chi-chi Einstein residual,
- `E_ell` : ell times the four-dimensional Einstein residual,
- `E_varphi` : ell times the scalar residual,
- `E_s` : finite-thickness amplitude residual,
- `E_flux` : conservative Maxwell flux residual,
- `C_rr` : ell times the radial Einstein constraint residual.

Define

`R_rr := C_rr/ell`,

`R_mu := E_ell/ell`,

`R_chi := E_A`.

## 2. Exact radial identity

For smooth fields with `ell>0`, direct symbolic differentiation of the coefficient-fixed v0.3 residual system gives

`dR_rr/dx + 4 A_x (R_rr - R_mu) + (ell_x/ell)(R_rr - R_chi)`

`+ (E_varphi/ell) varphi_x + E_s s_x + exp(-4A)(a_chi,x/ell) E_flux = 0`.

Equivalently,

`B_G4 := dR_rr/dx + 4 A_x (R_rr - R_mu) + (ell_x/ell)(R_rr - R_chi)`

`        + (E_varphi/ell) varphi_x + E_s s_x + exp(-4A)(a_chi,x/ell) E_flux = 0`.

This is the reduced radial Bianchi/Noether identity for the frozen proper-radial gauge.

## 3. Consequence

If the local evolution/matter/gauge residuals vanish,

`R_mu = 0`, `R_chi = 0`, `E_varphi = 0`, `E_s = 0`, `E_flux = 0`,

then

`dR_rr/dx + (4 A_x + ell_x/ell) R_rr = 0`.

Therefore

`R_rr(x) = const * exp(-4A(x))/ell(x)`.

Regular-axis data with finite physical radial constraint and `ell ~ x` force the integration constant to vanish. Hence a regular solution satisfying the constraint at the axis propagates

`R_rr = 0`

through the connected smooth branch.

This removes the radial Einstein equation as an independent bulk evolution equation once the remaining local equations and one regular constraint condition are imposed.

## 4. Axis caveat

The displayed identity is written for `ell>0`; the axis itself is singular in the coordinate ratio `ell_x/ell ~ 1/x`. The correct axis statement is obtained by the G2 Frobenius series. No numerical evaluation at exactly `x=0` is required or permitted by the candidate operator.

## 5. Gauge-sector sign and normalization check

The gauge term is fixed uniquely by the conservative residual

`E_flux = d/dx[exp(4A) Z_F a_chi,x/ell] + Gamma_Sigma exp(4A) s_hat^2 w/ell`,

with

`Gamma_Sigma = m_layer q_hat`.

The Bianchi identity contains

`+ exp(-4A)(a_chi,x/ell) E_flux`.

Changing the Maxwell-source sign or reintroducing the quarantined factor two destroys the exact cancellation.

## 6. Status

[BEWIESEN] Local continuum Bianchi/Noether identity for the coefficient-fixed v0.3 residual system.

[BEWIESEN] Constraint propagation on every connected smooth `ell>0` branch, conditional on the remaining local residuals vanishing and on one regular constraint condition.

[KONDITIONAL] Axis propagation uses the already-closed G2 regular-center Frobenius branch.

[OFFEN] Global BVP existence, outer matching, nonlinear convergence, uniqueness/multiplicity and physical response rank.

Therefore:

`G4_ANALYTIC_CONSTRAINT_PROPAGATION = PASS`

`G4_SOFTWARE_REGRESSION = PENDING`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`
