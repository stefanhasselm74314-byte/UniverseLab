# ULSH-01 / C-PHYS — Background3C5 G3.2 Two-Region Finite-Thickness Cap Bridge v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** TWO_REGION_BULK_LIFT_PASS / CAP_SECTOR_IDENTITY_BLOCKED / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Purpose

Reconcile the coefficient-fixed local finite-thickness Background3C5 operator with the canonical two-region MD2S/C-PHYS topology recovered in G3.1, without silently identifying the finite-thickness Sigma sector with the already-canonical localized cap sector.

The current canonical outer topology is:

- two smooth disk regions `N` and `S`;
- one regular pole in each region;
- each local radial coordinate grows from its pole to the common codimension-1 cap;
- one shared cap/junction carrying the eight canonical global residuals;
- no smooth-bulk outer handoff for the full ULSH-01 target branch.

The canonical residual set is

`R_A, R_L, R_phi, R_patch, R_4d, R_chi, R_scalar, R_gauge`.

## 2. Canonical source bindings

This bridge is constrained by the current merged repository canon, in particular:

- `registry/2026-08-03_MD2S_C1_BVPPreflightContract_v0.1.json`;
- `registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json`;
- the later CP01R3 protocol freeze preserving topology, physical ODEs and all eight boundary equations;
- PR #137 G5 coefficient-fixed finite-thickness local operator and G3.1 outer-topology reconciliation.

No older chat statement overrides these contracts.

## 3. Region-local finite-thickness lift

The Background3C5 finite-thickness Euler-Lagrange equations are local radial equations. Therefore the local operator can be lifted to each canonical disk region by a region label `s in {N,S}` without altering its coefficients.

For each region define

`U_s = (A_s, ell_s, varphi_s, s_hat_s, a_chi_s, P_s)`

with

`P_s = exp(4 A_s) Z_F(varphi_s) a_chi,s_x / ell_s`,

`Z_F(varphi_s)=exp(-2 a_F varphi_s)`,

`w_s = n - (m_layer q_hat) a_chi_s`.

The finite-thickness Maxwell residual is region-local:

`d_x P_s + (m_layer q_hat) exp(4 A_s) s_hat_s^2 w_s / ell_s = 0`.

The layer amplitude equation is region-local:

`s_hat_s,xx + (4 A_s,x + ell_s,x/ell_s) s_hat_s,x - (w_s^2/ell_s^2) s_hat_s - d_s Vhat_layer(varphi_s,s_hat_s) = 0`.

The Einstein and scalar equations receive exactly the same G5 finite-thickness source insertions in each region. No new sign or normalization is introduced by the `N/S` labeling.

**Result:** `TWO_REGION_LOCAL_OPERATOR_LIFT = PASS_BY_LOCALITY_AND_LABEL_SYMMETRY`.

This is an operator statement only. It does not prove a global solution.

## 4. Pole closure in both regions

Each region retains its own regular-center conditions at `x_s=0`:

- `ell_s(0)=0` with regular unit-slope axis convention;
- `A_s,x(0)=0`;
- `varphi_s,x(0)=0`;
- regular gauge potential in the local patch;
- `s_hat_s ~ x_s^abs(n)` for nonzero winding, subject to the single global discrete branch convention.

The global warp-frame redundancy remains one redundancy, not one per region. Regional discrete topology labels such as independent `n_N,n_S` or independent flux sectors are not introduced.

## 5. Canonical cap residuals that must be recovered

At the common cap the complete target must recover exactly one copy of the canonical global residual map:

`R_A = A_N(rho_N)-A_S(rho_S)`,

`R_L = L_N(rho_N)-L_S(rho_S)`,

`R_phi = phi_N(rho_N)-phi_S(rho_S)`,

`R_patch = A_chi,N(rho_N)-A_chi,S(rho_S)-N_F/q_ref` in the frozen two-patch convention,

plus the canonical metric, scalar and gauge junction residuals

`R_4d, R_chi, R_scalar, R_gauge`.

The rr Einstein constraints remain propagated QA channels and are not appended as additional cap equations.

The later M1/CP01R3 canon preserves an eight-equation boundary structure, so G3.2 does not replace it by a three-mismatch outer map.

## 6. Finite bulk stress does not by itself create a delta junction term

