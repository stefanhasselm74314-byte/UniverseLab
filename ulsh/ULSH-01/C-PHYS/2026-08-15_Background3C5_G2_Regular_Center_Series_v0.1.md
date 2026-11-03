# ULSH-01 / C-PHYS — Background3C5 G2 Regular Center Series v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** CONDITIONAL_ANALYTIC_DERIVATION / G2_ADVANCED_NOT_YET_FULLY_RATIFIED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Authoritative system and assumptions

Work in the frozen proper-radial metric gauge

`ds6^2 = exp(2A(r)) gbar_mn dx^m dx^n + dr^2 + L(r)^2 dchi^2`,

`gbar_R_mn = 3 K4 gbar_mn`,

with `Delta chi = 2*pi` and regular-axis conditions

`L(0)=0`, `L'(0)=1`, `A'(0)=0`, `phi'(0)=0`.

For the charged finite-thickness field

`Sigma = s(r)/sqrt(2) exp(i n chi)`,

`w(r)=n-gSigma A_chi(r)`.

Use the regular gauge at the north axis

`A_chi(0)=0`.

Assume all local potentials are smooth at the center and the frozen scalar/gauge normalization closure applies.

No physical BVP existence or global matching claim follows from a local Frobenius/Taylor expansion.

## 2. Regular center ansatz

For the metric/scalar/gauge variables use

`A(r)=A0 + A2 r^2 + A4 r^4 + O(r^6)`,

`L(r)=r + L3 r^3 + L5 r^5 + O(r^7)`,

`phi(r)=phi0 + phi2 r^2 + phi4 r^4 + O(r^6)`,

`A_chi(r)=a2 r^2 + a4 r^4 + O(r^6)`.

The angular one-form regularity requirement is the reason `A_chi=O(r^2)` in a regular polar gauge.

Useful derived expansions are

`L'/L = 1/r + 2 L3 r + O(r^3)`,

`L''/L = 6 L3 + O(r^2)`,

`A'=2 A2 r + O(r^3)`,

`phi'=2 phi2 r + O(r^3)`,

`w=n-gSigma a2 r^2+O(r^4)`.

## 3. Matter-field indicial equation for n != 0

The frozen layer equation is

`s'' + (4A'+L'/L)s' - (w^2/L^2)s - mSigma^2(phi)s - lambdaSigma s^3 = 0`.

Near `r=0`, retain only the singular radial terms:

`s'' + (1/r)s' - (n^2/r^2)s = 0`.

Insert `s ~ r^p`. Then

`p(p-1) r^(p-2) + p r^(p-2) - n^2 r^(p-2)=0`,

so

`p^2-n^2=0`.

Hence

`p=±|n|`.

Regularity selects

`p=|n|`.

Therefore for `n != 0`

`s(r)=s_p r^p [1 + alpha_s r^2 + O(r^4)]`,

`p=|n|`,

where `s_p` is a locally free regular amplitude.

This strengthens the weaker condition `s(0)=0`: smoothness fixes the leading power, not merely the value.

**Status:** proved within the frozen local equation and regular polar gauge.

## 4. Next coefficient of the winding field

Expanding to order `r^p` gives

`4(p+1) alpha_s`

`+ p(8 A2 + 2 L3)`

`+ 2 n gSigma a2`

`+ 2 n^2 L3`

`- mSigma^2(phi0) = 0`,

hence

`alpha_s = [mSigma^2(phi0) - p(8A2+2L3) - 2n gSigma a2 - 2n^2 L3] / [4(p+1)]`.

The quartic self-interaction enters only at higher order for `p>=1` because `s^3=O(r^(3p))`.

For `p=1`, it first contributes at order `r^3`.

## 5. n = 0 branch

For `n=0`, regularity permits

`s(r)=s0+s2 r^2+O(r^4)`.

Since `w=-gSigma A_chi=O(r^2)`, the angular term vanishes at leading order and

`4 s2 - mSigma^2(phi0) s0 - lambdaSigma s0^3 = 0`.

Thus

`s2 = [mSigma^2(phi0)s0 + lambdaSigma s0^3]/4`.

The `n=0` and `n!=0` center data are therefore structurally different and must not be mixed in one continuous Jacobian branch.

