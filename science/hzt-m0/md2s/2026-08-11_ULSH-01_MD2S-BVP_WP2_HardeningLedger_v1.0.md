# ULSH-01 / MD2S-BVP — WP2-H Release Hardening Ledger v1.0

Date: 2026-08-11  
Architecture: `HPVS -> HZT-M0 -> HZT-Full`  
Active solver: `ULSH-01 / MD2S-BVP`  
Run binding: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`  
Frozen payload SHA-256: `0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302`

## Scope

WP2-H is a **no-solve release-hardening block**. It addresses the four blockers identified by the physical release review merged at `bda7b098084d3c5862bdf48cd9c04facf48d40b8`.

WP2-H does **not** create a physical-solve release authorization, does **not** create a single-use grant, does **not** execute Newton, shooting, IVP integration or a physical BVP solve, and has `physical_evidence_effect = NONE`.

## RR-B01 — per-seed/per-level timeout

The hardened target v1.1 binds the exact frozen resource limits:

- total wall clock: 21600 s,
- per seed/per node-level entry: 1800 s,
- immutable order: 7 seeds × 5 node levels = 35 entries.

Each executable entry is placed under a fail-closed POSIX real-time timer. A timeout is classified as `TIMED_OUT_NO_RETRY`; higher mesh levels of the affected seed are skipped instead of retried or solved with a changed method. The remaining immutable seed order may continue only while the total budget remains.

Unsupported timeout infrastructure is an execution failure, not permission to run unbounded.

## RR-B02 — maximum result bytes

`BoundedStagingWriter` enforces the frozen 1 GiB result ceiling cumulatively before every artifact write and again before immutable directory promotion.

If the staged package would exceed the byte budget:

1. no final result directory is atomically committed,
2. the already-spent grant is not restored,
3. a machine-readable failure record is written in the grant transaction directory,
4. replay remains forbidden,
5. a later attempt requires a new reviewed grant.

## RR-B03 — mandatory result and QA closure

The hardened target captures the channels required by the frozen preregistration and result schema:

- per-seed/per-level convergence history,
- per-mesh bulk residual norms,
- all eight ordered boundary residuals,
- north/south `rr`-constraint profiles and maxima,
- 48→64 and 64→96 profile convergence,
- augmented-variable convergence,
- N=96 last-eight Chebyshev spectral tails,
- discrete Jacobian rank diagnostics,
- full discrete singular-value arrays,
- discrete condition estimates,
- independent-backend boundary residuals and constraint norms,
- independent-to-primary candidate distance,
- full admissibility gates,
- candidate profile artifacts,
- deterministic classification in the frozen result vocabulary,
- explicit forbidden-inference list.

The hardened transaction closes each candidate profile with a SHA-256 digest before writing `result.json`, validates every required top-level/backend/candidate field, creates a complete artifact manifest, then performs atomic promotion inside the external immutable quarantine.

No post-run numerical reconstruction is part of the protocol.

## RR-B04 — CPU / BLAS / LAPACK attestation

Before a future grant is spent, the hardened runtime preflight records:

- CPython implementation and version,
- `PYTHONHASHSEED`,
- exact frozen dependency versions,
- thread-control environment,
- architecture and platform,
- `uname`,
- CPU descriptors and logical core count,
- NumPy build configuration,
- SciPy build configuration,
- BLAS/LAPACK provenance text.

Missing required metadata is fail-closed before grant consumption.

## Nonblocking review warnings

`RR-W01` is normalized by using the canonical Background3C dependency-lock path from the Resource Policy. The lock bytes and SHA-256 remain unchanged.

`RR-W02` is closed structurally: the external quarantine now mirrors the canonical result package (`result.json`, `artifact-manifest.json`, frozen run input, provenance, runtime attestation, per-seed execution log, profile artifacts). Any later repository promotion is byte-for-byte only and requires separate review; recomputation is forbidden.

## Evidence firewall

The following remain false / not released:

- physical background established: **NO**,
- continuum existence: **NOT PROVEN**,
- uniqueness: **NOT PROVEN**,
- Fredholm property: **NOT PROVEN**,
- continuum BVP Jacobian invertibility: **NOT PROVEN**,
- perturbative stability: **OPEN**,
- ghost freedom: **OPEN**,
- `K1-D`: **NOT_RELEASED**,
- `K1-E`: **NOT_ADMISSIBLE**,
- physical evidence effect: **NONE**.

Numerical convergence, if a later authorized run occurs, remains a numerical diagnostic and is not a continuum existence theorem or physical confirmation.

## Hardening status

`PASS_WP2_HARDENING_IMPLEMENTED_NO_SOLVE_PENDING_REREVIEW`

The four release-review blockers are **implemented pending re-review**, not self-ratified as a solve release.

## Next allowed action

`ULSH-01 / WP2-RR2 — Hardening Re-Review`, still **no solve**.

A physical-solve release authorization or single-use grant remains forbidden until RR2 independently verifies all four closures against the merged hardening source bundle.
