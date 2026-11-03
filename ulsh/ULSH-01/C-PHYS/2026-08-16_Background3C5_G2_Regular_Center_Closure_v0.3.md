# ULSH-01 / C-PHYS — Background3C5 G2 Regular Center Closure v0.3

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** G2_ANALYTIC_CLOSURE_PASS__EXECUTABLE_REGRESSION_QA_PENDING  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Canonical variables

The regular north-axis formulation uses the frozen dimensionless variables

`x=M6*r`, `ell=M6*L`, `varphi=phi/M6^2`, `a_chi=A_chi/M6`.

Freeze-1A fixes `A(0)=0` and regular angular normalization fixes `ell_x(0)=1`.
There is no continuous conical-rescue shooting parameter.

## 2. Regular center series

`A=a2*x^2+O(x^4)`

`ell=x+l3*x^3+O(x^5)`

`varphi=f0+f2*x^2+O(x^4)`

`a_chi=g2*x^2+O(x^4)`

For nonzero winding,

`s_hat=s_p*x^abs(n)*(1+O(x^2))`.

For `n=0`, `s_hat=s0+s2*x^2+...`.

The Frobenius indicial equation is `p^2-n^2=0`; regularity selects `p=abs(n)`.

## 3. Layer amplitude normalization — closed by 6D dimensions

The finite-thickness parent action contains the canonical kinetic term

`-1/2 (partial s)^2`.

In six dimensions the Lagrangian density has mass dimension `M^6`, hence

`[s]=M^2`.

Therefore define uniquely relative to the already frozen dimensional anchor `M6`

`s_hat = s/M6^2`.

For

`V_Sigma = Lambda_layer + 1/2 mSigma^2 s^2 + lambdaSigma/4 s^4`,

the corresponding dimensionless quantities are

`Lambda_layer_hat = Lambda_layer/M6^6`,

`mSigma_hat^2 = mSigma^2/M6^2`,

`lambdaSigma_hat = lambdaSigma*M6^2`.

If `mSigma^2(phi)=mSigma0^2+etaSigma*(phi-phi_star)`, then

`mSigma_hat^2(varphi)=mSigma0_hat^2+etaSigma*(varphi-varphi_star)`,

so `etaSigma` is dimensionless.

This closes the amplitude normalization required for the local G2 center equation. It does not by itself close the full Maxwell-current/backreaction normalization of the global operator.

## 4. Mandatory bulk-control regression

With the finite-thickness layer removed, the executable center initializer must reproduce exactly

`rho_F0=0.5*q_s^2*exp(2*a_F*f0)`

`a2=(6*k4-Lambda_hat-0.5*mhat_phi_sq*f0^2+rho_F0)/8`

`f2=(mhat_phi_sq*f0-2*a_F*rho_F0)/4`

`g2=0.5*q_s*exp(2*a_F*f0)`

`l3=(3*k4-12*a2-Lambda_hat-0.5*mhat_phi_sq*f0^2-rho_F0)/6`.

The canonical candidate operator v0.2 implements these formulas verbatim. CI regression is required before the executable part of G2 is promoted.

## 5. Local free-data budget

At fixed model parameters, fixed discrete branch and fixed `k4`, the north-axis regular continuous data are

- `n != 0`: `(f0, g2, s_p)`;
- `n = 0`: `(f0, g2, s0)`.

If `k4` is promoted to a global eigenvalue, it adds one global unknown; it is not a local regularity degree of freedom.

Neither `A0` nor `ell_x(0)` is free.

## 6. Separation from G5

G2 closes local regularity and center normalization. It does **not** certify the complete finite-thickness backreacted operator.

Still belonging to G5/operator identity:

- exact dimensionless Maxwell current coefficient in the evolving flux equation;
- full layer contribution to Einstein residuals in the executable convention;
- scalar backreaction from `phi` dependence of `Lambda_layer` and `mSigma^2`;
- algebraic equivalence of the complete numerical residual vector to the parent Euler-Lagrange system.

Therefore no physical BVP run is authorized by G2 alone.

## 7. Gate disposition

`G2_FROBENIUS_EXPONENT = PASS_PROVED_LOCAL`

`G2_AXIS_METRIC_REGULARITY = PASS_FROZEN`

`G2_LAYER_AMPLITUDE_NORMALIZATION = PASS_DIMENSIONALLY_DERIVED`

`G2_BULK_POLE_REGRESSION_TARGET = PASS_FROZEN`

`G2_CANONICAL_CANDIDATE_IMPLEMENTATION = PRESENT`

`G2_EXECUTABLE_REGRESSION_QA = PENDING_AFTER_CI_FIX`

Overall:

`G2_REGULAR_CENTER = ANALYTIC_CLOSURE_PASS__SOFTWARE_QA_PENDING`

No global existence, uniqueness, Fredholm, stability, ghost, physical rank-R, K1-D or K1-E conclusion follows.
