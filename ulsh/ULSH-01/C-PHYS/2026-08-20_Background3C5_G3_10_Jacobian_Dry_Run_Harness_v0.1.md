# ULSH-01 / C-PHYS — Background3C5 G3.10 Jacobian Evaluation Harness / Dry-Run Contract v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** DRY_RUN_HARNESS_DEFINED / NO_SOLVER_EXECUTION / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This block implements the G3.9 preregistration as a non-executing orchestration harness. It may generate deterministic job manifests, branch-lock metadata, expected artifact paths and abort classifications. It must not invoke a Background3C5 kernel, shell out to a solver, submit remote jobs or produce physical BVP outputs.

## 2. Authoritative preregistration

The harness consumes the frozen G3.9 machine contract with:

- 10 dimensionless coordinates;
- central finite differences only;
- step levels `0.01, 0.005, 0.0025`;
- nominal solver metadata `rtol=1e-8, max_nodes=20000`;
- refined smallest-step metadata `rtol=1e-10, max_nodes=50000`;
- fixed branch locks `(N_F,m_layer,n_N,n_S,topology,pole_frobenius_branch,profile_node_class,boundary_operator_identity)`;
- exact scheduled count `81` BVP evaluations;
- `execution_authorized=false`.

The solver settings in the dry-run plan are metadata only.

## 3. Deterministic schedule

The schedule contains exactly:

1. one baseline nominal manifest;
2. for each of 10 coordinates, three nominal step magnitudes and both signs: `10*3*2=60` perturbation manifests;
3. for each of 10 coordinates, the smallest step `0.0025`, both signs, with refined solver metadata: `10*2=20` refinement manifests.

Hence

`N_plan = 1 + 60 + 20 = 81`.

No other job class is admissible in v0.1.

## 4. Manifest identity

Every planned evaluation must contain at minimum:

- deterministic `evaluation_id`;
- `kind in {baseline, perturbation}`;
- coordinate name or null for baseline;
- signed dimensionless offset;
- step magnitude and step-level index;
- solver-profile label `nominal` or `refined_h3`;
- copied branch-lock object;
- expected input/output artifact names;
- `execute=false`;
- `evidence_effect=NONE`.

No field named `command`, `solver_command`, `executable`, `submit`, `run` or equivalent execution hook is permitted in an emitted evaluation manifest.

## 5. Branch-lock firewall

The harness validates before planning that

`n_N - n_S = m_layer*N_F`.

The discrete branch values themselves are provided only by a future authorized run configuration; the v0.1 dry-run may use a synthetic QA branch solely to test schedule mechanics. Such a QA branch must be labeled `SYNTHETIC_DRY_RUN_ONLY` and is never physical evidence.

Within a generated plan all 81 evaluation manifests carry byte-for-byte identical branch-lock values.

## 6. Domain handling

The harness does not evaluate parameter-domain membership because no physical baseline is bound. Instead it records the G3.9 rule:

- symmetric `+/-` perturbations are mandatory;
- one-sided fallback is forbidden;
- if future binding reports a domain or branch violation, that coordinate/step certificate becomes `BRANCH_OR_DOMAIN_INVALID`.

The dry-run harness must not silently alter a step size.

## 7. Expected artifact topology

The plan reserves deterministic paths for future authorized outputs, including:

- baseline manifest;
- per-evaluation manifest;
- future `R_hat` vector placeholder path;
- branch diagnostics placeholder path;
- aggregate matrix targets `J_hat_h1`, `J_hat_h2`, `J_hat_h3`, `J_hat_h3_refined`;
- uncertainty and SVD report targets.

During dry-run no physical `R_hat` vectors or Jacobian matrices are created. Only the plan/index and manifests are emitted.

## 8. Fail-closed checks

Dry-run planning fails if:

- G3.9 `execution_authorized` is not false;
- coordinate count is not 10;
- step levels differ from the frozen three-level schedule;
- finite-difference scheme is not `CENTRAL_ONLY`;
- one-sided fallback is not `FORBIDDEN`;
- total planned count is not exactly 81;
- any emitted manifest contains an execution hook;
- branch locks differ across manifests;
- the bundle constraint is violated;
- any manifest claims physical evidence.

## 9. What this does not prove

A successful dry run proves only orchestration consistency. It does not prove:

- existence of a global nonlinear BVP solution;
- actual solver binding;
- derivative convergence;
- Jacobian rank 10;
- stability or ghost freedom;
- physical response rank `R`.

## 10. Verdict

`G3_10_DRY_RUN_HARNESS = DEFINED`

`G3_10_EXPECTED_PLAN_COUNT = 81`

`G3_10_SOLVER_INVOCATION = FORBIDDEN`

`G3_10_PHYSICAL_OUTPUT_GENERATION = FORBIDDEN`

`G3_10_BRANCH_LOCK_FIREWALL = REQUIRED`

`ACTUAL_81_BVP_EVALUATIONS = NOT_EXECUTED`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN_NOT_EVALUATED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`
