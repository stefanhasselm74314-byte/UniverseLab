# ULSH-01 / C-PHYS — Background3C5 G3.9 Functional-Jacobian Evaluation Preregistration v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** EVALUATION_PLAN_PREREGISTERED / EXECUTION_NOT_AUTHORIZED / ACTUAL_RANK_NOT_EVALUATED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This block preregisters the later numerical evaluation of the canonical dimensionless 10x10 boundary Jacobian `J_hat` defined by G3.7 and certified by the uncertainty logic of G3.8.

It performs no nonlinear BVP solve, no physical Jacobian evaluation and no response-rank run.

## 2. Fixed operator and branch

The evaluated boundary operator must be exactly the G3.6/G3.5 operator

`B10=(R_A,R_L,R_phi,R_patch,R_4d,R_chi,R_scalar,R_gauge^FT,R_s,R_s_flux)`

on the G3.4 supplementary finite-thickness path.

Before any derivative evaluation, fix the discrete bundle sector

`(N_F,m_layer,n_S)`

and derive

`n_N=n_S+m_layer*N_F`.

The four integers/labels `(N_F,m_layer,n_N,n_S)` must remain unchanged in every baseline, perturbation and refinement evaluation.

## 3. Continuous coordinates

Use the dimensionless G3.7 coordinates

`u_hat=(phi_N0_hat,Q_N0_hat,A_S0_hat,phi_S0_hat,Q_S0_hat,rho_N_hat,rho_S_hat,K4_hat,c_N_hat,c_S_hat)`.

No adaptive redefinition of these coordinates is permitted during one Jacobian certificate.

## 4. Finite-difference scheme and step levels

Use central finite differences in each of the ten canonical dimensionless coordinate directions.

The preregistered nested step levels are inherited from the already-frozen ULSH-01 response-rank method:

`h1=1.0e-2`,

`h2=5.0e-3`,

`h3=2.5e-3`.

For each direction `e_j`,

`J_hat[:,j;h_k]=[R_hat(u_hat+h_k e_j)-R_hat(u_hat-h_k e_j)]/(2 h_k)`.

Because G3.7 has already absorbed the physical characteristic scales into the definition of `u_hat`, these are absolute steps in canonical dimensionless coordinates. No undocumented `max(1,|u_j|)` or other adaptive rescaling is allowed.

If either `+h_k` or `-h_k` leaves the admissible domain, changes topology, changes pole regularity, changes node class, or violates the fixed bundle sector, the central derivative at that level is invalid. It must not be silently replaced by a one-sided derivative. The result is fail-closed until a new local step contract is preregistered.

## 5. Solver tolerance hierarchy

The nominal and refined solver settings are inherited from `background3c5_response_run_config_template_v1.1.json`:

Nominal:

`relative_tolerance = 1e-8`, `max_nodes = 20000`.

Refined:

`relative_tolerance = 1e-10`, `max_nodes = 50000`.

The refined solver is applied at the smallest derivative step `h3` for both signs of every one of the ten coordinate directions.

A solver-tolerance refinement comparison is mandatory for `epsilon_solver` in G3.8.

## 6. Preregistered evaluation count

The complete 10x10 finite-difference schedule contains:

- one nominal baseline evaluation;
- `10 directions x 3 step levels x 2 signs = 60` nominal perturbation evaluations;
- `10 directions x 2 signs = 20` refined-solver evaluations at `h3`.

Therefore

`N_BVP_evaluations = 1+60+20 = 81`.

This is a schedule count only. This document does not authorize execution of any of the 81 evaluations.

## 7. Mandatory branch locks

Every evaluation must verify all of the following before contributing to a Jacobian column:

- same `N_F`;
- same `m_layer`;
- same `n_N,n_S` satisfying `n_N-n_S=m_layer*N_F`;
- same topology and two-region cap handoff;
- same pole-regular Frobenius branch;
- same profile node class;
- no conical rescue mode;
- no replacement of `sigma_cap` by `Sigma_FT`;
- no change of the frozen ten-component boundary operator.

