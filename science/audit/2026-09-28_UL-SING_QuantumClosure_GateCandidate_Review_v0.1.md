# UL-SING — Quantum Closure Gate Candidate Review v0.1

**Date:** 2026-09-28  
**Classification:** NONCANONICAL SCIENTIFIC REVIEW / METHOD-GATE CANDIDATES  
**Base main:** `9e34903a09db17fb6d3c338be13ab934f16f09f1`  
**Status:** `PASS_WITH_CONDITIONS_NONCANONICAL_CANDIDATES`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Scope

This review evaluates three new UL-SING literature-monitor candidates:

- `QG-PI-01` — gravitational path-integral / saddle-family closure;
- `QG-GAP-01` — invariant geometric-gap derivation;
- `KK-CTP-01` — finite-time in-in heavy-mode closure.

These identifiers are **candidates only**. They are not current canonical UniverseLab gate IDs and this review does not promote them into the HPVS/HZT canon.

The reviewed preprints are:

1. Blommaert, Kudler-Flam, Narovlansky & Urbach, **The cosmological necklace problem**, arXiv:2609.29859.
2. Garay, Garay, Gugliotta, Rodríguez-González & Vera, **Global variables and dynamics of emergent cosmology in loop gravity**, arXiv:2609.31123.
3. Sun & Wong, **Tracing out massive fields in cosmology**, arXiv:2609.30370.

All three are preprints as of this review.

## 2. Repository context

Current main already keeps the relevant HZT sectors open and nonoperative:

- ULSH-07 KK Spectrum Solver is `PLANNED`; its release gate requires a converged eigenspectrum with normalized modes and boundary provenance.
- ULSH-08 Radion Stability Solver is `PLANNED`; its release gate requires a stabilized heavy radion or explicit exclusion with coupling and mode normalization.
- FM-0 still has an open parent-to-reduced-to-observable map, and the GW observable block is not released.
- physical background remains not established; physical response rank remains not executed; K1-D is not released; K1-E is not admissible.

The new candidates therefore constrain future derivations. They do not establish new HZT physics.

---

# 3. SCI-30 materiality review

## 3.1 QG-PI-01 — gravitational path-integral / saddle-family closure

### Source-supported result

arXiv:2609.29859 identifies an infinite family of real Euclidean "cosmological necklace" saddles in the studied 3d de Sitter axion-wormhole setup. Repeated covers correspond to repeated bounces. In the Euclidean saddle sum, the entropy grows without bound and the path integral diverges.

The same work studies an alternative mostly-Lorentzian lapse contour. In minisuperspace steepest descent, a single necklace dominates and the entropy is finite. Correct saddle counting requires the FLRW redundancy `a -> -a`. Higher-dimensional axion-flux and Yang-Mills-instanton cases are argued to behave similarly, but the higher-dimensional extension is less strongly established.

### HZT relevance

The supported methodological lesson is:

`regular individual saddle != well-defined quantum-cosmological state`.

For any future HZT no-boundary, Euclidean or complex bounce branch, a single regular 6D saddle is not sufficient evidence of quantum consistency. The relevant contour and the contributing saddle family must be specified and controlled.

### Conditioned candidate

`QG-PI-01` is admissible as a **method-gate candidate** if formulated as:

> A quantum-cosmological HZT branch may not be treated as closed merely because one regular saddle exists. The path-integral prescription must specify the contour, gauge/redundancy quotient, relevant saddle family, semiclassical weights and convergence or controlled resummation.

Negative modes / fluctuation determinants are sensible HZT additions to the closure test, but they are not the central theorem of arXiv:2609.29859.

**SCI-30:** `PASS_WITH_CONDITIONS`

---

## 3.2 QG-GAP-01 — invariant geometric-gap derivation

### Source-supported result

arXiv:2609.31123 solves the fixed two-vertex LQG model using global variables forming a closed Poisson subalgebra. Two Casimirs imply

`A^2 >= Sigma + L = A_gap^2`.

The paper derives a generalized Friedmann equation with an additional bounded `L^2` anisotropy term. For an illustrative matter branch, a Big Bounce occurs at `a_BB > a_gap`. The authors explicitly frame continuum/multi-vertex coarse-graining as future work.

### HZT relevance

The paper does **not** establish a universal minimum length/area in arbitrary quantum gravity, nor does it prove anything directly about HZT.

The useful HZT standard is conditional:

> If HZT invokes a fundamental minimum radius, area or volume as part of a singularity-avoidance mechanism, that minimum must be derived from the parent constraint/physical-invariant structure rather than inserted solely as a regulator.

A hand-imposed cutoff may still be useful numerically, but it is not by itself a fundamental singularity-resolution proof.

The finite graph anisotropy result does not close BKL/inhomogeneous continuum dynamics.

**SCI-30:** `PASS_WITH_CONDITIONS`

---

## 3.3 KK-CTP-01 — finite-time in-in heavy-mode closure

### Source-supported result

arXiv:2609.30370 derives the finite-time reduced density matrix obtained after tracing out a massive field in quasi-de Sitter. The trace generically produces Schwinger-Keldysh branch-mixing terms and an exact nonlocal description with kernels of the form

`G ~ (m^2 - Box)^(-1)`

and mixed terms such as

`J_+ G_+- J_-`.

The paper explicitly states that tracing out does not itself require `m >> H`, whereas a **local EFT** requires a physical hierarchy and adiabatic evolution. When `m ~ H`, the effective description generally remains nonlocal. It also demonstrates that late-time decay of the massive field does not by itself justify discarding its contribution to the trace.

