# HZT-M0-S6 C-PHYS-M1 — Background-3C6 Integrated Execution Release Ledger v0.1

## Scope

This block implements and audits an end-to-end execution transaction **only for synthetic and exact analytic controls**.

```text
track       = MD2S-R1-C-PHYS
model       = HZT-M0-S6-C-PHYS-M1
block       = C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY
CP01R1      = FORBIDDEN
physical run = NOT_AUTHORIZED
```

The purpose is to close the software integration gap identified by Background-3C5 without evaluating the physical target problem.

## Transaction implemented

The canonical v0.2 entry point executes the following fail-closed sequence:

1. validate the registered control case and control-ID prefix;
2. reject CP01, CP01R1 and BG3B identifiers before subprocess creation;
3. reproduce a closed-source SHA-256 package digest;
4. attest Python, platform, dependencies and thread environment;
5. create a no-overwrite sibling staging directory outside the repository;
6. launch exactly one physics-free worker subprocess;
7. impose CPU, address-space, file-size and open-file limits;
8. impose a stage timeout and deterministic SIGTERM/SIGKILL escalation;
9. capture bounded stdout and stderr with hashes;
10. validate a bounded worker payload;
11. classify the control outcome;
12. write canonical JSON and a SHA-256 manifest;
13. fsync and atomically rename committable controls;
14. remove staging without a final artifact after timeout, signal or failure.

## Registered controls

### Exact analytic success

The worker verifies exactly, using rational arithmetic,

\[
\left(\frac{3}{5}\right)^2+\left(\frac{4}{5}\right)^2=1.
\]

Expected classification:

```text
CONTROL_TRANSACTION_PASS
```

### Intentional rejection

A fixed synthetic residual is intentionally rejected.

Expected classification:

```text
CONTROL_TRANSACTION_REJECTED_AS_EXPECTED
```

### Timeout

A worker that sleeps beyond the frozen stage timeout must be terminated. The staging directory must be removed and no final artifact may appear.

Expected classification:

```text
CONTROL_TRANSACTION_TIMEOUT_CLEAN_ABORT
```

### Signal interruption

A worker terminates itself with SIGTERM. The parent must record the signal in memory, remove staging and create no final artifact.

Expected classification:

```text
CONTROL_TRANSACTION_SIGNAL_CLEAN_ABORT
```

## Independence and firewall

The worker contains no NumPy, SciPy, SymPy or Hyperzeit equation import. The canonical entry point parses the engine and worker with Python AST and rejects actual imports or calls involving:

- the primary collocation backend;
- the independent x-space backend;
- `damped_newton`;
- complex-step or centered-finite-difference Jacobians;
- the independent shooting residual.

The physical CLI command remains a hard refusal with exit code 73.

## Artifact semantics

Only the analytic-success and intentional-rejection controls may atomically commit artifacts, and only inside a caller-provided external temporary directory. Timeout and signal controls must leave no final artifact.

A committed control artifact contains:

- `result.json`;
- `artifact-manifest.json`;
- package digest;
- environment attestation;
- resource envelope;
- process exit, timing and stream hashes;
- worker payload;
- closed control classification;
- zero physical solver counters;
- explicit forbidden inferences.

No control artifact may be stored under the canonical CP01R1 repository path.

## What this block can establish

A successful audit may establish only:

```text
PASS_INTEGRATED_CONTROL_RELEASE_AUDIT_NO_PHYSICAL_EXECUTION
```

This means that the synthetic/control transaction correctly joins scope validation, source identity, environment attestation, subprocess limits, timeout and signal handling, classification and atomic artifacts.

## What this block cannot establish

It cannot establish:

- existence or uniqueness of an M1 background;
- convergence of the primary Newton method on CP01R1;
- convergence of the independent shooting method on CP01R1;
- agreement of the two backends on a physical candidate;
- continuum trace rank or Fredholm properties;
- stability or ghost freedom;
- a released forward map;
- K1-D or K1-E advancement;
- physical evidence for Hyperzeit.

## Required status after a successful audit

```text
BACKGROUND_3C6_INTEGRATED_CONTROL_RELEASE = PASS_AUDITED_CONTROL_ONLY
BACKGROUND_3C_EXECUTION                   = NOT_AUTHORIZED
PHYSICAL_BACKGROUND                       = NOT_ESTABLISHED
R1.1                                      = BLOCKED
R1.2                                      = BLOCKED
OFFICIAL_MD2S_SOLVER                       = NOT_AUTHORIZED
K1-D                                      = NOT_RELEASED
K1-E                                      = NOT_ADMISSIBLE
PHYSICAL_EVIDENCE_EFFECT                  = NONE
```

## Next admissible block

```text
C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY
```

Background-3C7 may approve or deny whether the integrated release is technically eligible for a later single-use CP01R1 grant. It may not automatically create that grant or execute either physical backend.
