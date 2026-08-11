# ULSH-01 / MD2S-BVP — WP3 CP01R1 single-use release decision ledger v1.0

**Date:** 2026-08-11  
**Architecture:** HPVS → HZT-M0 → HZT-Full  
**Reviewed main commit:** `001a098e4b16c434a6fffe4dbaa3a3c4cf2dfa7f`

## Decision

`PASS_ELIGIBLE_FOR_EXACT_H3_SINGLE_USE_RELEASE_ISSUANCE_NO_EXECUTION`

WP2-RR4 independently established that the frozen CP01R1 H3 transaction is release-ready and reported no new release blockers. WP3 therefore approves a later **separate issuance act** for the exact H3 Physical Solve Release Authorization and Single-Use Execution Grant.

This decision deliberately does **not** create either artifact and does not authorize solver execution by itself.

## Why release/grant issuance is deferred

The H3 grant has a maximum start-validity window of 3600 seconds and exact content-addressed bindings. Creating it during a static decision review would needlessly consume its validity window before execution and could leave a stale authorization if the repository changes.

Therefore the sequence is frozen as:

`WP3 release decision PASS → immediate pre-issuance source/repository recheck → exact release + exact single-use grant issuance → runtime/resource preflight → atomic grant spend → CP01R1 transaction`.

The last three stages have **not** occurred in this ledger.

## Exact frozen execution scope

Run: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1`  
Payload SHA-256: `0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302`  
Target: `a_F = 1/4`  
Seeds: `7`  
Node counts: `[24, 32, 48, 64, 96]`  
Primary schedule entries: `35`

No parameter mutation, topology mutation, random restart, adaptive mesh insertion or surrogate/control fallback is allowed. The independent backend remains required after a Primary numerical candidate.

## Content-addressed basis

RR4 review blob: `7d69a7187962f2b5be817d10dc9b2dac0d099b05`  
H3 contract blob: `a09067d749493fa14c61fc8a7678ca353a005566`  
H3 transaction blob: `2dd09d9ade6d6ae69c1949833e88b2af49c13710`  
H3 source-bundle SHA-256: `022b1ede18d217c3278445ea1cfd65fad475d28a6ebaa7327cc9c46904c877cd`

A later issuance act must recheck these bindings and the inherited frozen payload, 7×5 schedule, dependency lock, resource policy and result schema before creating authorization artifacts.

## Decision boundary

`Physical Solve Authorization = ABSENT`  
`Single-Use Grant = ABSENT`  
`CP01R1 = NOT_EXECUTED`  
`physical background = NOT_ESTABLISHED`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`  
`physical_evidence_effect = NONE`

The decision is a governance/transaction authorization decision only. It is not numerical evidence and not physical evidence.

## Interpretation firewall

Even a later successful CP01R1 transaction can establish at most a reproducible numerical background candidate under the preregistered QA gates. It does not by itself prove continuum existence or uniqueness, Fredholmness, continuum Jacobian invertibility, perturbative stability, ghost freedom, physical identification or observational confirmation of HZT-M0.

## Next admissible action

`ULSH-01_WP3_ISSUE_EXACT_H3_RELEASE_AUTHORIZATION_AND_SINGLE_USE_GRANT_FOR_IMMEDIATE_CP01R1_TRANSACTION`

Execution remains forbidden from this decision alone.
