# UniverseLab / UL-GRQM-2T02-001: 2T field-theory shadow and M0 boundary audit

**Created:** 2026-11-21  
**Version:** v0.1  
**Status:** DRAFT_ANALYTIC_NONCANONICAL  
**Architecture:** HPVS -> HZT-M0 -> HZT-Full  
**Evidence effect:** NONE  
**Physical gate effect:** NONE  
**Solver/Grant:** NOT_AUTHORIZED / NOT_CREATED  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE  
**Scope:** Bounded 2T literature and exact main source audit. No complete HZT-Full parent action inferred.

## Executive findings

**F01 [SOURCE-CHECKED].** Bars' 2T gravity is a separate 6D field theory with signature (4,2), ambient metric G, dilaton Omega and auxiliary W. The action has both delta(W) and delta'(W) terms. It admits a 4D Weyl shadow with GR after the appropriate local gauge fixing. This is a published construction, not a new UniverseLab result.

**F02 [PROVEN LOCAL GEOMETRIC OBSTRUCTION].** Under the closed-homothety kinematic equations, (grad W)^2 = 4 W. On the regular W=0 hypersurface (dW nonzero), the normal is null and the pullback metric is degenerate. The M0 r=constant cap has a spacelike normal and a nondegenerate Lorentzian five-dimensional pullback when L>0. They cannot be identified by a nonsingular change of coordinates.

**F03 [PROVEN CONDITIONAL SHADOW IDENTITY].** The two-scalar conformal shadow admits a positive-Einstein-coupling Weyl-gauge patch, with a regular physical scalar and the compensator removed as local gauge freedom. It does not establish HZT-Full global or quantum ghost-freedom.

**F04 [BLOCKER].** Bars/Chen remove the ordinary independent extra 1+1 KK excitations via gauge constraints; M0 compactifies an actual positive-definite two-space with a conditional internal spectral operator. Matching the 4D graviton coefficient alone is insufficient to identify these higher-dimensional theories.

## Field action comparison

