# ULSH-01 / C-PHYS — Background3C5 Kernel Availability & Binding Audit v0.1

Date: 2026-08-15
Status: `BLOCKED_NO_RATIFIED_EXACT_BACKGROUND3C5_KERNEL_FOUND`
Evidence effect: `NONE`
Architecture: `HPVS -> HZT-M0 -> HZT-Full`
Active block: `HZT-M0 / S6 / C-PHYS / ULSH-01`

## 1. Decision

No repository implementation was found that may presently be identified as the ratified exact finite-thickness nonlinear `Background3C5` physical BVP kernel required by `2026-08-15_Background3C5_Equation_Freeze_Audit_v0.2.md`.

Therefore:

- physical kernel binding is **BLOCKED**;
- the 41-job physical response campaign is **NOT AUTHORIZED**;
- `rank(R)=4` remains **OPEN / NOT EXECUTED**;
- `K1-D = NOT_RELEASED`;
- `K1-E = NOT_ADMISSIBLE`.

This is not a numerical failure. It is an implementation/provenance gate.

## 2. Repository search result

Current repository searches found no candidate under the expected or equivalent identifiers:

- `Background3C5`
- `background3c5.py`
- `src/hzt2six/blocks`
- `finite_thickness`
- `solve_bvp`
- nonlinear BVP code exposing center expansion plus outer matching for the frozen six-field system.

The absence result is scoped to the repository state audited on 2026-08-15. It is not a theorem that no implementation exists outside the repository.

## 3. H4R4B disposition

The repository contains the exact analytic `H4R4B` global control witness and parent-equivalence audit. Its own canonical registry classifies it as:

`EXACT_ANALYTIC_CONTROL_WITNESS_AND_EQUIVALENCE_AUDIT_NO_NUMERICAL_PHYSICAL_SOLVE`

and explicitly records:

- `solver_execution = false`;
- `physical_evidence_effect = NONE`;
- generic M1 global background existence = OPEN;
- physical parent solve authorized = false;
- nontrivial D2N-Q dynamic selection = OPEN.

Hence H4R4B is admissible as a **regression/consistency witness** for a future solver, but not as the missing finite-thickness nonlinear BVP solver and not as physical response-rank evidence.

## 4. Frozen target system for any future kernel

A bindable kernel must realize the equation-freeze v0.2 field content

`F = (A, B, C, phi, s, Q)`

with

`Q = exp(3A+B-C+gamma) Z_F(phi) A_t'`,

`chi = theta' - gSigma A_chi`,

and the canonical normalization

`varphi = phi/M6^2`,

`Z_phi = 1`,

`Z_F = exp(-2 a_F varphi)`,

`q_ref = q_hat/M6`,

`gSigma = m_layer q_hat/M6`.

At fixed discrete branch at least `(n, N_F, m_layer)` must remain unchanged through the Jacobian scan.

### Required dynamics

The implementation must include, without surrogate substitution:

1. Maxwell equation for `Q` with localized source current;
2. scalar divergence equation for `phi`;
3. finite-thickness matter equation for `s` and gauge-invariant `chi`;
4. Einstein evolution equations for `u=A'`, `v=B'`, `w=phi'`;
5. Hamiltonian/radial constraint `H=0`;
6. `V_tot = V(phi)+Lambda_Delta+V_Sigma(s)` and the frozen stress decomposition.

### Required boundary/global structure

The implementation must demonstrate:

- regular center expansion;
- conical regularity in the physical pole variables;
- finite field strength at the center;
- outer matching to the parent branch;
- `s -> 0` in the outer region;
- `Q -> Q_inf`;
- `H -> 0`;
- fixed discrete charge/flux sector;
- branch-continuity provenance.

## 5. Mandatory authorization gates

A physical binding MUST remain fail-closed until all gates are independently PASS:

| Gate | Required result | Current status |
|---|---|---|
| G1 symbolic residual realization | exact frozen equations represented | OPEN |
| G2 center expansion closure | regular coefficients/BC count close | OPEN |
| G3 outer-match closure | full outer BC map closes | OPEN |
| G4 constraint preservation | `H=0` propagated within certified tolerance | OPEN |
| G5 operator identity | implementation operator matches frozen operator | OPEN |
| G6 H4R4B control regression | analytic witness reproduced where applicable | OPEN |
| G7 solver convergence certificate | mesh/tolerance/refinement convergence | OPEN |
| G8 provenance firewall | no mock/surrogate output accepted as physical | PASS by contract, execution pending |

Physical execution authorization is

`AUTHORIZED <=> G1 & G2 & G3 & G4 & G5 & G6 & G7 & G8`.

At this audit state the conjunction is false.

## 6. Non-inferences

This audit does **not** imply:

- failure of the six-dimensional model;
- nonexistence of a finite-thickness solution;
- rank deficiency of the physical response matrix;
- ghost freedom or instability;
- generic global existence;
- physical selection of the H4R4B control witness.

It establishes only that the required exact executable kernel has not yet been located/ratified in the repository.

## 7. Next admissible implementation step

Create the physical kernel as a new explicitly reviewed implementation, preferably at the previously proposed path

`src/hzt2six/blocks/background3c5.py`,

but treat the file path itself as non-evidential. The implementation must first pass G1-G8. Only then may `hzt_background3c5_response_runner_v1.1.py` bind to it and launch the 41-job physical response campaign.

The H4R4B witness should be included as a regression fixture, not as a physical calibration point.
