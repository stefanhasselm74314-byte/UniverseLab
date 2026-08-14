# HZT-M0 / S6 / C-PHYS — H4R2 Boundary-Constraint, Two-Sided Complementing and Energy Preflight v0.1

**Date:** 2026-08-14  
**Block:** `C-PHYS-PARENT-H4R2-BOUNDARY-CONSTRAINT-COMPATIBILITY-TWO-SIDED-COMPLEMENTING-AND-ENERGY-ESTIMATE-PREFLIGHT`  
**Scope:** frozen-coefficient linear principal analysis only; no physical PDE solve; no solver authorization; no evidence effect.

## 1. Purpose

H4R1 established a dimensionless local wave-type principal system, homogeneous bulk constraint propagation, local cap normal rank five, and a conditional patch/flux propagation law. The unresolved issue was whether the *two-sided* cap problem admits nontrivial exponentially decaying homogeneous modes and whether the cap can inject constraint violations.

H4R2 answers those questions only at the frozen-principal/formal level. It does **not** prove the nonlinear variable-coefficient IBVP.

Gemini material remains `EXTERNAL_UNVERIFIED_GEMINI_DRAFT` and is not used as a premise.

## 2. Frozen principal system

For each bulk side `s in {N,S}`, choose a local dimensionless normal coordinate `x_s >= 0` measured away from the cap. H4R1 gives a nonsingular field-space matrix `K_s` multiplying the same two-dimensional Lorentzian principal factor. After left multiplication by `K_s^{-1}` and local normalization,

\[
(-\partial_\tau^2+\partial_{x_s}^2)U_s=\text{lower order},
\qquad
U_s=(\omega,u,v,\varphi,a_\chi)^T.
\]

This reduction is a PDE principal-symbol statement. It is not a physical Hamiltonian diagonalization and carries no ghost-freedom claim.

## 3. Decaying Laplace modes

Laplace transform tangentially in `tau` with frequency `zeta`, `Re(zeta)>0`. The decaying homogeneous modes are

\[
U_s(x_s)=e^{-\kappa_s x_s}v_s,
\qquad
\kappa_s=c_s\zeta,
\qquad c_s>0,
\]

where `c_s` captures the positive local normalization on each side. Continuity across the cap gives

\[
v_N=v_S\equiv v.
\]

Because the outward unit normal from each bulk points from increasing `x_s` back toward the cap,

\[
D_n U_s=\kappa_s v_s
\]

for the decaying mode.

## 4. Principal cap operator

The metric normal-derivative block inherited from H4/H4R1 is

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

The scalar normal coefficient is nonzero and normalized to one. The gauge coefficient on side `s` is

\[
z_s=\frac{Z_{F,s}}{\ell_\Sigma^2}>0
\]

on the canonical M1 domain. Thus

\[
J_s=\operatorname{blockdiag}(B_g,1,z_s).
\]

The two-sided homogeneous interface condition has principal symbol

\[
M(\zeta)v
=\left(\kappa_NJ_N+\kappa_SJ_S\right)v=0.
\]

Its determinant is

\[
\boxed{
\det M
=-4\,(\kappa_N+\kappa_S)^4
\left(\kappa_Nz_N+\kappa_Sz_S\right)
}.
\]

For `Re(zeta)>0`, positive `c_s`, and positive `z_s`, all `kappa_s` share the phase of `zeta`; therefore neither factor can vanish. Consequently

\[
\boxed{v=0}
\]

is the only decaying homogeneous mode.

This is the frozen two-sided Lopatinskii/complementing result.

## 5. Uniform bound on a compact coefficient domain

Assume

\[
c_s\in[c_{\min},c_{\max}],\quad c_{\min}>0,
\qquad
z_s\in[z_{\min},z_{\max}],\quad z_{\min}>0,
\]

and normalize `|zeta|=1`. Then

\[
|\kappa_N+\kappa_S|\ge 2c_{\min},
\]

and

\[
|\kappa_Nz_N+\kappa_Sz_S|\ge2c_{\min}z_{\min}.
\]

Hence

\[
\boxed{
|\det M|\ge128\,c_{\min}^5z_{\min}>0
}.
\]

