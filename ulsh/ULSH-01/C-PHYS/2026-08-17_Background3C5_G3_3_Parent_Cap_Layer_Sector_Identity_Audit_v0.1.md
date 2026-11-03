# ULSH-01 / C-PHYS — Background3C5 G3.3 Parent Cap/Layer Sector Identity Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** SUPPORT_IDENTITY_CLOSED / RESOLUTION_OR_REPLACEMENT_BRIDGE_NOT_DERIVED / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Question

Determine whether the Background3C5 radial finite-thickness field `Sigma=s(r)/sqrt(2) exp(i n chi)` is already canonically identical to the localized cap field/sector that sources the MD2S junction equations.

## 2. Current canonical parent action

The merged C-PHYS ParentActionOperatorEntry freezes the parent scaffold

`S = sum_s int_{M_s} sqrt(-g) [ M6^4/2 (R-2 Lambda6) - 1/2 (d phi)^2 - U(phi) - 1/4 Z_F(phi) F^2 ]`

`  + M6^4 sum_s int_Sigma sqrt(-h) K_s`

`  + int_Sigma sqrt(-h) [ -lambda(phi) - 1/2 Z_sigma(phi) h^{ab} D_a sigma D_b sigma ]`.

Thus the canonical source decomposition contains:

1. bulk Einstein-scalar-Maxwell fields on `M_N` and `M_S`;
2. GHY terms on the common cap;
3. a cap-localized tension/charged-winding sector supported only on the hypersurface `Sigma`.

The canonical junction residuals `R_4d`, `R_chi`, `R_scalar`, and `R_gauge` are derived from this cap-localized action.

## 3. Background3C5 finite-thickness sector

The PR #137 finite-thickness extension instead introduces a radially resolved field

`Sigma_FT = s(r)/sqrt(2) exp(i n chi)`

with radial kinetic energy, angular kinetic energy and a bulk/layer potential. It contributes smooth source densities to the regional Einstein, scalar and Maxwell equations wherever `s(r)` is nonzero.

Its support is therefore codimension zero in the radial bulk interval, not a delta-supported codimension-one cap term.

## 4. Support test

Let `T_FT(r)` denote a regular finite-thickness stress profile and `S_cap delta(r-rho)` a localized cap source.

As distributions these are not equal unless a separately controlled thin-limit family is supplied:

`T_FT,epsilon(r) -> S_cap delta(r-rho)` as `epsilon -> 0`

with the integrated moments and all scalar/gauge source coefficients shown to converge to the canonical cap action.

No such epsilon-family, normalization theorem, moment matching or distributional limit is present in the current canonical parent contracts or in PR #137.

Therefore:

`CURRENT_PARENT_SUPPORT_IDENTITY(FINITE_THICKNESS_LAYER, CAP_LOCALIZED_SIGMA) = FALSE`.

This is an operator-support statement. It does not prove that the two sectors could never represent the same physical object after a future controlled resolution map.

## 5. Consequence: no silent replacement or resolution

The current finite-thickness sector may not be treated as an already-proven replacement/resolution of the cap-localized sector.

In particular, it is forbidden to:

- remove the canonical cap action merely because `s(r)` is present;
- replace `Y_sigma` by a local value of finite-thickness stress;
- add the finite-thickness bulk stress directly to the Israel/junction source as a delta term;
- identify the finite-thickness winding `n` with the cap winding/flux integers without an explicit bundle/patch map;
- claim that the old eight cap residuals have been re-derived from the smooth layer.

## 6. What is canonically allowed now?

There are two logically admissible model paths, but they are not equivalent.

### Path S — Supplementary bulk layer

Keep the canonical cap action and its eight global residuals unchanged, and add the finite-thickness field as a genuinely additional bulk/layer matter sector.

This is mathematically well-defined at the operator level, but it is a model extension relative to the minimal canonical ParentActionOperatorEntry. Its parameter roles and global BVP count require a new explicit freeze before execution.

### Path R — Resolved-cap replacement

Declare that the finite-thickness sector resolves/replaces the localized cap sector. Then the localized cap action must be removed or obtained as the controlled thin limit of the smooth layer, and all metric/scalar/gauge junction equations must be re-derived from the new parent action.

This path is **not derived** in the current canon.

No hybrid path may retain the cap source and simultaneously count the same finite-thickness stress as its resolved version.

## 7. Implication for G3.2

G3.2 established the two-region local operator lift. G3.3 now sharpens its open identity:

- `SUPPORT_IDENTITY`: CLOSED — the current canonical operators have different support;
- `PHYSICAL_SECTOR_EQUIVALENCE`: NOT ESTABLISHED;
- `THIN_LIMIT_RESOLUTION_MAP`: NOT DERIVED;
- `REPLACEMENT_AUTHORIZATION`: ABSENT.

Therefore the canonical eight-residual cap target remains intact unless and until a new parent action explicitly chooses Path R.

## 8. BVP consequence

For the existing canonical M1 BVP, the eight-global-residual structure remains the reference target.

Adding a supplementary finite-thickness second-order amplitude equation in both regions introduces additional regular data. Those data cannot be assigned or counted away by importing the old 8x8 square count. A new augmented structural-count contract is required.

For a resolved-cap replacement, the old 8x8 count likewise cannot be retained automatically because the cap source equations themselves change.

Hence

`FINITE_THICKNESS_GLOBAL_BVP_SQUARENESS = OPEN_PENDING_MODEL_PATH_AND_COUNT_FREEZE`.

## 9. Next admissible block

The next safe block is **G3.4 Model-Path Decision and Augmented BVP Count**, still no execution.

It must choose exactly one:

- `SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`, or
- `RESOLVED_CAP_REPLACEMENT_WITH_NEW_PARENT_DERIVATION`.

If no explicit model decision is ratified, fail closed and do not bind Background3C5 as the physical ULSH-01 kernel.

## 10. Verdict

`G3_3_CANONICAL_CAP_SUPPORT = CODIMENSION_ONE_LOCALIZED`

`G3_3_FINITE_THICKNESS_LAYER_SUPPORT = RADIAL_BULK`

`G3_3_CURRENT_PARENT_SUPPORT_IDENTITY = FALSE`

`G3_3_PHYSICAL_SECTOR_EQUIVALENCE = NOT_ESTABLISHED`

`G3_3_THIN_LIMIT_RESOLUTION_MAP = NOT_DERIVED`

`G3_3_SILENT_REPLACEMENT = FORBIDDEN`

`G3_3_CANONICAL_EIGHT_CAP_RESIDUALS = PRESERVED_UNTIL_NEW_PARENT_DERIVATION`

`G3_3_FINITE_THICKNESS_GLOBAL_BVP_SQUARENESS = OPEN`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`PHYSICAL_EVIDENCE_EFFECT = NONE`
