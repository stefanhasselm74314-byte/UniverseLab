# ULSH-01 / C-PHYS — Background3C5 Kernel Availability & Binding Audit v0.2

Date: 2026-08-15
Supersedes: `2026-08-15_Background3C5_Kernel_Availability_Binding_Audit_v0.1.md`
Status: `CANDIDATE_IMPLEMENTATIONS_LOCATED__NO_CURRENT_RATIFIED_PARENT_EQUIVALENT_FINITE_THICKNESS_KERNEL`
Evidence effect: `NONE`
Architecture: `HPVS -> HZT-M0 -> HZT-Full`
Active block: `HZT-M0 / S6 / C-PHYS / ULSH-01`

## 1. Corrected decision

The v0.1 statement is retained as a correct statement about the audited canonical `main` tree: no bindable exact `Background3C5` kernel was present there under the searched identifiers.

A broader branch audit subsequently located a substantial historical Background-3C development lineage on unmerged `agent/background-3c*` branches. Therefore the repository-wide availability statement is corrected as follows:

- historical numerical kernel/runner/adapter candidates **exist**;
- they are **not present as a ratified canonical kernel on current `main`**;
- their own governance records keep physical execution unauthorized;
- the historical primary kernel is **not operator-identical** to the 2026-08-15 finite-thickness equation freeze v0.2;
- no historical candidate may therefore be bound directly to the v1.1 physical response runner as physical evidence machinery.

Physical binding remains **BLOCKED**.

## 2. Historical candidate lineage located

Relevant unmerged branches include, among others:

- `agent/background-3c-primary-implementation-v0-1`
- `agent/background-3c2-independent-backend-v0-1`
- `agent/background-3c4-execution-runner-v0-1`
- `agent/background-3c5-authorization-review-v0-1`
- `agent/background-3c8-physical-adapter-v0-1`
- `agent/background-3c9-authorization-review-v0-1`
- `agent/background-3c10-real-backend-control-v0-1`
- later status/review branches through Background-3C12.

Concrete reusable artifacts include historical collocation, independent-backend, execution-adapter, process-control, validator and result-schema machinery.

## 3. Historical governance result

The canonical historical C3C9 authorization review states

`DENIED_REAL_BACKEND_ADAPTER_TRANSACTION_AND_OPERATIVE_SINGLE_USE_GRANT_RELEASE_ABSENT`

with:

- physical execution authorization = false;
- CP01R1 attempted = false;
- physical result artifact created = false;
- `BACKGROUND_3C_EXECUTION = NOT_AUTHORIZED`;
- `official_MD2S_solver = NOT_AUTHORIZED`;
- `K1-D = NOT_RELEASED`;
- `K1-E = NOT_ADMISSIBLE`;
- physical evidence effect = `NONE`.

The subsequent C3C10 v0.3 audit passed only

`PASS_REAL_BACKEND_AF0_CONTROL_RELEASE_NO_TARGET_SOLVE`

and explicitly records:

- `a_F = 0` analytic control only;
- target `a_F=1/4` solves = 0;
- primary Newton calls = 0;
- independent shooting-root calls = 0;
- physical result artifacts = 0;
- physical background = `NOT_ESTABLISHED`;
- background existence/uniqueness = `NOT_PROVEN`.

Thus the historical lineage itself forbids interpreting its software-control PASS as a physical solve.

## 4. Operator identity audit

### 4.1 Historical primary kernel

The substantial historical primary kernel

`tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py`

uses the field order

`(u_A, u_ell, u_varphi, u_g)`

on two north/south regions and an eight-component global parameter vector

`(varphi_N_0, q_N, A_S_0, varphi_S_0, q_S, rho_N, rho_S, k4)`.

Its bulk equations are formulated for warp factor `A`, internal radius `ell`, scalar `varphi` and gauge potential `a_chi`, with thin/junction boundary residuals at the matching layer. The localized layer enters through boundary quantities such as `lambda_hat`, `z_sigma_hat`, `N_sigma`, `m_sigma` and the gauge-invariant boundary combination.

### 4.2 Current finite-thickness freeze

The 2026-08-15 freeze v0.2 requires explicit dynamical fields

`F = (A, B, C, phi, s, Q)`

with

`Q = exp(3A+B-C+gamma) Z_F(phi) A_t'`,

`chi = theta' - gSigma A_chi`,

and explicit finite-thickness matter dynamics:

