# HZT-M0 / S6 / C-PHYS — H4R3 Variable-Coefficient Symmetrizer and Nonlinear Energy Closure v0.1

**Date:** 2026-08-14  
**Block:** `C-PHYS-PARENT-H4R3-VARIABLE-COEFFICIENT-FIRST-ORDER-REDUCTION-CONSTRAINT-BOUNDARY-SYMMETRIZER-AND-NONLINEAR-ENERGY-CLOSURE`  
**Scope:** formal analytic preflight only; no physical PDE solve, no backend import, no evidence effect

## 1. Purpose and scientific firewall

H4R2 established a uniform frozen-coefficient two-sided Lopatinskii/complementing bound for the reduced time-radial M1 system. H4R3 asks the next question:

> Can the nondegenerate time-radial principal system be promoted to an explicit variable-coefficient first-order symmetric-hyperbolic form with a boundary-adapted positive PDE symmetrizer, and can one close a local Sobolev energy estimate without confusing that PDE estimate with a physical Hamiltonian positivity proof?

The answer is **yes, conditionally on a compact nondegenerate state domain and the existing cap/winding branch**, but this does **not** yet ratify a full local existence/uniqueness theorem and does not authorize a physical parent solve.

Gemini material remains `EXTERNAL_UNVERIFIED_GEMINI_DRAFT` and is not used as a premise.

The canonical ambient signature remains

\[
(-,+,+,+,+,+),
\]

with exactly one physical time.

## 2. Starting point from H4R2

On each side `s in {N,S}`, the H4/H4R1 principal block has the structure

\[
K_s(U)\,h_s^{pq}(U)\,\partial_p\partial_q U_s
+ \text{lower-order terms}=0,
\]

for

\[
U_s=(\omega,u,v,\varphi,a_\chi)^T,
\]

where `K_s` is nonsingular on the declared domain

\[
a>0,\qquad \ell>0,\qquad Z_F>0.
\]

After left multiplication by `K_s^{-1}` and a local time-radial principal normalization, write the quasilinear wave representative as

\[
\partial_\tau^2U_s-c_s^2(U,\partial U)\,\partial_{x_s}^2U_s
=F_s(U,\partial U),
\]

with

\[
0<c_{\min}\le c_s\le c_{\max}<\infty.
\]

This normalization is a PDE operation only. It does not determine the sign of the physical quadratic action and therefore does not establish ghost freedom.

## 3. Variable-coefficient first-order reduction

Define

\[
P_s:=\partial_\tau U_s,
\qquad
Q_s:=\partial_{x_s}U_s.
\]

Then the principal first-order system is

\[
\partial_\tau U_s=P_s,
\]

\[
\partial_\tau P_s-c_s^2\partial_{x_s}Q_s
=\mathcal F_s(U_s,P_s,Q_s),
\]

\[
\partial_\tau Q_s-\partial_{x_s}P_s=0.
\]

The last equation is the reduction constraint. If it holds initially, its propagation follows identically from commutation of partial derivatives for a smooth solution.

## 4. Exact row-normalization of the cap operator

H4R2 used the metric normal block

\[
B_g=
\begin{pmatrix}
0&-3&-1\\
-1&-2&-1\\
-1&-3&0
\end{pmatrix},
\qquad
\det B_g=-4.
\]

Its exact inverse is

\[
B_g^{-1}
=\frac14
\begin{pmatrix}
3&-3&-1\\
-1&1&-1\\
-1&-3&3
\end{pmatrix}.
\]

The side normal matrix in H4R2 was

\[
J_s=\operatorname{diag}(B_g,1,z_s),
\qquad
z_s:=\frac{Z_{F,s}}{\ell_s^2}>0.
\]

Use the **common invertible row transformation**

\[
L_B=\operatorname{diag}(B_g^{-1},1,1).
\]

Because left multiplication of a boundary equation by an invertible matrix does not change its zero set,

\[
J_s D_nU_s=0
\quad\Longleftrightarrow\quad
D_sD_nU_s=0,
\]

where

\[
\boxed{
D_s:=L_BJ_s
=\operatorname{diag}(1,1,1,1,z_s)
}.
\]

Thus the apparently indefinite metric junction block can be converted, without changing the boundary equation, into a strictly positive diagonal principal boundary weight.

This is a key H4R3 result.

## 5. Explicit PDE symmetrizer

For the derivative state

\[
Y_s=(P_s,Q_s)^T,
\]

multiply the `P_s` equation by `D_s/c_s^2` and the `Q_s` equation by `D_s`. The principal system becomes

