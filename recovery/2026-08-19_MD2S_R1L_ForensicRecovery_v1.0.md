# MD2S-R1-L Forensic Recovery v1.0

Status: `FORENSIC_RECOVERY_ONLY`

Physical gate effect: `NONE`

## 1. Scope

This record separates surviving MD-2S benchmark/boundary material by provenance. The exact historical identifier `MD2S-R1-L` has not been recovered as a canonical artifact identifier.

This document does **not** claim a recovered historical solver transaction, a physical MD2S background, or an exact two-junction replay.

## 2. Evidence classes

- `E1_VERIFIED_REPORTED_ARTIFACT`: explicitly reported in a surviving project artifact; this does not by itself prove a rerunnable solver output.
- `E2_VERIFIED_CONTRACT_DEFINITION`: explicitly defined in a surviving run-spec/method contract; not an executed result.
- `E3_DERIVED_CHECK`: later consistency calculation from surviving values.
- `E4_UNVERIFIED_HISTORICAL_CHAT_REPORT`: historically reported in chat, but no surviving primary solver/output/residual provenance has been recovered.
- `E5_MISSING_SURVIVING_ARCHIVE`: required for exact historical replay but absent from the surviving archive.

## 3. A0 benchmark block

The following A0 values are retained only as `E1_VERIFIED_REPORTED_ARTIFACT`:

- `sqrt(K4) * rho_cap = 1.1196329253611`
- `kappa6^2 * lambda_eff / (4 * sqrt(K4)) = 0.8931498683204`
- `K4 * rho_cap^2 = 1.2535778875527`
- `V_W = 0.5318111250097`
- for `K4 = beta = 1`: `R_circle = 0.6661500466003`

The near-unit product is a later consistency check and remains `E3_DERIVED_CHECK`; it is not promoted to raw historical solver output.

## 4. BVP boundary and benchmark contract

The surviving v0.4 BVP run specification defines the following center conditions:

- `L(0) = 0`
- `L'(0) = 1`
- `A'(0) = 0`
- `phi'(0) = 0`
- for nonzero winding: `s(0) = 0`

It also defines outer matching/decay/gauge-flux conditions and the finite-difference/SVD gates. These are `E2_VERIFIED_CONTRACT_DEFINITION` only. The preserved run specification is explicitly `NOT_EXECUTED`.

## 5. B1.4K / B1.4L

The numerical blocks historically reported for B1.4K and B1.4L are **not** promoted to verified solver outputs. Current classification:

`E4_UNVERIFIED_HISTORICAL_CHAT_REPORT`

Reason: repeated searches using the branch labels and exact numerical fingerprints did not recover a primary solver-output/residual artifact with input binding, solver identity, run identity and convergence provenance.

## 6. Missing historical two-sided interface export

An exact historical two-junction replay requires, at minimum, the run-bound values

- `A'_bulk`
- `A'_cap`
- `(L'/L)_bulk`
- `(L'/L)_cap`

plus the oriented normal convention and the associated solver/residual provenance.

These remain `E5_MISSING_SURVIVING_ARCHIVE`.

Any zero-valued defaults in an interactive junction calculator are UI defaults only and must not be interpreted as recovered historical measurements.

## 7. Promotion rule

A historical numerical value may be promoted to `VERIFIED_SOLVER_OUTPUT` only if a primary output artifact, solver/code identity, input binding, run identity, residual/convergence information and unambiguous branch association are all present.

Reconstructed values must be stored separately as `RECONSTRUCTED` and may never overwrite or masquerade as lost historical values.

## 8. Governance invariants

This forensic recovery has no physical evidence or release effect:

- `official_MD2S_solver = NOT_AUTHORIZED`
- `PHYSICAL_BACKGROUND = NOT_ESTABLISHED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical_evidence_effect = NONE`
- `physical_gate_effect = NONE`
