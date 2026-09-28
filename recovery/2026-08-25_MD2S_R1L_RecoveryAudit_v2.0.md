# MD2S-R1-L Recovery Audit v2.0

**Date:** 2026-08-25  
**Status:** `PARTIALLY_UNBLOCKED_PRIMARY_FGKL_RECOVERED_BUT_SOURCE_IDENTICAL_TWO_JUNCTION_REPLAY_STILL_BLOCKED`  
**Scope:** forensic provenance and numerical reproducibility only. No physical release, solver authorization, K1-D, or K1-E effect.

## 1. Executive result

The August 18 recovery ZIP is now directly available and has been independently checked. In parallel, a newer recovery state in the current File Library shows that the original B1.4F/G/K/L package binaries were recovered, CRC-tested, and their internal SHA-256 manifests validated.

This supersedes the older bounded statement that B1.4K/B1.4L were only unverified historical chat reports.

The correct current hierarchy is:

1. **Recovery bundle:** exact bytes available and internally verified.
2. **Historical transcript:** B1.4K/B1.4L message-level reports are recovered in the official export.
3. **Primary package layer:** original B1.4K/B1.4L package binaries are recovered with valid manifests.
4. **Selected numerical reproduction:** package-level K/L numerical claims have been independently recomputed within declared tolerances.
5. **Source-identical historical two-junction replay:** still blocked because the required two-sided interface and run-bound source/configuration data remain missing.

## 2. August 18 recovery bundle — direct byte audit

File:

`MD2S_Randdaten_Benchmark_RECOVERY_2026-08-18.zip`

Verified properties:

- size: **14,884 bytes**;
- SHA-256: `dbee345414409f29f6fee5cc161807fd3f8a2d4b337460d3cf9bb8a307c3dff9`;
- ZIP entries: **12**;
- archive integrity: **PASS**;
- internal manifest entries: **11**;
- manifest hashes valid: **11/11**;
- manifest hashes invalid: **0**.

The ZIP contains the recovered B1.4K and B1.4L visible assistant reports, A0 benchmark data, the SCI-001/002 v0.4 RunSpec, two-junction definitions, missing-data register, recovery ledger, state file, and internal manifest.

This classifies the bundle as `E9_RECOVERY_BUNDLE_BYTES_VERIFIED`.

## 3. Provenance correction: recovery chat versus source chat

The August 18 account/archive workflow was performed in `Kontoanalyse ChatGPT`.

The recovered B1.4K and B1.4L result reports themselves identify the historical source chat as:

`Hyperzeit Projektstatus Update`

The official export currently surfaced in the File Library contains the message-level package references for both phases. Therefore the source relationship is now:

`Hyperzeit Projektstatus Update` -> historical B1.4K/B1.4L reports and generated package links

`Kontoanalyse ChatGPT` -> later forensic search/recovery workflow

No private conversation or message identifiers are copied into this public repository.

## 4. Primary package recovery — critical upgrade

The current external recovery state `md2s_r1l_scope_and_status_v5.json` and `primary_package_inventory_v5.csv` report the following original binaries as recovered with CRC and manifest validation:

### B1.4K

`HZT_MD2S_B1_4K_RESOLVED_LOCALIZER_BVP_v0_1_PACKAGE.zip`

- SHA-256: `9cf13cd51baaef94258fcfa1690036798977565482acf2709a69494b0ed6e648`
- size: 2,391,636 bytes
- ZIP payload files: 12
- internal manifest: 11 entries
- valid manifest hashes: 11
- invalid hashes: 0
- provenance class: `quarantined_non_evidential_resolved_localizer_BVP_preflight`

### B1.4L

`HZT_MD2S_B1_4L_OFFSHELL_BACKREACTION_AUDIT_v0_1_PACKAGE.zip`

- SHA-256: `d5faf820ca984b40a78bb643aec23885aae8f753733054fc65eff0a6366eca0b`
- size: 1,890,136 bytes
- ZIP payload files: 13
- internal manifest: 12 entries
- valid manifest hashes: 12
- invalid hashes: 0
- provenance class: `quarantined_non_evidential_offshell_backreaction_identifiability_audit`

The same recovery state also reports B1.4F and B1.4G primary packages recovered and manifest-valid. This closes the former F/G/K/L package-binary gap, but does not close the entire MD2S-R1-L historical replay.

## 5. Numerical reproduction upgrade

The current `primary_numeric_reproduction_v5.csv` records selected independent recomputations from recovered primary data.

### B1.4K

Verified package-level checks include:

- integrated gradient contribution;
- extra A5-prime drop;
- integrated layer energy;
- cap potential value;
- effective `kappa_R` cross-package reconstruction;
- Robin boundary residual reconstructed from the serialized primary profile.

The earlier discrepancy obtained from the rounded secondary recovery CSV (~`7e-12`) is therefore resolved. Using the serialized primary profile gives approximately `-6.25e-16` against the archived `-6.94e-17`, well within the declared `1e-12` absolute tolerance. The remaining difference is consistent with decimal serialization precision.

### B1.4L

Verified package-level checks include:

- weighted total/tangent/normal source integrals;
- weighted RMS quantities;
- normal RMS fraction;
- rank-two cap response matrix;
- both reported cap-response singular values.

These checks justify `E12_PRIMARY_NUMERIC_REPRODUCTION_PASS` only for the specific reproduced package claims.

## 6. What remains blocked

The following are still not recovered at source-identical historical replay level:

- source-identical 6D action/potential/coupling set including prerequisite B1.4E/H inputs or equivalent source-bound definitions;
- `A_prime_bulk`;
- `A_prime_cap`;
- `Lprime_over_L_bulk`;
- `Lprime_over_L_cap`;
- historically bound oriented normals;
- full-precision two-sided interface/profile derivative tables;
- original two-junction solver residual logs;
- complete generation solver tolerances/configuration for all prerequisite runs.

Therefore:

`SOURCE_IDENTICAL_HISTORICAL_TWO_JUNCTION_REPLAY = STILL_BLOCKED`

The August 7 SCI forensic verdict remains applicable to that narrower question: one-sided/current package recovery cannot be silently promoted into the missing source-identical two-sided historical junction transaction.

## 7. Supersession map

### Superseded

- B1.4K/B1.4L = only `E4_UNVERIFIED_HISTORICAL_CHAT_REPORT`.
- "actual recovery ZIP bytes not exposed" from the earlier scoped extraction attempt.
- "original B1.4F/G/K/L binaries not recovered" from pre-v5 recovery rounds.
- the secondary-text claim that the B1.4K Robin residual cannot be reproduced beyond ~`1e-12` from available data.

### Still valid

- A0 remains a surviving reported benchmark/regression target, not a recovered full historical solver transaction.
- SCI-001/002 v0.4 RunSpec remains `NOT_EXECUTED`.
- C1/rebuild outputs must not substitute for historical missing fields.
- exact source-identical two-junction replay remains blocked.
- physical/scientific release gates remain unchanged.

## 8. Evidence firewall

Primary package recovery and numerical reproduction establish technical historical provenance for the directly supported package claims. They do **not** establish:

- an authorized official MD2S physical solver;
- a physical background;
- full ghost freedom;
- K1-D release;
- K1-E admissibility;
- empirical evidence;
- retrospective proof of the entire MD2S-R1-L legacy chain.

## 9. Governance state

Unchanged:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