\[
A_s^0\partial_\tau Y_s+A_s^1\partial_{x_s}Y_s
=\text{lower order},
\]

with

\[
\boxed{
A_s^0=
\begin{pmatrix}
D_s/c_s^2&0\\
0&D_s
\end{pmatrix}
},
\]

and

\[
\boxed{
A_s^1=
\begin{pmatrix}
0&-D_s\\
-D_s&0
\end{pmatrix}
}.
\]

Both matrices are symmetric.

Because

\[
D_s=\operatorname{diag}(1,1,1,1,z_s),
\qquad z_s\ge z_{\min}>0,
\]

and

\[
0<c_{\min}\le c_s\le c_{\max},
\]

`A_s^0` is uniformly positive definite on the declared compact state domain. In particular,

\[
\lambda_{\min}(A_s^0)
\ge
\min(1,z_{\min})
\min\left(1,\frac1{c_{\max}^2}\right)>0.
\]

Therefore the normalized variable-coefficient principal system is explicitly symmetrizable hyperbolic on that domain.

### Critical hygiene statement

\[
\boxed{
\text{positive PDE symmetrizer}
\neq
\text{positive physical Hamiltonian}
}
\]

The matrix `A_s^0` is constructed to control the PDE energy norm. It is not the Hessian of the reduced physical action with respect to canonical velocities. H4R3 therefore makes **no ghost-freedom claim**.

## 6. Principal interface flux and maximal conservativity

The field continuity conditions imply

\[
U_N|_\Sigma=U_S|_\Sigma.
\]

Differentiating in `tau` gives the principal relation

\[
P_N|_\Sigma=P_S|_\Sigma=:P_\Sigma.
\]

After the exact row normalization, the homogeneous principal normal matching is

\[
D_NQ_N+D_SQ_S=0,
\]

up to the already frozen outward-normal convention.

The boundary term generated by the symmetrized bulk energy is proportional to

\[
\mathfrak F_\Sigma
=P_\Sigma^T(D_NQ_N+D_SQ_S).
\]

Hence

\[
\boxed{\mathfrak F_\Sigma=0}.
\]

There are 20 principal derivative boundary variables,

\[
(P_N,Q_N,P_S,Q_S),
\]

with five components in each vector. The interface supplies ten independent principal relations:

- five from `P_N-P_S=0`,
- five from `D_NQ_N+D_SQ_S=0`.

Therefore the allowed principal boundary subspace has dimension 10, exactly half the derivative boundary phase space. Since the flux vanishes identically on that subspace, it is a **maximal isotropic**, equivalently maximally conservative, principal interface subspace for the H4R3 symmetrizer.

This is stronger than the H4R2 determinant test, but it still concerns the principal interface structure rather than the full nonlinear theorem.

## 7. Why the cap does not introduce a new principal time derivative in this branch

The canonical cap ledger fixes

\[
\sigma=n\chi
\]

for the static winding branch. Its localized kinetic object is

\[
X_\sigma=h^{ab}D_a\sigma D_b\sigma,
\]

which in this branch reduces to

\[
X_\sigma=\frac{(n-q_\sigma A_\chi)^2}{L^2}.
\]

Thus the currently frozen cap source maps `lambda(phi)`, `Z_sigma(phi)X_sigma`, the scalar matching source, and the gauge matching source are algebraic in the boundary fields at principal time-radial order. They do not add an independent second time derivative at the cap in the retained winding sector.

If a dynamical cap phase `sigma(t,chi)` is later released, the H4R3 principal boundary analysis must be redone.

## 8. Variable-coefficient constraint energy

H4R2 recorded the principal constraint system, up to orientation conventions, as

\[
\partial_\tau C_H=\partial_x C_M+\text{lower},
\]

\[
\partial_\tau C_M=\partial_x C_H+\text{lower}.
\]

Equivalently,

\[
\partial_\tau C+A_C(U)\partial_xC=B_C(U,\partial U)C,
\]

with a symmetric principal reference matrix. The cap Codazzi balance together with

- the dynamic junction equations,
- scalar matching,
- Maxwell matching,
- patch/flux preservation,
- and the bulk scalar/Maxwell equations

removes an external source in the combined two-sided constraint flux channel.

For a smooth parent solution satisfying those conditions, the constraint energy therefore obeys an estimate of the form

\[
\frac{dE_C}{d\tau}\le C_K E_C.
\]

Consequently,

\[
E_C(0)=0
\quad\Longrightarrow\quad
E_C(\tau)=0
\]

for as long as the assumed smooth solution remains in the compact state domain.

This is classified as

`PASS_CONDITIONAL_VARIABLE_COEFFICIENT_CONSTRAINT_ENERGY_PROPAGATION`.

