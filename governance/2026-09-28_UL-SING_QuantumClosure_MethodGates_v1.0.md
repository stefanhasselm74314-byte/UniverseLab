# UniverseLab — UL-SING Quantum-Closure Method Gates v1.0

**Date:** 2026-09-28  
**Classification:** CANONICAL METHOD GOVERNANCE / NO PHYSICAL PROMOTION  
**Status:** `OWNER_ADOPTED_CANONICAL_METHOD_GATES`  
**Basis main:** `21655418df14874857cfbfa189fdd43a9c0d54c6`  
**Source review:** PR #249, merge `97f12c99d2c4c68881ebae4170567a15eec3eaf6`  
**Owner adoption:** PR #250, merge `21655418df14874857cfbfa189fdd43a9c0d54c6`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Canonical decision

The project owner explicitly adopted all three reviewed candidates:

- `QG-PI-01`
- `QG-GAP-01`
- `KK-CTP-01`

The controlling owner statement was:

`Alle drei adoptieren`

The three identifiers are therefore canonical **method gates** under the scope and limitations below.

This decision changes method governance only. It does not establish a physical HZT solution, release any solver, validate a quantum bounce, create empirical evidence, or alter K1-D/K1-E.

---

## 2. QG-PI-01 — Gravitational path-integral / saddle-family closure

### Applicability

This gate activates only for a future HZT branch that uses a quantum-cosmological bounce, no-boundary prescription, or Euclidean/complex saddle construction.

### Canonical requirement

A quantum-cosmological HZT branch is not closed by finding one regular saddle.

At minimum, the construction must bind:

1. the parent action and relevant boundary terms;
2. gauge fixing or an explicit redundancy quotient;
3. the integration contour or equivalent path-integral prescription;
4. the relevant saddle family and the rule selecting contributing saddles;
5. semiclassical weights and fluctuation data where required;
6. a controlled definition of the resulting path integral or saddle sum, including convergence/resummation where needed.

### Source boundary

The source preprint arXiv:2609.29859 demonstrates the necklace pathology in a specific 3D de-Sitter axion-wormhole setup and analyzes a mostly Lorentzian alternative in minisuperspace.

It does **not** establish that HZT has the same divergence, nor does it select the correct HZT contour.

### Forbidden inferences

- one regular saddle ⇒ quantum consistency;
- the necklace divergence is already present in HZT;
- the mostly Lorentzian contour used in the source is automatically the HZT prescription.

### Current HZT status

`NOT_EVALUATED_CURRENTLY_NOT_APPLICABLE_TO_CLASSICAL_HZT_STATE`

---

## 3. QG-GAP-01 — Invariant geometric-gap derivation

### Applicability

This gate activates only if HZT invokes a **fundamental** minimum radius, area or volume as part of a singularity-avoidance argument.

### Canonical requirement

The minimum scale must be derived from the parent constraint/physical-invariant structure.

Required logical chain:

`S_parent → constraints → physical invariants / Casimirs / Dirac observables → R_min / A_min / V_min → claimed singularity-avoidance consequence`

A numerical floor, mesh cutoff, UV regulator or domain restriction may be useful computationally but is not, by itself, a fundamental geometric-gap proof.

### Source boundary

arXiv:2609.31123 derives an area lower bound from Casimirs of the closed Poisson structure of a fixed two-vertex loop-gravity model.

The result does not establish an HZT bounce and does not close inhomogeneous continuum BKL dynamics.

### Forbidden inferences

- regulator = physical gap;
- two-vertex LQG gap = HZT gap;
- finite graph anisotropy = continuum BKL closure;
- every valid bounce must contain a geometric gap.

### Current HZT status

`NOT_EVALUATED_CURRENTLY_NOT_APPLICABLE_WITHOUT_HZT_GAP_CLAIM`

---

## 4. KK-CTP-01 — Finite-time in-in heavy-mode closure

### Applicability

This gate activates when a quantum HZT 6D→4D derivation traces out unobserved KK, radion or bulk modes and uses the reduced theory for cosmological observables.

### Canonical requirement

The reduction must distinguish:

`exact/controlled partial trace ≠ nonlocal reduced effective description ≠ local EFT`

Before a local 4D EFT is used, the derivation must provide, where applicable:

1. heavy/light mode decomposition with provenance;
2. a finite-time reduced density matrix or influence functional;
3. Schwinger-Keldysh branch-mixing analysis;
4. control of nonlocal kernels or the derivative expansion;
5. modewise scale-hierarchy and adiabaticity checks;
6. KK-tower summation/truncation control.

The useful conservative HZT screening relation

`m_heavy ≫ max(H, sqrt(|Hdot|), tau_bounce^-1, k_phys)`

is **not** a theorem of arXiv:2609.30370 and cannot replace the actual derivative-expansion and adiabaticity checks.

### Repository integration

This gate supplements, but does not replace or invalidate:

- ULSH-07 · Kaluza-Klein Spectrum Solver;
- ULSH-08 · Radion Stability Solver;
- FM-0 parent→reduced→observable recovery.

### Forbidden inferences

- late-time decay of a heavy mode ⇒ zero contribution to the finite-time trace;
- tracing out ⇒ local EFT;
- `m ≫ H` alone is universally sufficient;
- existing ULSH-07/08 classical/eigenvalue work is invalid.

### Current HZT status

`NOT_EVALUATED_NO_RELEASED_QUANTUM_6D_TO_4D_OBSERVABLE_REDUCTION`

---

## 5. Global firewalls

The adoption and canonicalization of these method gates do not alter:

`physical_background = NOT_ESTABLISHED`  
`physical_response_rank = NOT_EXECUTED`  
`FM-G0 = OPEN`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`

The three source papers remain identified as **preprints**.

No direct HZT evidence is created by citing or adopting their methodological lessons.

`physical_gate_effect = NONE`  
`physical_evidence_effect = NONE`

## 6. Canonical machine-readable source

The binding machine-readable registry for this decision is:

`registry/2026-09-28_UL-SING_QuantumClosure_MethodGates_v1.0.json`
