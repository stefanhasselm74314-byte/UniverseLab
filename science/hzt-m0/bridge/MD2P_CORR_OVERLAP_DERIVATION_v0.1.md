# MD-2P-corr Overlap Derivation and Rank Bound v0.1

**Date:** 2026-08-01  
**Source chain:** MD-2I → MD-2P-corr → MD-2Q  
**Governance:** MD-0 / HPVS  
**Status:** CONDITIONAL DERIVATION OF `q`; EFFECTIVE CLOSURE FOR `eta_bulk`; K1-D NOT RELEASED  
**Evidence effect:** NONE

## 1. Executive result

The MD-2P-corr quantity

```text
q = 1 - exp(-x),
x = gamma R_chi^2,
gamma = 2 alpha + 1/sigma_B^2
```

admits an exact derivation as the cumulative normalized overlap fraction of a radial Gaussian weight on a flat two-dimensional internal space. The formula is therefore not arbitrary once the following assumptions are declared:

1. the relevant internal measure is locally the flat polar measure `dV_2 = r dr dchi`;
2. the effective overlap density is proportional to `exp(-gamma r^2)`;
3. the integration region is a sharp disk `0 <= r <= R_chi`;
4. the denominator is the same overlap integrated over the complete radial domain.

The second MD-2P-corr relation

```text
eta_bulk = beta_0 q(1-q)
```

is not derived from the 6D action by this result. It can be given a precise conditional semantic interpretation as a partition-variance or inside/outside mixing closure, but it remains an effective ansatz until the same structure follows from the normalized 6D mode action or Green-function kernel.

A new identifiability result follows: if several physical controls enter the observables only through the single scalar `x` and hence through `eta_bulk(x)`, their local Jacobian block has rank at most one. At the amplitude maximum `x = ln 2`, the first derivative `d eta_bulk/dx` vanishes and this block has rank zero at linear order.

## 2. Definitions and unit contract

Let

```text
gamma = 2 alpha + 1/sigma_B^2,
R_chi = 4/(kappa_6^2 lambda_chi),
x = gamma R_chi^2
  = 16 gamma/(kappa_6^4 lambda_chi^2).
```

Under the convention used by the recovered MD-2P-corr package,

```text
[kappa_6] = L^2,
[kappa_6^2] = L^4,
[lambda_chi] = L^-5,
[R_chi] = L,
[alpha] = L^-2,
[sigma_B] = L,
[gamma] = L^-2,
[x] = 1.
```

The dimensional consistency of `x` is therefore conditional on this convention. The numerical package value `kappa_6 = 1` must still be accompanied by a complete nondimensionalization or physical normalization contract before evidential use.

## 3. Exact two-dimensional overlap derivation

Assume a nonnegative radial overlap weight

```text
W(r) = exp(-gamma r^2),
gamma > 0.
```

On a flat two-dimensional internal plane with polar coordinate `chi in [0,2pi)`, define the normalized cumulative overlap fraction inside radius `R_chi`:

```text
q(R_chi) =
  [integral_0^{2pi} dchi integral_0^{R_chi} r exp(-gamma r^2) dr]
  /
  [integral_0^{2pi} dchi integral_0^infinity r exp(-gamma r^2) dr].
```

The denominator is

```text
D = 2pi integral_0^infinity r exp(-gamma r^2) dr
  = pi/gamma.
```

The numerator is

```text
N(R_chi)
= 2pi integral_0^{R_chi} r exp(-gamma r^2) dr
= (pi/gamma)[1 - exp(-gamma R_chi^2)].
```

Hence

```text
q(R_chi) = N/D
         = 1 - exp(-gamma R_chi^2)
         = 1 - exp(-x).
```

### Status

```text
q = 1 - exp(-x)
```

is **exact under the declared flat-2D Gaussian-overlap assumptions**. It is not yet an exact consequence of the full warped MD-2S geometry.

## 4. Why `gamma = 2 alpha + 1/sigma_B^2` is structurally plausible

If the overlap weight is the product of two Gaussian factors,

```text
W_1(r) = exp(-2 alpha r^2),
W_2(r) = exp(-r^2/sigma_B^2),
```

then

```text
W_1(r) W_2(r)
= exp[-(2 alpha + 1/sigma_B^2)r^2]
= exp(-gamma r^2).
```