- Maxwell `Q'` sourced by localized finite-thickness current;
- scalar divergence equation;
- second-order `s` matter equation;
- Einstein evolution for `u=A'`, `v=B'`, `w=phi'`;
- radial/Hamiltonian constraint `H=0`;
- center expansion and outer-parent matching in one resolved finite-thickness system.

### 4.3 Decision

The historical kernel and current target share useful geometric and numerical ancestry, but they are **not the same operator**.

In particular, the historical primary kernel does not expose an explicit bulk `s(r)` finite-thickness profile or the current six-field `(A,B,C,phi,s,Q)` residual system. A junction-layer formulation cannot be silently relabeled as the current finite-thickness BVP.

Therefore:

`G5_OPERATOR_IDENTITY = FAIL_FOR_DIRECT_BINDING`

This is an incompatibility for direct physical binding, not a falsification of either formulation.

## 5. C3C10 worker classification

`...background_3c10_real_backend_worker_v0.3.py` is an adapter layer. It validates the complete candidate field mapping, reconstructs an explicit contractual vector order and delegates to the v0.2 worker. It does not define a new physical differential operator.

Classification:

`REUSABLE_TRANSACTION_AND_HANDOFF_INFRASTRUCTURE__NON_IDENTIFYING_FOR_CURRENT_PHYSICAL_OPERATOR`

## 6. Reuse matrix

| Historical component | Reuse status | Physical meaning |
|---|---|---|
| Chebyshev-Lobatto collocation machinery | `REUSE_CANDIDATE` | numerical infrastructure only |
| complex-step Jacobian/Newton machinery | `REUSE_CANDIDATE` | numerical infrastructure only |
| independent backend architecture | `REUSE_CANDIDATE` | cross-check framework only |
| transaction/process isolation | `REUSE_CANDIDATE` | provenance/runtime QA |
| immutable candidate handoff | `REUSE_CANDIDATE` | serialization/provenance QA |
| result schema/firewalls | `REUSE_CANDIDATE` | governance QA |
| historical thin-layer bulk operator | `DO_NOT_DIRECT_BIND` | not current finite-thickness operator |
| manufactured backend | `QA_ONLY` | never physical evidence |
| C3C10 `a_F=0` analytic control | `REGRESSION_ONLY` | no target solve |
| H4R4B exact global witness | `REGRESSION_ONLY` | parent/control consistency only |

## 7. Updated authorization gates

| Gate | Required result | Current status |
|---|---|---|
| G1 symbolic residual realization | current frozen six-field equations implemented | `OPEN` |
| G2 center expansion closure | current regular center coefficients/BC count close | `OPEN` |
| G3 outer-match closure | current outer-parent BC map closes | `OPEN` |
| G4 constraint preservation | current `H=0` propagated within certified tolerance | `OPEN` |
| G5 operator identity | implementation equals current freeze v0.2 | `FAIL_FOR_HISTORICAL_DIRECT_BINDING` |
| G6 H4R4B/control regression | exact witness/control reproduced where applicable | `OPEN` |
| G7 solver convergence certificate | mesh/tolerance/refinement convergence | `OPEN` |
| G8 provenance firewall | mocks/surrogates cannot become physical evidence | `PASS_CONTRACT_LEVEL` |

Physical execution remains:

`AUTHORIZED <=> G1 & G2 & G3 & G4 & G5 & G6 & G7 & G8`.

The conjunction is false.

## 8. Best implementation path

Do **not** merge an old Background-3C branch wholesale.

Instead construct the current finite-thickness kernel by controlled transplantation:

1. retain current 2026-08-15 equation/normalization freeze as authoritative;
2. reuse only operator-agnostic numerical infrastructure from the historical lineage;
3. implement a new current residual operator for `(A,B,C,phi,s,Q)`;
4. derive and test center-series coefficients and BC counting explicitly;
5. implement outer-parent matching and constraint monitoring;
6. add H4R4B plus historical `a_F=0` controls as nonphysical regression fixtures;
7. require independent-backend agreement;
8. only after G1-G8 PASS bind the v1.1 response runner and execute the physical 41-job campaign.

## 9. Scientific status

- historical solver infrastructure exists: **FACT / VERIFIED**;
- historical physical execution authorization: **DENIED / BLOCKED**;
- direct operator identity with current finite-thickness freeze: **FALSIFIED FOR DIRECT BINDING**;
- current finite-thickness kernel existence in canonical executable form: **OPEN**;
- physical `rank(R)=4`: **OPEN / NOT EXECUTED**;
- `K1-D`: **NOT_RELEASED**;
- `K1-E`: **NOT_ADMISSIBLE**.
