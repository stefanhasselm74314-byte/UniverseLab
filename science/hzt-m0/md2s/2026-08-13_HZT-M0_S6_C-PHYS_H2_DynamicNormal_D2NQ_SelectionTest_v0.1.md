---
title: "HZT-M0 S6 C-PHYS H2 — Dynamic Normal Equations and D2N-Q Selection Test v0.1"
date: "2026-08-13"
track: "MD2S-R1-C-PHYS"
model: "HZT-M0-S6-C-PHYS-M1"
status: "Formal geometry PASS; parent dynamic selection blocked pending time-dependent bulk/embedding closure"
---

# H2 — Dynamic Normal Equations and D2N-Q Selection Test

## 0. Result

H2 answers one sharply posed question:

> Does the currently frozen one-time 6D C-PHYS-M1 parent action, without importing any external draft equations and without inserting a target equation of state by hand, dynamically select the D2N-Q profile
>
> \[
> B^2(a)=B_\Lambda^2+B_m^2a^{-3}?
> \]

The answer at the current closure level is

\[
\boxed{\text{NO — the profile is allowed by source-free Codazzi, but it is not uniquely selected.}}
\]

This is not a falsification of D2N-Q. It is a precise closure result: the present parent action does not contain an independent 4D embedding field and the projected Gauss-Codazzi-Ricci system remains sourced by ambient-curvature and normal-bundle data until a full time-dependent 6D solution is supplied.

Governance remains unchanged:

```text
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
WP4  = BLOCKED
physical evidence effect = NONE
solver execution = false
```

Gemini material remains `EXTERNAL_UNVERIFIED_GEMINI_DRAFT` and is not a premise.

---

## 1. Geometric setup

Let a four-dimensional FLRW spacetime be embedded as a codimension-two submanifold of the one-time six-dimensional parent geometry. The two normals are spacelike and carry positive-definite metric

\[
\delta_{ij}.
\]

With

\[
\gamma_{\mu\nu}=g_{\mu\nu}+u_\mu u_\nu,
\]

the most general FLRW-symmetric second fundamental form is

\[
\boxed{
K^i_{\mu\nu}=\alpha^i u_\mu u_\nu+\beta^i\gamma_{\mu\nu}.
}
\]

Define

\[
B^2\equiv\beta_i\beta^i,
\qquad
\alpha\cdot\beta\equiv\alpha_i\beta^i.
\]

The Gauss extrinsic tensor is

\[
Q_{\mu\nu}
=
K_i K^i_{\mu\nu}
-K^i_{\mu\rho}K_{\nu}^{i\ \rho}
-\frac12 g_{\mu\nu}
\left(K_iK^i-K^i_{\rho\sigma}K_i^{\rho\sigma}\right).
\]

Direct contraction gives the exact identities

\[
\boxed{Q_{00}=3B^2}
\]

and

\[
\boxed{
Q^{\rm spatial}_{\mu\nu}
=
(2\alpha\cdot\beta-B^2)\gamma_{\mu\nu}.
}
\]

If this sector is isolated with constant Einstein-normalized \(M_4\), then

\[
\rho_Q=3M_4^2B^2,
\qquad
p_Q=M_4^2(2\alpha\cdot\beta-B^2).
\]

These are projection identities. They do not yet select \(B(a)\).

---

## 2. Codazzi with the ambient source retained

The mixed normal-tangent projection of the ambient Riemann tensor appears in the Codazzi equation. After FLRW reduction it can be written as

\[
\boxed{
D_t^\perp\beta_i+H(\alpha_i+\beta_i)=\frac13S_i,
}
\]

where \(S_i\) denotes the symmetry-reduced mixed ambient-curvature source in the stated normal-bundle convention.

Contract with \(\beta^i\). Metric compatibility of the normal connection gives

\[
\beta^iD_t^\perp\beta_i
=\frac12D_t B^2.
\]

Hence

\[
\boxed{
\frac12D_tB^2
+H(\alpha\cdot\beta+B^2)
=\frac13\beta\cdot S.
}
\]

For \(H\neq0\),

\[
\boxed{
\alpha\cdot\beta
=-B^2-
\frac{D_tB^2}{2H}
+
\frac{\beta\cdot S}{3H}.
}
\]

No equation of state has been inserted.

---

## 3. Exact effective-fluid exchange identity

Substitute the contracted Codazzi relation into the pressure:

\[
\boxed{
 p_Q=M_4^2\left[
 -3B^2-
 \frac{D_tB^2}{H}
 +\frac{2\beta\cdot S}{3H}
 \right].
}
\]

With

\[
\rho_Q=3M_4^2B^2
\]

and constant \(M_4\), direct differentiation yields

\[
\boxed{
D_t\rho_Q+3H(\rho_Q+p_Q)
=2M_4^2\beta\cdot S.
}
\]

Therefore the source-free condition \(S_i=0\) implies exact conservation of the isolated \(Q_{\mu\nu}\) sector:

\[
\boxed{
D_t\rho_Q+3H(\rho_Q+p_Q)=0.
}
\]

This is stronger than merely checking two special components, but it still does not select a unique \(B^2(a)\).

---

## 4. Codazzi degeneracy theorem

For \(S_i=0\),

\[
p_Q=-M_4^2\left(3B^2+\frac{D_tB^2}{H}\right).
\]

Since \(D_t\ln a=H\),

