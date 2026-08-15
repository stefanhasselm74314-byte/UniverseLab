# ULSH-01 / C-PHYS — Background3C5 G2 Regular Center Series v0.2

**Supersedes:** v0.1 where this document is more restrictive.  
**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** CONDITIONAL_PASS_ANALYTIC_WITH_FROZEN_CONTROL_LIMIT  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Correction to v0.1 — A0 is already fixed

Freeze-1A / the M1 Function Freeze Contract explicitly removes the additive warp redundancy through

`A_N(0)=0`.

Therefore the north-axis expansion is not to be counted with a free `A0`:

`A(x)=a2 x^2 + a4 x^4 + ...`,

where the canonical dimensionless radius is

`x=M6 r`.

Likewise define

`ell(x)=M6 L(r)`, `varphi=phi/M6^2`, `a_chi=A_chi/M6`.

The regular-axis metric expansion is

`ell(x)=x+l3 x^3+l5 x^5+...`.

This fixes the local angular slope and forbids a continuous conical-rescue parameter.

## 2. Canonical regular center fields

Use

`A(x)=a2 x^2+a4 x^4+O(x^6)`,

`ell(x)=x+l3 x^3+l5 x^5+O(x^7)`,

`varphi(x)=f0+f2 x^2+f4 x^4+O(x^6)`,

`a_chi(x)=g2 x^2+g4 x^4+O(x^6)`.

For the finite-thickness amplitude:

- if `n != 0`, `s(x)=s_p x^p(1+alpha_s x^2+...)`, `p=abs(n)` after expressing `s` in the selected canonical dimensionless amplitude convention;
- if `n=0`, `s(x)=s0+s2 x^2+...`.

The winding combination is

`w=n-gSigma A_chi = n - m_layer*q_hat*a_chi`

because `gSigma=m_layer*q_hat/M6` and `A_chi=M6*a_chi`.

Hence `w` is dimensionless exactly as required.

## 3. Bulk-only frozen control limit

The already-frozen M1 Function Freeze Contract supplies exact pole coefficients for the corresponding bulk control system:

`a2_bulk = [6*k4 - Lambda_hat - 0.5*mhat_phi_sq*f0^2 + rho_F0]/8`,

`f2_bulk = [mhat_phi_sq*f0 - 2*a_F*rho_F0]/4`,

`g2_bulk = 0.5*q_s*exp(2*a_F*f0)`,

`l3_bulk = [3*k4 - 12*a2_bulk - Lambda_hat - 0.5*mhat_phi_sq*f0^2 - rho_F0]/6`,

where the canonical north frame has `A(0)=0` and

`rho_F0 = 0.5*q_s^2*exp(2*a_F*f0)`.

These coefficients are MODEL-DEFINITION/LOCAL-CONTROL results, not global-background evidence.

## 4. Mandatory finite-thickness regression condition

Any replacement finite-thickness center initializer and residual kernel must satisfy the following limit:

when the finite-thickness layer stress/current is continuously removed while the bulk control sector is held fixed,

`(a2,f2,g2,l3)_finite-thickness -> (a2,f2,g2,l3)_bulk`

with the four frozen expressions above.

Failure of any one coefficient is an operator-identity failure and blocks physical execution.

This condition is stronger than merely obtaining finite residuals at the axis.

## 5. Winding-field Frobenius result

Near the regular axis,

`ell=x+O(x^3)`, `w=n+O(x^2)`.

The layer equation has indicial part

`s_xx + (1/x)s_x - (n^2/x^2)s = 0`.

For `s~x^p`,

`p^2-n^2=0`.

Regularity selects

`p=abs(n)`.

Thus

`n != 0 => s(0)=0 AND s~x^abs(n)`.

Status: **proved locally**.

## 6. Next winding coefficient

Writing

`s=s_p x^p(1+alpha_s x^2+...)`,

