# HZT-M0-S6-C-PHYS-M1 — Operator-2A Ledger v0.1

**Date:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Model:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-OPERATOR-2A`  
**Classification:** formal continuum-operator closure; no solver execution

## 1. Scope

This block specializes the current-canonical M1 differential equations, proves the radial-constraint propagation identity, derives the next nontrivial smooth-pole coefficients, and audits the principal differential matrix.

It does **not** construct a physical background, a continuum Jacobian, a Fredholm theorem, a nonlinear solver, a stability proof, or an observable map.

## 2. Dimensionless M1 system

Use

\[
x=M_6r,\qquad \ell=M_6L,\qquad \varphi=\phi/M_6^2,\qquad
a_\chi=A_\chi/M_6,
\]

\[
k_4=\mathcal K_4/M_6^2,\qquad
\widehat\Lambda=\Lambda_6/M_6^2,\qquad
q_s=Q_s/M_6^3.
\]

The frozen functions are

\[
U=\frac12\widehat m_\phi^2M_6^6\varphi^2,\qquad
Z_F=e^{-2a_F\varphi},\qquad
\lambda=\widehat\lambda M_6^5,\qquad
Z_\sigma=\widehat z_\sigma M_6^3.
\]

The Maxwell first integral gives

\[
\rho_F=\frac12q_s^2e^{-8A+2a_F\varphi},
\qquad
\rho_{F,x}=\rho_F(-8A_x+2a_F\varphi_x).
\]

The independent residuals are

\[
E_A=
4A_{xx}+10A_x^2-6k_4e^{-2A}
+\widehat\Lambda
+\frac12\varphi_x^2
+\frac12\widehat m_\phi^2\varphi^2
-\rho_F,
\]

\[
E_\ell=
\ell_{xx}+3A_{xx}\ell+6A_x^2\ell+3A_x\ell_x
-3k_4e^{-2A}\ell+\widehat\Lambda\ell
+\ell\left(
\frac12\varphi_x^2+
\frac12\widehat m_\phi^2\varphi^2+
\rho_F
\right),
\]

\[
E_\varphi=
\ell\varphi_{xx}
+(4A_x\ell+\ell_x)\varphi_x
-\ell\widehat m_\phi^2\varphi
+2a_F\ell\rho_F,
\]

\[
E_g=
a_{\chi,x}-q_s\ell e^{-4A+2a_F\varphi}.
\]

These form the independent local evolution system. The \(rr\) equation is retained as a propagated quality-assurance channel.

## 3. Exact constraint identity

Define

\[
C_{rr}=
\ell\left(
-6k_4e^{-2A}+6A_x^2+\widehat\Lambda
\right)
+4A_x\ell_x
-\ell\left(
\frac12\varphi_x^2
-\frac12\widehat m_\phi^2\varphi^2
+\rho_F
\right).
\]

Direct differentiation, using only the exact derivative of \(\rho_F\), gives the off-shell identity

\[
\boxed{
C_{rr,x}+4A_xC_{rr}
=
\ell_xE_A+4A_xE_\ell-\varphi_xE_\varphi.
}
\]

Consequently, on solutions of \(E_A=E_\ell=E_\varphi=0\),

\[
\boxed{C_{rr,x}=-4A_xC_{rr}}
\]

and therefore

\[
\boxed{
C_{rr}(x)
=
C_{rr}(x_0)
e^{-4[A(x)-A(x_0)]}.
}
\]

Thus a pole-regular solution satisfying the leading constraint data keeps \(C_{rr}=0\) throughout the open interval.

This proves dependency and propagation. It does not prove existence of the underlying solution.

## 4. Smooth-pole expansion through the next order

At either smooth pole,

\[
A=A_0+a_2x^2+a_4x^4+O(x^6),
\]

\[
\ell=x+\ell_3x^3+\ell_5x^5+O(x^7),
\]

\[
\varphi=\varphi_0+f_2x^2+f_4x^4+O(x^6),
\]

\[
a_\chi=g_2x^2+g_4x^4+O(x^6).
\]

Define

\[
K_0=k_4e^{-2A_0},
\qquad
R_0=\frac12q_s^2e^{-8A_0+2a_F\varphi_0},
\qquad
G_2=\frac12q_se^{-4A_0+2a_F\varphi_0}.
\]

The leading coefficients are

\[
a_2=
\frac{
6K_0-\widehat\Lambda
-\frac12\widehat m_\phi^2\varphi_0^2
+R_0
}{8},
\]

\[
f_2=
\frac{
\widehat m_\phi^2\varphi_0-2a_FR_0
}{4},
\]

\[
\ell_3=
\frac{
3K_0-12a_2-\widehat\Lambda
-\frac12\widehat m_\phi^2\varphi_0^2-R_0
}{6},
\qquad
g_2=G_2.
\]

The next coefficients are

\[
a_4=
-\frac14K_0a_2
-\frac16R_0a_2
+\frac1{24}R_0a_Ff_2
-\frac56a_2^2
-\frac1{24}f_2^2
-\frac1{48}\widehat m_\phi^2\varphi_0f_2,
\]

\[
f_4=
R_0a_Fa_2
-\frac14R_0a_F^2f_2
-\frac18R_0a_F\ell_3
-a_2f_2
-\frac12f_2\ell_3
+\frac1{16}\widehat m_\phi^2f_2
+\frac1{16}\widehat m_\phi^2\varphi_0\ell_3,
\]

\[
g_4=
g_2\left(
-2a_2+a_Ff_2+\frac12\ell_3
\right),
\]

\[
\ell_5=
-\frac3{20}K_0(2a_2-\ell_3)
-\frac1{20}\widehat\Lambda\ell_3
-\frac1{20}R_0(-8a_2+2a_Ff_2+\ell_3)
-\frac65a_2^2
-\frac65a_2\ell_3
-\frac{12}{5}a_4
-\frac1{10}f_2^2
-\frac1{20}\widehat m_\phi^2\varphi_0f_2
-\frac1{40}\widehat m_\phi^2\varphi_0^2\ell_3.
\]

All eight coefficient equations were checked by exact symbolic substitution.

The series are sufficient for formal regularity analysis. They are not yet authorization for numerical initialization.

## 5. Principal differential matrix

With profile order

\[
(A,\ell,\varphi,a_\chi)
\]

and highest derivatives

\[
(A_{xx},\ell_{xx},\varphi_{xx},a_{\chi,x}),
\]

the principal matrix is

\[
P(\ell)=
\begin{pmatrix}
4&0&0&0\\
3\ell&1&0&0\\
0&0&\ell&0\\
0&0&0&1
\end{pmatrix}.
\]

Hence

\[
\boxed{\det P=4\ell}.
\]

For every interior point with \(\ell>0\), the differential system has full principal rank.

At a smooth pole, \(\ell\to0\), so the scalar equation is regular-singular in the raw variables. The proper domain uses parity-factorized profiles:

\[
A=A_0+x^2\widetilde A(x^2),
\]

\[
\ell=x+x^3\widetilde\ell(x^2),
\]

\[
\varphi=\varphi_0+x^2\widetilde\varphi(x^2),
\]

\[
a_\chi=x^2\widetilde g(x^2).
\]

## 6. Boundary/complementing audit

This problem is a one-dimensional regular-singular ODE boundary-value problem. A PDE-style Lopatinskii statement with tangential frequencies is therefore not directly the final criterion.

The relevant unresolved object is the linearized pole-regular endpoint trace map, including the eight cap residuals and the global/eigenparameter augmentation. Its kernel, cokernel and singular spectrum can only be evaluated at a declared candidate background.

No physical M1 background currently exists. Therefore:

```text
interior principal rank          = PASS
constraint propagation           = PROVEN_SYMBOLIC_CONDITIONAL
higher pole series               = DERIVED
pole parity domain               = FORMALLY_DEFINED
linearized endpoint trace map    = NOT_CONSTRUCTED
complementing boundary condition = NOT_PROVEN
Fredholm property                = NOT_PROVEN
continuum Jacobian               = NOT_PROVEN
```

## 7. Gate effect

```text
R1.0                     = ACTIVE_BOUNDARY_TRACE_AND_FUNCTION_SPACE_CLOSURE_REMAINING
R1.1                     = BLOCKED
R1.2                     = BLOCKED
continuum BVP operator   = SPECIALIZED_FORMAL_OPERATOR_DEFINED
physical background      = NOT_ESTABLISHED
official solver          = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical evidence effect = NONE
```

## 8. Next block

`C-PHYS-R1.0-OPERATOR-2B`

Required work:

1. freeze the weighted pole-regular domain and target Banach spaces;
2. define trace maps at both poles and the cap;
3. audit operator closedness and density;
4. define the linearized boundary operator template;
5. preregister kernel/cokernel tests;
6. state explicitly that actual invertibility requires a candidate background.
