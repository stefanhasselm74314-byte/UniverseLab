# HZT-M0 / S6 / C-PHYS H3 — Time-dependent 6D M1 cosmological closure v0.1

**Status:** `PASS_LOCAL_PARENT_TO_B2_RECONSTRUCTION_AND_MINIMAL_AXISYMMETRIC_D2NQ_NO_GO_FULL_DYNAMIC_SELECTION_STILL_OPEN`

**Classification:** formal parent-geometry derivation and fail-closed ansatz test. No solver execution. No physical-evidence effect.

## 1. Scope and firewall

H3 uses only the canonical one-time C-PHYS parent, the frozen M1 function family, and H2. Gemini material remains `EXTERNAL_UNVERIFIED_GEMINI_DRAFT` and is not a premise.

The ambient signature remains

\[
(-,+,+,+,+,+),
\]

with a positive-definite two-dimensional normal metric.

## 2. Minimal local 4+2 cosmological form

A local codimension-two decomposition sufficiently general to expose the normal channels is

\[
ds_6^2=g_{\mu\nu}(t,y)dx^\mu dx^\nu
+\gamma_{ij}(t,y)
(dy^i+N^i_{\mu}dx^\mu)(dy^j+N^j_{\nu}dx^\nu),
\]

where cosmological symmetry permits

\[
g_{\mu\nu}dx^\mu dx^\nu
=-n^2(t,y)dt^2+a^2(t,y)q_{ab}^{(k)}dx^a dx^b,
\]

and requires `N^i_a=0`. A possible normal shift/twist `N^i_t` is not globally discarded.

At one event of the observed 4D section we may choose an orthonormal Gaussian-normal frame, so locally `N^i_mu=0` and `gamma_ij=delta_ij`. This is a local frame construction, not a global product-gauge assumption.

## 3. Exact local parent-to-B² bridge

Using the convention

\[
K^i_{\mu\nu}=\frac12\mathcal L_{n_i}g_{\mu\nu},
\]

and the FLRW decomposition

\[
K^i_{\mu\nu}=\alpha^i u_\mu u_\nu+\beta^i\gamma^{(4)}_{\mu\nu},
\]

the temporal component gives

\[
K^i_{00}=-n^2 n_i(\ln n)=\alpha^i n^2,
\]

hence

\[
\boxed{\alpha_i=-n_i(\ln n)}.
\]

The spatial component gives

\[
K^i_{ab}=a^2 n_i(\ln a)q_{ab}^{(k)},
\]

hence

\[
\boxed{\beta_i=n_i(\ln a)}.
\]

Therefore

\[
\boxed{
B^2=\beta_i\beta^i
=\delta^{ij}n_i(\ln a)n_j(\ln a)
}
\]

in the local orthonormal normal frame.

This is the first direct local reconstruction of the D2N-Q invariant from the 6D metric. It does **not** yet select its time dependence.

## 4. Parent meaning of the H2 Codazzi source

The mixed normal-tangent Einstein equation controls the source appearing in H2. In the local section frame with `G_i0=0`, the cosmological and trace terms do not contribute to the mixed component, so schematically

\[
R_{i0}=M_6^{-4}T_{i0}.
\]

For the canonical scalar-Maxwell bulk,

\[
T^{(\phi)}_{i0}=n_i(\phi)\,u(\phi),
\]

and

\[
T^{(F)}_{i0}=Z_F F_{iP}F_0{}^P.
\]

Thus `S_i=0` is justified only when the actual parent solution has vanishing mixed energy flux and satisfies the mixed Einstein equation. It is not a generic identity of M1.

## 5. Factorised static-internal warp theorem

Consider the most conservative cosmological promotion of the frozen static warped sector,

\[
a(t,y)=a_4(t)e^{A(y)},
\]

with time-independent internal geometry and normal frame. Then

\[
\beta_i=n_i(A),
\qquad
B^2=|\nabla_\perp A|^2,
\]

so `B²` is independent of `a4(t)`.

Under source-free H2 conservation,

\[
w_Q=-1-\frac13\frac{d\ln B^2}{d\ln a_4},
\]

therefore

\[
\boxed{w_Q=-1}.
\]

**Result:** merely replacing the frozen maximally symmetric 4D metric by FLRW while leaving the internal warp static cannot generate a matterlike `B_m² a^-3` term.

## 6. Minimal axisymmetric fixed-section no-go

Now restrict further to the natural static-M1-like axisymmetric subsector: all metric functions are `chi` independent, the internal metric is diagonal, the observed 4D section is at fixed `(r,chi)`, and there is no gravitational normal shift/twist.

The angular Killing symmetry gives

\[
\beta_\chi=n_\chi(\ln a)=0,
\]

while `beta_r` may be nonzero. Hence the normal extrinsic vector has rank one.

The exact D2N-Q target with two nonzero amplitudes is

\[
B^2=B_\Lambda^2+B_m^2a^{-3}.
\]

If both pieces lived in the same single normal direction, one would need

\[
\beta=B_\Lambda+B_ma^{-3/2},
\]

which squares to

\[
\beta^2=B_\Lambda^2+2B_\Lambda B_ma^{-3/2}+B_m^2a^{-3}.
\]

The cross term is absent from the target. Therefore, for nonzero `B_Lambda` and `B_m`, the exact target requires two orthogonal nonzero normal channels or an equivalent nontrivial embedding/twist construction.

\[
\boxed{
\text{Minimal chi-independent diagonal fixed-section M1 subsector}
\;\not\Rightarrow\;
B_\Lambda^2+B_m^2a^{-3}
\text{ with both amplitudes nonzero.}
}
\]

This is an **ansatz-level no-go only**. It does not falsify the full one-time 6D parent theory or every possible codimension-two embedding.

## 7. What a full parent selection now requires

At least one genuinely second-normal ingredient must survive the parent equations: two-normal dependence of the 4D warp, a gravitational normal shift/twist generating an independent extrinsic channel, or a nontrivial 4D section/embedding inside the existing metric degrees of freedom. Any such extension must remain compatible with the canonical one-time signature, cap regularity, flux quantisation, and the M1 action.

The full closure must solve the tangent-tangent, normal-tangent and normal-normal Einstein equations together with scalar, Maxwell, cap, regularity and normal-bundle Ricci conditions. Only then may one reconstruct `S_i`, `B²(a)`, the normal eigenbasis and, if possible, `B_Lambda` and `B_m` from parent integration data.

## 8. Gate state

- `H3 local parent -> B² bridge`: **PASS / exact local geometry**.
- Factorised static-internal warp as dust source: **falsified within that subsector**.
- Two-nonzero-component D2N-Q in the minimal chi-independent diagonal fixed-section subsector: **falsified within that subsector**.
- Full M1 D2N-Q dynamic selection: **open**.
- Full ghost freedom: **open**.
- Negative-rho-squared bounce term: **not derived**.
- Global bounce: **open**.
- `K1-D`: **NOT_RELEASED**.
- `K1-E`: **NOT_ADMISSIBLE**.
- `WP4`: **BLOCKED**.
- Physical evidence: **NONE**.

## 9. Next admissible block

`C-PHYS-PARENT-H4-TWO-NORMAL-TIME-DEPENDENT-CLOSURE-DESIGN-AND-RANK-TEST`

H4 must determine the smallest one-time M1-compatible extension that carries two independent normal extrinsic channels and perform an equation/unknown/rank preflight before any numerical PDE execution is considered.
