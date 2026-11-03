# ULSH-01 / C-PHYS — Background3C5 G3 Outer Matching Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** NECESSARY_OUTER_STRUCTURE_CLOSED / UNIQUE_OUTER_TARGET_CONTRACT_OPEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Purpose

Define the strongest outer-boundary statement supported by the currently frozen Background3C5 contracts without silently inventing an asymptotic vacuum, cap radius, scalar target value, conical parameter, or gauge patch condition.

The existing equation/run freezes require simultaneously:

- outer layer decay,
- bulk matching,
- gauge regularity,
- flux quantization / charge-lattice consistency,
- no conical rescue mode,
- fixed discrete branch `(n, N_F, m_layer)` during a continuous response scan.

However, no independent current repository contract was found that fixes one unique outer target manifold such as specific values of `(A, ell, varphi)` and derivatives, a unique `rho_cap`, or a unique smooth-vs-junction handoff prescription.

Therefore G3 can be closed only at the level of necessary matching structure, not as a unique executable boundary-value target.

## 2. Canonical fields and Maxwell flux variable

Use the coefficient-fixed local operator variables

`(A, ell, varphi, s_hat, a_chi)`

with

`P = exp(4A) Z_F a_chi_x / ell`,

`Z_F = exp(-2 a_F varphi)`,

and exact finite-thickness Maxwell equation

`P_x = -(m_layer q_hat) exp(4A) s_hat^2 w / ell`,

`w = n - (m_layer q_hat) a_chi`.

When the layer has decayed,

`s_hat -> 0`,

one has

`P_x -> 0`,

so the exterior/bulk flux variable is constant on each connected source-free patch.

This is the correct local outer Maxwell matching variable. A free Dirichlet choice of `a_chi` alone is not equivalent to the frozen flux/patch contract.

## 3. Layer-decay stable manifold

The exact amplitude equation is

`s_hat_xx + (4 A_x + ell_x/ell) s_hat_x - [w^2/ell^2] s_hat - dV_hat_layer/ds_hat = 0`.

Linearizing about the layer-off outer branch `s_hat=0` gives

`s_hat_xx + H(x) s_hat_x - mu_eff^2(x) s_hat = 0`,

where

`H(x) = 4 A_x + ell_x/ell`,

`mu_eff^2(x) = w^2/ell^2 + mhat_Sigma^2(varphi)`

for the frozen quartic layer potential.

If the outer coefficients approach finite limits with

`H -> H_inf`, `mu_eff^2 -> mu_inf^2`,

then exponential modes satisfy

`lambda^2 + H_inf lambda - mu_inf^2 = 0`,

hence

`lambda_± = [-H_inf ± sqrt(H_inf^2 + 4 mu_inf^2)]/2`.

The physical layer-decay condition is selection of the decaying stable-manifold mode, not an arbitrary independent pair `s_hat=0`, `s_hat_x=0` at a finite numerical boundary.

For `mu_inf^2 > 0` there is one growing and one decaying real mode. If the asymptotic coefficients do not settle, or if the effective mass changes sign, decay must be established from the actual exterior solution rather than assumed.

**Status:** local asymptotic statement proven conditional on the stated coefficient limit.

## 4. Smooth bulk handoff

If the outer matching surface contains no delta-localized source, second-order field equations require continuity of the canonical fields and their normal fluxes. The natural smooth-handoff data are therefore continuity of

`A`, `A_x`, `ell`, `ell_x`, `varphi`, `varphi_x`, `a_chi`, `P`,

with `s_hat` constrained to the decaying layer stable manifold.

The radial Einstein constraint is not an additional freely specifiable boundary datum because G4 proves its propagation once the remaining equations are satisfied and the regular center fixes the constraint constant.

## 5. Cap / junction handoff is a distinct branch

If the intended outer surface is a cap/brane junction with localized stress, smooth derivative continuity is not valid. The previously frozen junction structure must instead be used, including the metric jump relations and

`Y_Sigma = M6^4 (L_Sigma - A_Sigma)`.

A cap/junction branch also requires explicit scalar and gauge source/matching laws compatible with the same parent action and charge lattice.

The current C-PHYS PR does not expose a unique complete outer cap contract that selects all of these data for the coefficient-fixed finite-thickness operator.

Therefore the two cases

1. `SMOOTH_BULK_HANDOFF`,
2. `CAP_OR_BRANE_JUNCTION_HANDOFF`

must not be mixed inside one solver run.

## 6. Flux quantization and gauge regularity

The frozen discrete flux sector `N_F` and the U(1) charge lattice are global constraints. Locally, once `s_hat` has decayed, `P` is constant; globally, the corresponding gauge field must belong to the fixed flux/patch sector.

Consequences:

- `N_F` is fixed before the continuous Jacobian scan;
- changing `q_hat` does not permit branch drift in `N_F` or `m_layer`;
- gauge-patch regularity and flux quantization must be checked together;
- a solver may not use an arbitrary shift/rescaling of `a_chi` to repair a failed outer match.

No new numerical flux-quantization formula is introduced here because the current PR does not independently expose the complete patch endpoint convention needed to turn the global lattice condition into one unique scalar boundary equation.

## 7. BVP counting consequence

G2 leaves, for fixed `k4` and fixed discrete branch, a local regular-center family parameterized typically by three continuous amplitudes

`(varphi_0, g_2, s_|n|)` for `n != 0`

(or `(varphi_0, g_2, s_0)` for `n=0`).

The outer problem is therefore square only after an explicit target contract states:

- which outer handoff branch is used;
- which three independent global mismatch functions are driven to zero by the three center amplitudes;
- which remaining global conditions are identities, derived observables, fixed discrete-sector constraints, or are solved by promoting an allowed model/eigenparameter.

Imposing every verbal requirement (`metric match`, `scalar match`, `gauge match`, `layer decay`, `flux quantization`) as an independent scalar Dirichlet condition would generally overconstrain the three-parameter regular-center family.

Thus the historical statement `square-conditional` is structurally justified, but a unique square BVP is not yet executable until the outer mismatch map is ratified.

## 8. Required executable outer contract

Before physical solver binding, one machine-readable outer contract must freeze at minimum:

- `outer_mode = SMOOTH_BULK_HANDOFF | CAP_OR_BRANE_JUNCTION_HANDOFF`;
- outer location rule (`x_match` finite, derived cap location, or asymptotic compactification rule);
- target bulk/cap solution family and provenance;
- exactly three independent continuous mismatch functions for fixed `(k4,n,N_F,m_layer)` or an explicit declaration of any promoted eigenparameter;
- layer stable-manifold condition;
- gauge patch / flux quantization equation;
- constraint treatment as monitor/propagated identity, not extra BC;
- branch-continuity and no-conical-rescue rules.

## 9. Verdict

`G3_NECESSARY_OUTER_STRUCTURE = PASS_ANALYTIC`

`G3_LAYER_DECAY_STABLE_MANIFOLD = PASS_CONDITIONAL`

`G3_SMOOTH_VS_JUNCTION_BRANCH_SEPARATION = PASS`

`G3_UNIQUE_EXECUTABLE_OUTER_TARGET = OPEN`

`G3_GLOBAL_BVP_COUNT = SQUARE_CONDITIONAL_ONLY`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

This audit changes no physical evidence status.