It is not an independent proof that such a parent solution exists.

## 9. Nonlinear Sobolev energy

Take an integer regularity index

\[
m\ge3
\]

for the 1D radial reduction. Define a schematic energy

\[
E_m(\tau)
=\sum_s\sum_{|\alpha|\le m-1}
\int dx_s\,
\left[
(\partial^\alpha P_s)^T\frac{D_s}{c_s^2}(\partial^\alpha P_s)
+(\partial^\alpha Q_s)^TD_s(\partial^\alpha Q_s)
+|\partial^\alpha U_s|^2
\right]
+E_{C,m}.
\]

On a compact state set `K`, assume

\[
a\ge a_{\min}>0,
\quad
\ell\ge\ell_{\min}>0,
\quad
Z_F\ge Z_{\min}>0,
\quad
c_s\in[c_{\min},c_{\max}],
\]

and that all coefficient/source maps are `C^{m+1}`.

In one spatial dimension, the Sobolev/Moser product estimates at `m>=3` control the coefficient commutators generated by differentiating `D_s(U)` and `c_s(U,partial U)` without principal derivative loss.

The homogeneous principal interface flux cancels exactly by Section 6. The remaining nonlinear cap terms appear only as lower-order trace/source contributions in the retained static winding branch.

Accordingly the energy inequality has the local template

\[
\boxed{
\frac{dE_m}{d\tau}
\le
C_K\bigl(1+\sqrt{E_m}\bigr)E_m
+C_K\|G_\Sigma\|_{H^{m-1/2}}^2
}
\]

where `G_Sigma` denotes compatible nonhomogeneous lower-order cap residual/source data.

For homogeneous compatible boundary data,

\[
G_\Sigma=0,
\]

one obtains a local Gronwall bound while the solution remains inside `K`.

### H4R3 classification

This establishes a

`PASS_CONDITIONAL_LOCAL_QUASILINEAR_SOBLEV_ENERGY_CLOSURE_TEMPLATE`.

It does **not** yet ratify the full local IBVP existence/uniqueness theorem, because the exact nonlinear coefficient maps, the complete compatibility hierarchy, and the theorem hypotheses must still be checked against the unreduced H4 residual equations rather than only their principal structure.

## 10. What H4R3 proves and what it does not

### Proven/formally established within the declared reduced branch

1. Exact invertible normalization of the metric cap block:

\[
L_BJ_s=D_s=\operatorname{diag}(1,1,1,1,z_s)>0.
\]

2. Explicit variable-coefficient positive PDE symmetrizer:

\[
A_s^0=\operatorname{diag}(D_s/c_s^2,D_s)>0.
\]

3. Symmetric spatial principal matrix.

4. Exact cancellation of the homogeneous principal two-sided interface energy flux.

5. Maximal-isotropic/maximally-conservative principal interface count.

6. Conditional variable-coefficient constraint energy propagation for an already smooth cap-compatible parent solution.

7. Conditional local Sobolev energy closure template on a compact nondegenerate state domain.

### Still open

- exact full nonlinear compatibility hierarchy,
- theorem-level local existence and uniqueness,
- continuation criterion beyond the compact state domain,
- global existence,
- singularity/bounce behavior,
- positivity of the physical canonical Hamiltonian,
- full spin-2/spin-1/spin-0 ghost analysis,
- an actual parent PDE solution,
- D2N-Q dynamic selection,
- identification of `B_Lambda` and `B_m` from parent integration constants.

## 11. Governance

The following remain unchanged:

```text
PHYSICAL_PARENT_SOLVE = NOT_AUTHORIZED
D2NQ_PARENT_DYNAMIC_SELECTION = OPEN_NOT_EXECUTED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
WP4 = BLOCKED
PHYSICAL_EVIDENCE_EFFECT = NONE
```

A PDE symmetrizer is not a physical stability certificate. A conditional energy inequality is not evidence for HZT and does not close K1-D.

## 12. Next candidate

The next admissible block is

`C-PHYS-PARENT-H4R4-EXACT-COEFFICIENT-COMPATIBILITY-HIERARCHY-LOCAL-IBVP-THEOREM-RATIFICATION-AND-MANUFACTURED-SOLUTION-PREFLIGHT`.

H4R4 should inspect the **exact nonlinear H4 coefficient/residual maps**, enumerate compatibility conditions through the required order, and only then decide whether a standard local quasilinear symmetric-hyperbolic IBVP theorem is genuinely applicable. A manufactured-solution test may be prepared as a nonphysical code-verification step, but no physical parent solve is authorized by H4R3.
