# ULSH-01 / WP2 — CP01R4 AuthorizationDecision + SingleUseGrant Filling Checklist v0.1

**Date:** 2026-08-28  
**Architecture:** HPVS → HZT-M0 → S6 → C-PHYS → ULSH-01  
**Classification:** `NONOPERATIVE / NO AUTHORIZATION / NO GRANT / NO BACKEND IMPORT / NO SOLVER EXECUTION`

## 1. Gate result

The technical field mapping for a possible later `AuthorizationDecision` and `SingleUseGrant` is complete.

The operative transition is nevertheless blocked by two independent gates:

1. `AUTHORITY_SIGNATURE_PROVENANCE = BLOCKED`
2. `RUNTIME_ISSUANCE_BINDINGS = BLOCKED`

Therefore:

```text
ULSH-01-WP2 = READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED

operative AuthorizationDecision = NOT CREATED
operative SingleUseGrant         = NOT CREATED
backend import                   = FALSE
solver execution                 = FALSE
physical background              = NOT ESTABLISHED
physical evidence effect         = NONE
```

A chat command such as `Go` is not an operative authorization artifact. Neither an assistant nor an automation path may self-authorize the physical transaction.

## 2. Frozen release identity

Any later decision would have to bind exactly:

| Binding | Frozen value |
|---|---|
| Run ID | `HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4` |
| Release subject | `d8890b9ef47936edf8bb7e758b882c898241b314` |
| Target digest | `237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823` |
| Target file SHA-256 | `1b3f410e837371f11b50d8550c86c2d6409efeb25232114284f778754d1ae31f` |
| Run payload SHA-256 | `8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c` |
| 16-member package SHA-256 | `1d6f45725a66b145d2907943ddc7fe3a989411e5ccfe6c0f29053c91253c7621` |
| Resource policy SHA-256 | `f01a4c13248dcc82d759da7ff291b68a3100bb7bec91d81cc515b6ff067c3fa7` |
| Backend rebind SHA-256 | `e60cc73cd3f1211dc8f4f504c427ac4f7b4dc59587d88ad1be4d710089b294a8` |
| Result schema SHA-256 | `c9ed6807d36872ebcb2070d861fe472f4fd168b0c2f3abd630bbd3250d1d581d` |
| Backend interface SHA-256 | `ce40d78f3ab50ebab5ca2bc7d43b86ab54371a492bfab6a8bedb6e1d0de23048` |
| Dependency lock SHA-256 | `4f0095cc5e8c2a9eff7f22140c05cadb571a4809b87ce74aa79f460cfa2ab95f` |
| Primary source SHA-256 | `8ce1c0eceed64245d091d4bed492f3cf2a9c8314f631a03045aaa9696fb11c92` |
| Primary base source SHA-256 | `830d4b4fdd28c8888876125479df3542eeb3864d4328764feb96b5d34bd91599` |
| Target | `a_F = 1/4` |

Later checklist, review, or governance commits do not retarget the reviewed release subject.

## 3. AuthorizationDecision fields

Source template:

`registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_AuthorizationDecisionSchema_v0.1.json`

### Prebound fields

The run, scope, release subject, target digest, payload digest, package digest, resource policy, backend rebind, result schema, backend interface, single-use requirement, and all downstream firewalls are fixed.

Mandatory false values remain:

```text
automatic_execution               = false
wp3_authorized                    = false
wp4_authorized                    = false
physical_response_rank_authorized = false
K1_D_release_authorized           = false
K1_E_admissible                   = false
```

### Unfilled fields

```text
authorization_decision_id = null
decision_status           = NOT_AUTHORIZED
not_before_utc            = null
expires_at_utc            = null
```

The operative status literal may appear only after a separate valid authority decision:

`AUTHORIZED_SINGLE_USE_WP2_CP01R4_PRIMARY_TARGET_EXECUTION`

## 4. SingleUseGrant fields

Source template:

`registry/2026-08-27_HZT_M0_S6_C_PHYS_M1_ULSH01_WP2_SingleUseGrantSchema_v0.2.json`

