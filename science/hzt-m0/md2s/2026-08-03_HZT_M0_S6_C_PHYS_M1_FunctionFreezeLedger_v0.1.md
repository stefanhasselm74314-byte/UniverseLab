# HZT-M0-S6-C-PHYS-M1 — Function Freeze Ledger v0.1

**Date:** 2026-08-03  
**Track:** `MD2S-R1-C-PHYS`  
**Block:** `C-PHYS-R1.0-FREEZE-1B`  
**Classification:** `VERSIONED_PHYSICAL_CANDIDATE_MODEL_SELECTION_NOT_DERIVATION`

## 0. Executive result

The exact function family of the first current-canonical physical candidate is fixed as

\[
\boxed{
U(\phi)=\frac12\widehat m_\phi^{\,2}M_6^6\varphi^2,
\qquad
Z_F(\phi)=e^{-2a_F\varphi},
\qquad
\lambda(\phi)=\widehat\lambda M_6^5,
\qquad
Z_\sigma(\phi)=\widehat z_\sigma M_6^3
}
\]

with

\[
\varphi\equiv \frac{\phi}{M_6^2},
\qquad
\phi\in\mathbb R,
\]

and parameter domains

\[
\widehat m_\phi^{\,2}>0,\qquad
a_F>0,\qquad
\widehat z_\sigma>0,\qquad
\widehat q>0,\qquad
\widehat\lambda,\widehat\Lambda_6\in\mathbb R.
\]

The charge normalization is

\[
q_{\rm ref}=\frac{\widehat q}{M_6},
\qquad
q_\sigma=m_\sigma q_{\rm ref},
\qquad
m_\sigma\in\mathbb Z_{>0}.
\]

This result closes the exact-function part of the model definition. It does **not** establish a background solution, a continuum implicit-function theorem, perturbative stability, K1-D, K1-E, or solver authorization.

---

## 1. What is derived and what is selected

### 1.1 Already derived or frozen before this block

The following structures are inherited from the current-canonical parent-action and Freeze-1A contracts:

1. canonical six-dimensional scalar kinetic term, `Z_phi=1`;
2. Einstein-Hilbert and Maxwell normalizations;
3. static two-disk background ansatz;
4. generic radial Einstein, scalar and Maxwell equations;
5. cap tension plus gauge-covariant winding sector;
6. angular period `Delta_chi=2*pi`;
7. local boundary normals and global two-form orientations;
8. regular gauge patches and patch/flux equivalence;
9. charge lattice `q_sigma=m_sigma q_ref`;
10. frame `A_N(0)=0`;
11. the conditional eight-unknown/eight-residual BVP count.

### 1.2 Newly selected in this block

The specific functions `U`, `Z_F`, `lambda`, and `Z_sigma` are **not derived from first principles** by the available project record. They are selected as the smallest nontrivial exact family satisfying:

- correct mass dimensions;
- global smoothness on the declared scalar domain;
- lower bounded bulk potential;
- strictly positive gauge kinetic function;
- strictly positive winding coefficient;
- one and only one nontrivial scalar-coupling slope in the first physical candidate;
- no redundant constant in `U` that would duplicate `Lambda6`;
- no direct localized scalar source in the first candidate;
- a finite information budget.

The resulting model is assigned the independent identity

```text
HZT-M0-S6-C-PHYS-M1
```

and is neither historical A0 nor C1-V.

---

## 2. Dimensions and dimensionless variables

The parent action fixes

\[
[M_6]=M,\quad [\phi]=M^2,\quad [U]=M^6,\quad [\lambda]=M^5,\quad [Z_\sigma]=M^3,\quad [q]=M^{-1}.
\]

Define

\[
x=M_6r,\qquad
\ell=M_6L,\qquad
\varphi=\frac{\phi}{M_6^2},\qquad
\mathcal A_\chi=\frac{A_\chi}{M_6},\qquad
\mathcal Q_s=\frac{Q_s}{M_6^3},
\]

and

\[
k_4=\frac{\mathcal K_4}{M_6^2},\qquad
\widehat\Lambda_6=\frac{\Lambda_6}{M_6^2}.
\]

The selected functions become

\[
u(\varphi)\equiv \frac{U}{M_6^6}
 =\frac12\widehat m_\phi^{\,2}\varphi^2,
\]

\[
z_F(\varphi)=e^{-2a_F\varphi},
\qquad
\widehat\lambda\equiv \frac{\lambda}{M_6^5},
\qquad
\widehat z_\sigma\equiv \frac{Z_\sigma}{M_6^3}.
\]