## 6. Scalar center coefficient

Write the canonical scalar equation schematically as

`phi'' + (4A'+L'/L)phi' = S_phi(phi,s,A_chi',L)`,

where `S_phi` is the complete finite center source obtained from the frozen bulk potential, gauge kinetic coupling and layer potential derivative.

Using

`phi''=2phi2+O(r^2)`,

`(L'/L)phi'=2phi2+O(r^2)`,

`4A'phi'=O(r^2)`,

gives

`4 phi2 = S_phi(0)`.

Therefore

`phi2 = S_phi(0)/4`.

In the dimensionful SCI-001 notation,

`S_phi(0) = d_phi V6|0 + d_phi V_Sigma|0 + (d_phi Z_F)/(2 g6^2) * [A_chi'^2/L^2]_0`,

with signs following the frozen equation

`phi''+(4A'+L'/L)phi' - d_phi V6 - (d_phi Z_F)/(2g6^2) A_chi'^2/L^2 - d_phi V_Sigma = 0`.

Since

`A_chi'=2a2 r+O(r^3)`, `L=r+O(r^3)`,

we have

`[A_chi'^2/L^2]_0 = 4 a2^2`.

Thus the gauge contribution is finite, not singular.

## 7. Maxwell center structure

The frozen Maxwell equation is

`d/dr [ exp(4A) (Z_F/g6^2) A_chi'/L ] = - exp(4A) gSigma s^2 w/L`.

With

`A_chi=a2 r^2+a4 r^4+...`,

`A_chi'/L = 2a2 + (4a4-2a2L3)r^2+...`.

Hence `a2` is not fixed by local axis regularity alone: it is the local magnetic/flux-density shooting datum.

The equation determines `a4` once `(A2,L3,phi2,s_p,a2)` and the branch are fixed.

For `|n|>1`, the matter current starts beyond order `r`, so the order-`r` Maxwell balance is homogeneous.

For `|n|=1`, the current contributes already at order `r` and shifts `a4` by a term proportional to

`g6^2 gSigma n s_1^2 / Z_F(phi0)`.

For `n=0`, the induced `w=O(r^2)` also produces a finite order-`r` correction proportional to `gSigma^2 a2 s0^2`.

No local condition fixes the total flux; flux quantization is a global outer/patch condition.

## 8. Einstein center equations

Define at the axis

`k40 = K4 exp(-2A0)`.

The geometric limits are

`A''(0)=2A2`,

`A' L'/L -> 2A2`,

`L''/L -> 6L3`.

The frozen Einstein equations therefore give

### radial constraint

`8 A2 - 6 k40 + Lambda6 = T^r_r(0)/M6^4`,

so

`A2 = [T^r_r(0)/M6^4 + 6k40 - Lambda6]/8`.

### mu-mu equation

`12 A2 + 6 L3 - 3 k40 + Lambda6 = T^mu_mu(0)/M6^4`,

so

`L3 = [T^mu_mu(0)/M6^4 + 3k40 - Lambda6 - 12A2]/6`.

### chi-chi equation

`8 A2 - 6 k40 + Lambda6 = T^chi_chi(0)/M6^4`.

Consistency therefore requires

`T^r_r(0)=T^chi_chi(0)`.

For a regular winding field this holds automatically at leading order:

- if `|n|>1`, both radial and angular gradient energies vanish at the axis;
- if `|n|=1`, `s'^2` and `s^2 w^2/L^2` approach the same finite value, so their difference vanishes;
- if `n=0`, both angular contribution and center derivative vanish.

Thus the axis does not overconstrain the Einstein system.

## 9. Explicit center stress-energy bookkeeping

Using the frozen definitions

`E_phi=1/2 phi'^2`,

`E_r=1/2 s'^2`,

`E_chi=1/2 s^2 w^2/L^2`,

`rho_F=Z_F/(2g6^2) A_chi'^2/L^2`,

`V_tot=V6+V_Sigma`,

we obtain

`E_phi(0)=0`,

`rho_F(0)=2 Z_F(phi0) a2^2/g6^2`.

For `|n|=1` with `s=s1 r+...`:

`E_r(0)=E_chi(0)=s1^2/2`.

For `|n|>1`:

`E_r(0)=E_chi(0)=0`.

For `n=0`:

`E_r(0)=E_chi(0)=0`.

Therefore

`T^r_r(0) = -V_tot(0) + rho_F(0)`

for every regular branch after the equal radial/angular winding terms cancel.

This yields the compact result

`A2 = [-V_tot(0)/M6^4 + rho_F(0)/M6^4 + 6k40 - Lambda6]/8`.

Meanwhile `T^mu_mu(0)` contains the sum of the winding gradient energies, so `L3` retains branch dependence for `|n|=1`.

## 10. Local free-data count

At fixed discrete branch `(n,N_F,m_layer,...)`, the regular center expansion contains the following continuous local data before removal of gauge redundancies and global conditions:

- `A0` — four-dimensional warp normalization;
- `phi0` — scalar center value;
- `a2` — local internal magnetic/flux-density amplitude;
- one layer amplitude: `s_p` for `n!=0`, or `s0` for `n=0`;
- `K4` (equivalently `k40` once `A0` is fixed) if treated as a global curvature eigenvalue rather than externally prescribed.

The coefficients

`A2`, `L3`, `phi2`, `a4`, `alpha_s` / `s2`, ...

are recursively determined by the equations.

`L'(0)=1` removes the conical slope freedom; no independent `L1` shooting parameter remains.

A constant rescaling of the four-dimensional coordinates can be used to fix `A0=0` provided the associated normalization of `K4` is transformed consistently. In that gauge the local continuous shooting content is reduced by one redundant parameter.

Hence, for fixed `K4`, a typical regular center has three physical local amplitudes

`(phi0, a2, s_p)` for `n!=0`,

or `(phi0,a2,s0)` for `n=0`,

before imposing outer decay/matching and global flux quantization.

If `K4` is solved as an eigenvalue, add one global continuous unknown.

## 11. Dimensional check

With `[r]=M^-1`, `[A]=1`, `[L]=M^-1`, `[phi]=M^2`, `[A_chi]=M`, `[gSigma]=M^-1`:

- `[A2]=M^2`,
- `[L3]=M^2` because `L3 r^3` has dimension `M^-1`,
- `[phi2]=M^4`,
- `[a2]=M^3`,
- `[gSigma A_chi]=1`,
- `rho_F(0)` has dimension `M^6`,
- `T/M6^4` has dimension `M^2`, matching `A2`, `L3`, `Lambda6`, `K4`.

The center equations are dimensionally consistent.

## 12. Grenzfälle

### weak layer amplitude

`s_p -> 0` removes the localized matter contribution continuously, but does not remove the magnetic datum `a2`.

### zero magnetic seed

`a2 -> 0` implies `rho_F(0)->0`. A nonzero total flux may then be impossible on a one-axis patch unless generated away from the axis; this is a global question, not settled locally.

### flat four-dimensional slice

`K4 -> 0` is algebraically admissible in the local series, even though the previously studied hybrid background sector may exclude a globally regular `K4=0` branch. Local admissibility is not global existence.

### large |n|

The matter field is increasingly suppressed near the axis as `s~r^|n|`; its local stress decouples faster in the IR-center expansion, while global angular-gradient cost generally increases away from the axis.

## 13. What G2 does and does not establish

### Established conditionally

- correct Frobenius exponent `p=|n|`;
- regular gauge behavior `A_chi=O(r^2)`;
- recursive determination of subleading coefficients;
- center Einstein constraint and `A2/L3` relations;
- local free-data count in proper-radial gauge;
- no independent conical-slope shooting mode.

### Not established

- existence of a global solution;
- uniqueness;
- outer layer decay;
- flux quantization compatibility;
- full boundary-map rank;
- Fredholm property;
- stability or ghost freedom;
- physical response rank.

## 14. Gate disposition

`G2_REGULAR_CENTER_SERIES = CONDITIONAL_PASS_ANALYTIC`

The remaining conditions before full G2 ratification are:

1. bind the scalar source notation completely to the executable M1 potential derivative convention;
2. encode this center series into the replacement parent-equivalent kernel;
3. regression-test the numerical center initializer against the analytic coefficients.

Until then:

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`RANK_R_CLAIM_ALLOWED = FALSE`.