### HZT relevance

This is directly relevant to any future quantum 6D -> 4D reduction involving unobserved KK, radion or bulk modes.

Current HZT roadmaps already require physical KK masses/profiles and a stabilized heavy radion, but they do not yet constitute a finite-time in-in reduction of those sectors.

The monitor-proposed inequality

`m_heavy >> max(H, sqrt(|Hdot|), tau_bounce^-1, k_phys)`

is a useful conservative **HZT screening condition**, not a theorem of the paper. The more fundamental local-EFT checks are the relevant derivative expansion and adiabaticity on the actual background, schematically

`||Box|| / m_heavy^2 << 1`

and modewise

`|omega_dot / omega^2| << 1`.

For a KK tower, the check must apply to the actually coupled modes/tower and not only to a single nominal mass scale.

**SCI-30:** `PASS_WITH_CONDITIONS`

---

# 4. SCI-31 formal-consistency review

## 4.1 QG-PI-01 formal closure requirements

A usable HZT implementation must distinguish:

1. parent action and boundary terms;
2. gauge fixing / redundancy quotient;
3. complexification and integration contour `Gamma`;
4. relevant saddles `sigma` on that contour;
5. intersection numbers / saddle inclusion rule;
6. semiclassical action and fluctuation data;
7. convergence, resummation or another mathematically explicit definition of `Z_Gamma`.

The generic schematic object

`Z_Gamma ~ sum_sigma n_sigma exp(i S_sigma / hbar)`

is not closed by exhibiting one finite `S_sigma`.

**SCI-31:** `PASS_WITH_CONDITIONS`

Condition: do not promote a contour prescription until the exact HZT variables, gauge redundancies and boundary data are defined.

## 4.2 QG-GAP-01 formal closure requirements

The proposed HZT gate is logically valid only when a fundamental gap is actually claimed.

Required chain:

`S_parent -> constraints -> reduced/Dirac observables or Casimirs -> bound -> R_min/A_min/V_min -> bounce consequence`.

A numerical domain floor, mesh cutoff or regularization parameter must be labeled separately from a physical invariant gap.

**SCI-31:** `PASS_WITH_CONDITIONS_CONDITIONAL_APPLICABILITY`

## 4.3 KK-CTP-01 formal closure requirements

A future HZT reduction must distinguish three operations:

1. exact partial trace / influence functional;
2. nonlocal reduced effective description;
3. local derivative-expanded EFT.

The logical implications are one-way:

`trace exists` does not imply `local EFT valid`;

`late-time heavy-field decay` does not imply `trace contribution vanishes`;

`heavy asymptotically` does not imply `adiabatic through a bounce`.

For a time-dependent internal radius, `m_n(t)` can vary even when the mode is heavy before and after the nonadiabatic interval.

**SCI-31:** `PASS_WITH_CONDITIONS`

---

# 5. CTRL-02 gate decision

## QG-PI-01

**Decision:** `PASS_WITH_CONDITIONS_NONCANONICAL_GATE_CANDIDATE`

Allowed meaning: path-integral/saddle-family closure requirement for future quantum-cosmological HZT branches.

Forbidden meaning: proof that HZT currently has a necklace divergence, or proof that one particular Lorentzian contour is the correct HZT contour.

Priority: `P0_WHEN_QUANTUM_BOUNCE_OR_NO_BOUNDARY_BRANCH_IS_ACTIVATED`.

## QG-GAP-01

**Decision:** `PASS_WITH_CONDITIONS_NONCANONICAL_GATE_CANDIDATE`

Allowed meaning: if HZT claims a fundamental geometric gap, derive it from parent invariant/constraint structure.

Forbidden meaning: universal requirement that all bounce mechanisms possess a minimum geometric gap.

Priority: `P1_CONDITIONAL`.

## KK-CTP-01

**Decision:** `PASS_WITH_CONDITIONS_NONCANONICAL_GATE_CANDIDATE`

Allowed meaning: finite-time in-in / reduced-density-matrix closure before treating heavy KK/radion/bulk sectors as a local 4D EFT for quantum observables.

Forbidden meaning: current ULSH-07/08 classical/eigenvalue work is invalid, or `m >> H` alone is a sufficient universal criterion.

Priority: `P0_FOR_FUTURE_QUANTUM_6D_TO_4D_OBSERVABLE_REDUCTION`.

---

# 6. Integration with existing UniverseLab gaps

These candidates do not create physical evidence. They refine closure conditions around existing open gaps:

- `QG-PI-01` and `QG-GAP-01` belong to a future quantum-singularity branch and do not modify the current classical ULSH/HZT-M0 no-go state.
- `KK-CTP-01` refines the already-open parent-to-reduced-to-observable map and future GW/quantum-observable reduction.
- Existing ULSH-07 and ULSH-08 release gates remain unchanged.
- FM-G0 remains open.
- No likelihood/evidence layer is released.

## Explicit non-effects

`physical_background = NOT_ESTABLISHED`  
`physical_response_rank = NOT_EXECUTED`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`physical_gate_effect = NONE`  
`physical_evidence_effect = NONE`

# 7. Next allowed repository step

Do not modify historical gate files or current canonical state in place.

The next allowed step is a separate owner-reviewed / CTRL-01 versioned successor only if the project owner explicitly adopts one or more candidate IDs as canonical method gates.

Until then, this review remains noncanonical provenance and QA material.
