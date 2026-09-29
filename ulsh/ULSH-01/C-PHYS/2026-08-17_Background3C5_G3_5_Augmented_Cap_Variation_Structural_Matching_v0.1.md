# ULSH-01 / C-PHYS — Background3C5 G3.5 Augmented Cap Variation & Structural Matching v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** AUGMENTED_CAP_VARIATION_PASS / STRUCTURAL_MATCHING_10_PASS / PATCH_WINDING_CORRECTION_FROZEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE

## 1. Scope and assumptions

This block continues the G3.4 development path

`SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`.

The canonical localized cap sector is retained unchanged. The new finite-thickness field `Sigma_FT` is a distinct smooth charged bulk field on both regions. No cap-localized coupling involving `Sigma_FT` is introduced in this block.

## 2. Augmented parent variation for the layer amplitude

For each region `s in {N,S}`, use the canonical amplitude kinetic structure

`S_FT,s = - int_Ms sqrt(-g) [ 1/2 (partial s_s)^2 + 1/2 s_s^2 (D theta_s)^2 + V_FT(s_s,varphi_s) ]`.

Variation with respect to `s_s` gives the already-frozen regional amplitude equation plus the cap boundary term

`delta S_FT|cap = - int_cap sqrt(-h) sum_s n_s^r s_s'(rho_s) delta s_Sigma`.

The canonical topology uses local coordinates increasing from each smooth pole to the common cap and fixes

`n_N^r = n_S^r = +1`

in those local coordinates.

For one continuous gauge-invariant amplitude on the glued manifold, the cap trace must satisfy

`R_s = s_N(rho_N)-s_S(rho_S)=0`.

The common cap variation `delta s_Sigma` is otherwise arbitrary. Since there is no localized `Sigma_FT` cap potential/source in the selected path, stationarity therefore requires

`R_s_flux = s_N'(rho_N)+s_S'(rho_S)=0`.

More invariantly,

`R_s_flux = sum_s n_s^r Pi_s = 0`,

with `Pi_s=partial_r s_s` for the frozen canonical kinetic normalization.

Thus the two G3.4 candidate layer cap residuals are parent-derived, not imposed ad hoc.

## 3. Charged two-patch winding compatibility

The canonical gauge patch relation is

`A_chi,N(rho_N)-A_chi,S(rho_S)=N_F/q_ref`.

For a charged bulk layer with

`gSigma = m_layer q_ref`, `m_layer in Z`,

write local sections

`Sigma_FT,N = s_N/sqrt(2) exp(i n_N chi)`,

`Sigma_FT,S = s_S/sqrt(2) exp(i n_S chi)`.

Gauge covariance across the patch transition requires

`theta_N-theta_S = gSigma Lambda`,

with `partial_chi Lambda=N_F/q_ref` in the frozen orientation. Therefore

`n_N-n_S = gSigma N_F/q_ref = m_layer N_F`.

Hence

`n_N = n_S + m_layer N_F`.

This is a discrete bundle-compatibility condition. It is not an additional continuous BVP residual.

Consequences:

- the two local Frobenius laws are generally different:
  `s_N ~ c_N r_N^|n_N|`, `s_S ~ c_S r_S^|n_S|`;
- a single identical local winding integer on both patches is forbidden when `m_layer N_F != 0`;
- a continuous response scan must hold the discrete bundle sector fixed and derive one patch winding from the other.

This append-only statement corrects the shorthand `s_s~c_s r^|n|` used in G3.4 when applied to the full two-patch geometry.

## 4. Maxwell cap law with a distributed current

Define the dimensionful canonical radial Maxwell momentum

`Pcal_s(r) = exp(4A_s) Z_F A_chi,s'(r)/L_s(r)`.

Without distributed charged matter `Pcal_s=Q_s` is constant. With `Sigma_FT`,

`Pcal_s' != 0`

according to the coefficient-fixed finite-thickness Maxwell equation.