and denoting by `mhat_Sigma_sq(f0)` the dimensionless center mass coefficient in the executable layer convention, one obtains

`alpha_s = [mhat_Sigma_sq(f0) - p(8a2+2l3) - 2n*m_layer*q_hat*g2 - 2n^2*l3] / [4(p+1)]`,

up to the explicit dimensionless normalization chosen for the finite-thickness potential.

The structural dependence and denominator are fixed; the precise hatted mass symbol must be bound to the finite-thickness model contract before executable use.

## 7. n=0 branch

For `n=0`,

`s=s0+s2 x^2+...`,

and `w=O(x^2)`.

Thus the leading amplitude equation has the generic form

`4s2 = d_s Vhat_Sigma(f0,s0)`

in the canonical dimensionless potential convention.

For a quartic layer potential

`Vhat_Sigma = ... + 0.5*mhat_Sigma_sq(f0)s^2 + lambdahat_Sigma/4*s^4`,

this becomes

`s2=[mhat_Sigma_sq(f0)s0+lambdahat_Sigma*s0^3]/4`.

The `n=0` and `n!=0` sectors remain separate discrete BVP branches.

## 8. Local free data after frozen gauge fixing

At fixed discrete branch `(n,N_F,m_layer,...)` and fixed model parameters, the north-axis regular local amplitudes are structurally

`(f0, g2, s_p)` for `n!=0`,

or

`(f0, g2, s0)` for `n=0`,

unless the global formulation promotes an additional quantity such as `k4` to an eigenvalue/shooting unknown.

There is no free `A0` and no free `ell_x(0)`.

The next coefficients are recursively constrained by the field equations.

This local count must not be confused with the older two-cap/background structural count of eight continuous BVP unknowns; the global finite-thickness problem may acquire additional outer/matching unknowns. G2 fixes only the north-axis local regularity budget.

## 9. Center curvature/stress structure

In the dimensionful representation, regularity gives

`T^r_r(0)=T^chi_chi(0)`.

For `|n|=1`, this follows from equality of the finite axis limits of radial and angular winding gradient energies; for `|n|>1` both vanish; for `n=0` both vanish at leading order.

Therefore the radial Einstein constraint and chi-chi equation are compatible at the axis rather than furnishing two independent center conditions.

## 10. Why the quarantined operator cannot satisfy this gate by construction

The implementation-only file

`2026-08-15_hzt_background3c5_finite_thickness_operator_v0.1.py`

uses a `B/C/Q/At_prime` representation not provenance-bound to the frozen `(A,ell,varphi,a_chi)` system.

Consequently it cannot be used to test the frozen bulk pole-coefficient limit without an explicit equivalence map.

Its QA, even if numerically green, therefore cannot promote G2.

## 11. Required executable center representation

The replacement kernel should evolve variables regular at `x=0`, for example

`A/x^2`, `(ell/x-1)/x^2`, `(varphi-f0)/x^2`, `a_chi/x^2`, and `s/x^p`

or an algebraically equivalent regularized basis.

Direct numerical evolution of `ell_x/ell ~ 1/x` at the first node should be avoided unless the singular terms are analytically cancelled.

## 12. Gate disposition

`G2_FROBENIUS_EXPONENT = PASS_PROVED_LOCAL`

`G2_AXIS_GAUGE_AND_METRIC_REGULARITY = PASS_FROZEN`

`G2_BULK_CONTROL_POLE_REGRESSION_TARGET = PASS_FROZEN`

`G2_FINITE_THICKNESS_EXECUTABLE_NORMALIZATION = PARTIAL_OPEN`

`G2_REPLACEMENT_KERNEL_REGRESSION = NOT_EXECUTED`

Overall:

`G2_REGULAR_CENTER_SERIES = CONDITIONAL_PASS_ANALYTIC_WITH_CONTROL_LIMIT`

No global existence, uniqueness, Fredholm, stability, ghost, rank-R, K1-D or K1-E conclusion follows.
