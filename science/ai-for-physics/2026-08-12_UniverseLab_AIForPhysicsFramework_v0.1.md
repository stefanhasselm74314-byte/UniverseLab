# UniverseLab AI-for-Physics Framework / UL-AIP v0.1

**Date:** 2026-08-12  
**Status:** `METHODS_FRAMEWORK_DEFINED_NOT_RELEASED`  
**Architecture:** `HPVS -> HZT-M0 -> HZT-Full`  
**Effect on physics gates:** none

## 1. Purpose

UL-AIP defines how machine learning may be used inside UniverseLab as a **methods, acceleration, inference and diagnostic layer** without replacing authoritative physics, mathematical verification or evidence governance.

The framework is intentionally non-evidential. It does not release a model, train a network, execute a HZT solver, alter a physical parameter, change a topology, modify a likelihood, advance WP4, release K1-D, make K1-E admissible, or create physical evidence.

The governing inequality is:

```text
AI acceleration != solver validation != physical identification != evidence
```

A second mandatory rule is:

```text
ML accuracy != physical admissibility
```

A third mandatory rule is:

```text
simulator validation != real-data validation
```

## 2. Research inspiration and scope

The framework is motivated by current AI-for-physics practice represented by the following institutional research programmes supplied for this methods review:

- MIT Physics, Strong Interaction and Nuclear Theory: https://physics.mit.edu/research-areas/strong-interaction-and-nuclear-theory/
- IAIFI domain research, astrophysics: https://iaifi.org/domain-research.html#astrophysics
- IAIFI domain research, experimental physics: https://iaifi.org/domain-research.html#experimental-physics
- IAIFI domain research, foundational AI: https://iaifi.org/domain-research.html#foundational-ai
- IAIFI theory papers: https://iaifi.org/papers-theory.html
- IAIFI domain research, theoretical physics: https://iaifi.org/domain-research.html#theoretical-physics

These sources motivate design principles such as symmetry-aware architectures, simulation-based inference, generative sampling, model-misspecification tests, interpretability, uncertainty calibration and independent physical validation. They do **not** constitute evidence for HZT.

## 3. UL-AIP module map

### AIP-SYM — symmetry and constraint preservation

Purpose: architectures or numerical parameterizations that encode known gauge, coordinate, geometric, conservation, boundary or junction constraints rather than forcing a generic network to learn them approximately.

Candidate applications include 6D field configurations, gauge-equivariant representations, constrained PDE/BVP surrogates and symmetry-aware feature extraction.

Required rule:

```text
A learned field is inadmissible until all registered constraints have been checked independently.
```

### AIP-SURR — verified solver surrogates

Purpose: emulate expensive authoritative forward calculations while retaining a mandatory return path to the authoritative solver.

Required flow:

```text
authoritative solver
    -> provenance-locked training set
    -> surrogate
    -> candidate prediction
    -> authoritative solver verification
```

A surrogate may rank, interpolate, propose or accelerate. It may not certify existence, uniqueness, regularity, stability, ghost freedom or a physical claim.

### AIP-SBI — simulation-based inference

Purpose: infer parameters or likelihood ratios from simulator output when an analytic likelihood is unavailable or impractical.

Candidate HZT context:

```text
theta_HZT -> simulator/forward map -> synthetic observables -> SBI layer
```

SBI is blocked from evidential use until the underlying forward map is independently admissible for the observable in question. An efficient inversion of an unratified forward map remains an unratified result.

### AIP-ANOM — anomaly and model-misspecification detection

Purpose: distinguish at least three states whenever scientifically meaningful:

```text
data consistent with baseline model
data consistent with candidate model
data inconsistent with both / neither-model state
```

The `neither` state is mandatory where a closed two-class classifier would otherwise force unknown physics, data systematics, simulation defects or out-of-distribution observations into a false model identification.

### AIP-LENS — weak/strong lensing applications

Purpose: field-level or map-level inference, reconstruction, compression and anomaly tests for lensing observables, including future contexts involving `Phi+Psi`, `Sigma` and `eta`.

Initial pilot policy: begin with a baseline/null reproduction task under an accepted reference cosmology before attempting HZT-vs-baseline discrimination. The A1/MACS J0308 false-anomaly control remains a methods-control example: catalogue or ML classification is not physical identification.

### AIP-GW — gravitational-wave applications

Purpose: waveform emulation, residual diagnostics, detector-domain reconstruction or population-level inference.

Mandatory nuisance coverage includes waveform systematics, detector noise, calibration uncertainty and population uncertainty before any new-physics interpretation.

### AIP-COSMO — large-scale cosmology applications