A smooth finite-thickness stress profile contributes to the bulk Einstein/scalar/Maxwell equations on each side. By itself it does not generate a distributional delta source at the cap.

Therefore the G5 bulk stress insertions must not simply be added algebraically to the canonical thin-cap jump equations as if they were localized cap tensions.

A modification of `R_4d`, `R_chi`, `R_scalar`, or `R_gauge` requires a parent-action term localized on the cap or an explicitly derived thin-limit reduction of the finite-thickness sector.

This separates two logically distinct objects:

1. finite-thickness bulk source terms in the regional ODEs;
2. localized cap source terms entering junction conditions.

## 7. Critical unresolved identity: what is the finite-thickness Sigma sector relative to the cap Sigma sector?

The current canon available to this bridge does not establish one of the following mutually distinct identifications:

- `SUPPLEMENT`: finite-thickness Sigma is an additional bulk/layer sector coexisting with the canonical localized cap sector;
- `RESOLUTION`: finite-thickness Sigma is a resolved representation whose thin limit reproduces the canonical localized cap action;
- `REPLACEMENT`: finite-thickness Sigma replaces the localized cap Sigma sector and therefore requires newly derived cap equations;
- `DECOUPLED_CONTROL`: finite-thickness Sigma is only a controlled auxiliary sector and is not part of the final canonical cap source.

Choosing among these possibilities without a provenance-bound parent-action statement would risk either double counting or deleting canonical localized stress/current.

Hence

`FINITE_THICKNESS_TO_CAP_SIGMA_IDENTITY = OPEN_PROVENANCE_BLOCKER`.

## 8. Consequence for the junction equations

Until the identity in section 7 is closed:

- the canonical eight-residual cap map remains the required target structure;
- its coefficient/source content may not be mutated by inference from the finite-thickness bulk stress alone;
- no finite-thickness contribution may be inserted into `Y_sigma` or the scalar/gauge cap source without an explicit parent derivation;
- no canonical localized cap term may be removed merely because a smooth layer exists;
- no physical BVP is executable.

Thus the two-region operator lift is established, while the full operator-to-cap equivalence is not yet ratified.

## 9. BVP counting

The canonical full BVP count remains the repository count, not the superseded one-region G3 count:

- two-region regular data plus cap locations and the allowed global eigenparameter/frame quotient;
- eight continuous global unknowns in the canonical square preflight;
- eight independent global residuals.

The finite-thickness field adds regional profile degrees of freedom governed by its own second-order ODE and regular-pole data. Whether its extra regular amplitudes are independent global shooting controls, fixed by a resolved-cap construction, or constrained by a thin-limit normalization depends on the unresolved sector identity above.

Therefore a new finite-thickness global unknown/residual count must not be declared square until the parent-level cap identity is fixed.

## 10. Required G3.3 recovery target

The next admissible theory block is a parent/canon sector-identity audit that must answer, with repository provenance:

1. Is the Background3C5 finite-thickness `Sigma` the same physical field/sector as the localized cap `Sigma` entering `Y_sigma`, scalar and gauge junction sources?
2. If yes, is there a controlled thin-limit derivation mapping the smooth profile to the canonical cap action and its coefficients?
3. If no, what localized cap action remains independently present?
4. Which finite-thickness field conditions hold at the common cap: continuity, parity, decay before the cap, or a derived localized interaction law?
5. What is the resulting exact augmented unknown/residual count?

No numerical execution is required or allowed for this recovery pass.

## 11. Verdict

`G3_2_CANONICAL_OUTER_MODE = CAP_OR_BRANE_JUNCTION_HANDOFF`

`G3_2_TWO_REGION_LOCAL_OPERATOR_LIFT = PASS_ANALYTIC`

`G3_2_CANONICAL_EIGHT_RESIDUAL_TARGET = PRESERVED`

`G3_2_FINITE_BULK_STRESS_IS_NOT_DELTA_JUNCTION_SOURCE = PASS_DISTRIBUTIONAL_STRUCTURE`

`G3_2_FINITE_THICKNESS_TO_CAP_SIGMA_IDENTITY = OPEN_PROVENANCE_BLOCKER`

`G3_2_FULL_GLOBAL_BVP_COUNT = NOT_RATIFIED_FOR_FINITE_THICKNESS_EXTENSION`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`PHYSICAL_EVIDENCE_EFFECT = NONE`
