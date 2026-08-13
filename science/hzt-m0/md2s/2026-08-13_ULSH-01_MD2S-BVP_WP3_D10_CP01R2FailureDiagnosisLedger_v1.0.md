# ULSH-01 / MD2S-BVP — WP3-D10 CP01R2 Failure-Mode Diagnosis Ledger v1.0

Date: 2026-08-13  
Architecture: HPVS → HZT-M0 → HZT-Full  
Scope: post-result diagnosis only; no solver execution, no backend import, no grant issuance, no replay

## 1. Input state

WP3-D9 froze the exact CP01R2 D8 outcome as a complete transaction with a negative numerical candidate result:

`NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL`

The preserved D8 artifact contains 35/35 durable write-ahead checkpoints. D10 reads the already preserved diagnostics and the frozen source equations only. It does not produce new physical numerical data.

## 2. Confirmed realized ETRN path

Across all 35 schedule entries:

- recorded ETRN iterations: 1785
- accepted iterations: 1785
- rejected iterations: 0
- entries using mesh continuation from a previous entry: 0
- entries initialized from `FRESH_FROZEN_CP01R1_SEED_SAME_INDEX`: 35
- entries reaching the frozen 10% progress-continuation criterion: 0
- best complete-stage relative residual improvement: 0.007993134821050813, at `CP01R2-E31-S6-N24`

The frozen continuation rule is `final <= 0.90 * initial`. The best observed complete-stage improvement is only about 0.7993%, so the intended progress-continuation mechanism never activates. This is a confirmed realized protocol path, not a protocol violation.

## 3. N=96 trust-region geometry

For the seven N=96 entries:

- ETRN iterations: 84
- accepted: 84
- rejected: 0
- all terminal failures: `STAGNATION`
- rho range: 0.9746469077294196 … 1.0117346904819102
- final trust radius: 64 for every seed
- unconstrained equilibrated step norm: about 1.893e8 … 4.624e8
- maximum frozen trust radius / unconstrained step norm: about 1.38e-7 … 3.38e-7
- relative terminal-state displacement from the frozen N=96 seed: about 1.064e-5 … 1.133e-5
- maximum single-component displacement: about 1.407e-5 … 1.509e-5

The local model-reduction ratio remains close to one and every trial is accepted, but the step is continuously trust-clipped by many orders of magnitude in the equilibrated coordinates. The accepted movement in original state space is consequently tiny before the 12-accepted-step stagnation rule fires.

This supports a **trust/scale geometry diagnosis**. It does not itself justify changing the trust radius, scaling, stagnation threshold, or method under the CP01R2 identity.

## 4. Exact combined junction identity

The frozen physical kernel defines

`R_4D = -3 A_sum - ell_sum + lambda_hat + 0.5 Y_sigma`

and

`R_chi = -4 A_sum + lambda_hat - 0.5 Y_sigma`.

Adding them eliminates the localized `Y_sigma` contribution exactly:

`R_4D + R_chi = -7 A_sum - ell_sum + 2 lambda_hat`.

For the frozen physical point `lambda_hat = 1`, simultaneous satisfaction of these two junction equations therefore requires the exact necessary condition

`7 A_sum + ell_sum = 2`.

The seven preserved N=96 terminal states instead give:

| seed | entry | R_4D | R_chi | R_4D + R_chi | 7 A_sum + ell_sum |
|---:|---|---:|---:|---:|---:|
| 0 | CP01R2-E05-S0-N96 | 1.6282890439830813 | 0.3717076262734026 | 1.999996670256484 | 3.3297435159272195e-06 |
| 1 | CP01R2-E10-S1-N96 | 1.6281832263056222 | 0.37156622454972055 | 1.9997494508553428 | 0.00025054914465729073 |
| 2 | CP01R2-E15-S2-N96 | 1.6281826627203042 | 0.3715660959341093 | 1.9997487586544134 | 0.00025124134558636663 |
| 3 | CP01R2-E20-S3-N96 | 1.6278651991287156 | 0.3711418757881625 | 1.9990070749168782 | 0.000992925083122063 |
| 4 | CP01R2-E25-S4-N96 | 1.627864070588854 | 0.3711416184889226 | 1.9990056890777765 | 0.0009943109222232032 |
| 5 | CP01R2-E30-S5-N96 | 1.6265923616634084 | 0.36944412717711894 | 1.9960364888405273 | 0.003963511159472731 |
| 6 | CP01R2-E35-S6-N96 | 1.626590093183676 | 0.3694436119414338 | 1.99603370512511 | 0.003966294874889976 |

Thus the terminal states remain extremely close to `7 A_sum + ell_sum ≈ 0` compared with the exact combined junction target `2`. Equivalently, the combined residual remains approximately 2.

This is the strongest current diagnostic obstruction: the frozen path does not move the seed family appreciably toward the combined junction manifold.

It is **not** a proof that the continuum BVP has no solution. A solution could exist outside the explored seed/method path.

## 5. Discrete rank is no longer the leading N=96 explanation

CP01R2 reports raw discrete diagnostic rank 776/776 for every N=96 terminal state and condition estimates approximately 5.34e10 … 1.79e11. Yet every N=96 stage stagnates with no local root.

The previous CP01R1 fine-grid rank-deficiency observations therefore cannot by themselves explain the CP01R2 result. This narrows the diagnosis, while preserving the firewall:

`full discrete rank != continuum BVP Jacobian invertibility`.

## 6. Ranked diagnosis

### D10-H1 — Boundary-manifold seed mismatch — STRONG DIAGNOSTIC

The frozen seed family begins near the analytic control geometry, while the physical brane junction combination at `lambda_hat=1` requires `7 A_sum + ell_sum = 2`. After the actual N=96 ETRN path, the observed combination is still only `3.3e-6 … 3.97e-3`.

### D10-H2 — Equilibrated trust-space step squeeze — STRONG NUMERICAL DIAGNOSTIC

All N=96 steps are accepted and rho is near one, yet the unconstrained equilibrated Newton step is millions of times larger than the frozen maximum trust radius. The resulting original-state movement is only O(1e-5) before stagnation.

### D10-H3 — Progress continuation never activated — CONFIRMED

No mesh level achieves the required 10% improvement, so no fine mesh is initialized from a coarser solved/progress state. Every stage restarts from the corresponding frozen seed.

### D10-H4 — N=96 discrete rank deficiency not primary explanation — CONFIRMED NARROWING

Full discrete rank and improved condition estimates coexist with persistent O(1) boundary residuals and no local root.

## 7. Interpretation firewall

D10 establishes a numerical-path diagnosis only. It does not establish:

- continuum nonexistence;
- uniqueness or nonuniqueness;
- Fredholm invertibility;
- continuum Jacobian rank;
- perturbative stability or ghost freedom;
- physical identification or observational falsification.

The physical parameter point is not altered in D10.

## 8. Governance

- WP3: `NOT_CLOSED_DIAGNOSIS_COMPLETE_NEW_PROTOCOL_REQUIRES_SEPARATE_DESIGN_REVIEW`
- WP4: `BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`
- ULSH-02: `BLOCKED_PENDING_ULSH-01_RELEASE_GATE`
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

## 9. Next allowed block

`ULSH-01_WP3_D11_BOUNDARY_AWARE_INITIALIZATION_AND_TRUST_SCALING_PROTOCOL_DESIGN_NO_EXECUTION`

D11 may design, but not execute, a new protocol. Any new seed construction requires a new seed-set identity and hash. Any altered nonlinear method, trust rule, scaling, or continuation rule requires a new run identity. CP01R1 and CP01R2 remain immutable negative numerical outcomes.
