# HZT-M0 Forward Map — FM-0 a₀ Parent Recovery v0.1

**Date:** 2026-08-31  
**Program:** UL-HZT-10M-2026-2027  
**Workstream:** WS1 — HZT-M0 Forward Map & Observables  
**Work package:** FM-0  
**Gate:** FM-G0 = **OPEN**  
**Classification:** `PROVENANCE_RECOVERY_NO_NEW_PHYSICS`

## 1. Decision

The targeted recovery does **not** recover a current canonical HZT-M0 Parent definition for lowercase `a0` / a₀.

It does recover a precise historical provenance chain. The correct status is therefore:

`HISTORICAL_PROVENANCE_RECOVERED_CANONICAL_PARENT_OPEN`

This is a narrower and more informative state than wholly unresolved, but it does not close `FM0-GAP-001`.

## 2. Historical source chain

`legacy-formeln-H1-H64.csv` contains the following legacy relations:

- H31: `S_Theta ≈ div[mu(|grad vartheta|/a0) grad vartheta]` — status `open`;
- H34: `a0 = lambda_Theta c beta` — status `historical`;
- H35: `beta = H0` — status `historical`;
- H36: `a0 = lambda_Theta c H0` — status `historical`;
- H37: `g_obs = |grad Phi_dyn|` — status `historical`;
- H38: `g_bar = |grad Phi_N|` — status `historical`;
- H39: `g_obs = sqrt(a0 g_bar)` — status `historical`;
- H40: `g_obs = g_bar nu(g_bar/a0)` — status `historical`;
- H41: `nu(y) = 1/2 + sqrt(1/4 + 1/y)` — status `historical`;
- H42: `v^4 = G a0 M_b` — status `historical`.

The same repository's `legacy-snapshot-2026-06-29.json` explicitly classifies H34-H42 as:

`historical — historical branch; no current Hyperzeit prediction`

Its claim audit states that `a0/MOND/MDAR/BTFR relations are legacy phenomenology without current parent derivation`, and its import policy quarantines `MOND and a0 result claims`.

`legacy.html` repeats the same scientific firewall publicly: the old a₀/MDAR/BTFR relations are historical phenomenology, not a current 6D Parent derivation.

## 3. What can and cannot be recovered

### Recovered

- historical use of lowercase a₀;
- the exact legacy formula IDs and relations;
- its phenomenological role in the MOND/MDAR/BTFR branch;
- the fact that the repository itself later downgraded/quarantined those relations;
- an algebraic historical dimension relation: within H37-H40, a₀ must have the same dimension as `g_bar` and `g_obs` for the product and ratio to be dimensionally meaningful.

### Not recovered

- a current canonical HZT-M0 definition of a₀;
- a current Parent-action derivation producing a₀;
- a current source-backed unit/dimension declaration for a₀;
- a current upstream parameter map;
- a released Reduced→Observable mapping;
- any admissible data-fit or MOND confirmation claim.

The historical dimensional statement is therefore recorded only as:

`ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING`.

## 4. Lowercase a₀ is not uppercase A0

The repository also uses uppercase `A0` in the MD-2S background-recovery context. In particular:

- `SCI-001-002_v0.2_MD-2S_Background_Substitution_Preflight.md` refers to `global A0 benchmark values`;
- `md2s-artifact-recovery-rank-audit-v0.1.json` requires reproduction of `published A0 benchmarks` during background recovery.

Those records belong to the MD-2S benchmark chain. They contain no explicit alias or equality statement linking uppercase `A0` to lowercase `a0`.

Therefore the existing guard remains mandatory:

`identity_with_A0 = NO_IDENTITY_ASSERTED`

Case similarity, historical memory, or semantic guesswork is insufficient to identify the two symbols.

## 5. Gap decision

`FM0-GAP-001` is changed from wholly unresolved to:

`PARTIALLY_RESOLVED_HISTORICAL_PROVENANCE_RECOVERED_CANONICAL_PARENT_OPEN`

The gap remains **blocking** because the current canonical Parent definition and Forward-Map role remain open.

After this targeted pass the global FM-0 picture is:

- `a0`: historical provenance recovered; current canonical Parent open;
- `kappa_6`: canonical Parent recovered; reduced/observable mapping open;
- `beta_tau`, `R_chi`, `I_B`: still fully unresolved;
- all five observable blocks: still open at the current Forward-Map interface level.

Therefore:

`FM-G0 = OPEN`

## 6. Scientific firewall

This recovery performs no physical execution and creates no evidence or release effect.

- `WP1 = CLOSED_TARGET_FROZEN_NO_EXECUTION`
- `WP2 = READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED`
- operative AuthorizationDecision = `NOT_CREATED`
- SingleUseGrant = `NOT_CREATED`
- backend import = `NOT_EXECUTED`
- solver run = `NOT_EXECUTED`
- physical background = `NOT_ESTABLISHED`
- `WP3 = NOT_STARTED`
- `WP4 = BLOCKED_NOT_AUTHORIZED`
- `rank R = OPEN_NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `CP01R4 = FROZEN_NO_EXECUTION`
- physical evidence effect = `NONE`

## 7. Next admissible FM-0 move

Continue targeted provenance recovery with `beta_tau`, while keeping every historical relation separated from current canonical Parent definitions and without opening any CP01R4 execution path.