The canonical normal Maxwell flux entering the cap variation is

`Z_F F^{r chi} = Pcal_s exp(-4A_s)/L_s`.

Therefore the old cap gauge residual is generalized by the representation-preserving substitution

`Q_s -> Pcal_s(rho_s)`:

`R_gauge^FT = sum_s n_s^r Pcal_s(rho_s) exp(-4A_s(rho_s))/L_Sigma - q_sigma Z_sigma d_chi/L_Sigma^2 = 0`.

The gauge-potential patch residual `R_patch` is unchanged in form. No extra local gauge boundary condition is introduced.

## 5. Continuous unknown count

The inherited canonical global unknown set has eight members:

`U8=(phi_N0,Q_N,A_S0,phi_S0,Q_S,rho_N,rho_S,K4)`.

In the distributed-current formulation, `Q_N,Q_S` are interpreted as pole/initial Maxwell momenta (or an exactly equivalent pair of initial-flux variables), not constants throughout a region.

The two regular amplitude equations add

`c_N,c_S`.

Thus

`U10=(U8,c_N,c_S)`

and

`dim U10 = 10`.

## 6. Residual count

The inherited cap/global residuals remain

`R8=(R_A,R_L,R_phi,R_patch,R_4d,R_chi,R_scalar,R_gauge^FT)`.

The parent variation adds

`R_s`, `R_s_flux`.

Hence

`R10=(R8,R_s,R_s_flux)`

and

`dim R10 = 10`.

The two propagated rr constraints remain QA channels and are not appended as independent residuals.

The discrete winding compatibility `n_N-n_S=m_layer N_F` is a branch constraint and is not counted in `R10`.

## 7. Structural matching proof

The canonical 8x8 preflight already supplies a perfect structural matching for the inherited block:

`R_A -> A_S0`

`R_L -> rho_N`

`R_phi -> phi_N0`

`R_patch -> Q_N`

`R_4d -> rho_S`

`R_chi -> K4`

`R_scalar -> phi_S0`

`R_gauge -> Q_S`.

Adding the finite-thickness sector does not remove these structural dependencies; backreaction only adds further edges.

For the new 2x2 amplitude block, generically

`R_s` depends on `(c_N,c_S)`

and

`R_s_flux` depends on `(c_N,c_S)`.

Choose, for example,

`R_s -> c_N`

`R_s_flux -> c_S`.

Together with the inherited matching this yields a matching of cardinality 10.

Therefore

`maximum_structural_matching >= 10`.

Since the matrix has only 10 rows and 10 columns,

`maximum_structural_matching = 10`.

Thus

`G3_5_STRUCTURAL_RANK = 10`.

This is a combinatorial structural-rank result only. It does not prove that the numerical/functional Jacobian at a solution has rank 10.

## 8. Rank-risk surfaces and singular cases

Actual rank can still fail on special surfaces, including:

- a layer-decoupling or exact zero-mode surface where the two new cap traces lose independent sensitivity to `(c_N,c_S)`;
- symmetric parameter points producing accidental linear dependence;
- scalar-shift risk inherited from the canonical C1 branch;
- fixing `K4` without promoting another continuous parameter;
- singular or nonregular pole branches;
- a later introduction of a cap-localized `Sigma_FT` interaction, which would change `R_s_flux` and require a new contract.

## 9. Verdict

`G3_5_LAYER_CAP_VARIATION = PASS_PARENT_DERIVED`

`G3_5_PATCH_WINDING = n_N-n_S=m_layer*N_F`

`G3_5_CONTINUOUS_UNKNOWN_COUNT = 10`

`G3_5_GLOBAL_RESIDUAL_COUNT = 10`

`G3_5_MAXIMUM_STRUCTURAL_MATCHING = 10`

`G3_5_STRUCTURAL_BVP = SQUARE_PREFLIGHT_PASS`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No existence, uniqueness, stability, ghost-freedom or physical-rank claim follows.