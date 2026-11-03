# ULSH-01 / C-PHYS — Background3C5 WP1 Canonical-Scope Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Master Build Order:** `registry/2026-08-10_ULSH_MasterBuildOrder_v1.0.json`  
**Work package:** `ULSH-01-WP1`  
**Classification:** Governance/provenance audit only; no solver execution  
**Physical evidence effect:** `NONE`

## 1. Core result

`ULSH-01-WP1 = NOT_CLOSED`

Reason: the repository has advanced the finite-thickness Background3C5 implementation and software QA substantially, but the surviving canonical restart handoff freezes `HZT-M0-S6-C-PHYS-M1` without explicitly ratifying the additional smooth bulk field `Sigma_FT` as part of the frozen M1/C1 field content.

This absence is **not** proof that `Sigma_FT` is forbidden. It means the relevant field-content provenance is not established by the restart handoff and must therefore be classified

`M1_FIELD_CONTENT_SCOPE = RECONSTRUCTION_REQUIRED`.

No physical binding of the supplementary finite-thickness path to the official ULSH-01 solver is admissible until that provenance question is recovered or separately ratified by an authorized model-scope decision.

## 2. What is already closed

### [BEWIESEN] Frozen M1 functions and global conventions remain unchanged

The restart handoff freezes the M1 functions, parameter vector, active domain, `Delta chi = 2*pi`, flux orientation and charge lattice. This audit changes none of them.

### [BEWIESEN] Normalization bridge

The scalar/gauge normalization closure establishes the canonical dimensionless scalar convention and the charge-lattice relation

`gSigma = m_layer*q_ref = m_layer*q_hat/M6`.

Independent continuous variation of `gSigma` at fixed `q_hat` is forbidden.

### [BEWIESEN] Maxwell current coefficient in canonical M1 normalization

The coefficient-fixed finite-thickness candidate establishes

`Gamma_Sigma = m_layer*q_hat`

inside the canonical M1 gauge normalization. This is an operator-coefficient identity, not physical evidence.

### [BEWIESEN] Local constraint propagation

For the coefficient-fixed local operator the radial Bianchi/Noether identity is analytically closed. Conditional on the remaining local Euler-Lagrange residuals vanishing and on the regular-center branch, the radial Einstein constraint propagates and remains a QA channel rather than an additional independent bulk equation.

### [BEWIESEN] Canonical global topology

The official MD2S/C-PHYS target topology is two smooth regions `N,S`, one regular pole in each, joined at a common cap with the canonical cap/patch/junction structure.

### [BEWIESEN] Finite-thickness support is not identical to the canonical localized cap support

`Sigma_FT` has smooth codimension-zero radial support. The canonical `sigma_cap` sector is codimension-one cap-localized. They are not distributionally identical without a separately derived thin-limit map.

Therefore silent replacement, double counting, or identification is forbidden.

## 3. Conditional development result

G3.4 selects

`SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`

as the minimal-change development path. G3.5 then derives two additional cap conditions for the smooth amplitude and proves a structural `10 x 10` matching.

These results are valuable but their epistemic scope is limited:

`structural square 10x10 != actual functional Jacobian rank 10`

and

`conditional development path != ratified frozen-M1 field content`.

The actual functional Jacobian rank, existence, uniqueness, conditioning, nonlinear convergence and branch multiplicity remain open.

## 4. Mapping to the canonical four ULSH-01 work packages

| Work package | Canonical purpose | Current audit status |
|---|---|---|
| `ULSH-01-WP1` | Freeze physical BVP equation set and BC/regularity | **NOT_CLOSED — field-content scope RECONSTRUCTION_REQUIRED** |
| `ULSH-01-WP2` | Finalize executable backend interface and result schema | **ADVANCED_IMPLEMENTATION_ONLY** |
| `ULSH-01-WP3` | Analytical/manufactured controls and provenance QA | **ADVANCED_SOFTWARE_QA_NO_PHYSICAL_EVIDENCE** |
| `ULSH-01-WP4` | Authorized physical background execution and convergence | **BLOCKED / NOT_AUTHORIZED** |

G3.10 belongs primarily to WP2/WP3: it provides the two-sided finite-difference Jacobian dry-run harness and QA contract. It does not close WP1 and cannot enter WP4.

## 5. Hidden assumption caught by this audit

A direct transition

`G3.10 green -> evaluate physical 10x10 Jacobian -> rank verdict`

would silently assume that the supplementary `Sigma_FT` sector is already part of frozen M1.

That assumption is not established by the surviving restart handoff and conflicts with the repository's own G3.3 statement that the supplementary layer is a model extension relative to the minimal canonical ParentActionOperatorEntry.

Therefore the transition is blocked pending provenance recovery/ratification.

## 6. Next safe action

The next scientific/governance action is **not** another numerical G3.x run.

It is:

`RECOVER_OR_RATIFY_M1_PARENT_FIELD_CONTENT_SCOPE_BEFORE_ANY_PHYSICAL_BINDING_OF_SIGMA_FT`

The review must answer exactly one question:

> Is `Sigma_FT` a ratified additional degree of freedom of the frozen `HZT-M0-S6-C-PHYS-M1/C1` target, or must the finite-thickness work remain a noncanonical development extension until a separately governed model-scope change is authorized?

If provenance establishes inclusion, WP1 may proceed to a final target-contract freeze using the two-region augmented equations and boundary map.

If provenance does not establish inclusion, `Sigma_FT` must not be bound to the official M1 physical solver; the finite-thickness branch remains development-only unless a separately governed model change is explicitly authorized.

No C2 jump is made by this audit.

## 7. Gates unchanged

`official_MD2S_solver = NOT_AUTHORIZED`

`physical_background = NOT_ESTABLISHED`

`R1.1 = BLOCKED`

`R1.2 = BLOCKED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`physical_evidence_effect = NONE`

## 8. Forbidden inferences

- structural `10 x 10` matching does not prove functional rank;
- G3.10 dry-run QA does not evaluate the physical Jacobian;
- green CI does not establish a physical background;
- a supplementary-layer development choice is not automatically a frozen-M1 field-content ratification;
- numerical stability does not establish ghost freedom;
- technical readiness does not establish physical identification.

## 9. Machine-readable companion

`2026-08-20_ULSH01_Background3C5_WP1_CanonicalScopeAudit_v0.1.json`
