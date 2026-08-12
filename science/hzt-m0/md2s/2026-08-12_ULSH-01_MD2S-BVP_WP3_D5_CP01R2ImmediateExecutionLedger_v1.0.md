# ULSH-01 / WP3-D5 — CP01R2 Immediate Single-Use Physical Transaction Ledger v1.0

Date: 2026-08-12  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Solver: `ULSH-01 / MD2S-BVP`  
Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`

## Purpose

WP3-D5 is the controlled transition from the positive D4 release decision to exactly one physical CP01R2 transaction. The repository trigger does not contain a pre-generated nonce or a long-lived grant. On the first `main` workflow attempt, the runtime issuer must freshly recheck D4, D3H1-RR1, the D3H1 contract, exact source blobs, payload, schedule and dependency lock before creating the runtime authorization and fresh grant.

## Frozen identity

- governance release decision: `ULSH-01-WP3-D4-CP01R2-RELEASE-DEC-20260812-A`
- `run_id = HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`
- `run_payload_sha256 = e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36`
- `schedule_sha256 = 929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b`
- `dependency_lock_sha256 = 4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f`
- schedule: seven frozen seeds × five frozen node levels = 35 planned entries
- execution holder: `GITHUB_ACTIONS_HOSTED_UBUNTU_24_04`
- reproducibility ticket: `ULSH-01-WP3-D5-CP01R2-GHA-20260812-A`

## Runtime issuance semantics

The issuer creates, in the ephemeral checked-out runtime workspace only:

- `registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_PhysicalSolveReleaseAuthorization_v1.0.json`
- `registry/2026-08-12_ULSH-01_MD2S-BVP_WP3_D3H1_CP01R2_SingleUseExecutionGrant_v1.0.json`

The fresh grant uses a 128-bit hexadecimal nonce derived from the unique first-attempt Actions identity plus the exact checked-out commit, issuance time, source-bundle digest and D4 decision. Its start-validity window is 3300 seconds, below the contractual 3600-second maximum. The transaction permanently spends the grant before physical target import/solve and forbids replay.

The runtime release and grant both bind to the exact D4 governance decision and to the same runtime `UL-DEC-CP01R2-...` authorization decision identifier. They also bind the frozen run payload, schedule, dependency lock, result schema, target, D3H1 transaction contract and source-bundle digest.

## Execution constraints

The workflow refuses any `GITHUB_RUN_ATTEMPT != 1` before issuance. It uses Python 3.12, installs the frozen dependency lock, fixes all OpenMP/BLAS thread environment variables to one, then calls the independently reviewed CP01R2 transaction supervisor exactly once.

No parallel execution, adaptive retry, scan, fallback method, random restart, adaptive mesh insertion, parameter/topology mutation, method change, threshold relaxation or grant replay is permitted. The independent backend remains mandatory after a qualifying primary candidate.

The transaction supervisor itself retains the D3H1 controls: immutable output collision guard, single-use spend, 1800-second per-entry limits, 21600-second total transaction limit, 8 GiB child address-space ceiling, Python-level solver network denial, nonfinite JSON sanitation, bounded result staging, atomic result commit and commit-aware recovery.

## Artifact preservation

Regardless of execution success or failure, the workflow preserves for 90 days:

- fresh recheck and issuance summary;
- exact runtime release authorization;
- exact runtime grant;
- grant-state ledger including spent/state records;
- execution log;
- immutable CP01R2 result package if committed.

These runtime records are evidence of transaction provenance. They are not, by themselves, evidence that the physical model is correct.

## Scientific firewall

Starting CP01R2 does not establish convergence, continuum existence, uniqueness, Fredholmness/invertibility, ghost freedom, physical identification or observational confirmation. Scaled conditioning and trust-region diagnostics remain numerical diagnostics only. Candidate acceptance remains controlled by the frozen raw physical residual/QA criteria.

Until a separate post-execution result review is completed:

- `WP4 = BLOCKED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`

## Next state

After the one CP01R2 transaction terminates, the only admissible next stage is a separate immutable-result review of the produced Actions artifact. No automatic transition to WP4, K1-D or K1-E is permitted.
