# HZT-M0 / S6 / C-PHYS — H4R1 Dimensionless IBVP, Constraint Propagation and Boundary-Rank Preflight v0.1

**Date:** 2026-08-14  
**Block:** `C-PHYS-PARENT-H4R1-DIMENSIONLESS-IBVP-CONSTRAINT-PROPAGATION-AND-BOUNDARY-RANK-PREFLIGHT`  
**Scope:** formal preflight only; no physical backend import, no PDE solve, no evidence effect

## 1. Purpose

H4 established a formally closed time-radial M1 subsector and a nondegenerate local field-space principal matrix. H4R1 now asks the next narrower question:

> Can that reduced system be written as a dimensionless initial-boundary value problem with a controlled constraint identity and a locally full-rank cap boundary operator, without yet claiming a globally well-posed nonlinear solve?

The answer is **yes at the local/formal preflight level**, but **no global IBVP release follows**. In particular, incoming constraint preservation at the cap, the full two-sided complementing condition, nonlinear energy estimates, existence and uniqueness remain open.

Gemini material remains `EXTERNAL_UNVERIFIED_GEMINI_DRAFT` and is not used as a premise.

## 2. Dimensionless variables

The frozen M1 conventions already fix

\[
\tau=M_6 t,\qquad x=M_6 r,\qquad
\varphi=\phi/M_6^2,\qquad \ell=M_6L,\qquad
a_\chi=A_\chi/M_6.
\]

For the nonseparable time-radial geometry define positive fixed reference values and logarithmic fields

\[
u=\ln(a/a_{\rm ref}),\qquad v=\ln(\ell/\ell_{\rm ref}).
\]

For the local principal-symbol representative use the 2D conformal gauge

\[
h_{pq}=e^{2\omega}\eta_{pq}.
\]

Thus the gauge-fixed field vector for local principal analysis is

\[
q^I=(\omega,u,v,\varphi,a_\chi).
\]

The model parameters remain frozen per model instance:

\[
\hat\Lambda=\Lambda_{\rm geom}/M_6^2,
\quad \hat\kappa_6^2=\kappa_6^2M_6^4,
\quad \hat\lambda=\lambda/M_6^5,
\quad \hat z_\sigma=Z_\sigma/M_6^3,
\quad \hat q=M_6q_{\rm ref}.
\]

No member of the frozen parameter vector is silently promoted to an adaptive shooting variable.

## 3. Principal characteristic structure

H4 gave the gravitational field-space principal matrix for `(omega,a,L)` with

\[
\det K_g=12a^7L.
\]

The scalar and gauge principal coefficients are respectively

\[
K_\varphi=-\frac12a^3L,
\qquad
K_A=-\frac12\frac{a^3Z_F}{L},
\]

with

\[
Z_F=e^{-2a_F\varphi}>0
\]

for every finite `varphi` in M1. Hence, on

\[
a>0,\quad L>0,
\]

the complete local field-space principal matrix is nonsingular.

After a local algebraic field redefinition the principal symbol has the factorized form

\[
P(\xi)=K_{\rm field}\,h^{pq}\xi_p\xi_q.
\]

Therefore the local characteristic set is

\[
\boxed{h^{pq}\xi_p\xi_q=0}.
\]

This establishes a **local wave-type characteristic preflight**. It does not establish global hyperbolicity, nonlinear existence, Hamiltonian positivity or ghost freedom.

## 4. Initial-data inventory

A second-order gauge-fixed formulation has the candidate initial traces

\[
q^I(\tau_0,x),\qquad \partial_\tau q^I(\tau_0,x),
\]

for the five fields. These ten functions are not a physical degree-of-freedom count. They must satisfy the two Einstein constraints

\[
C_H=E_{AB}u^Au^B=0,
\qquad
C_M=E_{AB}u^As^B=0,
\]

where

\[
E_{AB}=G_{AB}+\Lambda_{\rm geom}g_{AB}-\kappa_6^2T_{AB}.
\]

Residual conformal-coordinate normalization must also be fixed as coordinate gauge, not interpreted as physical data.

## 5. Bulk constraint propagation

The contracted Bianchi identity gives exactly

\[
\nabla^A(G_{AB}+\Lambda_{\rm geom}g_{AB})=0.
\]

For the frozen scalar-Maxwell action, the scalar and Maxwell Euler-Lagrange equations imply

\[
\nabla^AT_{AB}=0.
\]

Therefore

\[
\boxed{\nabla^AE_{AB}=0}.
\]

Once the independent evolution equations are imposed, the two remaining reduced Einstein constraints obey a homogeneous first-order system of the structural form

\[
\partial_\tau C=\mathsf A(\tau,x)\partial_xC+\mathsf B(\tau,x)C,
\qquad
C=(C_H,C_M)^T.
\]

Hence zero constraints propagate in the bulk **provided** the homogeneous constraint subsystem is well posed and no incoming constraint mode is injected at a boundary.

This is the exact scope of the H4R1 result:

