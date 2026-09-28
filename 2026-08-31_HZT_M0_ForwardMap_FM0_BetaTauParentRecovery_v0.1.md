# HZT-M0 Forward Map — FM-0 β_τ Parent Recovery v0.1

**Date:** 2026-08-31  
**Program:** UL-HZT-10M-2026-2027  
**Workstream:** WS1 — HZT-M0 Forward Map & Observables  
**Work package:** FM-0  
**Gate:** FM-G0 = **OPEN**  
**Classification:** `PROVENANCE_RECOVERY_NO_NEW_PHYSICS`

## 1. Decision

The targeted recovery does not establish a canonical 6D Parent derivation for `beta_tau` / `β_τ`.

It does recover two current, source-backed layers that were missing from the initial FM-0 inventory:

1. an implemented, dimensionless **effective bridge proxy** used by UniverseLab for diagnostic sensitivity curves;
2. the declared **physical mapping roles** MDS-02, MDS-03 and MDS-04, all of which remain open or effectively bypassed.

The correct status is therefore:

`PARTIALLY_RESOLVED_CURRENT_EFFECTIVE_PROXY_AND_MAPPING_ROLES_RECOVERED_PARENT_DERIVATION_OPEN`

This narrows `FM0-GAP-002` but does not close it.

## 2. Repository-wide diagnostic scan

A read-only lexical scan was run over the tracked UTF-8 text corpus. At the first scan head it inspected 927 text files and found exact current `beta_tau` / `β_τ` occurrences both in FM-0 declarations and outside them.

The most important non-inventory hits were:

- `guide.html`;
- `compare-app.js` and the compare UI;
- `hyperlab.html`;
- `science/hzt-m0/bridge/MD2F_H_I_INTEGRATION_AUDIT_v0.1.md`;
- `science/hzt-m0/bridge/MD2N_Q_PACKAGE_RIGOR_AUDIT_v0.1.md`;
- `science/hzt-m0/bridge/MD2P_CORR_OVERLAP_DERIVATION_v0.1.md`.

The scan also recovered many unrelated uses of `beta`, `β` and `tau`. Those lexical collisions are not evidence of identity and are treated separately below.

A search hit is a discovery signal, not authority by itself. Every promoted statement in this report is tied to the content and status of a named source.

## 3. Current effective implementation

### 3.1 Direct definition

`guide.html` describes HyperLab as an audit and sensitivity laboratory for an effective bridge model that has not been fundamentally derived. It defines

```text
E_eff(a)^2 = E_LCDM(a)^2 [1 + beta_tau I_B exp(-(a/a_c)^2)].
```

Equivalently, define

```text
Delta(a) = beta_tau I_B exp[-(a/a_c)^2].
```

`compare-app.js` classifies this bridge correction as:

```text
status = model-dependent
unit   = dimensionless
```

and explicitly warns that it is not a released fundamental 6D prediction.

`hyperlab.html` likewise states that the displayed curves visualize effective ansatzes rather than predictions calculated from the full 6D Parent action.

Therefore the implementation-level definition is recovered:

> `β_τ` is the effective mixing-amplitude factor multiplying `I_B` and the chosen transition kernel in the current UniverseLab 4D sensitivity ansatz.

### 3.2 Dimension check

The implemented correction `Delta` is dimensionless. The same guide declares `I_B` dimensionless, while `a/a_c` and its exponential are dimensionless. Hence

```text
[beta_tau]_implemented = 1.
```

This is valid for the current effective implementation only. It does not determine the dimension or normalization of a hypothetical 6D Parent quantity before reduction.

### 3.3 Identifiability in the implemented model

The current bridge depends on `beta_tau` and `I_B` only through

```text
A_bridge = beta_tau I_B.
```

For any modeled output `O` that depends on this bridge only through `A_bridge`,

```text
partial O / partial beta_tau = I_B partial O / partial A_bridge,
partial O / partial I_B      = beta_tau partial O / partial A_bridge.
```

The two Jacobian columns are therefore proportional whenever both parameters enter no other channel:

```text
rank J_(beta_tau,I_B) <= 1.
```

This is an exact structural degeneracy of the implemented ansatz, not a data-dependent near-degeneracy.

The implemented limit

```text
beta_tau -> 0
```

implies

```text
Delta -> 0,
E_eff -> E_LCDM.
```

This is a 4D implementation limit, not a proof that a fundamental HZT-M0 branch reduces to GR or LambdaCDM when a 6D coupling vanishes.

### 3.4 UI range is not a prior

The current interfaces use demonstration ranges of roughly `-0.3 <= beta_tau <= 0.3` with a typical default near `0.05`. These bounds are UI controls for sensitivity exploration. They are not a physical prior, stability range, posterior interval or 6D consistency bound.

## 4. Current physical mapping declarations

`MD2F_H_I_INTEGRATION_AUDIT_v0.1.md` separates

```text
P_phys = (a0, beta_tau, R_chi, I_B, kappa_6),
P_mod  = (m, omega_c, eta, s; k_c derived),
O      = observables or diagnostic responses.
```

It declares three β_τ-dependent mapping edges.

### MDS-02

```text
(beta_tau, I_B, kappa_6) -> omega_c.
```

Because `omega_c` is dimensionless, a physical bridge must be built from dimensionless invariants. The audit states that the units and normalizations of `beta_tau` and `I_B`, and their combination with `kappa_6`, are unknown.

**Status:** `OPEN / CRITICAL BLOCKER`.

### MDS-03

```text
(a0, beta_tau, I_B) -> eta.
```

`eta` is dimensionless, but no current 6D/4D response equation derives it from these controls.

