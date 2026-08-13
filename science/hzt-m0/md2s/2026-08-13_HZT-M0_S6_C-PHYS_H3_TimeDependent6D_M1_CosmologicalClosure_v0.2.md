# HZT-M0 / S6 / C-PHYS H3 — Time-dependent 6D M1 cosmological closure v0.2

**Status:** `PASS_LOCAL_PARENT_TO_B2_RECONSTRUCTION_FACTORIZED_WARP_NO_DUST_RANK_ONE_TARGET_REALISED_DYNAMIC_SELECTION_OPEN`

**Correction:** This document supersedes H3 v0.1. The v0.1 claim that two nonzero D2N-Q components require two orthogonal normal directions was too strong and is retracted. An explicit rank-one counterexample exists.

## 1. Results retained from v0.1

The canonical C-PHYS signature remains one-time,

\[
(-,+,+,+,+,+).
\]

In a local orthonormal Gaussian-normal frame around the observed 4D section,

\[
K^i_{\mu\nu}=\frac12\mathcal L_{n_i}g_{\mu\nu},
\]

with

\[
g_{\mu\nu}dx^\mu dx^\nu=-n^2dt^2+a^2q_{ab}^{(k)}dx^a dx^b
\]

gives exactly

\[
\boxed{\alpha_i=-n_i(\ln n)},
\qquad
\boxed{\beta_i=n_i(\ln a)},
\]

and hence

\[
\boxed{B^2=\delta^{ij}n_i(\ln a)n_j(\ln a)}.
\]

The H2 source `S_i` is controlled by the mixed parent Einstein equation. `S_i=0` is therefore conditional on the actual parent solution having the required vanishing mixed flux; it is not a generic identity.

The factorised static-internal warp result also survives unchanged. If

\[
a(t,y)=a_4(t)e^{A(y)}
\]

with time-independent internal geometry and normal frame, then

\[
B^2=|\nabla_\perp A|^2
\]

is time independent. Under source-free H2 conservation this yields `w_Q=-1`, so this factorised subsector cannot generate the matterlike `B_m^2 a^{-3}` term.

## 2. Correction of the v0.1 rank-one claim

Define

\[
X(a)=B_\Lambda^2+B_m^2a^{-3}.
\]

A single nonzero normal component is enough:

\[
\boxed{\beta_r=\sqrt{X(a)},\qquad \beta_\chi=0}.
\]

Then immediately

\[
\boxed{B^2=\beta_r^2=X(a)=B_\Lambda^2+B_m^2a^{-3}}.
\]

Thus the v0.1 cross-term argument applied only to the additional, unnecessary assumption

\[
\beta_r=B_\Lambda+B_ma^{-3/2}.
\]

It did **not** prove a no-go for the target `B²` profile itself.

Therefore

\[
\boxed{\text{H3 v0.1 rank-one no-go is falsified by counterexample.}}
\]

This is a correction of our own derivation, not an import from Gemini.

## 3. Exact source-free rank-one completion

For `H != 0` and `S_r=0`, H2 gives

\[
\alpha_r\beta_r=-B^2-\frac{\dot B^2}{2H}.
\]

Since

\[
B^2=X=B_\Lambda^2+B_m^2a^{-3},
\qquad
\dot X=-3HB_m^2a^{-3},
\]

we obtain

\[
\boxed{
\alpha_r\beta_r
=-B_\Lambda^2+\frac12B_m^2a^{-3}
}.
\]

Choosing the positive orientation `beta_r=sqrt(X)`, this is

\[
\boxed{
\alpha_r=
\frac{-B_\Lambda^2+\tfrac12B_m^2a^{-3}}
{\sqrt{B_\Lambda^2+B_m^2a^{-3}}}
}.
\]

Substitution into the exact H1 effective-fluid map gives

\[
\rho_Q=3M_4^2(B_\Lambda^2+B_m^2a^{-3})
\]

and

\[
\boxed{p_Q=-3M_4^2B_\Lambda^2}.
\]

Hence the complete desired D2N-Q background is **kinematically and source-free-Codazzi-consistent even with normal rank one**.

That still does not mean the M1 parent action dynamically selects it.

## 4. Corrected minimal dynamical target

The next parent test can remain axisymmetric and chi independent. A minimal nonfactorisable time-radial ansatz is

\[
ds_6^2=-n^2(t,r)dt^2+a^2(t,r)q_{ab}^{(k)}dx^a dx^b+c^2(t,r)dr^2+L^2(t,r)d\chi^2,
\]

with the M1 scalar and gauge sector consistently promoted, e.g. `phi(t,r)` and `A_chi(t,r)` plus any Maxwell components forced by the equations.

On a fixed internal section in the diagonal gauge,

\[
\boxed{\beta_r=\frac1c\partial_r\ln a},
\qquad
\boxed{\alpha_r=-\frac1c\partial_r\ln n}.
\]

The actual scientific question is now narrower:

**Do the time-dependent one-time M1 Einstein-scalar-Maxwell-cap equations produce**

\[
\beta_r^2=B_\Lambda^2+B_m^2a^{-3}
\]

and the corresponding `alpha_r beta_r` relation as outputs of the parent solution?

They must not be inserted as target boundary data without an independent parent justification.

## 5. Gate state

- Local parent-to-`B²` reconstruction: **bewiesen**.
- Factorised static-internal warp producing a dust term: **falsifiziert innerhalb dieses Subsegments**.
- H3 v0.1 rank-one no-go: **falsifiziert durch explizites Gegenbeispiel**.
- Rank-one D2N-Q background realisation: **bewiesen kinematisch / konditional auf source-free Codazzi**.
- Parent-dynamische Auswahl von `B_Lambda`, `B_m` und der Skalierung: **offen**.
- Full ghost freedom: **offen**.
- Bounce: **offen**.
- `K1-D`: **NOT_RELEASED**.
- `K1-E`: **NOT_ADMISSIBLE**.
- `WP4`: **BLOCKED**.
- Physical evidence: **NONE**.

## 6. Next block

`C-PHYS-PARENT-H4-AXISYMMETRIC-TIME-RADIAL-NONSEPARABLE-M1-CLOSURE-AND-RANK-TEST`

H4 must derive the independent PDE/constraint set and perform an unknown/equation/gauge/rank preflight before any physical PDE solver execution is considered.