All six background-shape parameters are dimensionless:

\[
\boxed{
P_{\rm M1}=
(\widehat\Lambda_6,
\widehat m_\phi^{\,2},
a_F,
\widehat\lambda,
\widehat z_\sigma,
\widehat q)
}
\]

while `M6` is the dimensional reconstruction anchor.

---

## 3. Bulk-function audit

### 3.1 Scalar potential

\[
U(\phi)=\frac12\widehat m_\phi^{\,2}M_6^6\varphi^2
       =\frac12\widehat m_\phi^{\,2}M_6^2\phi^2.
\]

Therefore

\[
U(0)=0,\qquad
U_{,\phi}=\widehat m_\phi^{\,2}M_6^4\varphi,\qquad
U_{,\phi\phi}=\widehat m_\phi^{\,2}M_6^2>0.
\]

Consequences:

- `U` is `C^infinity` on `R`;
- `U>=0`;
- `phi=0` is the unique global minimum;
- the scalar has a positive bare mass scale;
- no constant `U0` is present.

The last point is essential. A constant contribution to `U` is exactly degenerate with the separately defined bulk cosmological constant. The convention

\[
U(0)=0
\]

prevents double counting.

### 3.2 Gauge kinetic function

\[
Z_F(\phi)=e^{-2a_F\varphi}.
\]

For every finite real `phi`,

\[
Z_F>0.
\]

Moreover

\[
Z_F(0)=1,\qquad
\partial_\phi\ln Z_F=-\frac{2a_F}{M_6^2},\qquad
\partial_\phi^2\ln Z_F=0.
\]

This accomplishes three tasks simultaneously:

1. it fixes the gauge-field normalization at the scalar reference point;
2. it prevents a sign change of the Maxwell kinetic term;
3. it introduces exactly one nontrivial scalar-flux coupling slope.

The active M1 branch requires

\[
a_F>0.
\]

The transformation `phi -> -phi` maps `a_F -> -a_F`. Restricting `a_F>0` chooses one representative of this redundant reflection pair.

The limit

\[
a_F\rightarrow0
\]

is retained only as a declared decoupling control. It is not the active model and does not establish C1-V identity.

---

## 4. Cap-function audit

### 4.1 Constant cap tension

\[
\lambda(\phi)=\widehat\lambda M_6^5.
\]

Hence

\[
\lambda_{,\phi}=0,\qquad
\lambda_{,\phi\phi}=0.
\]

The sign of `lambda_hat` is not silently fixed. Positive, zero, and negative tension sectors are separate model instances and must be recorded.

The constant choice is deliberate:

- it is the lowest-information exact cap tension;
- it does not inject an additional localized scalar force;
- it avoids the unbounded linear cap function used in the manufactured C1-V system;
- it leaves all nontrivial scalar forcing in the physical M1 candidate traceable to the bulk flux coupling.

### 4.2 Constant positive winding coefficient

\[
Z_\sigma(\phi)=\widehat z_\sigma M_6^3,
\qquad
\widehat z_\sigma>0.
\]

Therefore

\[
Z_{\sigma,\phi}=0,\qquad
Z_{\sigma,\phi\phi}=0.
\]

The winding energy is positive on the active branch:

\[
Y_\sigma=Z_\sigma\frac{d_\chi^2}{L_\Sigma^2}\ge0.
\]

The boundary value `z_sigma_hat=0` is not part of active M1. It is a separate no-anisotropy boundary limit.

---

## 5. Specialized dimensionless equations

For each region `s=N,S`, define

\[
\widehat\rho_{F,s}
 =\frac12\mathcal Q_s^2
   e^{-8A_s+2a_F\varphi_s}.
\]

### 5.1 Warp equation