\[
\boxed{
 w_Q
=-1-\frac13\frac{d\ln B^2}{d\ln a}.
}
\]

Hence every differentiable positive function \(B^2(a)\) on an interval with \(H\neq0\) defines a source-free Codazzi-compatible effective fluid. In particular, for

\[
B^2\propto a^{-n}
\]

one obtains

\[
\boxed{w_Q=-1+\frac n3.}
\]

Examples:

| \(n\) | \(w_Q\) |
|---:|---:|
| 0 | -1 |
| 1 | -2/3 |
| 2 | -1/3 |
| 3 | 0 |
| 4 | 1/3 |

Therefore source-free Codazzi **permits** the cosmological-constant and dust scalings, but it does not prefer them over infinitely many alternatives.

This is the H2 degeneracy theorem:

\[
\boxed{
\text{Codazzi conservation}\;\not\Rightarrow\;\text{unique D2N-Q scaling.}
}
\]

---

## 5. D2N-Q target profile remains an exact allowed solution

Choose

\[
B^2(a)=B_\Lambda^2+B_m^2a^{-3}.
\]

Then

\[
D_tB^2=-3HB_m^2a^{-3}.
\]

The source-free formula gives

\[
\boxed{
\rho_Q=3M_4^2\left(B_\Lambda^2+B_m^2a^{-3}\right)
}
\]

and

\[
\boxed{
 p_Q=-3M_4^2B_\Lambda^2.
}
\]

So the target is mathematically consistent with the exact projection identities and source-free Codazzi.

Its correct classification is

```text
EXACT_KINEMATIC_SOURCE_FREE_CODAZZI_SOLUTION_FAMILY
ALLOWED_NOT_SELECTED
```

not `PARENT_DERIVED`.

---

## 6. Why the present parent action cannot yet select alpha and beta

The canonical C-PHYS parent action varies the six-dimensional bulk fields

\[
g_{AB},\quad\phi,\quad A_A
\]

plus the regulated cap fields. It does **not** contain an independent embedding map

\[
X^A(x^\mu)
\]

for a distinguished dynamical four-dimensional submanifold, nor does it contain \(K^i_{\mu\nu}\) as an independent field.

Consequently there is no present Euler-Lagrange equation of the form

\[
\frac{\delta S}{\delta K^i_{\mu\nu}}=0
\]

that could directly select

\[
\alpha_\Lambda=-\beta_\Lambda,
\qquad
\alpha_m=\frac12\beta_m.
\]

The Gauss, Codazzi and Ricci equations remain identities relating the induced geometry to projections of the solved ambient geometry. In particular:

- Codazzi contains the mixed ambient-curvature source \(S_i\);
- the Ricci equation contains normal-bundle curvature;
- normal-normal Einstein projections contain bulk curvature and normal derivatives;
- the projected 4D Einstein equation also contains bulk Ricci/Weyl information in addition to \(Q_{\mu\nu}\).

Thus an autonomous evolution equation for \(B^2(a)\) does not emerge before these data are closed.

---

## 7. Two possible completion paths

### Path A — preferred inside current C-PHYS

Construct and solve a genuinely time-dependent 6D M1 cosmological ansatz satisfying:

1. bulk Einstein, scalar and Maxwell equations;
2. radial/temporal constraints;
3. flux quantization;
4. cap junction conditions;
5. regularity;
6. a precise 4D projection prescription.

Then compute \(K^i_{\mu\nu}\), \(S_i\), the normal connection, \(B^2(a)\), and the projected Weyl/Ricci sector from that solution rather than inserting them.

### Path B — separate parent branch

Introduce explicit embedding variables \(X^A(x^\mu)\) and their action. This would be a different parent architecture and requires a new governance audit. It is not silently added to C-PHYS-M1.

H2 selects **Path A** as the next admissible step.

---

## 8. Scientific status after H2

| Statement | Status |
|---|---|
| \(Q_{00}=3B^2\) | **bewiesen** within the frozen FLRW projection convention |
| contracted Codazzi identity | **bewiesen** |
| source-free effective conservation | **bewiesen** |
| \(w_Q=-1-\frac13d\ln B^2/d\ln a\) | **bewiesen** under constant \(M_4\), \(S_i=0\) |
| \(B^2=B_\Lambda^2+B_m^2a^{-3}\) | **konditional / exact allowed solution** |
| unique Lambda+dust selection | **not derived** |
| source-free \(S_i=0\) from dynamic M1 bulk | **offen** |
| orthogonal Lambda/m normal eigenbasis dynamically preserved | **offen** |
| \(B_\Lambda,B_m\) fixed by flux/cap/regularity | **offen** |
| full projected Weyl/Ricci closure | **offen** |
| full ghost freedom | **offen** |
| bounce | **offen** |
| K1-D | **NOT_RELEASED** |
| K1-E | **NOT_ADMISSIBLE** |
| physical evidence | **NONE** |

---

## 9. Next block

\[
\boxed{
\texttt{C-PHYS-PARENT-H3-TIME-DEPENDENT-6D-M1-COSMOLOGICAL-ANSATZ-AND-PROJECTED-CLOSURE}
}
\]

H3 must define the smallest time-dependent six-dimensional ansatz that is still rich enough to determine the mixed and normal curvature projections. Only after solving or analytically reducing that system may D2N-Q be reconsidered as a parent-dynamically selected sector.