This proves only the algebraic composition of the profiles. The 6D theory must still determine:

- which normalized mode profiles enter the overlap;
- why their exponents have these coefficients;
- which metric and warp factors belong in the measure;
- whether the radial domain is finite, capped or noncompact;
- and whether a sharp boundary at `R_chi` is physically appropriate.

## 5. Warped-geometry generalization

For the MD-2S internal metric

```text
ds_2^2 = dr^2 + L(r)^2 dchi^2,
```

the internal volume element is

```text
dV_2 = L(r) dr dchi.
```

A generic normalized overlap fraction is therefore

```text
q_W(R) =
  [integral_0^R dr L(r) exp(p A(r)) W(r)]
  /
  [integral_0^{r_max} dr L(r) exp(p A(r)) W(r)].
```

Here `p` depends on the field, kinetic term and normalization being reduced. The flat formula is recovered when

```text
L(r) = r,
A(r) = 0,
r_max = infinity,
W(r) = exp(-gamma r^2).
```

The canonical MD-2S bridge must ultimately use `q_W`, not assume the flat formula, unless the flat/local approximation is independently justified.

## 6. Dimension dependence

For a radially symmetric Gaussian on `d` flat internal dimensions, the normalized cumulative fraction is

```text
q_d(x) = lower_incomplete_gamma(d/2, x) / Gamma(d/2).
```

The recovered formula is special to two internal dimensions:

```text
q_2(x) = 1 - exp(-x).
```

This is a nontrivial consistency point for a 6D theory with two internal dimensions. It does not by itself prove that the physical overlap weight is Gaussian.

## 7. Conditional interpretation of `eta_bulk`

Define the indicator variable

```text
I_R(r) = 1 for r <= R_chi,
       = 0 for r > R_chi.
```

With respect to the normalized overlap measure,

```text
E[I_R] = q,
Var(I_R) = q(1-q).
```

Therefore

```text
eta_bulk = beta_0 q(1-q)
```

can be interpreted as a response proportional to the variance of the inside/outside partition, or equivalently to the product of the overlap fractions on the two sides of the boundary.

This interpretation requires the additional postulate:

> the leading effective deformation is proportional to partition mixing rather than to the overlap itself.

That postulate is physically motivated but not derived from the current 6D action. The status remains:

```text
EFFECTIVE PARTITION-MIXING CLOSURE
```

not `DERIVED_PHYSICAL_BRIDGE`.

## 8. Exact asymptotics and maximum

Using

```text
q = 1 - exp(-x),
eta_bulk = beta_0[exp(-x) - exp(-2x)],
```

### Small `x`

```text
q = x - x^2/2 + O(x^3),
eta_bulk = beta_0[x - 3x^2/2 + O(x^3)].
```

Since `x = 16 gamma/(kappa_6^4 lambda_chi^2)`,

```text
eta_bulk
= 16 beta_0 gamma/(kappa_6^4 lambda_chi^2)
  + O(lambda_chi^-4)
```

for `lambda_chi -> infinity` at fixed `gamma` and `kappa_6`.

### Large `x`

```text
q -> 1,
eta_bulk = beta_0 exp(-x)[1 - exp(-x)]
         ~ beta_0 exp(-x).
```

Thus the amplitude is exponentially suppressed as `lambda_chi -> 0`.

### Maximum

```text
d eta_bulk/dx
= beta_0 exp(-x)[2 exp(-x) - 1].
```

The unique interior maximum occurs at

```text
exp(-x_*) = 1/2,
x_* = ln 2,
q_* = 1/2,
eta_bulk,max = beta_0/4.
```

With `x = 16 gamma/(kappa_6^4 lambda_chi^2)`,

```text
lambda_chi,*
= 4 sqrt[gamma/(kappa_6^4 ln 2)].
```

## 9. Parameter sensitivities

Let

```text
eta_x = d eta_bulk/dx
      = beta_0 exp(-x)[2 exp(-x)-1].
```

Then

```text
partial x/partial lambda_chi = -2x/lambda_chi,
partial x/partial kappa_6    = -4x/kappa_6,
partial x/partial gamma      =  x/gamma,
partial gamma/partial alpha  = 2,
partial gamma/partial sigma_B = -2/sigma_B^3.
```

Therefore

```text
partial eta_bulk/partial p
= eta_x partial x/partial p.
```

