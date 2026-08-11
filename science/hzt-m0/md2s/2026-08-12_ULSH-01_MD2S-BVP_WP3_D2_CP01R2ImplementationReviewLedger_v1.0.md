# ULSH-01 / MD2S-BVP — WP3-D2 CP01R2 Implementation + Independent Review Ledger v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Run under design: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Scope

WP3-D2 implements the `ETRN-01_EQUILIBRATED_TRUST_REGION_NEWTON` method frozen in WP3-D1 and independently reviews the implementation protocol. This work package is **NO EXECUTION**. It does not bind the new method to the physical CP01R2 backend, does not create a release authorization or single-use execution grant, and cannot execute CP01R2.

## Physical freeze

The CP01R1 physical sector remains unchanged: `a_F=1/4`, all six model parameters, topology, physical residual equations, eight boundary residuals, seven deterministic seeds, meshes `[24,32,48,64,96]`, and every scientific acceptance/QA threshold remain fixed. Scaling is preconditioning only and is never an acceptance quantity.

## ETRN-01 implementation

The generic review kernel implements column equilibration, row equilibration, truncated-SVD minimum-norm Newton steps, a trust norm in scaled coordinates, model-reduction-ratio radius control, deterministic half-step backtracking, 120 iterations per mesh, and 12-iteration stagnation detection at relative improvement floor `1e-4`.

The trust-radius update is:

- `rho < 0.25`: shrink by `0.25`;
- `rho > 0.75` and accepted scaled step norm `>=0.8 Delta`: double, capped at `64`;
- otherwise unchanged.

The original unscaled residual infinity norm remains the acceptance merit. A trial is accepted only when it is admissible, strictly lowers the original residual infinity norm, has a positive model-reduction denominator, and has `rho>=0.10`.

## Deterministic progress continuation

For `N>24`, only the immediately preceding mesh terminal state may be prolonged, and only if it is finite, admissible, not timed out, and achieves at least 10% reduction of the stage's original residual infinity norm. Otherwise the same-index fresh CP01R1 seed is used. No random restart, parameter scan, homotopy, parameter loading, adaptive mesh insertion, or extra seed is introduced.

## Independent review

Seven review gates are required and all are represented in the independent review artifact and CI:

`IR01_PROTOCOL_FIDELITY`, `IR02_SYNTHETIC_SCALING_AND_TRUST_RADIUS`, `IR03_ORIGINAL_RESIDUAL_ACCEPTANCE_FIREWALL`, `IR04_PROGRESS_CONTINUATION_DETERMINISM`, `IR05_RAW_AND_SCALED_DIAGNOSTIC_CAPTURE`, `IR06_NO_PHYSICAL_EXECUTION_CAPABILITY`, `IR07_NO_RELEASE_OR_GRANT_ARTIFACT`.

Two implementation clarifications are explicitly quarantined as numerical control semantics with no physics effect: the predicted-reduction denominator uses the exact backtracked trial displacement; if every deterministic backtracking trial is rejected, the radius shrinks once by 0.25 and the implementation fails closed at the minimum radius.

## Synthetic review probes

An independent diagonal probe uses `J=diag(1e6,1e-6)`: the raw condition is `1e12`, while the designed equilibration maps the linear solve geometry to condition `1` without changing the original equations. A separate one-dimensional clipped-step probe reduces residual only from `10` to `9` (10%) while obtaining `rho=1`; ETRN-01 therefore expands `Delta: 1 -> 2`. This directly tests the CP01R1 trust-radius starvation diagnosis without requiring a physical solve.

## Epistemic status

**Implemented/reviewed:** generic ETRN-01 method semantics, deterministic progress-continuation policy, diagnostic capture, and the no-execution firewall.  
**Not established:** CP01R2 physical convergence, disappearance of the `R_4D` obstruction, continuum existence/uniqueness, Fredholm properties, continuum invertibility, perturbative stability, ghost freedom, physical identification, or observational support.

## Governance

`WP3 = OPEN_CP01R2_METHOD_IMPLEMENTED_AND_REVIEWED_PHYSICAL_BINDING_PENDING`  
`WP4 = BLOCKED`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`physical_solve_authorized = false`  
`physical_solve_executed = false`  
`physical_evidence_effect = NONE`

If and only if WP3-D2 CI and independent review pass, the next allowed work package is `ULSH-01 / WP3-D3 — CP01R2 physical target binding and release-readiness review, NO EXECUTION`.
