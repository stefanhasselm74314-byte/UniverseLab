# HZT-M0 Forward Map — FM-0 Parent/Canon Recovery v0.1

**Date:** 2026-08-31  
**Program:** UL-HZT-10M-2026-2027  
**Workstream:** WS1 — HZT-M0 Forward Map & Observables  
**Work package:** FM-0  
**Gate:** FM-G0 = **OPEN**  
**Classification:** `PROVENANCE_RECOVERY_NO_NEW_PHYSICS`  

## 1. Purpose

This recovery pass converts unresolved HZT-M0 program declarations into an explicit, fail-closed provenance state. It does **not** introduce a new physical definition, fit a parameter, execute a solver, or promote any physical/release gate.

The governing baseline is `registry/2026-08-29_HZT_M0_ForwardMap_FM0_Inventory_v0.1.json`. That inventory already requires exact definitions, dimensions, provenance and status classes before new mapping relations are introduced.

## 2. Recovery method

The pass used repository-level searches for the declared HZT-M0 core symbols and likely ASCII spellings, followed by comparison with the ratified FM-0 inventory. Searches included the declared spellings/variants for `a0`, `beta_tau`/`β_τ`, `R_chi`/`R_χ`, `I_B`/`𝓘_B`, `kappa_6`/`kappa6`/`κ_6`, and the declared observable-block identifiers.

A repository search miss is **not** treated as proof that no historical occurrence exists. It is only sufficient to prevent promotion: where a direct canonical parent binding was not located and verified in this pass, the item remains `OPEN_RECOVERY_REQUIRED`.

## 3. Parameter recovery result

| FM-0 item | Recovery status | Definition | Dimension | Parent/canon binding | Decision |
|---|---|---|---|---|---|
| `a0` | `OPEN_RECOVERY_REQUIRED` | not canonically recovered | open | not recovered | no new definition; no alias/equality with `A0` is asserted |
| `beta_tau` (`β_τ`) | `OPEN_RECOVERY_REQUIRED` | not canonically recovered | open | not recovered | remain unresolved |
| `R_chi` (`R_χ`) | `OPEN_RECOVERY_REQUIRED` | not canonically recovered | open | not recovered | remain unresolved |
| `I_B` (`𝓘_B`) | `OPEN_RECOVERY_REQUIRED` | not canonically recovered | open | not recovered | remain unresolved |
| `kappa_6` (`κ_6`) | `OPEN_RECOVERY_REQUIRED` | not canonically recovered | open | not recovered | no dimensional inference promoted without a direct canonical source |

### `a0` lexical guard

FM-0 now records `identity_with_A0 = NO_IDENTITY_ASSERTED`. Case-changing, notation similarity, historical memory, or textbook convention is not sufficient to bind lowercase `a0` to uppercase `A0`.

### `κ_6` inference guard

No statement such as `κ_6² ~ M^-4` or the algebraic consequence `κ_6 ~ M^-2` is promoted in this recovery version because no direct canonical repository source for that relation was verified in the bounded pass. If such a parent relation is recovered later, the source statement and any algebraic inference must be recorded as separate provenance objects.

## 4. Observable-block recovery result

The program-level identifiers

- `O_RAR`
- `O_cosmo`
- `O_growth`
- `O_lensing`
- `O_GW`

remain `PROGRAM_DECLARATION_ONLY` with `OPEN_RECOVERY_REQUIRED` provenance. Their presence in the ratified 10-month program defines work scope, not a completed Parent→Reduced or Reduced→Observable map.

## 5. Blocking gaps

The machine-readable blocking gaps are frozen in:

`registry/2026-08-31_HZT_M0_ForwardMap_FM0_GapRegister_v0.1.json`

Every unresolved core parameter and every unresolved observable interface has an explicit blocking gap. Therefore **FM-G0 cannot be CLOSED/PASS**.

## 6. FM-G0 exit condition

FM-G0 may be considered for closure only when, for every FM-0 core parameter and observable block:

1. a canonical source or explicit ratified new definition is identified;
2. definition and dimension/unit status are explicit;
3. provenance class is explicit;
4. upstream/downstream relations are explicit or explicitly declared absent/not-applicable;
5. all blocking gaps are resolved or formally reclassified by a later governed review;
6. no lexical/notation identity is inferred silently;
7. the recovery QA passes with `FM-G0` in a state consistent with the unresolved-gap set.

## 7. Fail-closed QA semantics

`tools/2026-08-31_validate_hzt_m0_fm0_parent_canon_recovery_v1.0.py` enforces that:

- all five declared core parameters and all five observable blocks exist;
- unresolved items have explicit blocking gaps;
- blocking gaps coexist only with an OPEN FM-G0 state;
- `a0` cannot claim identity/alias/equality with `A0` while unresolved;
- algebraic inferences, if introduced later, require an explicit `ALGEBRAIC_INFERENCE_NOT_CANONICAL_BINDING` classification and a recorded basis;
- the CP01R4/HZT release firewall remains exact.

The current truthful OPEN state is intended to **PASS QA**. QA success means only that uncertainty is represented correctly; it is not evidence that the Forward Map has been derived.

## 8. Scientific firewall — unchanged

This recovery has **zero physical evidence effect** and **zero physical release effect**.

- `WP1 = CLOSED_TARGET_FROZEN_NO_EXECUTION`
- `WP2 = READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED`
- operative `AuthorizationDecision = NOT_CREATED`
- `SingleUseGrant = NOT_CREATED`
- backend import = `NOT_EXECUTED`
- solver run = `NOT_EXECUTED`
- `physical background = NOT_ESTABLISHED`
- `WP3 = NOT_STARTED`
- `WP4 = BLOCKED_NOT_AUTHORIZED`
- `rank R = OPEN_NOT_EXECUTED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`

CP01R4 remains frozen. Nothing in this document, the registry update, or its CI workflow authorizes or performs physical execution.

## 9. Next admissible FM-0 step

The next admissible action is targeted provenance recovery against specific ratified/frozen parent artifacts and, where genuinely absent, creation of an explicit proposal for a new definition subject to separate review. No Forward-Map relation is to be promoted merely to eliminate a gap.