For the MD-2Q point

```text
alpha = 0.15 Mpc^-2,
sigma_B = 1.2 Mpc,
kappa_6 = 1,
lambda_chi = 4.25 Mpc^-5,
beta_0 = 0.1,
```

one obtains

```text
gamma = 0.9944444444444445,
x = 0.8808919646289889,
q = 0.5855868950525662,
eta_bulk = 0.024267488339526102,
partial eta_bulk/partial lambda_chi
= 0.0029405899018908354
```

in the package's effective unit convention.

The logarithmic sensitivities are

```text
partial ln eta/partial ln lambda_chi = 0.5149897224,
partial ln eta/partial ln kappa_6    = 1.0299794448,
partial ln eta/partial ln gamma      = -0.2574948612.
```

These are local effective sensitivities, not physical Fisher information.

## 10. New local-rank theorem

Assume the observable vector has the form

```text
O_a(p) = O_a^0 + C_a eta_bulk[x(p)],
```

where all parameters `p_i` in a subset enter only through the single scalar `x(p)`. Then

```text
partial O_a/partial p_i
= C_a [d eta_bulk/dx] [partial x/partial p_i].
```

Every Jacobian column is proportional to the same observable-space vector `C_a`. Therefore

```text
rank(J_subset) <= 1.
```

At the amplitude maximum `x = ln 2`,

```text
d eta_bulk/dx = 0,
```

so

```text
rank(J_subset) = 0
```

at linear order for all parameters entering only through `x`.

### Consequences

1. Varying `lambda_chi`, `alpha`, `sigma_B` and `kappa_6` simultaneously does not create four locally identifiable directions if they modify only `eta_bulk(x)`.
2. A one-column MD-2Q Jacobian has condition number `1` whenever it is nonzero; this is algebraically automatic.
3. Near `x = ln 2`, a first-order Fisher analysis loses sensitivity to all `x`-only controls even though the amplitude is maximal.
4. Rank greater than one requires independent shape or channel responses, for example derived variations of `m`, `s`, background evolution, slip, lensing normalization or additional mode profiles.

## 11. Relation to the MD-2I minimal derivation set

| MDS edge | Effect of this derivation | Status |
|---|---|---|
| MDS-01 `R_chi -> m` | no eigenvalue equation is supplied | OPEN |
| MDS-02 `beta_tau,I_B,kappa_6 -> omega_c` | not addressed | OPEN |
| MDS-03 `a0,beta_tau,I_B -> eta` | replaced by a conditional partition-mixing ansatz | ALTERNATIVE EFFECTIVE, NOT DERIVED |
| MDS-04 `R_chi,beta_tau -> s` | not addressed; `s=2` remains fixed | FIXED EFFECTIVE |
| MDS-05 `kappa_6 -> N_4` | not addressed; dependence of `x` on `kappa_6` is not a 4D normalization derivation | OPEN |

The derivation upgrades only the status of `q`:

```text
q: DEFINITION CANDIDATE
   -> CONDITIONAL EXACT OVERLAP FRACTION
```

It does not release the full bridge or K1-D.

## 12. Falsification and replacement conditions

The flat-Gaussian formula is falsified as the relevant physical overlap if the recovered MD-2S reduction shows any of the following:

- the normalized measure is not proportional to `r dr` in the relevant regime;
- the mode product is materially non-Gaussian;
- warp factors change the cumulative fraction beyond the declared approximation;
- the internal domain is compact with a normalization denominator different from the infinite-plane value;
- no sharp partition at `R_chi` arises from the localized action;
- or the effective response is not proportional to partition variance.

In that case `q_W` from the actual normalized geometry and mode profiles replaces `1-exp(-x)`.

## 13. Next required work

1. Recover or derive the MD-2S profiles `A(r)` and `L(r)`.
2. Derive the normalized bulk, brane and source mode functions entering the overlap.
3. Determine the correct warp exponent `p` from the reduced quadratic action.
4. Compute `q_W(R_chi)` and compare it with the flat-Gaussian approximation.
5. Derive or reject the partition-mixing closure from the reduced interaction kernel.
6. Introduce independent observable shapes before any multi-parameter K1 rank claim.

No step in this document changes `K1-D`, `K1-E`, the MD-2S gate status or the evidence status of MD-2Q.
