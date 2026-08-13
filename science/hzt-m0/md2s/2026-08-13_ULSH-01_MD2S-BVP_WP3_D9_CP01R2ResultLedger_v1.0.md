# ULSH-01 / MD2S-BVP — WP3-D9 CP01R2 Post-Execution Result Ledger v1.0

Date: 2026-08-13  
Architecture: HPVS → HZT-M0 → HZT-Full  
Active solver: ULSH-01 / MD2S-BVP  
Review type: independent post-execution artifact review; no rerun, no replay, no solver import

## 1. Review disposition

**PASS_TRANSACTION_COMPLETE_NEGATIVE_NUMERICAL_OUTCOME_NO_CANDIDATE_UNDER_PREREGISTERED_CP01R2_PROTOCOL**

The D8 transaction itself completed successfully and committed an immutable result package. This operational `SUCCEEDED` state must not be confused with numerical candidate acceptance. The scientific/numerical result is:

`NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL`

No accepted physical background is established.

## 2. Exact execution binding

- main commit: `e718cff2613a00810f9edb6183e5fccd413370f9`
- workflow run: `31595841858`, attempt 1
- job: `94111018415`
- run ID: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`
- authorization decision: `UL-DEC-CP01R2-D8-31595841858-1`
- D7 governance decision: `ULSH-01-WP3-D7-CP01R2-FRESH-RELEASE-DEC-20260812-A`
- grant nonce: `2f466fb5a41d432290d978b647c3386c`
- grant SHA-256: `4bb2e6eb5d3ec3e4192ba7bbc728773b8f49101504c8bcbfbdff0368f0adf3a8`
- release authorization SHA-256: `a2d9a217f2fd93c308ae3bea15436aac2b67a8e526a5785fa5d1baaf070fbbde`
- grant spent: yes
- replay permitted: no

## 3. Preserved artifact binding

- artifact ID: `9141488748`
- artifact: `ULSH-01-CP01R2-D8-physical-transaction-31595841858-attempt-1`
- artifact size: 1,782,594 bytes
- artifact ZIP SHA-256: `57548e8352b128a084d356b0f61ac1055092bcd831c2752e0ad542c56293268e`
- result SHA-256: `08afdedfea172209ef03228dd3313e07cdce54b9a1491b29a10ef54315c544d1`
- artifact-manifest SHA-256: `c35ad437d58c32a39ff49112b9572a66cc2c56f1282acd7797bc7fb0e0c876ea`
- result-commit-marker SHA-256: `1ac40f0e1d908e6aa82c49531d216e4a82b71fdb48fe3c2a3b034f0226294d25`
- checkpoint-chain head SHA-256: `8456bed7680f4e8c26ac647e736edaf0ae4991a41884a263543199236b04e3eb`
- artifact retention expiry: 2026-11-10T12:18:55Z

The artifact contained all 35 per-entry write-ahead checkpoints. Finalization inputs were rebuilt from the durable checkpoint chain before the immutable result package was committed.

## 4. Execution summary

- planned entries: 35
- completed entries: 35
- durable checkpoints: 35
- stage timeouts: 0
- elapsed wall time: 892.9924008579999 s
- candidate count: 0
- independent-backend candidate comparisons: 0
- higher-precision candidate audits: 0

Failure inventory over the 35 schedule entries:

- `STAGNATION`: 24
- `MAXIMUM_ITERATIONS`: 11

By node count:

- N=24: 5 maximum-iterations, 2 stagnation
- N=32: 6 maximum-iterations, 1 stagnation
- N=48: 7 stagnation
- N=64: 7 stagnation
- N=96: 7 stagnation

## 5. N=96 result

Every preregistered seed reached its N=96 entry. None produced a qualifying local root.

For the seven N=96 terminal states:

- local-root count: 0 / 7
- terminal failure: `STAGNATION` for all 7
- final residual infinity norm: 1.626590093183676 … 1.6282890439830813
- bulk residual maximum: 0.019493820841228377 … 0.39529287767052723
- rr-constraint maximum: 2.7872840840936774e-10 … 0.16058714454710754
- dominant boundary residual: `R_4D` for all 7
- |R_4D|: 1.626590093183676 … 1.6282890439830813
- |R_gauge|: 0.816084998375896 … 0.8577026061875156
- |R_chi|: 0.3694436119414338 … 0.3717076262734026
- discrete diagnostic rank: 776 / 776 for all 7
- reported discrete condition estimate: 5.336436430394959e10 … 1.7893482038957547e11
- N=96 condition estimates above 1e12: 0

The preregistered acceptance limits remain:

- boundary residual maximum ≤ 1e-10
- bulk residual maximum ≤ 1e-10
- rr constraint maximum ≤ 1e-9

The boundary and bulk channels therefore remain many orders of magnitude outside the required acceptance region. Seed 0 reaches the rr-constraint threshold at N=96, but still fails the simultaneously required boundary, bulk, local-root, fine-pair, spectral-tail and independent-backend gates.

## 6. Diagnostic comparison with CP01R1

This comparison is diagnostic only. It is not a cross-protocol acceptance test.

The CP01R1 result review recorded N=96 condition estimates up to approximately 3.55e13 and discrete rank-deficiency observations. CP01R2 instead reports full diagnostic rank 776/776 for all seven N=96 states and condition estimates below 1e12.

Nevertheless, all seven CP01R2 N=96 stages still terminate by stagnation without a local root, and the O(1) `R_4D` boundary mismatch persists.

Therefore the negative CP01R2 outcome cannot be explained solely by the discrete rank-deficiency observations that appeared in CP01R1. This narrows the next diagnosis toward the target/boundary residual structure, local basin geometry, scaling and method/target compatibility, while still forbidding any continuum-nonexistence inference.

## 7. What is established

1. The exact frozen CP01R2 v2 transaction executed once under the fresh single-use grant.
2. The complete 35-entry schedule survived as a durable checkpoint chain.
3. The transaction committed an immutable result package and completed without stage timeout.
4. No preregistered seed produced a qualifying N=96 local root.
5. The CP01R2 candidate-existence result is negative for this exact parameter point, seed set, mesh schedule and frozen method.
6. `R_4D` remains the dominant fine-mesh obstruction despite improved discrete rank/conditioning diagnostics.

## 8. What is not established

This result does **not** establish:

- continuum nonexistence of an M1 background solution;
- nonexistence outside the preregistered seed basins or numerical method;
- uniqueness or nonuniqueness;
- Fredholm properties;
- continuum BVP-Jacobian invertibility;
- perturbative stability;
- ghost freedom;
- K1-D release;
- K1-E admissibility;
- confirmation or falsification of HZT-M0.

## 9. Governance consequence

- WP3: `NOT_CLOSED_NO_CANDIDATE_AVAILABLE_FOR_REQUIRED_CONVERGENCE_AND_INDEPENDENT_BACKEND_GATES`
- WP4: `BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`
- ULSH-02: blocked pending ULSH-01 release gate
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

## 10. Next allowed block

`ULSH-01_WP3_D10_CP01R2_FAILURE_MODE_DIAGNOSIS_NO_EXECUTION`

D10 may inspect the preserved result, checkpoint histories, residual component structure, trust/rho histories, scaling and target equations. It may design hypotheses and manufactured/no-execution tests.

D10 may **not** rerun CP01R2, replay the spent grant, relax acceptance thresholds, add seeds, mutate parameters/topology, advance to WP4/ULSH-02, or promote full discrete rank to continuum invertibility.
