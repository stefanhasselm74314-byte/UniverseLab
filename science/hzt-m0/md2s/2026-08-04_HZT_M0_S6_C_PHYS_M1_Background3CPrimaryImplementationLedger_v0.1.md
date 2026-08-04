# HZT-M0-S6-C-PHYS-M1 — Background-3C1 Primary Implementation Ledger v0.1

## Purpose

Background-3C1 translates the preregistered Background-3A method and the hash-frozen CP01R1 input into one auditable primary numerical implementation. It does not authorize or perform a nonlinear solve.

## Input identity

The implementation is bound to:

```text
run_id = HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1
run payload SHA256 = 0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302
```

The parameters, topology, Holder exponent, deterministic seed set and dependency lock are inherited unchanged from Background-3B v0.2.

## Primary discrete system

For `N` Lobatto nodes in each regional tau chart:

```text
unknowns  = 8N profile values + 8 augmented variables
residuals = 8N regularized bulk values + 8 cap/global values
```

Hence the implemented residual is square:

\[
\mathcal R_N:\mathbb R^{8N+8}\longrightarrow\mathbb R^{8N+8}.
\]

All regularized bulk blocks are evaluated at all Lobatto points, including the continuous pole extension and the cap endpoint. The radial constraint remains a propagated QA channel and is excluded from the nonlinear residual vector.

## Implemented nonlinear method

The kernel implements the already preregistered method:

- Chebyshev-Gauss-Lobatto collocation in `tau`;
- `degree = node_count - 1`;
- componentwise complex-step Jacobian;
- rank-revealing QR as the primary linear solve;
- singular values only as a conditioning diagnostic;
- damped Newton with Armijo backtracking;
- trust-radius restriction and deterministic adaptation;
- 60 Newton iterations maximum;
- 20 backtracking steps maximum;
- minimum step fraction `2^-20`;
- six-iteration stagnation window;
- seven deterministic seeds and no randomness.

The implementation uses the raw unit-scaled dimensionless residuals frozen in Background-3A. It does not introduce adaptive component rescaling.

## Audit-only capability

The permitted `audit` command checks:

1. contract and hash identity;
2. Chebyshev differentiation on low-order polynomials;
3. square state/residual dimensions;
4. exact `a_F=0` bulk and radial-constraint control-seed assembly;
5. the three deliberately nonzero cap defects;
6. seven-seed construction;
7. a finite-dimensional RRQR regression problem;
8. equality of implementation defaults with the preregistered method;
9. denied authorization and absence of output artifacts.

The audit never calls Newton. The kernel carries an in-process Newton-call counter, and the audit must finish with the counter equal to zero.

## Execution firewall

Two distinct entry points are used:

- the primary kernel has no direct execution interface and exits with code 73 when invoked as a program;
- the gate exposes `audit` and `run`, but `run` checks authorization before any numerical iteration and currently exits with code 73.

The v0.1 denial artifact is immutable. A grant would require a new v0.2 authorization artifact and append-only decision. Even such a future grant cannot make the current v0.1 gate an execution package: a new runner version must bind the independent backend and result writer.

## Result and resource contracts

Background-3C1 freezes:

- a machine-readable result schema;
- an immutable run/authorization-specific output path;
- a no-overwrite rule;
- atomic temporary-directory-to-final-directory publication;
- a six-hour total wall-clock budget;
- a one-thread, no-network, no-GPU and no-randomness environment.

No output directory or result artifact is created in this block.

## Remaining blocking prerequisite

The required independent backend does not yet exist. Background-3A requires separately coded residual assembly; therefore a wrapper around the primary residual function is not admissible. Background-3C2 must implement and audit an independent finite-difference or separately coded Lobatto backend before an execution decision can even be considered.

## What is established

- the primary numerical equations are encoded consistently with the current contracts;
- the primary algorithmic defaults match the preregistration;
- the audit and authorization boundary is fail-closed;
- result formatting, output immutability and resource limits are defined.

## What is not established

- no Newton iteration has run;
- no discrete root or candidate background exists;
- no multi-resolution convergence result exists;
- no independent-backend comparison exists;
- no continuum existence, uniqueness, Fredholm or Jacobian theorem exists;
- no perturbative stability or ghost-freedom result exists;
- no physical evidence or release-gate change follows.

The correct status is therefore:

```text
PRIMARY_IMPLEMENTATION_AUDITED_EXECUTION_NOT_AUTHORIZED
```

conditional on CI passing, with physical evidence effect `NONE`.