### Prebound fields

```text
single_use               = true
scope                    = HZT-M0-S6-C-PHYS-M1-ULSH01-WP2-CP01R4_TARGET_ONLY
control_only             = false
authorized               = false
control_override_allowed = false
automatic_authorization  = false
```

All release, target, payload, package, policy, source, dependency, result-schema, and interface digests must match the frozen values above.

### Unfilled fields

```text
grant_id                      = null
authorization_decision_id     = null
authorization_decision_sha256 = null
nonce                         = null
not_before_utc                = null
expires_at_utc                = null
```

An operative grant would require `authorized = true`, but that transition is forbidden until the authority/signature gate passes and a valid separate decision exists.

## 5. Authority and signature provenance blocker

### Finding

The current technical decision/grant schemas and release verifier bind:

- IDs,
- scopes,
- hashes,
- release subject,
- time windows,
- single-use reservation semantics.

They do **not** presently bind or verify:

- a ratified issuing authority,
- signer identity or public-key fingerprint,
- a trust root,
- canonical signed bytes,
- signature or equivalent attestation algorithm,
- validity and revocation/rotation rules,
- a fail-closed authority/signature verifier.

### Required closure

Before any operative decision:

1. create or recover an append-only canonical authority contract;
2. define the competent issuer and exact authority scope;
3. define a signature or equivalently strong ratified attestation profile;
4. define canonicalization, trust root, validity, revocation/rotation, and replay rules;
5. implement an independent fail-closed verifier;
6. record issuer identity and authoritative basis in an immutable audit artifact;
7. ratify separation of duties, or explicitly ratify a narrow exception.

Until this exists:

```text
operative decision permitted = false
operative grant permitted    = false
```

## 6. Runtime issuance blocker

The following inputs are also not yet designated:

- execution-environment identity;
- persistent reservation-store identity and path/URI;
- crash persistence and access-control attestation;
- exclusive result path and absence check;
- machine/platform and exact dependency attestation;
- one-thread BLAS attestation;
- GPU-disabled and network-isolation attestation;
- `RLIMIT_AS` enforcement attestation;
- final pre-import package recomputation.

An ephemeral `/tmp` directory or ephemeral CI workspace is not admissible for an operative grant reservation store.

## 7. Required fail-closed order

```text
authority/signature profile
→ exact release-subject checkout
→ all package/digest checks
→ runtime and persistent-store attestation
→ separate decision, only after explicit ratification
→ canonical decision hash
→ separately bound grant
→ decision/grant time-window and identity checks
→ atomic grant-ID + nonce reservation
→ resource limits
→ backend import
→ exactly one CP01R4 primary transaction
→ atomic no-overwrite result commit
→ stop; WP3 and WP4 remain unauthorized
```

Any mismatch, expiry, replay, ephemeral operative store, pre-existing result path, failed environment attestation, or mutation under the same run ID aborts fail-closed.

## 8. Scientific firewall

Even a later successful WP2 transaction could establish at most:

`PRIMARY_NUMERICAL_CANDIDATE_PENDING_WP3_INDEPENDENT_CROSSCHECK`

It would not establish continuum existence, uniqueness, Fredholmness, stability, ghost freedom, physical response rank, K1-D release, K1-E admissibility, or theory confirmation.

## 9. Current verdict

| Item | Status |
|---|---|
| Technical field mapping | `COMPLETE` |
| Authority/signature provenance | `BLOCKED` |
| Runtime issuance bindings | `BLOCKED` |
| Authorization | `NOT_GRANTED` |
| Grant | `NOT_CREATED` |
| Backend import | `FALSE` |
| Solver execution | `FALSE` |
| Physical evidence effect | `NONE` |

## 10. Next safe action

`CREATE_OR_RECOVER_CANONICAL_AUTHORITY_AND_SIGNATURE_OR_EQUIVALENT_ATTESTATION_PROVENANCE_CONTRACT`

After that—and still without physical execution—the next allowed implementation block is a fail-closed authority/signature verifier plus synthetic negative/positive QA.
