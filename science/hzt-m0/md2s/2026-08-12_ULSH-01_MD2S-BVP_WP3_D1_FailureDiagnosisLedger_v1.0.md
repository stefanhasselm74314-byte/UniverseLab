# ULSH-01 / MD2S-BVP — WP3-D1 Failure-Mode Diagnosis Ledger v1.0

Date: 2026-08-12

## Scope

This ledger diagnoses the completed CP01R1 transaction and freezes a CP01R2 protocol design. It does **not** authorize or execute CP01R2. CP01R1 is never replayed.

Source result SHA-256: `8562ba77cb0aeda87aceee3b7be301c06e948070beebc8916769c38d99b45ec8`

Source artifact SHA-256: `ddbec713207748bcdedc50486624effa14924a92beb476a746641f314f9843e8`

## Diagnosis

### D1-F01 — trust-region cap starvation

**Status: strong numerical + source diagnostic; causal proof not established.**

Across all 35 CP01R1 entries there are 1,967 recorded Newton iterations. In all 1,967 iterations the recorded step norm is equal to the active trust radius under the frozen diagnostic tolerance. Thirty entries terminate at `MAXIMUM_ITERATIONS`; none of those thirty records a rejected step. They therefore make accepted but trust-capped progress until the 60-iteration limit.

The frozen CP01R1 kernel expands the trust radius only when a full-factor accepted trial satisfies `candidate_norm < 0.25 * current_norm`, i.e. a single step must reduce the residual by more than 75 percent. In the observed clipped slow-progress regime this creates a self-locking geometry: accepted steps reduce the residual but do not satisfy the very aggressive radius-expansion trigger.

This establishes a leading algorithmic failure hypothesis. It does not establish that a differently scaled Newton method has a root to find.

### D1-F02 — no progress continuation occurred

**Status: established implementation behavior.**

The CP01R1 runtime writes a coarse state into its continuation map only after that state has already passed the local primary-candidate gate. Since CP01R1 produced zero local candidates, no terminal coarse state was prolonged to a finer mesh. Every one of the 35 mesh entries therefore began from its same-index fresh seven-seed construction at that mesh.

The nominal 24→32→48→64→96 hierarchy consequently did not perform basin continuation in this negative run.

### D1-F03 — persistent R_4D junction obstruction

**Status: established discrete diagnostic only.**

At N=96, `R_4D` is the dominant boundary residual for all seven seeds. Its absolute range is

`1.1252699553439607 <= |R_4D| <= 1.408873406960302`,

versus the unchanged boundary acceptance threshold `1e-10`.

Because the solver never entered a local-root neighborhood, this observation does **not** distinguish an actual incompatibility of the frozen junction sector from an algorithmic failure to reach the relevant basin.

### D1-F04 — fine-mesh conditioning degradation

**Status: established discrete diagnostic only.**

Median final discrete condition estimates rise monotonically across the mesh hierarchy:

- N=24: `4.5114272786901724e8`
- N=32: `1.2866425516506166e9`
- N=48: `7.089817354981332e9`
- N=64: `2.2234488268301258e10`
- N=96: `2.8644213665286554e11`

Final rank deficit occurs once at N=64 and twice at N=96. This motivates scale-aware linear algebra but is not a continuum-rank or Fredholm statement.

### D1-F05 — narrow seed-basin coverage

**Status: established protocol scope; basin implication heuristic.**

The canonical CP01R1 seed adapter uses amplitude `1/20` and maximum multiplier magnitude `1/2`, so the largest scalar displacement coefficient along its single fixed seed direction is only `0.025`. Across all 35 fresh starts, the initial residual infinity norm spans only `1.6265939343090037` to `1.62829175487399`.

This is narrow deterministic basin coverage; it does not show that a root exists outside that region.

## CP01R2 design freeze

CP01R2 is designed to test the leading **algorithmic** hypothesis while preserving causal isolation. The physical model parameters, topology, equations, boundary rows, seven seed identities, mesh hierarchy and every scientific acceptance threshold remain identical to CP01R1. No parameter scan, random restart, adaptive mesh insertion or homotopy is permitted in CP01R2.

The new primary method is `ETRN-01_EQUILIBRATED_TRUST_REGION_NEWTON`: complex-step Jacobian retained; deterministic column and row equilibration used only for the linear solve; an SVD minimum-norm step with fixed relative cutoff `1e-12`; trust norm evaluated in scaled coordinates; original unscaled residuals retained for every acceptance decision. Radius evolution uses the actual/predicted model-reduction ratio rather than requiring a 75 percent single-step residual collapse. Maximum radius is 64; maximum iterations are 120 per mesh.

For N>24, the immediately preceding mesh terminal state may be prolonged only when it is finite, admissible, not timed out, and has reduced the original residual infinity norm by at least 10 percent. Otherwise the same-index frozen seed at the new mesh is used. This is a deterministic initialization branch, not an acceptance relaxation.

All downstream candidate gates remain unchanged: local bulk/boundary root gate, required N=48/64/96 success, residual monotonicity, fine-profile and augmented-variable convergence, spectral tail, propagated `C_rr`, admissibility, condition gate, independent backend agreement and >=80-bit audit.

## Governance

`CP01R2 = DESIGNED_NOT_AUTHORIZED_NOT_EXECUTED`

`WP3 = OPEN_DIAGNOSIS_COMPLETE_CP01R2_DESIGNED_NOT_AUTHORIZED`

`WP4 = BLOCKED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`physical_evidence_effect = NONE`

No result here proves continuum existence/nonexistence, uniqueness, Fredholmness, continuum Jacobian invertibility, perturbative stability, ghost freedom, physical identification or observational confirmation/falsification.

## Next allowed action

`ULSH-01 / WP3-D2 — implement ETRN-01 and the deterministic CP01R2 progress-continuation protocol, then perform an independent implementation/protocol review. NO EXECUTION.`

A CP01R2 release authorization or execution grant is forbidden until that separate review passes.