Purpose: emulation, nonlinear field inference, fast simulation proposals and cosmological data compression. Generative or super-resolution output must be validated beyond means and one-point summaries; covariance structure, tails and scale-dependent discrepancies are explicit QA targets.

## 4. Mandatory gate stack

### AIP-G0 — scope and non-evidence firewall

Pass condition: the task is classified as methods/acceleration/diagnostic work and explicitly declares zero automatic effect on physics gates.

Fail condition: any wording or automation promotes ML output directly to physical evidence, K1-D release, K1-E admissibility, WP4 release or theory confirmation.

### AIP-G1 — provenance and split integrity

Pass condition: training, validation and test data have immutable provenance records; simulator version, parameter domain, random seeds where relevant, preprocessing and split logic are recorded. Leakage between train, validation and test sets is excluded by construction.

### AIP-G2 — symmetry, constraint and unit conformance

Pass condition: all applicable registered invariances, conservation laws, boundary/junction conditions, dimensional conventions and forbidden regions are checked independently of predictive loss.

### AIP-G3 — numerical fidelity

Pass condition: performance is evaluated against held-out authoritative calculations using predeclared tolerances appropriate to the observable. Residuals, extrema, tails and physically important derived quantities are included; a single average error metric is insufficient.

### AIP-G4 — calibration, coverage and OOD

Pass condition: uncertainty calibration and empirical coverage are tested; out-of-distribution detection or a fail-closed domain boundary is implemented. Extrapolation beyond the validated domain is labeled non-authoritative.

### AIP-G5 — authoritative return test

Pass condition: candidate regions selected by ML are recomputed using the authoritative physics solver or reference pipeline. Disagreement is resolved in favor of the authoritative calculation unless that calculation itself is under a separately documented defect review.

### AIP-G6 — real-data/null/control test

Pass condition: where real observations are used, simulation-only validation is supplemented by null tests, control samples, nuisance perturbations and real-data consistency checks. A model may not claim discovery merely because it distinguishes two synthetic classes.

### AIP-G7 — evidence firewall and promotion review

Pass condition: any transition from methods output to scientific evidence requires a **separate pre-registered review** under the governing HPVS/HZT evidence process. UL-AIP itself has no authority to change K1-D, K1-E, WP4 or physical-evidence status.

## 5. Validation matrix

Every released UL-AIP model must carry a model card containing at least:

| Field | Requirement |
|---|---|
| scientific target | exact observable or numerical task |
| authoritative reference | solver/pipeline and immutable version binding |
| training domain | explicit parameter and data domain |
| split policy | leakage-resistant train/validation/test definition |
| symmetry/constraints | enumerated and independently checked |
| units/conventions | canonical registry binding |
| metrics | predeclared numerical and scientific metrics |
| uncertainty | calibration and coverage results |
| OOD | fail-closed boundary or detector |
| nuisance tests | perturbations relevant to the observable |
| return verification | authoritative solver cross-check |
| known failures | explicit failure modes |
| evidence effect | always `NONE` until a separate evidence review |

## 6. First pilot sequence

The recommended first implementation sequence is deliberately conservative:

1. `AIP-LENS-01-NULL`: reproduce a published/reference weak-lensing inference or compression task under a baseline cosmology only.
2. `AIP-SURR-01`: construct a small surrogate around an already released, stable numerical map; do not use an unresolved physics branch as the first training target.
3. `AIP-ANOM-01`: implement a three-way baseline/candidate/neither diagnostic with injected systematics and OOD cases.
4. `AIP-SBI-01`: only after a forward map for the target observable is separately admissible.
5. `AIP-SYM-01`: prototype constraint-preserving representations for a mathematically controlled subproblem before attempting a full 6D field surrogate.

No pilot is authorized by this document; each requires its own scoped release record.

## 7. Prohibited inferences

UL-AIP outputs must never be described as proving any of the following without an independent mathematical/physical review:

- existence or uniqueness of a continuum solution;
- regularity of a 6D geometry;
- absence of ghosts or gradient instabilities;
- satisfaction of untested junction/boundary conditions;
- identification of new physics from a classifier score;
- HZT confirmation from synthetic discrimination;
- K1-D release or K1-E admissibility;
- physical evidence from surrogate agreement alone.

## 8. Governance state at creation

```text
UL-AIP                  = METHODS_FRAMEWORK_DEFINED_NOT_RELEASED
model_training          = NO
model_execution         = NO
solver_execution_effect = NONE
WP4                      = BLOCKED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical_evidence_effect = NONE
```

UL-AIP therefore adds a controlled research capability without changing the scientific status of HZT-M0.