Bars/Chen (2009, Eq. 1–2; d=4, a=1/12):
\[
S_{\rm 2T}=\gamma\int d^6X\sqrt{|G|}\{
\delta(W)[\Omega^2R(G)+(1/2a)(\nabla\Omega)^2-V(\Omega)]
+\delta'(W)[\Omega^2(4-\Box W)+\nabla W\cdot\nabla(\Omega^2)]\},
\qquad V=\lambda\Omega^4.
\]

HZT-M0-S6 canonical core (SCI-001/002):
\[
S_{\rm M0}=\sum_s\int_{\mathcal M_s}\sqrt{|g|}[
(M_6^4/2)(R-2\Lambda_6)-(\nabla\phi)^2/2-U(\phi)
-Z_F(\phi)F_{AB}F^{AB}/4]
+S_{\rm GHY}+S_{\rm cap}.
\]

The latter uses one physical time and a positive two-dimensional internal metric. The M1 model-selection contract freezes
\(U=0.5\,\hat m_\phi^2 M_6^6(\phi/M_6^2)^2\),
\(Z_F=\exp(-2a_F\phi/M_6^2)\),
\(\lambda_\Sigma=\hat\lambda M_6^5\),
\(Z_\sigma=\hat z_\sigma M_6^3\).
These are model choices, not a derivation from Bars' dilaton and W. No off-shell field, distributional measure, cap or matter-source dictionary has been supplied.

In distribution theory, for a smooth compactly supported test function and local coordinate w:
\[
\langle\delta(w),f\rangle=f(0),\qquad
\langle\delta'(w),f\rangle=-f'(0).
\]
Thus the delta-prime action cannot be equated to an ordinary GHY cap contribution simply by matching dimension or codimension.

## Shadow Weyl model and explicit gauge reduction

Bars/Chen (2009, Eq. 7) with one matter scalar, after rescaling the original dilaton \(\chi=\phi_{\rm Bars}/\sqrt{a}\):
\[
S_4=\int d^4x\sqrt{|g|}\left[
(\chi^2-s^2)R/12
+(\nabla\chi)^2/2-(\nabla s)^2/2-V_4(\chi,s)\right].
\]

For \(g\to e^{2\omega}g\), \(\chi,s\to e^{-\omega}(\chi,s)\), a homogeneous quartic \(V_4\) gives local Weyl invariance up to a boundary divergence. Writing \(F=\chi^2-s^2\), one finds
\[
\delta_\omega(\sqrt{|g|}\,\mathcal L_{\rm kin+R})
=-(\sqrt{|g|}/2)\nabla_\mu(F\nabla^\mu\omega).
\]
This bulk identity is insufficient to close variations on the M0 cap: the boundary must be treated independently.

In the positive branch \(F>0\), the gauge \(F=6M_4^2\) yields
\[
F R/12=M_4^2 R/2.
\]
With \(q=\sqrt6M_4\), \(\chi=q\cosh(\psi/q)\), \(s=q\sinh(\psi/q)\), one has
\[
\chi^2-s^2=q^2,\quad
(\partial\chi)^2-(\partial s)^2=-(\partial\psi)^2.
\]
For signature (-,+,+,+), this is the healthy canonical scalar sign in the local Einstein patch. The Einstein gauge breaks down at \(F=0\); quantized BRST unitarity, full S/V/T Hessian and continuation between branches are not established here.

An un-compensated constant-mass potential \(m^2s^2\) has Weyl weight -2 instead of -4; it is not invariant as a bare 4D potential. Effective masses after gauge fixing are not forbidden by this check.

## Exact null-vs-cap rank counterexample

For the 2T-01 ambient metric
\[
ds_6^2=2\rho\,dt^2+2t\,dt\,d\rho
+t^2g_{\mu\nu}(x,\rho)dx^\mu dx^\nu,\qquad W=2\rho t^2
\]
at \(t>0\), \(W=0\) implies \(\rho=0\). In intrinsic coordinates \((t,x^\mu)\):
\[
h_{W=0}=0\,dt^2+t^2g_{\mu\nu}(x,0)dx^\mu dx^\nu,
\qquad {\rm rank}(h_{W=0})=4.
\]
For the M0 r=cap background:
\[
ds_6^2=e^{2A(r)}\bar g_{\mu\nu}dx^\mu dx^\nu+dr^2+L(r)^2d\chi^2,
\]
\[
h_{\Sigma}=e^{2A_\Sigma}\bar g_{\mu\nu}dx^\mu dx^\nu
+L_\Sigma^2d\chi^2,\qquad {\rm rank}(h_\Sigma)=5
\quad(L_\Sigma>0),
\]
and its normal obeys \(n^2=+1\). Under nonsingular intrinsic coordinate changes \(h\to J^T hJ\), rank is invariant. Therefore direct W=0/cap equivalence is blocked. This does NOT exclude a new cap being introduced after a 4D shadow or a genuinely new embedding.

Because W=0 is null, its boundary variational problem differs from the conventional non-null GHY term used for M0. The M0 cap also requires BOTH four-dimensional and chi-chi Israel components, scalar and gauge matching, global U(1) flux, pole regularity and boundary constraints.

## Planck coefficient matching is necessary, not sufficient

M0 warp volume reduction (MDS-05), assuming static profiles, a fixed 4D frame, no induced Einstein-Hilbert cap terms:
\[
V_W=\int d^2y\sqrt{\gamma_2}\,e^{2A},\qquad
M_{4,\rm M0}^2=M_6^4 V_W.
\]
Conformal shadow Einstein-gauge coefficient is \(M_{4,\rm 2T}^2=(\chi^2-s^2)/6\).
An attempted 4D-coefficient matching imposes
\[
\boxed{\chi^2-s^2=6M_6^4 V_W}.
\]
This is dimensionally correct (mass dimension 2) but no dynamical parent map. No scalar/gauge/cap/spectrum matching follows.

MDS-01 defines a *conditional* internal Sturm-Liouville spectrum for M0; a specific physical KK tower and its normalized modes remain unreleased. The 2T 4D shadow is not such an ordinary K2 KK compactification. Matching observables would require an explicit state/field dictionary.

## Closure gates and conclusion

| Gate | Requirement | Status |
|:--|:--|:--|
| FT-01 | Original 2T field action identified | SOURCE-CHECKED |
| FT-02 | 4D Weyl shadow and local Einstein gauge | ANALYTIC CHECK PASS |
| FT-03 | W=0 vs M0 cap equivalence | DIRECT IDENTIFICATION BLOCKED |
| FT-04 | HZT-Full (4,2) complete parent field action | OPEN |
| FT-05 | Full 2T variation / anomaly & BRST analysis | NOT PERFORMED |
| FT-06 | M0 GHY/Israel/scalar/gauge/flux matching | NOT DERIVED FROM 2T |
| FT-07 | Einstein coefficient equality | CONDITIONAL MATCHING ONLY |
| FT-08 | Physical 4D scalar-vector-tensor spectrum | OPEN |
| FT-09 | Ghost freedom and positivity | OPEN |
| FT-10 | Physical forward map / tests | OPEN |

The local test file supplied with this ledger implements twelve symbolic checks: Bars coefficient/potential power; ambient null constraint; null induced rank; cap induced rank; rank invariance; Einstein gauge; quartic homogeneity; bare-mass mismatch; Weyl boundary divergence; warped coefficient; delta/delta-prime functionals; positive/negative/zero Einstein-coupling sectors. Twelve local checks passed, but **none** is evidence of full 2T field-equation closure, a HZT-Full parent, or empirical confirmation.

**Governance:** Existing K1-D, K1-E, FM-G0, physical background, AuthorizationDecision and SingleUseGrant stay unchanged. This ledger is not an operational artifact; no backend import or solver run is authorized.

**Next candidate:** UL-GRQM-2T03 – 4D shadow-EFT matching and localized boundary field dictionary, with a formal rule to reject any direct 6D parent identification that lacks the necessary constraint and cap evidence.

## Verifiable references

External:
- Bars (2008), Gravity in two-time physics, Phys. Rev. D 77, 125027: https://doi.org/10.1103/PhysRevD.77.125027
- Bars & Chen (2009), Geometry and symmetry structures in two-time gravity, Phys. Rev. D 79, 085021: https://arxiv.org/abs/0811.2510
- Bars (2000), Two-time physics with gravitational and gauge field backgrounds: https://doi.org/10.1103/PhysRevD.62.085015
- Parattu et al. (2016), Unified boundary counter-term for null and non-null surfaces: https://doi.org/10.1140/epjc/s10052-016-3979-y

UniverseLab main source paths:
- SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md (blob df1b4a65d613622dcb176a2acc3879044292ac1e)
- hzt-s6-parent-action-v0.1.json (blob aab94691b3a960b744825393fd090da098f58e39)
- registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json (blob 13fbe0084dcf91f2d0696d00947c9eed221a58ce)
- registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json (blob 6d18236526a9a2178b1a73e318e63e83a4d6ece6)
- science/hzt-m0/bridge/MD2I_MDS01_SPECTRAL_BRIDGE_DERIVATION_v0.1.md (blob 9eb51c4ab8447fc2eb16446a428d28e8ab08f753)
- science/hzt-m0/bridge/MD2I_MDS05_WARP_VOLUME_BRIDGE_DERIVATION_v0.1.md (blob 82a0587a8eb4a82ed21ed6225209976fd3dba0e7)

Previous PRs #302-304 are noncanonical draft references, not proof of merged main evidence.