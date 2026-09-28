# HZT-M0 Forward Map — FM-0 κ₆ Parent Recovery v0.1

**Date:** 2026-08-31  
**Program:** UL-HZT-10M-2026-2027  
**Workstream:** WS1 — HZT-M0 Forward Map & Observables  
**Work package:** FM-0  
**Gate:** FM-G0 = **OPEN**  
**Classification:** `PROVENANCE_RECOVERY_NO_NEW_PHYSICS`

## 1. Decision

The targeted recovery changes the κ₆ item from wholly unresolved to:

`PARTIALLY_RESOLVED_CANONICAL_PARENT_RECOVERED`

This is a provenance correction, not a new theory assumption. The canonical repository already contains an explicit κ₆ convention that the broader FM-0 search pass did not bind.

The recovered canonical statements are in `convention-registry.json` under `gravity`:

- `S_EH = (1/(2 kappa_6^2)) integral d^6X sqrt(|g_6|) (R_6 - 2 Lambda_6)`;
- `kappa_6^2 = 8 pi G_6`;
- `[kappa_6^2] = L^4 = M^-4`;
- natural units with `[L]=[M]^-1`.

Therefore κ₆ has a canonical Parent definition and κ₆² has a canonical dimension statement.

## 2. Dimension recovery

From the canonical source statement

`[kappa_6^2] = L^4 = M^-4`,

the dimension of κ₆ itself follows algebraically:

`[kappa_6] = L^2 = M^-2`.

This second line is classified as:

`ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING`.

The distinction is deliberate: the squared dimension is directly source-backed; halving the exponents is an algebraic consequence.

## 3. Relation to the controlled M₆ parent action

`SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md`, equation `HZT-S6-PAR-v0.1-EQ-001`, writes the controlled HZT-M0-S6 Einstein-Hilbert coefficient as

`M_6^4 / 2`.

The accompanying machine artifact `hzt-s6-parent-action-v0.1.json` fixes `[M_6]=M^1`, and `hzt_parent_action_checker_v0_1.py` audits `M6^4 R` at total mass dimension 6.

Comparing the two Einstein-Hilbert coefficients,

`1/(2 kappa_6^2)` and `M_6^4/2`,

would give

`kappa_6^2 = M_6^-4`

**if** both records are intended as exactly the same normalization with no additional branch-specific prefactor.

That coefficient match is mathematically straightforward but the repository pass has not located a direct canonical statement declaring `kappa_6^2 = M_6^-4`. It is therefore recorded only as:

`ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING`.

It must not be silently promoted into a direct κ₆↔M₆ identity.

## 4. Corroborating usage

`SCI-001-002_v0.2_MD-2S_Background_Substitution_Preflight.md` contains the source-supported benchmark combination

`kappa6^2 lambda_eff / (4 sqrt(K4)) = 0.8931498683204`.

This corroborates that κ₆ is actually used in the controlled HZT-M0-S6 calculation chain. It does **not** by itself define κ₆ or establish its Forward-Map observable role.

## 5. Gap decision

`FM0-GAP-005` remains **blocking**, but it is narrowed.

Resolved now:

1. canonical Parent definition of κ₆;
2. canonical relation `kappa_6^2 = 8 pi G_6`;
3. canonical squared dimension `[kappa_6^2]=L^4=M^-4`;
4. κ₆ dimension `[kappa_6]=L^2=M^-2` with explicit algebraic provenance;
5. Parent source and status class.

Still open:

1. an explicit canonical κ₆↔M₆ normalization identity, if the reduced parameter contract requires that identity rather than coefficient matching;
2. the Parent→Reduced role of κ₆ inside the five-parameter HZT-M0 Forward Map;
3. the downstream dependencies of `O_RAR`, `O_cosmo`, `O_growth`, `O_lensing`, and `O_GW`.

For that reason the gap is **not closed** and `FM-G0` remains **OPEN**.

## 6. Append-only correction to the broad recovery pass

The earlier `2026-08-31_HZT_M0_ForwardMap_FM0_ParentCanonRecovery_v0.1.md` truthfully reported that no direct κ₆ source was verified in that bounded search pass. The targeted pass found a relevant root-level canonical registry and therefore supersedes only the κ₆ recovery state through Inventory v0.3 and Gap Register v0.2.

The historical recovery report is retained unchanged for provenance.

## 7. Scientific firewall

No solver or physics backend was imported or executed. No AuthorizationDecision or SingleUseGrant was created. No physical background, response rank, K1 release, or likelihood admissibility follows from this provenance recovery.

Current firewall remains:

- `physical background = NOT_ESTABLISHED`
- `rank R = OPEN_NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `CP01R4 = FROZEN_NO_EXECUTION`
- `physical_evidence_effect = NONE`

## 8. Next FM-0 target

After this κ₆ recovery, the next targeted Parent-Provenance item is `a0`. The existing lexical guard remains mandatory: lowercase `a0` must not be identified with uppercase `A0` merely by notation similarity.