**Status:** `OPEN`.

### MDS-04

```text
(R_chi, beta_tau) -> s.
```

The form exponent `s` would require an operator, spectral-density, asymptotic or other physical derivation. The audit recommends fixing or excluding it in reduced diagnostics rather than treating it as an independently derived physical direction.

**Status:** `OPEN / FIX-OR-EXCLUDE CANDIDATE`.

## 5. Later audit disposition

The later bridge audits do not close these edges:

| Edge | Later result | Current interpretation |
|---|---|---|
| MDS-02 | `omega_c` is frozen or bypassed in the reduced effective package | `OPEN / BYPASSED` |
| MDS-03 | replaced by a conditional partition-mixing amplitude | alternative effective ansatz, not derived |
| MDS-04 | `s=2` is fixed | fixed effective, not a β_τ derivation |

Consequently, the current effective UI proxy and the declared physical parameter use the same project notation and broadly aligned bridge role, but the Parent→Reduced derivation remains absent.

The appropriate classification is:

`PROJECT_LEVEL_SEMANTIC_ALIGNMENT_NOT_PARENT_DERIVATION`.

## 6. Historical β candidate

The Legacy Formula Bible contains a different, older `β` chain:

- H32: `partial_tau vartheta = beta vartheta - lambda_Theta laplacian vartheta` — `open`;
- H33: `laplacian vartheta - (beta/lambda_Theta) vartheta = 0` — `open`;
- H34: `a0 = lambda_Theta c beta` — `historical`;
- H35: `beta = H0` — `historical`;
- H36: `a0 = lambda_Theta c H0` — `historical`;
- H52: `delta phi(f) = beta/f` — `open`;
- H53: `beta <-> H0` — `open`.

This historical β behaves as a drift/rate or cosmological anchoring parameter in the legacy Θ closure and appears again in an open GW-phase ansatz.

If H35 is adopted within that historical branch, then

```text
[beta]_legacy = [H0] = time^-1.
```

H32 independently requires β to have the same scaling as the selected `tau` derivative. But the normalization and dimension of the historical `tau` coordinate are not frozen in the current controlled branch.

Therefore:

```text
legacy beta != current beta_tau
```

unless a future source-backed alias and reduction explicitly establishes the identity.

The historical rate dimension must not be transferred to the current dimensionless effective proxy or to a future physical β_τ normalization.

## 7. Notation-collision audit

The repository contains several independent β objects:

1. legacy drift/rate `β` in H32–H36 and H52–H53;
2. historical MD-2S potential coefficient in `V(phi)=Lambda6+beta phi^2`;
3. normal-bundle/extrinsic-curvature components `beta^i` and `B^2=beta_i beta^i`;
4. an internal conical or metric parameter `beta`, including the benchmark notation `K4=beta=1`;
5. `beta_0`, the amplitude of the MD-2P-corr partition-mixing ansatz;
6. renormalization-group beta functions;
7. the current effective bridge proxy `beta_tau`.

No pair in this list is identified by notation alone. In particular:

```text
beta_tau != legacy beta
beta_tau != MD-2S potential beta
beta_tau != beta^i
beta_tau != conical beta
beta_tau != beta_0
beta_tau != an RG beta function
```

unless a dedicated canonical binding is later supplied.

## 8. What is recovered and what remains open

### Recovered

- current effective definition as a bridge mixing amplitude;
- dimensionless implementation contract;
- implemented formula and LambdaCDM zero limit;
- exact β_τ–I_B product degeneracy in the implemented model;
- current project-level roles in MDS-02, MDS-03 and MDS-04;
- later audit disposition of those three edges;
- historical β drift/rate context;
- notation-collision guards.

### Still open

- canonical 6D Parent definition of β_τ;
- physical Parent dimension and normalization;
- explicit derivation or rejection of MDS-02;
- explicit derivation, fixation or exclusion of MDS-03;
- explicit derivation, fixation or exclusion of MDS-04;
- proof that the dimensionless UI proxy is the normalized image of the physical β_τ parameter;
- an independent channel that breaks or correctly quotients the β_τ–I_B degeneracy;
- a released Reduced→Observable contract.

## 9. Gap decision

`FM0-GAP-002` changes from wholly unresolved to:

`PARTIALLY_RESOLVED_EFFECTIVE_PROXY_AND_MAPPING_ROLES_RECOVERED_PARENT_DERIVATION_OPEN`.

It remains **blocking**.

After this pass:

- `a0`: historical provenance recovered; current Parent open;
- `beta_tau`: effective proxy and mapping roles recovered; current Parent derivation open;
- `kappa_6`: canonical Parent recovered; reduced/observable mapping open;
- `R_chi`, `I_B`: still fully unresolved at FM-0 level;
- all five observable blocks: still open.

Thus:

```text
blocking gaps             = 10
partially resolved gaps   = 3
fully unresolved gaps     = 7
FM-G0                      = OPEN
```

## 10. Scientific firewall

This recovery does not:

- import a physics backend;
- execute a solver;
- create an AuthorizationDecision;
- create a SingleUseGrant;
- establish a physical background;
- execute response rank R;
- release K1-D;
- make K1-E admissible;
- authorize or modify CP01R4.

The frozen state remains:

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

## 11. Next admissible FM-0 move

The next targeted recovery should address `R_chi` because the same scan already located both:

- an implemented relative transition/compactification scale in the 4D sensitivity model; and
- conditional physical roles in MDS-01 and MDS-04, plus a separate effective overlap radius in MD-2P-corr.

Those uses must be separated before any identification is made.
