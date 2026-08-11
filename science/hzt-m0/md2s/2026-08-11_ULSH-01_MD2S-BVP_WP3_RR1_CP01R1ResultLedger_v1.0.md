# ULSH-01 / MD2S-BVP — WP3-RR1 CP01R1 Result Ledger v1.0

Date: 2026-08-11  
Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`  
GitHub Actions: `31495350499`, attempt 1  
Reviewed source commit: `63af440955431f8a1315ec29271887c5ae2d442b`

## Canonical result

The first exact physical CP01R1 transaction completed successfully as a transaction. All 35 frozen primary entries were executed, no per-entry timeout occurred, the total wall-clock budget was not exhausted, the single-use grant was spent exactly once, replay is forbidden, and the immutable result package was committed and preserved.

The numerical/scientific outcome is nevertheless negative under the preregistered protocol:

`NO_CANDIDATE_FOUND_UNDER_PREREGISTERED_PROTOCOL`

This is not an implementation failure. It means that no one of the seven preregistered seed paths produced a qualifying N=96 local root, so the later fine-mesh, spectral-tail, independent-backend and >=80-bit acceptance stages had no candidate to evaluate.

## Immutable bindings

- Actions artifact ID: `9104240692`
- Artifact SHA-256: `ddbec713207748bcdedc50486624effa14924a92beb476a746641f314f9843e8`
- Result SHA-256: `8562ba77cb0aeda87aceee3b7be301c06e948070beebc8916769c38d99b45ec8`
- Artifact-manifest SHA-256: `f85a077a9327708f194596a0873b608c404a8c81a2b72c08df3a11b9608c3e07`
- Authorization decision: `UL-DEC-CP01R1-31495350499-1`
- Grant SHA-256: `764cb65f12071ad756fdbe5112f4b9fb1556830a1ef1801309311c29b47bd0da`
- Release SHA-256: `ce3dc84134198867f08804cc56063f12c2cc67189ec643fe1f2c54166ee8e9fa`
- Grant state: `SUCCEEDED`, spent, non-replayable.

## Numerical failure inventory

Across the 35 scheduled entries the terminal solver classifications were:

- `MAXIMUM_ITERATIONS`: 30
- `TRUST_RADIUS_BELOW_MINIMUM`: 4
- `RRQR_RANK_DEFICIENT`: 1

The target execution took 2569.4414 s. No stage timeout occurred and the total transaction budget was not exhausted.

At N=96 all seven seeds failed the local-root gate. The final infinity-norm residuals were:

| seed | terminal failure | final residual_inf | bulk max | rr constraint max | dominant boundary residual | discrete condition |
|---:|---|---:|---:|---:|---|---:|
| 0 | MAXIMUM_ITERATIONS | 1.2537618785 | 0.1526916378 | 0.0973980303 | R_4D | 1.5368853067e11 |
| 1 | MAXIMUM_ITERATIONS | 1.1252699553 | 0.2542841216 | 0.1924357995 | R_4D | 8.1963245749e10 |
| 2 | RRQR_RANK_DEFICIENT | 1.4088734070 | 0.0856521146 | 0.0372048953 | R_4D | 3.5491772430e13 |
| 3 | MAXIMUM_ITERATIONS | 1.2196901019 | 0.2021190972 | 0.1654672800 | R_4D | 1.7896801453e11 |
| 4 | MAXIMUM_ITERATIONS | 1.1712682816 | 0.1721159425 | 0.0832174572 | R_4D | 3.4113088084e11 |
| 5 | MAXIMUM_ITERATIONS | 1.2932758323 | 0.2220127064 | 0.1858197368 | R_4D | 2.8644213665e11 |
| 6 | TRUST_RADIUS_BELOW_MINIMUM | 1.3847841182 | 0.3117277527 | 0.1241686789 | R_4D | 5.3224241649e12 |

The preregistered limits were `1e-10` for both boundary and bulk residuals and `1e-9` for the propagated rr constraint. The observed N=96 state is therefore not a near miss: the residuals remain many orders of magnitude above the acceptance thresholds.

Three final discrete diagnostics were one rank below the square dimension: E15/S2/N96 = 775/776, E19/S3/N64 = 519/520, and E35/S6/N96 = 775/776. Only E15 terminated explicitly as `RRQR_RANK_DEFICIENT`; the other two terminated through trust-region stagnation. These are discrete numerical diagnostics only and are not a continuum rank theorem.

## Interpretation firewall

What is established: the exact frozen CP01R1 experiment ran, and the proposition “one of the seven preregistered seeds reaches an accepted N=96 numerical background under this exact protocol” received a negative result.

What is not established: continuum nonexistence, uniqueness/nonuniqueness, Fredholmness, continuum Jacobian invertibility, perturbative stability, ghost freedom, physical identification, or observational falsification of HZT-M0.

The strongest diagnostic signal is the persistent O(1) `R_4D` boundary mismatch at N=96 for every seed, with substantial bulk and rr residuals remaining as well. This can indicate a boundary/parameter-sector obstruction, an initialization/basin problem, solver scaling/stagnation, or a combination. CP01R1 alone does not distinguish these hypotheses.

## Governance decision

`WP3 = NOT_CLOSED_NO_CANDIDATE_AVAILABLE_FOR_REQUIRED_CROSSCHECK_AND_CONVERGENCE_GATES`

`WP4 = BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`

`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`physical_evidence_effect = NONE`

The spent grant must never be replayed. The next allowed action is `ULSH-01 / WP3-D1`: a no-execution failure-mode diagnosis followed by a separately preregistered CP01R2 protocol only if the diagnosis justifies another physical run. Any changed seed set, solver policy, parameter sector or continuation strategy is a new protocol and must not be relabeled CP01R1.