A branch-lock failure invalidates the affected Jacobian level and yields `BRANCH_OR_DOMAIN_INVALID`, not a numerical rank result.

## 8. Required output artifacts

A future evaluation bundle must contain at minimum:

1. baseline manifest with code/operator/config digests;
2. one manifest for each perturbation and refinement evaluation;
3. full ten-component `R_hat` vectors for every evaluation;
4. branch-lock flags and pole/node-class diagnostics;
5. `J_hat_h1`, `J_hat_h2`, `J_hat_h3`;
6. `J_hat_h3_refined`;
7. `epsilon_step`, `epsilon_solver`, `epsilon_J`;
8. full singular spectra and `kappa_2` at all derivative levels;
9. smallest right-singular directions and inter-level angles;
10. normalized 8+2 block decomposition and Schur diagnostic when `J8_hat` is nonsingular;
11. machine-readable final G3.8 rank-certification verdict;
12. immutable statement that `rank(R)` has not been evaluated by this BVP-Jacobian program.

## 9. Abort and verdict classes

Before rank adjudication, classify failures as follows:

- `BVP_EVALUATION_FAILED`: a required baseline/perturbation/refinement solve fails or returns nonfinite data;
- `BRANCH_OR_DOMAIN_INVALID`: fixed discrete/topological/pole/node-class contract not preserved;
- `DERIVATIVE_PLATEAU_FAILED`: G3.8 derivative convergence criterion fails;
- `SOLVER_REFINEMENT_FAILED`: refined `h3` comparison unavailable or incompatible;
- `CONDITIONING_GUARDRAIL_FAILED`: `kappa_2(J_hat)>1e6`;
- `SIGMA10_DIRECTION_UNSTABLE`: smallest right-singular direction changes by more than 10 degrees between accepted levels;
- `RANK10_UNCERTAINTY_NOT_SEPARATED`: `sigma_10<=5*epsilon_J`;
- `RANK10_CERTIFIED_NUMERICALLY`: all G3.8 numerical certification conditions pass.

The last label is only a local functional-BVP Jacobian statement. It is not physical response-rank evidence and does not release K1-D or K1-E.

## 10. Relation to G3.8 thresholds

The preregistered numerical guardrails are inherited from the existing ULSH-01 numerical-method contract:

- derivative relative-change maximum: `1e-2`;
- uncertainty separation factor: `q=5`;
- condition-number maximum: `1e6`;
- smallest-direction angle maximum: `10 deg`;
- formal relative singular-value threshold for reporting only: `1e-8*sigma_1`.

The robust rank verdict remains controlled by `sigma_10>5*epsilon_J`, not by the formal SVD threshold alone.

## 11. Execution firewall

This preregistration freezes how a later 81-evaluation program must be run if separately authorized.

It does not itself authorize:

- a physical nonlinear Background3C5 solve;
- the 81-evaluation BVP-Jacobian campaign;
- any 41-job observable-response campaign;
- `rank(R)` evaluation;
- K1-D release;
- K1-E admissibility;
- stability or ghost-freedom claims.

## 12. Verdict

`G3_9_FUNCTIONAL_JACOBIAN_PLAN = PREREGISTERED`

`G3_9_STEP_LEVELS = [1e-2,5e-3,2.5e-3]`

`G3_9_SOLVER_TOLERANCES = [1e-8,1e-10]`

`G3_9_NOMINAL_PERTURBATION_EVALUATIONS = 60`

`G3_9_REFINED_H3_EVALUATIONS = 20`

`G3_9_TOTAL_BVP_EVALUATIONS = 81`

`G3_9_ONE_SIDED_FALLBACK = FORBIDDEN`

`G3_9_BRANCH_LOCK = MANDATORY`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN_NOT_EVALUATED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence claim follows from this preregistration.
