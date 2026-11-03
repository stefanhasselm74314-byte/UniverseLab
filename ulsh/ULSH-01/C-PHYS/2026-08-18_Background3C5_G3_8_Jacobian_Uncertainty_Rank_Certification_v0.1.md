# ULSH-01 / C-PHYS — Background3C5 G3.8 Jacobian Uncertainty & Rank Certification v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** UNCERTAINTY_MODEL_DEFINED / RANK_CERTIFICATION_CONTRACT_FROZEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This block continues G3.6/G3.7. It defines how a future dimensionless functional boundary Jacobian

`Jhat = D_R^(-1) J10 D_U`

may be assigned a numerical uncertainty and how a rank-10 statement may be certified without confusing small singular values, finite-difference error, solver error, conditioning or branch drift.

No nonlinear physical BVP is executed here.

## 2. Inherited ULSH-01 numerical guardrails

The existing physical response-rank auditor v1.3 already freezes the following ULSH-01 numerical guardrails:

- uncertainty separation factor `q = 5`;
- condition-number guardrail `kappa_max = 1e6`;
- relative derivative-refinement tolerance `delta_rel_max = 1e-2`;
- weakest-singular-direction angle tolerance `theta_max = 10 deg`;
- formal relative SVD threshold `tau_formal = 1e-8`.

G3.8 inherits these as a project-internal numerical method standard. They are not physical constants and do not constitute evidence for rank 10.

## 3. Required Jacobian sequence

On one fixed discrete branch

`(N_F,m_layer,n_N,n_S)` with `n_N-n_S=m_layer*N_F`, evaluate the canonical dimensionless Jacobian at derivative step levels

`Jhat_h`, `Jhat_h2`, `Jhat_h4`,

where `h2=h/2`, `h4=h/4`.

A solver-refined Jacobian at the finest derivative level is additionally required:

`Jhat_h4_ref`.

Automatic differentiation may be used as the primary derivative backend only if an independent finite-difference refinement sequence remains available as a cross-check.

No comparison is admissible if the discrete branch, parent operator, normalization maps, cap contract or solver acceptance class changes between these matrices.

## 4. Empirical Jacobian uncertainty

Define the step-refinement uncertainty

`epsilon_step = ||Jhat_h2 - Jhat_h4||_2`.

Define the solver-refinement uncertainty

`epsilon_solver = ||Jhat_h4 - Jhat_h4_ref||_2`.

The conservative empirical uncertainty is

`epsilon_J = epsilon_step + epsilon_solver`.

This is the same additive uncertainty architecture already used by the ULSH-01 physical response-rank auditor.

The derivative-refinement relative change is

`delta_rel = epsilon_step / max(1, ||Jhat_h4||_2)`.

The derivative plateau gate requires

`delta_rel <= 1e-2`.

For diagnostic purposes define

`d1 = ||Jhat_h - Jhat_h2||_2`,

`d2 = ||Jhat_h2 - Jhat_h4||_2`,

`r_R = d1/d2`

when `d2>0`. For a clean second-order central-difference regime one expects `r_R -> 4`; however G3.8 does not require equality to 4 because nonlinear solver contamination and nonasymptotic steps can alter the observed ratio. The hard plateau criterion remains the frozen relative-change gate.

## 5. Weyl bound and rank separation

Let the singular values of `Jhat_h4` be

`sigma_1 >= ... >= sigma_10 >= 0`.

For any perturbation `Delta J`, Weyl's singular-value perturbation bound gives

`|sigma_i(Jhat_h4 + Delta J) - sigma_i(Jhat_h4)| <= ||Delta J||_2`.

Therefore `epsilon_J` is the natural operator-norm uncertainty scale for singular-value separation.

A rank-10 certification requires the weakest singular value to satisfy

`sigma_10 > q * epsilon_J`

with the inherited value

`q = 5`.

Thus the uncertainty separation metric is

`S10 = sigma_10/epsilon_J`

and the certification gate requires

`S10 > 5`.

