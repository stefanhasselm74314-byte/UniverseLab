# UniverseLab UL-GRQM-2T03: 4D EFT / Weyl-Bridge – Analytical Ledger v0.1

**Date:** 2026-11-26  
**Status:** DRAFT_ANALYTIC_NONCANONICAL  
**Project:** HPVS -> HZT-M0 -> HZT-Full  
**Physical gate effect:** NONE  
**Physical evidence effect:** NONE  
**Solver authorization:** FALSE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE  
**Prerequisite:** 2T-02, draft PR #305 (not canonical; no implicit merge)

## 0. Decision and scope

**CONDITIONAL FORMAL RESULT.** A 4D Einstein-frame action with a positive Einstein-Hilbert coefficient and one healthy canonical scalar has a local Weyl-invariant compensator representation. This is a **4D field-representation equivalence**, not a proof that the 4D theory originates from Bars' (4,2) two-time field theory or from the UniverseLab HZT-M0-S6 Einstein-Maxwell-scalar-cap parent.

**IDENTIFICATION BLOCKER.** Matching the 4D Planck mass alone does not fix the number of light scalar modes, kinetic inertia, effective potentials, Maxwell coupling, matter coupling, KK spectrum or boundary conditions. Those data must be independently reduced from each proposed parent. A 4D Weyl lift cannot promote a 6D parent claim.

This ledger accompanies a separate nine-page A4 analytical dossier and an 18-test local SymPy package delivered in the current research conversation. The repository gate remains draft-only; the local downloadable package is not represented as a committed GitHub file.

## 1. Model identities

* Bars (2008) / Bars & Chen (2009): 6D 2T gravitational fields (G_MN, W, Omega), two times, delta(W)/delta'(W) structure and kinematic/dynamical constraints; a 4D Weyl-symmetric 1T shadow. Bars & Chen describe no independent KK tower from the two extra 2T directions in this construction.
* UniverseLab HZT-M0-S6: six-dimensional **one-time** signature (-,+,+,+,+,+), bulk Einstein-Hilbert + scalar + Maxwell, GHY and cap terms, internal positive-definite 2D geometry. The chosen C-PHYS-M1 functions are versioned model definitions, not 2T consequences.
* HZT-Full: distinct hypothetical 2T parent; the relevant complete field and boundary variation is not established by this ledger.

Primary source URLs:
- https://doi.org/10.1103/PhysRevD.77.125027
- https://doi.org/10.1103/PhysRevD.79.085021
- https://doi.org/10.1103/PhysRevD.89.043515

## 2. Constructive 4D Weyl lift

Use signature (-,+,+,+) and units hbar=c=1. Start with

$$
S_E=\int d^4x\sqrt{-g_E}\left[\frac{M_4^2}{2}R_E
-\frac12(\partial\psi)^2-U_E(\psi)\right],\qquad M_4>0.
$$

On the patch chi>0, chi^2-s^2>0 introduce Theta>0 and

$$
\chi=\sqrt{6}M_4\Theta\cosh\left(\frac{\psi}{\sqrt{6}M_4}\right),\quad
s=\sqrt{6}M_4\Theta\sinh\left(\frac{\psi}{\sqrt{6}M_4}\right),\quad
g^E_{\mu\nu}=\Theta^2g_{\mu\nu}.
$$

Then chi^2-s^2=6 M_4^2 Theta^2 and

$$
\psi=\sqrt{6}M_4\,\mathrm{artanh}(s/\chi),\qquad
\Theta^2=(\chi^2-s^2)/(6M_4^2).
$$

Define the Weyl potential

$$
V_{\rm comp}(\chi,s)=\left(\frac{\chi^2-s^2}{6M_4^2}\right)^2
U_E\left(\sqrt{6}M_4\,\mathrm{artanh}(s/\chi)\right).
$$

It is homogeneous of degree four. The Weyl action is

$$
S_W=\int d^4x\sqrt{-g}\left[
\frac{\chi^2-s^2}{12}R[g]
+\frac12(\partial\chi)^2-\frac12(\partial s)^2
-V_{\rm comp}(\chi,s)\right].
$$

Under g -> exp(2omega)g and (chi,s)->exp(-omega)(chi,s), both g_E and psi are invariant. The scalar kinetic identity is

$$
\tfrac12[(\partial\chi)^2-(\partial s)^2]
=3M_4^2(\partial\Theta)^2-\tfrac12\Theta^2(\partial\psi)^2.
$$

After the conformal curvature transformation, the compensator gradient terms cancel. On a regular patch, the remaining action differs from S_E only by

$$3M_4^2\int\sqrt{-g_E}\,\Box_E\ln\Theta,$$

a boundary term requiring boundary treatment. No global extension through chi^2-s^2=0, no 2T parent lift and no quantum ghost theorem follow.

## 3. HZT-M0 termwise 6D to 4D reduction: three independent conditions

Assume a **trial** static background

$$ds_6^2=e^{2A(y)}g_{\mu\nu}^{(4)}dx^\mu dx^\nu+\gamma_{mn}(y)dy^m dy^n$$