\[
\boxed{
4A_s''+10(A_s')^2
-6k_4e^{-2A_s}
+\widehat\Lambda_6
+\frac12(\varphi_s')^2
+\frac12\widehat m_\phi^{\,2}\varphi_s^2
-\widehat\rho_{F,s}=0
}
\]

where primes now denote `d/dx`.

### 5.2 Internal-radius equation

\[
\boxed{
\ell_s''+3A_s''\ell_s+6(A_s')^2\ell_s+3A_s'\ell_s'
-3k_4e^{-2A_s}\ell_s+\widehat\Lambda_6\ell_s
+\ell_s\left[
\frac12(\varphi_s')^2
+\frac12\widehat m_\phi^{\,2}\varphi_s^2
+\widehat\rho_{F,s}
\right]=0
}
\]

### 5.3 Scalar equation

Because

\[
\partial_\varphi\ln z_F=-2a_F,
\]

the scalar equation is

\[
\boxed{
\ell_s\varphi_s''
+(4A_s'\ell_s+\ell_s')\varphi_s'
-\ell_s\widehat m_\phi^{\,2}\varphi_s
+2a_F\ell_s\widehat\rho_{F,s}=0
}
\]

The last term is the sole explicit nontrivial scalar source selected in M1.

### 5.4 Gauge equation

\[
\boxed{
\mathcal A_{\chi,s}'
-\mathcal Q_s\ell_s
 e^{-4A_s+2a_F\varphi_s}=0
}
\]

### 5.5 Radial constraint

\[
\boxed{
\ell_s\left[-6k_4e^{-2A_s}+6(A_s')^2+\widehat\Lambda_6\right]
+4A_s'\ell_s'
-\ell_s\left[
\frac12(\varphi_s')^2
-\frac12\widehat m_\phi^{\,2}\varphi_s^2
+\widehat\rho_{F,s}
\right]=0
}
\]

This remains a propagated QA channel only after the Bianchi-dependency proof.

---

## 6. Smooth-pole coefficients

With Freeze-1A period `Delta_chi=2*pi`, the smooth pole series are

\[
A_s=A_{0,s}+a_{2,s}x^2+O(x^4),
\]

\[
\ell_s=x+l_{3,s}x^3+O(x^5),
\]

\[
\varphi_s=\varphi_{0,s}+f_{2,s}x^2+O(x^4),
\]

\[
\mathcal A_{\chi,s}=g_{2,s}x^2+O(x^4).
\]

Let

\[
\widehat\rho_{F0,s}
=\frac12\mathcal Q_s^2e^{-8A_{0,s}+2a_F\varphi_{0,s}}.
\]

Then

\[
\boxed{
a_{2,s}=\frac{
6k_4e^{-2A_{0,s}}
-\widehat\Lambda_6
-\frac12\widehat m_\phi^{\,2}\varphi_{0,s}^2
+\widehat\rho_{F0,s}}{8}
}
\]

\[
\boxed{
f_{2,s}=\frac{
\widehat m_\phi^{\,2}\varphi_{0,s}
-2a_F\widehat\rho_{F0,s}}{4}
}
\]

\[
\boxed{
g_{2,s}=\frac12\mathcal Q_s
 e^{-4A_{0,s}+2a_F\varphi_{0,s}}
}
\]

\[
\boxed{
l_{3,s}=\frac{
3k_4e^{-2A_{0,s}}
-12a_{2,s}
-\widehat\Lambda_6
-\frac12\widehat m_\phi^{\,2}\varphi_{0,s}^2
-\widehat\rho_{F0,s}}{6}
}
\]

Higher-order series remain part of Operator-2A.

---

## 7. Specialized cap system

Freeze-1A gives

\[
q_{\rm ref}=\frac{\widehat q}{M_6},\qquad
q_\sigma=m_\sigma q_{\rm ref}.
\]

The gauge-invariant winding is

\[
\boxed{
d_\chi=N_\sigma-m_\sigma\widehat q\,\mathcal A_{\chi,\Sigma}
}
\]

and

\[
\boxed{
\widehat Y_\sigma
=\frac{Y_\sigma}{M_6^5}
=\widehat z_\sigma\frac{d_\chi^2}{\ell_\Sigma^2}
}
\]

The dimensionless metric junctions are

\[
\boxed{
R_{4D}=-3\widehat A_\Sigma-\widehat L_\Sigma
+\widehat\lambda+\frac12\widehat Y_\sigma=0
}
\]

\[
\boxed{
R_\chi=-4\widehat A_\Sigma
+\widehat\lambda-\frac12\widehat Y_\sigma=0
}
\]

The scalar junction collapses to the source-free cap condition

\[
\boxed{
R_{\rm scalar}
=\varphi_N'(x_N=1)+\varphi_S'(x_S=1)=0
}
\]

and the local gauge residual is

\[
\boxed{
R_{\rm gauge}
=\sum_{s=N,S}\frac{\mathcal Q_s e^{-4A_{s,\Sigma}}}{\ell_\Sigma}
-\frac{m_\sigma\widehat q\widehat z_\sigma d_\chi}{\ell_\Sigma^2}=0
}
\]

while the single global topological residual remains

\[
\boxed{
R_{\rm patch}
=\mathcal A_{\chi,N}(1)-\mathcal A_{\chi,S}(1)
-\frac{N_F}{\widehat q}=0.
}
\]

`R_patch` and flux quantization are not counted twice.

---

## 8. Redundancy audit

### 8.1 Scalar shift

A generic shift

\[
\phi\rightarrow\phi+c
\]

would move the potential minimum and rescale `Z_F`. M1 removes this duplicate labeling by defining

\[
\phi=0
\]

as both the unique potential minimum and gauge-kinetic normalization point.

### 8.2 Scalar scale

The canonical kinetic term fixes the multiplicative scalar normalization. A rescaling of `phi` would alter the kinetic term and is not a remaining redundancy.

### 8.3 Scalar reflection

The pair

\[
(\phi,a_F)
\quad\hbox{and}\quad
(-\phi,-a_F)
\]

represents the same field orientation. The convention `a_F>0` removes this duplicate.

### 8.4 Vacuum constant

A constant in `U` is absorbed into `Lambda6`. Therefore `U(0)=0` is a no-double-counting convention.

### 8.5 Gauge normalization

`Z_F(0)=1`, together with the frozen Maxwell coefficient, fixes gauge normalization. Consequently `q_hat` is physical model data and cannot be set to one without changing the model.

---

## 9. Information and identifiability budget

The dimensionless model vector has six entries:

\[
P_{\rm M1}=
(\widehat\Lambda_6,
\widehat m_\phi^{\,2},
a_F,
\widehat\lambda,
\widehat z_\sigma,
\widehat q).
\]

This is deliberately smaller than a generic exponential bulk-plus-cap model, which would add independent slopes to `lambda` and `Z_sigma`.

The following combinations may remain correlated at background level:

1. bulk flux energy:
   \[
   \mathcal Q_s^2e^{2a_F\varphi_s};
   \]
2. cap anisotropy:
   \[
   \widehat z_\sigma d_\chi^2;
   \]
3. gauge matching:
   \[
   m_\sigma\widehat q\widehat z_\sigma d_\chi;
   \]
4. dimensional reconstruction:
   `M6` is absent from the dimensionless background equations.

Therefore this function freeze has no K1-D effect. Later work must compute both

\[
\frac{\partial R}{\partial X_{\rm BVP}}
\]

and

\[
\frac{\partial R}{\partial P_{\rm M1}}.
\]

---

## 10. Alternatives audit

### 10.1 Constant `Z_F`

Deferred to the `a_F=0` control because it removes the only selected nontrivial scalar-flux coupling.

### 10.2 Linear `Z_F`

Rejected for M1 because a globally linear kinetic function can cross zero and change the sign of the Maxwell kinetic sector.

### 10.3 Linear `lambda`

Rejected for M1 because it introduces a new unbounded localized scalar slope before identifiability is established. It would also make the first physical candidate unnecessarily close in functional appearance to the manufactured C1-V cap ansatz.

### 10.4 Exponential `lambda` and `Z_sigma`

Deferred. These choices preserve positivity where needed but add two extra scalar slopes and localized scalar forcing. They belong to a later nested extension only after M1 identifiability and existence are understood.

### 10.5 Quartic or multi-minimum `U`

Deferred because such potentials introduce extra coefficients, additional vacua and branch structure not required for the first controlled physical candidate.

---

## 11. Gate decision

```text
FUNCTION_SELECTION       = PASS_POSTULATED_MODEL_FAMILY
MF-001 bulk functions    = FROZEN_FOR_C_PHYS_M1
MF-002 cap functions     = FROZEN_FOR_C_PHYS_M1
R1.0                     = ACTIVE_OPERATOR_CLOSURE_REMAINING
R1.1                     = BLOCKED
R1.2                     = BLOCKED
structural BVP count     = SQUARE_CONDITIONAL
continuum BVP operator   = SCAFFOLD_ONLY
continuum BVP Jacobian   = NOT_PROVEN
physical background      = NOT_ESTABLISHED
official solver          = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical evidence effect = NONE
```

---

## 12. Exact next block

```text
C-PHYS-R1.0-OPERATOR-2A
```

Required tasks:

1. specialize an independent ODE set;
2. prove the radial-constraint Bianchi dependency;
3. derive higher-order pole series;
4. test constraint propagation symbolically;
5. audit principal parts and complementing boundary conditions;
6. only then reconsider whether R1.1 can be entered.
