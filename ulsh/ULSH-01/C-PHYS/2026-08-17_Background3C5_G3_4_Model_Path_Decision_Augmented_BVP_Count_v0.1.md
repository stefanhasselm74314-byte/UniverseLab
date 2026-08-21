# ULSH-01 / C-PHYS — Background3C5 G3.4 Model Path Decision & Augmented BVP Count v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** DEVELOPMENT_PATH_SELECTED_CONDITIONALLY / AUGMENTED_BVP_STRUCTURAL_COUNT_CLOSED / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Canonical starting point

The merged C-PHYS parent action contains two smooth bulk regions `N,S` joined on one common codimension-1 cap and, separately, a cap-localized sigma sector

`S_cap = int_Sigma sqrt(-h)[-lambda(phi) - 1/2 Z_sigma(phi) h^{ab} D_a sigma D_b sigma]`.

The canonical C1/M1 BVP has eight continuous global unknowns and eight global residuals

`(R_A,R_L,R_phi,R_patch,R_4d,R_chi,R_scalar,R_gauge)`.

G3.3 established that the finite-thickness field

`Sigma_FT = s(r)/sqrt(2) exp(i n chi)`

is a smooth radial bulk/layer sector and is not, in the current parent, identical as an operator-support sector to the hypersurface-localized cap sigma field.

## 2. Compared development paths

### Path A — SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP

Keep the canonical cap action and all eight canonical cap/global residuals. Add `Sigma_FT` as a distinct bulk field in each region.

Consequences:

- minimal change to the already frozen parent topology and cap sector;
- no deletion or reinterpretation of existing junction terms;
- finite-thickness stress enters the regional bulk Einstein/scalar/Maxwell equations;
- one new second-order amplitude equation exists in each region;
- the new bulk field requires its own cap matching conditions;
- physical identification of `Sigma_FT` with `sigma_cap` is explicitly forbidden.

### Path B — RESOLVED_CAP_REPLACEMENT_WITH_NEW_PARENT_DERIVATION

Interpret the finite-thickness layer as a resolution/replacement of the localized cap matter sector.

This requires a new parent action and a controlled distributional/thin-limit derivation. At minimum one must rederive the metric, scalar and gauge cap laws and determine whether a residual pure-tension term remains. The present canonical `R_4d,R_chi,R_scalar,R_gauge` cannot simply be retained by assumption.

Therefore Path B changes more canonical structure and is not currently provenance-closed.

## 3. Development-path decision

For continuation of the existing M1/C-PHYS branch, select

`G3_4_DEVELOPMENT_PATH = SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`.

This is a **conditional model-development choice**, not a physical identification theorem. It is selected because it preserves the current parent topology and localized cap action while adding the already-derived finite-thickness local operator as a distinct field sector.

The alternative resolved-cap program remains admissible only as a separate future parent-action branch.

## 4. Augmented continuous unknown count

The canonical two-region problem has

`8` continuous global unknowns:

`(phi_N0,Q_N,A_S0,phi_S0,Q_S,rho_N,rho_S,K4)`.

For fixed discrete finite-thickness winding/charge sector, a regular second-order amplitude equation in each smooth region contributes one additional regular pole amplitude:

`c_N`, `c_S`,

where for `n != 0`

`s_s(r) = c_s r^|n| + O(r^(|n|+2))`.

Thus

`N_unknown_continuous = 8 + 2 = 10`.

No layer thickness is counted as an independent variable; it remains derived from the profile.

## 5. New layer cap conditions

Under the selected supplementary path, and **provided no new cap-localized coupling of Sigma_FT is introduced**, the variational principle for a smooth bulk scalar amplitude requires at the common cap:

`R_s = s_N(rho_N) - s_S(rho_S) = 0`,

and continuity of the canonical normal momentum. With canonical radial kinetic normalization this is represented schematically by

`R_s_flux = Pi_s,N + Pi_s,S = 0`,

with signs fixed by the canonical normal-orientation table and

`Pi_s,s = n_s^r * d_r s_s`

(up to any provenance-frozen kinetic prefactor if a generalized layer kinetic function is later introduced).

These are two independent continuous cap residuals.

Therefore the augmented global residual count is

`N_residual_global = 8 + 2 = 10`.

Hence

`G3_4_AUGMENTED_BVP_COUNT = STRUCTURALLY_SQUARE_10x10`.

This is a counting result only. It does not prove actual Jacobian rank, existence, uniqueness, conditioning or convergence.

## 6. Maxwell and patch consistency

The finite-thickness current changes the regional flux from a constant `Q_s` to a radially evolving canonical flux variable

`P_s = exp(4A_s) Z_F a_chi,s,x / ell_s`,

`P_s,x = -(m_layer q_hat) exp(4A_s) s_hat_s^2 w_s / ell_s`.

The original `Q_N,Q_S` therefore survive only as pole/initial flux data or equivalent global parameters, not as constants throughout each region when `s_hat != 0`.

The canonical `R_patch` and `R_gauge` must be rewritten in terms of endpoint values of the evolved flux variables before executable binding. This is a coefficient-preserving representation change, not permission to add extra gauge boundary conditions.

## 7. Double-counting firewall

The selected path is admissible only with explicit field identity separation:

- `sigma_cap`: hypersurface-localized canonical cap field;
- `Sigma_FT`: new smooth bulk finite-thickness field.

They may carry related charge-lattice data only if a separate contract states the relation. Their stresses, winding energies and gauge currents must not be merged or substituted without a parent derivation.

Therefore

`SIGMA_CAP_EQ_SIGMA_FT = FORBIDDEN_INFERENCE`.

## 8. Remaining gates before executable BVP

Required next:

1. derive the exact two new cap residuals for `Sigma_FT` from an explicit augmented parent variation with the canonical normal orientation;
2. rewrite canonical gauge junction/patch residuals using the evolved finite-thickness flux `P_N,P_S`;
3. construct the full 10x10 structural dependency graph and verify maximum matching 10;
4. verify the two regional rr constraints remain QA-only and propagated;
5. implement only after the augmented boundary operator is provenance-frozen;
6. physical execution remains separately authorization-gated.

## 9. Status

`G3_4_DEVELOPMENT_PATH = SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`

`G3_4_PATH_STATUS = CONDITIONAL_MODEL_CHOICE_MINIMAL_CANON_CHANGE`

`G3_4_CONTINUOUS_UNKNOWNS = 10`

`G3_4_GLOBAL_RESIDUALS = 10`

`G3_4_AUGMENTED_BVP_COUNT = STRUCTURALLY_SQUARE_10x10`

`ACTUAL_BVP_JACOBIAN_RANK = NOT_PROVEN`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence claim follows from this decision.