with a positive internal metric and no independent localized curvature terms.

(1) The Einstein-Hilbert coefficient:

$$
M_4^2=M_6^4V_{\rm warp},\qquad
V_{\rm warp}=\int d^2y\sqrt{\gamma}\,e^{2A}.
$$

(2) For phi_6=phi_bar(y)+f(y) varphi(x), the **unmixed** scalar kinetic coefficient is

$$K_\varphi=\int d^2y\sqrt\gamma\,e^{2A}f(y)^2.$$

Canonical varphi normalization requires K_varphi=1. This is **not** the coupled physical scalar eigenmode when metric/gauge mixing is present.

(3) If and only if a constant internal U(1) vector zero mode exists in an independently fixed normalization S_F=-[4g_6^2]^{-1}int sqrt(|g6|)Z_F calF^2, then

$$g_4^{-2}=g_6^{-2}\int d^2y\sqrt\gamma\,Z_F(\bar\phi).$$

Here [g_6]=mass^-1; internal flux, cap winding and normal-mode boundary conditions may alter the field content. No Maxwell zero mode has been released from HZT-M0 by this calculation. All three integrals are independent constraints.

## 4. Hard counterexamples and field-count criteria

**Counterexample A (matter response).** Let two models have identical M_4 and U_E= m^2 psi^2/2, but different conformal matter metrics:
A_1(psi)=1 and A_2(psi)=exp(beta psi/M_4), beta != 0. Both possess the 4D Weyl representation above. However alpha_i=M_4 d ln A_i/dpsi obey alpha_1=0 and alpha_2=beta. In the weak, quasistatic, unscreened *toy* scalar model the potential changes by the factor [1+2 beta^2 exp(-mr)]. Thus same Weyl structure does not force same observables. This is **not a released HZT prediction**.

**Counterexample B (kinetic inertia).** Under an invertible local scalar field redefinition with Jacobian J, K transforms to J^T K J. Sylvester inertia and rank are invariant. A physically negative kinetic direction cannot be removed by an ordinary invertible redefinition, and two genuinely light independent scalars cannot become one by invertible reparametrization.

**Counterexample C (bulk mass vs 4D eigenmass).** Even for a factorized free massive scalar in an unwarped compact space, KK masses contain internal Laplacian eigenvalues: m_n^2=m_bulk^2+lambda_n. Therefore the 6D potential curvature U'' does not alone identify a physical 4D mass. The actual M0 fluctuation operator remains to be derived.

The Bars/Chen 2T shadow and a generic compact M0 reduction therefore have potentially distinct spectral and constraint structures. An observed 4D scalar or good background fit cannot resolve the parent identity.

## 5. Governance and open test matrix

| Gate | State |
|:--|:--|
| E01 Local 4D Weyl compensator lift | ANALYTIC PASS on stated patch |
| E02 Einstein scalar action and potential recovery | ANALYTIC PASS up to boundary term |
| E03 Full M0 background / 5D-cap matching | OPEN |
| E04 M0 gauge-fixed physical scalar count / kinetic inertia | OPEN |
| E05 Normalizable graviton mode and physical KK spectrum | OPEN |
| E06 M4 warped coefficient | CONDITIONAL DERIVATION |
| E07 Scalar, vector and matter coupling from parent | OPEN |
| E08 Direct 6D-2T ↔ 6D-M0 parent identity | NOT DERIVED |
| E09 Full 2T BRST, anomalies and quantum ghost freedom | NOT REASSESSED |
| E10 HZT-specific mu, Sigma, eta, f-sigma8 mapping | NOT DERIVED |
| E11 Independent empirical multi-probe testing | NOT EXECUTED |

Physical background NOT_ESTABLISHED; full quadratic action NOT_DERIVED; physical response rank NOT_EXECUTED; K1-D NOT_RELEASED; K1-E NOT_ADMISSIBLE. The tests are algebraic/toy checks only, not a HZT numerical validation.

## 6. Next controlled block

**UL-GRQM-2T04:** Derive the actual physical 4D scalar/vector/tensor mode basis, kinetic norms and matter couplings from a constrained on-shell HZT-M0 background. Only then compare the resulting 4D EFT with the Bars shadow. Do not infer a common 6D parent from the generic availability of a Weyl-compensator representation. No 8D architecture change, no solver grant, no implicit main merge.

## 7. UniverseLab primary source paths and Git blobs (read-only)

* SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md: df1b4a65d613622dcb176a2acc3879044292ac1e
* hzt-s6-parent-action-v0.1.json: aab94691b3a960b744825393fd090da098f58e39
* registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json: 13fbe0084dcf91f2d0696d00947c9eed221a58ce
* registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json: 6d18236526a9a2178b1a73e318e63e83a4d6ece6
* science/hzt-m0/bridge/MD2I_MDS05_WARP_VOLUME_BRIDGE_DERIVATION_v0.1.md: 82a0587a8eb4a82ed21ed6225209976fd3dba0e7

**Status: DRAFT / NONCANONICAL / NO PHYSICAL EVIDENCE.**