\[
\boxed{\text{bulk Bianchi propagation identity: PASS}}
\]

but

\[
\boxed{\text{cap incoming-constraint compatibility: OPEN}}.
\]

## 6. Dynamic cap boundary normal-rank test

Use the normalized outward normal derivative variables

\[
d_n=(K_t,K_a,K_\chi,D_n\varphi,D_na_\chi)^T.
\]

The three metric junction residuals are

\[
J_t=-(3K_a+K_\chi)+\hat\kappa_6^2(\hat\lambda+\hat Y_\sigma/2),
\]

\[
J_s=-(K_t+2K_a+K_\chi)+\hat\kappa_6^2(\hat\lambda+\hat Y_\sigma/2),
\]

\[
J_\chi=-(K_t+3K_a)+\hat\kappa_6^2(\hat\lambda-\hat Y_\sigma/2).
\]

Their Jacobian with respect to `(K_t,K_a,K_chi)` is

\[
B_g=
\begin{pmatrix}
0&-3&-1\\
-1&-2&-1\\
-1&-3&0
\end{pmatrix},
\qquad
\boxed{\det B_g=-4}.
\]

The M1 scalar matching has unit normal coefficient because `Z_phi=1` and both `lambda_,phi` and `Z_sigma_,phi` vanish. The gauge matching normal coefficient is proportional to

\[
\frac{Z_F}{\ell^2},
\]

which is nonzero for finite `varphi` and `ell>0`.

Thus, up to nonzero orientation and normalization factors,

\[
\boxed{
\det B_n=-4\frac{Z_F}{\ell^2}\neq0
}
\]

and the local cap normal-derivative boundary operator has rank five.

This is a **boundary normal-rank preflight**, not a two-sided Lopatinski-Shapiro theorem. The latter additionally couples boundary values, decaying normal modes, both regional principal symbols, orientations and constraint-preserving incoming characteristics.

## 7. Continuity and two-sided inventory

The two-sided cap problem must still enforce the value traces

\[
\Delta n=0,
\quad
\Delta a=0,
\quad
\Delta L=0,
\quad
\Delta\varphi=0,
\quad
\Delta a_\chi=0\ \text{modulo the frozen patch relation}.
\]

H4R1 does not replace the outward-sum convention by an unmarked jump convention.

## 8. Flux and gauge-patch propagation

The frozen global patch residual is

\[
R_{\rm patch}=a_{\chi,N}-a_{\chi,S}-\frac{N_F}{\hat q}.
\]

With fixed integer `N_F` and fixed `q_hat`, differentiation gives

\[
\partial_\tau R_{\rm patch}
=
\partial_\tau a_{\chi,N}
-
\partial_\tau a_{\chi,S}.
\]

Therefore a quantized patch sector initialized with `R_patch=0` is preserved if the boundary evolution produces zero tangential-time mismatch in `a_chi`.

Equivalently, from `dF=0`, the time derivative of the magnetic flux through the internal `(r,chi)` surface equals the boundary electromotive mismatch. Flux conservation is therefore a boundary compatibility condition, not an automatic consequence of the local Maxwell equation alone.

## 9. Smooth-pole alternative

If an endpoint is a smooth pole rather than a codimension-1 cap, with `Delta_chi=2*pi`, proper radial distance `s` requires locally

\[
L=s+O(s^3).
\]

Regular scalar invariants are even in `s` to leading order, while a regular gauge patch has

\[
A_\chi=A_{\chi,0}^{\rm pure\ gauge}+O(s^2).
\]

This pole branch is an alternative endpoint condition and is not imposed simultaneously with the cap interface at the same endpoint.

## 10. Gate disposition

H4R1 establishes:

- dimensionless IBVP variable contract: **PASS**;
- local wave-type characteristic preflight: **PASS**;
- formal homogeneous bulk constraint-propagation identity: **PASS**;
- local cap normal boundary rank: **PASS, rank 5**;
- flux/patch preservation condition: **PASS, conditional**.

H4R1 does **not** establish incoming constraint compatibility at the cap, the complete two-sided complementing condition, a nonlinear energy estimate, global existence/uniqueness, ghost freedom, a bounce, or dynamic D2N-Q selection.

Therefore the governance state remains

```text
PHYSICAL_PARENT_SOLVE = NOT_AUTHORIZED
D2NQ_PARENT_DYNAMIC_SELECTION = OPEN_NOT_EXECUTED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
WP4 = BLOCKED
PHYSICAL_EVIDENCE_EFFECT = NONE
```

## 11. Next block

The next permitted step is

`C-PHYS-PARENT-H4R2-BOUNDARY-CONSTRAINT-COMPATIBILITY-TWO-SIDED-COMPLEMENTING-AND-ENERGY-ESTIMATE-PREFLIGHT`.

H4R2 must explicitly analyze incoming constraint characteristics at the cap and the two-sided frozen-coefficient normal-mode boundary determinant before any physical time-dependent parent solve can be considered.
