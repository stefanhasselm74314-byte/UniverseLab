# ULSH-01 / MD2S-BVP — WP3 CP01R1 Immediate Execution Ledger v1.0

Date: 2026-08-11

## Decision

The operator explicitly requested transition across the previous NO-SOLVE boundary for the frozen physical run `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`.

The admissible sequence is fixed as:

`fresh recheck -> exact H3 v1.3 release authorization -> exact single-use H3 v1.3 grant -> exact-binding validation -> one grant spend -> H3 v1.4 transaction execute`.

No parameter, topology, seed, mesh, backend, threshold, dependency or resource-policy mutation is permitted.

## Frozen numerical scope

- payload SHA-256: `0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302`
- target `a_F = 1/4`
- seed set: `M1-BG3B-CP01-SEEDS-01`
- seeds: 7
- node counts: `24, 32, 48, 64, 96`
- primary schedule entries: 35
- independent backend: mandatory after a primary candidate
- random restart: forbidden
- adaptive mesh insertion: forbidden
- parameter/topology scan: forbidden
- control/surrogate fallback: forbidden

## Fresh issuance design

The release authorization and grant are deliberately not committed ahead of execution. The one-shot GitHub Actions runner first checks the exact WP3 PASS decision, RR4 PASS, H3 contract and transaction blobs, full H3 source-bundle digest, frozen payload, schedule, dependency lock, resource policy and result schema. Only if all checks pass are the exact v1.3 authorization and grant written into the checked-out runtime workspace.

The start-validity interval is created at runtime and is at most 3300 seconds, below the H3 maximum of 3600 seconds. The grant is consumed by the immediately following transaction step. A workflow rerun is fail-closed before issuance.

The transaction itself still performs the required pre-spend immutable-output collision check, strict one-thread startup check, exact dependency/runtime attestation and effective BLAS thread-pool attestation. Replay is forbidden. A failure or crash requires a separately authorized new grant; this trigger does not authorize one.

## Result preservation

The exact runtime release authorization, single-use grant, grant-state ledger, execution log and immutable result package are preserved as a GitHub Actions artifact. A later repository promotion, if any, is byte-for-byte only after separate result review; no recomputation is permitted for promotion.

## Scientific firewall

Starting or even successfully completing this transaction does not by itself establish continuum existence, uniqueness, Fredholmness, continuum Jacobian invertibility, perturbative stability, ghost freedom, physical identification, K1-D release, K1-E admissibility, or observational confirmation.

Before result review, `physical_evidence_effect = NONE` remains mandatory. A successful preregistered numerical outcome can establish at most a reproducible numerical background candidate subject to the frozen QA gates.