If `epsilon_J=0` in an exact/synthetic algebra test, `S10=+infinity` only when `sigma_10>0`; this special case does not authorize physical execution.

## 6. Formal rank versus certified rank

For reporting only, define

`tau_formal = 1e-8 * sigma_1`

and

`rank_formal = #{i : sigma_i > tau_formal}`.

This formal SVD rank is not sufficient for certification.

A matrix can satisfy `rank_formal=10` while `sigma_10 <= 5 epsilon_J`; in that case the verdict is

`NUMERICAL_RESOLUTION_INSUFFICIENT`.

Conversely, a robust rank-deficiency claim requires a converged/branch-stable sequence for which the weakest direction remains unresolved or tends toward zero under refinement. A single small singular value is not by itself evidence for a physical null mode.

## 7. Conditioning firewall

Define

`kappa_2(Jhat_h4) = sigma_1/sigma_10`

when `sigma_10>0`.

The inherited guardrail is

`kappa_2 <= 1e6`.

Failure of this guardrail does not mathematically prove rank deficiency; it classifies the numerical rank verdict as insufficiently conditioned.

Optional equilibrated matrices from G3.7 may be reported as conditioning diagnostics but may not replace `Jhat_h4` in the canonical rank-certification gate.

## 8. Weakest-direction stability

Let `v10_h2` and `v10_h4` be normalized right singular vectors associated with the weakest singular value at the two finest derivative levels.

Because singular vectors are sign-indeterminate, define

`theta = arccos(|v10_h2 dot v10_h4|)`.

The inherited direction-stability guardrail is

`theta <= 10 deg`.

If the weakest singular value is clustered/degenerate with its neighbors, a one-vector angle can become ill-defined; in that case the implementation must compare the corresponding singular subspaces and must not force a scalar-angle PASS.

## 9. Rank-10 certification state machine

A future functional-Jacobian audit may return `RANK10_CERTIFIED_NUMERICALLY` only if all of the following hold simultaneously:

1. exact same parent/boundary operator and fixed discrete branch at every refinement level;
2. solver-refined finest Jacobian is present;
3. `delta_rel <= 1e-2`;
4. `rank_formal = 10`;
5. `sigma_10 > 5 epsilon_J`;
6. `kappa_2(Jhat_h4) <= 1e6`;
7. weakest singular direction/subspace is stable under refinement;
8. all background-solution acceptance and rr-constraint QA gates pass independently.

If the derivative/solver uncertainty is too large, conditioning is excessive, or direction stability fails, verdict:

`NUMERICAL_RESOLUTION_INSUFFICIENT`.

If a converged branch-stable calculation robustly exhibits a null direction, verdict may be

`RANK_DEFICIENT_CANDIDATE_REQUIRES_PHYSICAL_INTERPRETATION`,

not automatic falsification of the parent model.

## 10. Separation from the physical response-rank gate

`rank(J10)=10` concerns local invertibility of the augmented nonlinear BVP boundary map.

`rank(R)=4` in the existing ULSH-01 response program concerns the physical observable response to model-control variations.

These are distinct Jacobians and distinct scientific claims.

Therefore

`BVP_JACOBIAN_RANK10 != PHYSICAL_RESPONSE_RANK4`.

A rank-10 BVP certification does not establish response rank 4, phenomenological success, stability or ghost freedom.

## 11. Status

`G3_8_EPSILON_STEP = ||Jhat_h2-Jhat_h4||_2`

`G3_8_EPSILON_SOLVER = ||Jhat_h4-Jhat_h4_ref||_2`

`G3_8_EPSILON_J = epsilon_step+epsilon_solver`

`G3_8_Q = 5`

`G3_8_DERIV_REL_MAX = 1e-2`

`G3_8_CONDITION_MAX = 1e6`

`G3_8_DIRECTION_MAX_DEG = 10`

`G3_8_FORMAL_REL_TOL = 1e-8`

`G3_8_RANK10_CERTIFICATION = DEFINED_NOT_EXECUTED`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN_NOT_EVALUATED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence claim follows from this contract.
