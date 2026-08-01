# MD-2I MDS-01 Spectral Bridge Derivation v0.1

**Date:** 2026-08-01  
**Scope:** `R_chi -> m` bridge  
**Governance:** MD-0 / HPVS / MD-2I  
**Status:** CONDITIONAL SPECTRAL THEOREM / SPECIFIC HZT-M0 EIGENVALUE NOT YET RELEASED  
**Evidence effect:** NONE

## 1. Executive result

The candidate bridge

```text
m = xi_m / R_chi
```

is not an arbitrary dimensional guess. It follows from an internal eigenvalue problem whenever the compact geometry is self-similar under rescaling by `R_chi` and no independent dimensional scale remains in the operator.

The correct general statement is

```text
m_n = Xi_n(G, BC, M_i R_chi, R_chi/ell_A, flux ratios, ...)/R_chi,
```

where `Xi_n` is a dimensionless spectral function determined by:

- the internal metric and warp profiles,
- field spin and angular sector,
- localized and bulk potentials,
- flux background,
- boundary/junction conditions,
- and all additional dimensionless scale ratios.

Only in the scale-free or self-similar limit does `Xi_n` reduce to a constant `xi_n`.

Therefore MDS-01 can be upgraded from a free effective scale relation to a **conditional spectral bridge**, but the numerical value of `xi_m` remains unreleased until the MD-2S operator and boundary conditions are frozen.

## 2. Generic self-adjoint problem

A broad class of radial internal fluctuations can be written in Sturm-Liouville form

```text
- d/dr [p(r) du_n/dr] + Q(r) u_n
= m_n^2 w(r) u_n,
```

on a radial interval `r in [0,R_chi]` or on a capped two-sided domain.

The coefficients satisfy, in a regular self-adjoint sector,

```text
p(r) > 0,
w(r) > 0,
```

with a specified domain and boundary form.

For normalized modes,

```text
integral dr w(r) u_m(r) u_n(r) = delta_mn.
```

The corresponding Rayleigh quotient is

```text
m_n^2
= [integral dr {p(r)[u_n'(r)]^2 + Q(r)u_n(r)^2} + B_boundary]
  / [integral dr w(r)u_n(r)^2].
```

This expression shows directly that numerical stability of a mode solver does not establish positivity: the signs of `p`, `w`, the potential and boundary contribution must be derived from the quadratic action.

## 3. Scaling derivation

Set

```text
y = r/R_chi,
r = R_chi y.
```

If the operator coefficients can be written as

```text
p(r) = R_chi^a p_hat(y),
Q(r) = R_chi^(a-2) Q_hat(y),
w(r) = R_chi^a w_hat(y),
```

with boundary conditions depending only on dimensionless constants, then the eigenvalue equation becomes

```text
- d/dy [p_hat(y) du_n/dy] + Q_hat(y)u_n
= (m_n R_chi)^2 w_hat(y)u_n.
```

The dimensionless eigenvalues are therefore

```text
xi_n^2 = (m_n R_chi)^2,
```

and

```text
m_n = xi_n/R_chi.
```

### Unit check

```text
[xi_n] = 1,
[R_chi] = L,
[m_n] = L^-1.
```

## 4. Failure of the constant-`xi` reduction

If the operator contains an independent bulk mass `M`, warp length `ell_A`, flux scale `ell_F`, brane kinetic coefficient or other dimensional quantity, the rescaled equation contains dimensionless combinations such as

```text
M R_chi,
R_chi/ell_A,
R_chi/ell_F.
```

Then

```text
m_n = Xi_n(M R_chi, R_chi/ell_A, R_chi/ell_F, ...)/R_chi,
```

and `xi_n` cannot be treated as a universal constant.

This is the expected situation for a warped flux compactification unless a controlled limit removes the extra scales.

## 5. Flat two-dimensional disk benchmark

For a scalar mode on the flat disk

```text
ds_2^2 = dr^2 + r^2 dchi^2,
0 <= r <= R_chi,
```

separate

```text
u(r,chi) = f_l(r) exp(i l chi).
```

The radial Laplacian eigenproblem

```text
-Delta_2 u = m^2 u
```

becomes

```text
f_l'' + (1/r)f_l' + [m^2 - l^2/r^2]f_l = 0.
```

Regularity at `r=0` selects

```text
f_l(r) = J_l(mr).
```

### Dirichlet boundary

```text
f_l(R_chi) = 0
```

implies

```text
m_l,n = j_l,n/R_chi,
```

where `j_l,n` is the `n`th positive zero of `J_l`.

For the axisymmetric lowest mode,

```text
xi_D = j_0,1 = 2.4048255577...
```

### Neumann boundary

```text
f_l'(R_chi) = 0
```

implies

```text
m_l,n = j'_l,n/R_chi.
```

For `l=0`, the constant function is a zero mode. The first massive axisymmetric mode satisfies

```text
J_1(mR_chi) = 0,
xi_N,massive = j_1,1 = 3.8317059702...
```

### Robin boundary

For

```text
f_l'(R_chi) + h f_l(R_chi) = 0,
```

the roots obey

