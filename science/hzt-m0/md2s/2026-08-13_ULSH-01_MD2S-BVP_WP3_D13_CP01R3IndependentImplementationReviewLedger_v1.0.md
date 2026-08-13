# ULSH-01 / MD2S-BVP — WP3-D13 CP01R3 Independent Implementation Review Ledger v1.0

Date: 2026-08-13  
Architecture: HPVS → HZT-M0 → HZT-Full  
Scope: independent source/control review only; no physical backend import or evaluation

## 1. Disposition

**PASS_D13_INDEPENDENT_IMPLEMENTATION_REVIEW_D14_BINDING_ALLOWED_NO_PHYSICAL_EXECUTION**

D13 independently reviews the D12 BJP-01 / ETRN-02 implementation and persistent manufactured-control audit. It does not call the D12 physical-denial path as a substitute for scientific testing and does not import any MD2S physical backend.

The review finds no implementation blocker to a separately versioned D14 exact binding/freeze block. This is not physical authorization.

## 2. Reviewed source identity

- implementation: `tools/2026-08-13_ulsh_01_md2s_bvp_wp3_d12_cp01r3_bjp01_etrn02_v1.0.py`
- implementation Git blob SHA-1: `d6313721a459254b13bdc9e06b4b83fc5a0fcca9`
- seed specification SHA-256: `05315df34903188284b4ea58bffc6b440a06bda9486362a6760c7cc0cfcb1474`
- D12 merge commit: `8228446464c13e55f83f98bce0f964f9af5cdc37`
- D12 measured audit source: `registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3ManufacturedControlAudit_v1.0.json`

## 3. Independent BJP-01 review

The independent reference derivation starts from the frozen pair

`R_4D = -3 A_sum - ell_sum + lambda_hat + 0.5 Y_sigma`

`R_chi = -4 A_sum + lambda_hat - 0.5 Y_sigma`.

Solving the pair for fixed `Y_sigma` gives

`A_sum* = (lambda_hat - 0.5 Y_sigma)/4`

and

`ell_sum* = -3 A_sum* + lambda_hat + 0.5 Y_sigma`.

Substitution independently returns both residuals to zero for the review cases.

For the derivative-only basis `delta u=c(tau-1)`, the physical value deformation `tau delta u` vanishes at both `tau=0` and `tau=1`, while the derivative at the brane remains available to change the junction derivative sums. This is consistent with the D11 design claim.

## 4. Independent state-metric review

D13 reimplements the registered mesh-normalization control without importing the D12 module. For the same Chebyshev-Lobatto samples and smooth control perturbation, the independent reference reproduces the D12 relative spread

`0.004915480656330283`

within floating-point tolerance, below the frozen `0.006` control limit.

This is a finite manufactured-control result only. It does not prove exact mesh invariance for arbitrary functions.

## 5. Static ETRN-02 semantics review

AST/source review confirms:

- row/column equilibration is used to recover an original-variable direction `dx_unclipped`;
- trust clipping consumes that original-variable direction and a frozen `StageMetric`;
- the equilibrated `linear_coordinate` is not used as the trust distance;
- the `StageMetric` is frozen once before the outer iteration loop;
- there is no inner backtracking-factor loop in ETRN-02;
- rejected trials shrink the radius and consume an outer iteration;
- the current generic implementation calls `jacobian_fn(state)` twice per outer iteration: once to build the direction and once again for the model-reduction ratio.

The double Jacobian call is not a D12 correctness failure. It is, however, a physical resource-accounting and source-identity constraint. D14 must either preserve it exactly or stop and require a new versioned implementation plus manufactured controls.

## 6. Source-isolation review

The D12 implementation imports NumPy but not SciPy, importlib-based physical kernels, subprocess execution infrastructure, or the MD2S physical backend. No physical run-input or single-use grant implementation is present.

D13 therefore confirms that D12 remains a manufactured-control component, not a physical solver entry point.

## 7. Review of D12 measurement scope

The D12 results remain correctly classified:

- BJP-01 exact algebra: PASS, error 0;
- endpoint invariants: PASS, drift 0;
- mesh metric: PASS within the finite registered control tolerance;
- preconditioner/trust decoupling: PASS on a synthetic reparameterization;
- stiff known-root system: PASS in three iterations with root error about `9.15e-9`;
- fail-closed controls: 3/3.

The stiff problem is linear and manufactured. It does not validate nonlinear MD2S basin geometry.

## 8. D14 binding requirements

D14 may freeze the exact CP01R3 run input, generated seed vectors and source bundle only if it preserves the reviewed implementation semantics. In particular:

1. stage metric frozen once per mesh/seed stage;
2. no hidden inner backtracking loop;
3. double-Jacobian-call behavior included in resource accounting unless a new implementation version is created;
4. physical parameters, topology, equations, boundary equations and acceptance thresholds unchanged;
5. generated BJP-01 physical seed vectors receive their own deterministic manifest/hash;
6. no physical solve or release authorization in D14.

## 9. Governance

- WP3: `OPEN_D13_REVIEW_PASS_D14_EXACT_BINDING_FREEZE_ALLOWED_NO_SOLVE`
- WP4: `BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`
- ULSH-02: blocked pending ULSH-01 release gate
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

## 10. Next allowed block

`ULSH-01_WP3_D14_CP01R3_EXACT_RUN_INPUT_GENERATED_SEED_AND_SOURCE_BUNDLE_FREEZE_NO_SOLVE`

D13 itself creates no grant and performs no physical computation.
