# ULSH-01 / WP3-D7 — CP01R2 Fresh Single-Use Release Decision v1.0

**Date:** 2026-08-12  
**Architecture:** HPVS → HZT-M0 → HZT-Full  
**Classification:** release decision only — **NO EXECUTION**

## Decision

WP3-D6R1 independently verified D6-B01 and D6-B02 closed for the exact D6H1 hardened CP01R2 source bindings. No new release blockers remain. Therefore the frozen CP01R2 protocol is **eligible for one future fresh single-use runtime release issuance**, subject to an immediate fresh runtime recheck before issuance.

This document is not a runtime release authorization, is not a single-use execution grant, and does not authorize execution from the repository artifact alone.

## Exact frozen scope

- Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R2`
- Payload SHA-256: `e8b8e82d2cb1472d91c387a40c8f84024c2549a3dcc2c897df5561f7bf721b36`
- Schedule SHA-256: `929f59d018cc511f36c98ef26a8614ed495fe699a067b1b33e6c5b53efaf8e0b`
- Dependency lock SHA-256: `4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f`
- 7 frozen seeds × 5 meshes `[24,32,48,64,96]` = 35 schedule entries
- `a_F = 1/4`
- physical equations, parameters, topology, ETRN-01 rule, continuation rule, thresholds, independent-backend requirement and higher-precision audit remain unchanged.

## Failed-attempt firewall

The prior D5 grant is spent and permanently non-replayable. Actions run `31573154936` may not be rerun as a substitute for a new authorization. Its numerical outcome remains `INDETERMINATE_UNPRESERVED_DUE_FINALIZATION_FAILURE` and may not be retrospectively reclassified.

## Fresh future issuance contract

A subsequent execution work package must, immediately before execution, perform a fresh exact source/run/repository recheck. Only then may it create the D6H1 v2.0 runtime release authorization and a fresh single-use grant bound to this D7 decision, frozen run/payload/schedule/dependency/source bindings and a new 128–256-bit lowercase-hex nonce. Maximum grant validity is 3600 seconds. Replay, retry, scan, fallback, parameter/topology mutation and threshold/method relaxation remain forbidden.

## Scientific firewall

This decision establishes transaction eligibility only. It does **not** establish CP01R2 convergence, existence or uniqueness of an M1 background, the numerical or physical origin of `R_4D`, continuum invertibility/Fredholm properties, perturbative stability, ghost freedom, physical identification, or observational confirmation.

Current governance after this decision remains: WP4 `BLOCKED`, K1-D `NOT_RELEASED`, K1-E `NOT_ADMISSIBLE`, physical evidence effect `NONE`.

## Next threshold

`ULSH-01_WP3_D8_CP01R2_FRESH_RUNTIME_RECHECK_RELEASE_ISSUANCE_SINGLE_USE_GRANT_AND_IMMEDIATE_EXECUTION`

Crossing that threshold requires a separate explicit execution instruction; WP3-D7 itself performs zero solver calls and issues no runtime release/grant.
