# ULSH-01 / MD2S-BVP — WP3-D12 CP01R3 Manufactured-Control Audit Ledger v1.0

Date: 2026-08-13  
Architecture: HPVS → HZT-M0 → HZT-Full  
Scope: BJP-01 / ETRN-02 implementation audit on analytic and manufactured systems only

## 1. Audit disposition

**PASS_D12_BJP01_ETRN02_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION**

The first complete D12 control run passed all six preregistered manufactured-control families on tested commit `132e140490682daa0274849773156c9f135e03c4`.

This is an implementation/control result only. No physical MD2S backend was imported and no physical CP01R3 residual, Jacobian, solver call, grant, or result artifact exists.

## 2. Source binding

- implementation: `tools/2026-08-13_ulsh_01_md2s_bvp_wp3_d12_cp01r3_bjp01_etrn02_v1.0.py`
- implementation Git blob SHA-1: `d6313721a459254b13bdc9e06b4b83fc5a0fcca9`
- seed specification: `registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3SeedSpec_v1.0.json`
- seed specification SHA-256: `05315df34903188284b4ea58bffc6b440a06bda9486362a6760c7cc0cfcb1474`
- reserved run ID: `HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3`
- reserved seed set: `M1-BG3B-CP01R3-BJP01-SEEDS-01`
- manufactured-control NumPy: `2.1.3`
- workflow run: `31691213900`
- job: `94418730440`

## 3. Measured controls

### D11-C1 — Exact BJP-01 algebra

- status: PASS
- maximum absolute projected junction residual: `0.0`

The registered synthetic tuples satisfy `R_4D=R_chi=0` to arithmetic precision after BJP-01.

### D11-C2 — Endpoint invariants

- status: PASS
- endpoint invariant maximum absolute drift: `0.0`

The derivative-only basis preserves the registered pole/brane endpoint conditions in control space.

### D11-C3 — Mesh-normalized state metric

- status: PASS
- measured relative spread over N=24,32,48,64,96: `0.004915480656330283`
- registered tolerance: `0.006`

The measured spread is below the frozen manufactured-control tolerance. This validates the intended removal of raw `sqrt(N)` metric growth for the registered smooth-control perturbation; it is not a continuum statement.

### D11-C4 — Linear-preconditioner / trust-metric decoupling

- status: PASS
- relative original-state metric difference: `2.9979433129228975e-10`
- registered limit: `1e-7`

A large synthetic coordinate reparameterization of the Jacobian does not materially change the recovered original-state trust metric under the registered control.

### D11-C5 — Stiff manufactured known-root system

- status: PASS
- iterations: `3`
- infinity-norm root error: `9.150495999810104e-09`
- registered limit: `1e-7`

ETRN-02 reaches the known root of the registered stiff coupled synthetic system well inside the control limit.

### D11-C6 — Fail-closed controls

- status: PASS
- required checks passed: `3 / 3`

Nonfinite displacement, invalid trust radius, and an always-inadmissible trial path are rejected without physical execution.

## 4. Physical execution firewall

```text
physical backend imported       false
physical residual evaluations   0
physical Jacobian evaluations   0
physical solver calls           0
grant issued                    false
physical CLI                    exit 73
physical evidence effect        NONE
```

The implementation contains no path to the MD2S physical backend.

## 5. Scientific boundary

D12 establishes only that the new initialization algebra and generic trust geometry behave as specified on the registered controls.

D12 does **not** establish:

- correct behavior on the physical M1 BVP;
- a CP01R3 candidate background;
- continuum existence or uniqueness;
- continuum Jacobian invertibility;
- Fredholm properties;
- perturbative stability;
- ghost freedom;
- physical identification;
- K1-D or K1-E release.

## 6. Governance consequence

- WP3: `OPEN_D12_MANUFACTURED_CONTROLS_PASS_D13_INDEPENDENT_IMPLEMENTATION_REVIEW_REQUIRED`
- WP4: `BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`
- ULSH-02: blocked pending ULSH-01 release gate
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

## 7. Next allowed block

`ULSH-01_WP3_D13_CP01R3_INDEPENDENT_IMPLEMENTATION_REVIEW_NO_PHYSICAL_EXECUTION`

D13 must independently inspect BJP-01 algebra, ETRN-02 metric semantics, source isolation, control adequacy, and the frozen D12 measurements. It may not bind the physical backend or execute CP01R3.