```text
z J_l'(z) + (h R_chi) J_l(z) = 0,
z = mR_chi.
```

The dimensionless combination `hR_chi` changes the spectrum and may generate a parametrically light mode near a critical boundary condition.

## 6. Diagnostic comparison with MD-2Q locked values

The recovered MD-2Q effective point uses

```text
m_eff = 0.055 Mpc^-1,
kappa_6 = 1 effective unit,
lambda_chi = 4.25 Mpc^-5,
R_chi = 4/(kappa_6^2 lambda_chi)
      = 0.9411764705882353 Mpc
```

under the package's mixed effective-unit convention.

The implied dimensionless spectral coefficient is

```text
xi_eff = m_eff R_chi
       = 0.05176470588235294.
```

This is far below the standard flat-disk values

```text
j_0,1 = 2.4048255577,
j_1,1 = 3.8317059702.
```

Equivalently, the flat-disk predictions at the same radius would be

```text
m_D = 2.555127154... Mpc^-1,
m_N,first massive = 4.071187594... Mpc^-1.
```

The discrepancy is diagnostic, not a falsification, because:

- the package mixes physical Mpc labels with `kappa_6=1` effective units;
- the actual internal operator may be warped and contain potentials;
- a near-zero Robin or localized mode could be parametrically light;
- `R_chi` in the bridge ansatz may not equal the spectral domain radius;
- and `m_eff` may be a phenomenological damping scale rather than a KK eigenmass.

However, the comparison proves that the delivered `m_eff` is not the ordinary first scalar eigenvalue of a flat disk with standard Dirichlet or Neumann boundary conditions at the delivered `R_chi`.

## 7. Identifiability implications

If

```text
m_n = Xi_n(theta)/R_chi,
```

then

```text
d ln m_n
= -d ln R_chi + d ln Xi_n.
```

For a constant spectral coefficient,

```text
partial ln m/partial ln R_chi = -1.
```

With additional shape parameters `theta_a`,

```text
partial ln m/partial theta_a
= partial ln Xi_n/partial theta_a.
```

Therefore a physical Jacobian must not vary `m` independently of `R_chi` and the spectral controls. Treating both `m` and `R_chi` as free directions double-counts the same scale unless the model explicitly contains an additional independent mechanism.

## 8. Transition regimes

### Scale-free regime

```text
M_i R_chi << 1,
R_chi/ell_A << 1,
```

and weak deformation of the reference geometry may yield

```text
Xi_n = xi_n^(0) + delta xi_n,
|delta xi_n| << xi_n^(0).
```

Then

```text
m_n approximately xi_n^(0)/R_chi.
```

### Strong-warp or strong-potential regime

For order-one or large dimensionless ratios, `Xi_n` may differ substantially from flat roots, produce localization, level crossings or a parametrically light mode. The simple inverse-radius law retains only the overall dimensional prefactor and loses predictive content unless `Xi_n` is calculated.

### Decompactification

If `R_chi -> infinity` while all other lengths scale with `R_chi`,

```text
m_n -> 0 as 1/R_chi.
```

If a fixed bulk mass remains,

```text
m_n^2 -> M^2 + O(R_chi^-2),
```

so the spectrum does not become massless.

### Small-radius limit

For a scale-free positive operator,

```text
m_n -> infinity as 1/R_chi.
```

This is the decoupling limit expected for ordinary KK modes. A failure of this behavior indicates an additional scale, a zero mode, a boundary-tuned light state or an inconsistent identification of `m`.

## 9. MDS-01 release contract

MDS-01 may enter K1-D only after the following are frozen:

1. the exact quadratic operator for the relevant internal mode;
2. the field and angular sector;
3. the radial domain and whether `R_chi` is its physical size;
4. center regularity and all cap/brane boundary conditions;
5. mode normalization and inner product;
6. all additional dimensional scales;
7. the selected eigenvalue index `n`;
8. the relation between this eigenmass and the damping-kernel parameter `m`.

The admissible bridge is then

```text
m = m_n[A,L,phi,F,localized terms,BC]
```

or, after controlled reduction,

```text
m = Xi_n(...)/R_chi.
```

## 10. Status update

```text
MDS-01 dimensional form     = DERIVED CONDITIONALLY
MDS-01 numerical xi_m       = OPEN
m_eff identification        = OPEN
flat-disk standard-mode match = REJECTED FOR THE LOCKED MD-2Q NUMBERS
K1-D                        = NOT RELEASED
K1-E                        = NOT ADMISSIBLE
Evidence effect             = NONE
```

## 11. Next required work

1. Derive the relevant quadratic fluctuation operator from the frozen MD-2S action.
2. Compute `p(r)`, `Q(r)` and `w(r)` from `A(r)`, `L(r)` and the background fields.
3. Derive the oriented cap/brane boundary form.
4. Solve the spectrum with two independent numerical implementations.
5. Test flat, weak-warp, heavy-mode and decompactification limits.
6. Identify whether the damping-kernel `m` is a KK eigenmass, radion mass, response-pole scale or independent EFT coefficient.

No numerical `xi_m` is ratified by this document.
