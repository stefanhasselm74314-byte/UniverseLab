# HZT-M0-S6-C-PHYS-M1 — Background-3A Assembly Correction v0.3

## Scope

This ledger records one append-only correction to the preregistered numerical bookkeeping. It performs no numerical solve and changes no model parameter, topology, seed, threshold or result class.

## Defect found before execution

Background-3A v0.1 stated that the regularized bulk equations would be enforced at “interior nodes.” Read literally as strict exclusion of the Lobatto endpoints, that sentence is incompatible with the frozen unknown layout.

For `N` Lobatto points in each regional chart:

- eight profile blocks contribute `8N` unknown values;
- the augmented vector contributes eight unknowns;
- total unknown count is `8N+8`.

Strict interior enforcement would provide only

\[
8(N-2)+8=8N-8
\]

residuals after appending the eight cap/global equations. The discrete problem would be underdetermined by sixteen equations.

Excluding only the cap endpoints would produce

\[
8(N-1)+8=8N,
\]

which remains underdetermined by eight equations.

## Correct square assembly

The regularized operator from Operator-2B has continuous extensions at `tau=0`. Therefore the canonical collocation assembly is

\[
8N\;\text{regularized bulk rows}
+
8\;\text{boundary/global rows}
=
8N+8.
\]

Each bulk block is enforced at every Lobatto point, including:

1. the continuously extended pole value at `tau=0`,
2. all strict interior points,
3. the cap endpoint at `tau=1`.

The eight boundary/global residuals are appended. They are not substitutions for cap bulk rows because the eight augmented variables enlarge the unknown vector by exactly eight components.

The propagated radial constraint remains a QA channel and is not counted as a nonlinear residual.

## Why the affine pole chart is not enough by itself

The affine chart guarantees the parity and regularity form of the represented fields. It does not determine the pole values of the regular profile coefficients. The continuously extended bulk equations at the pole determine those coefficients.

## Run-identity consequence

The original CP01 payload was frozen but never executed. Its immutability rule forbids reusing the same run ID after a method-contract correction. Therefore the unchanged control point is rebound as

```text
HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1
```

The following remain exactly unchanged:

- model parameters `(1,1,1/4,1,1,1)`,
- topology `(N_F,N_sigma,m_sigma)=(1,1,1)`,
- `alpha_H=1/2`,
- the seven-seed specification and seed hash,
- dependency lock and dependency hash,
- all Background-3A nonlinear limits and acceptance thresholds.

## Evidence boundary

This correction proves only that the declared discrete bookkeeping is square and internally consistent. It does not prove:

- existence or uniqueness of a discrete root,
- convergence to a continuum solution,
- trace rank or Fredholmness,
- perturbative stability or ghost freedom,
- physical validity or observational support.

No solver is implemented or executed in this block. Physical evidence effect remains `NONE`.