This is a **uniform frozen-principal complementing bound** on the declared compact coefficient set. It is not yet the variable-coefficient Kreiss theorem required for a nonlinear evolution.

## 6. Constraint compatibility at the cap

Let

\[
E_{AB}=G_{AB}+\Lambda g_{AB}-\kappa_6^2T_{AB}.
\]

When the scalar and Maxwell Euler-Lagrange equations hold,

\[
\nabla^AE_{AB}=0.
\]

In the reduced 1+1 problem the Hamiltonian/momentum constraint pair has principal propagation structure

\[
\partial_\tau C_H=\partial_x C_M+\text{lower},
\qquad
\partial_\tau C_M=\partial_x C_H+\text{lower},
\]

up to side-orientation conventions. Its principal characteristic combinations are

\[
C_\pm=C_H\pm C_M.
\]

At the cap, the contracted Codazzi identity applied to the junction equations gives the balance law

\[
D^\mu S_{\mu\nu}
+\sum_s T^{(s)}_{AB}n_s^Ah^B{}_{\nu}=0,
\]

provided the localized cap equations and the scalar/Maxwell matching conditions hold. Therefore there is no *external* source for the combined two-sided momentum-constraint flux. With initially vanishing constraints, homogeneous bulk constraint propagation and the cap balance law prevent a frozen-principal boundary source.

Classification:

\[
\boxed{\text{PASS, conditional/formal}}
\]

because a full variable-coefficient constraint boundary theorem is still absent.

## 7. Linear frozen-frequency estimate

The H4R1 principal reduction is strongly hyperbolic at the frozen level after multiplication by the nonsingular `K_s^{-1}`. Together with the uniform complementing bound above, the standard frozen-frequency argument yields a Kreiss-type resolvent estimate on the declared compact coefficient set.

This is deliberately classified as

`PASS_FROZEN_LINEAR_PRINCIPAL_RESOLVENT_ESTIMATE_PREFLIGHT`.

It is **not**:

- a positive physical Hamiltonian proof,
- a ghost-freedom proof,
- a nonlinear energy estimate,
- a variable-coefficient existence/uniqueness theorem.

## 8. Gauge patch / flux condition

The already frozen patch residual remains

\[
R_{\rm patch}=a_{\chi,N}-a_{\chi,S}-N_F/\hat q.
\]

Its preservation requires zero electromotive mismatch at the boundary. H4R2 therefore includes this condition among the hypotheses of the gauge-sector interface preflight rather than treating flux conservation as automatic.

## 9. Disposition

H4R2 closes the *frozen linear* gap left by H4R1:

- two-sided decaying-mode complementing test: **PASS**;
- uniform frozen Lopatinskii lower bound: **PASS** on the declared compact coefficient domain;
- cap constraint-flux compatibility: **PASS conditional/formal**;
- frozen linear resolvent estimate: **PASS preflight**.

Still open:

- variable-coefficient first-order/symmetric-hyperbolic reduction;
- a genuine boundary symmetrizer for the evolving coefficients;
- nonlinear Sobolev energy estimate;
- global/local-in-time existence and uniqueness for admissible data;
- full ghost freedom;
- physical parent solve;
- D2N-Q dynamic selection.

Governance therefore remains

\[
\boxed{K1\!\!-D=\mathrm{NOT\_RELEASED}},\qquad
\boxed{K1\!\!-E=\mathrm{NOT\_ADMISSIBLE}},
\]

\[
\boxed{WP4=\mathrm{BLOCKED}},\qquad
\boxed{\text{physical evidence}=\mathrm{NONE}}.
\]

## 10. Next candidate

`C-PHYS-PARENT-H4R3-VARIABLE-COEFFICIENT-FIRST-ORDER-REDUCTION-CONSTRAINT-BOUNDARY-SYMMETRIZER-AND-NONLINEAR-ENERGY-CLOSURE`

H4R3 must not start a physical parent solve. It must first promote the frozen principal result to a variable-coefficient constraint-preserving formulation and establish the corresponding local-in-time energy closure or identify the obstruction.
