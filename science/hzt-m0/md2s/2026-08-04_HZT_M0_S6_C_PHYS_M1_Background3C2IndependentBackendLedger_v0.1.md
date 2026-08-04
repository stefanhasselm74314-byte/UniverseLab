# HZT-M0-S6-C-PHYS-M1 — Background-3C2 Independent Backend Ledger v0.1

## Purpose

Background-3C2 implements the independent numerical representation required by the preregistered Background-3A protocol. It is an audit-only block. It does not run a shooting Jacobian, root iteration or target-background solve.

## Genuine implementation independence

The second backend does not import or wrap the primary tau-collocation residual. It independently codes:

- the dimensionless M1 first-order equations in physical radial coordinate `x`;
- the radial constraint;
- all eight cap and global residuals;
- the pole expansion through `A4`, `ell5`, `varphi4` and `a_chi4`;
- regional DOP853 integration;
- a future centered finite-difference shooting Jacobian interface.

An AST and source-token audit rejects references to the primary residual implementation.

## Control-background comparison

The comparison uses only the exact `a_F=0` bulk-and-patch control background. It is deliberately not a full cap solution. The nonzero cap defects remain visible.

The independent backend was integrated from the preregistered pole cutoffs:

```text
1e-3
5e-4
2.5e-4
```

with DOP853, relative tolerance `1e-11`, absolute tolerance `1e-13`, and 513 recorded points per region.

### Measured errors

| epsilon | profile max | constraint max | exact boundary distance | primary-independent boundary distance |
|---:|---:|---:|---:|---:|
| 1e-3 | 1.1102230246251565e-15 | 1.3877787807814457e-17 | 8.881784197001252e-16 | 1.0369483049998962e-13 |
| 5e-4 | 4.440892098500626e-16 | 1.3877787807814457e-17 | 4.440892098500626e-16 | 1.0413891970983968e-13 |
| 2.5e-4 | 4.440892098500626e-16 | 1.3877787807814457e-17 | 2.220446049250313e-16 | 1.0458300891968975e-13 |

These values show that the separately coded equations reproduce the analytic control background and its nonzero cap defects to floating-point precision.

## Execution counters

```text
primary Newton calls                  = 0
independent regional integrations     = 6
independent shooting Jacobian calls   = 0
independent shooting-root calls       = 0
target a_F=1/4 solves                 = 0
result artifacts                      = 0
```

The six integrations are exactly two regions times three pole cutoffs.

## What is established

- the independent source is genuinely separate from the primary residual;
- higher pole series and x-space equations are implemented consistently;
- the primary and independent representations agree on the analytic control background;
- cutoff behavior is stable for the tested control background;
- the dual package remains fail-closed and audit-only.

## What is not established

- no target `a_F=1/4` root exists or was sought;
- no nonlinear family, uniqueness or conditioning result exists;
- no resolution study of a target candidate exists;
- no trace matrix, Fredholm or continuum-Jacobian result exists;
- no perturbative stability or ghost-freedom result exists;
- no physical or observational evidence follows.

The appropriate classification is:

```text
PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION
```

The next admissible block is an execution-authorization review only. Such a review may deny authorization. It may not reinterpret this control-background software audit as a physical result.
