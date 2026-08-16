# ULSH-01 / C-PHYS — Background3C5 G5 Maxwell Normalization Closure v0.2

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** MAXWELL_CURRENT_COEFFICIENT_PROVENANCE_CLOSED / LOCAL_OPERATOR_CLOSURE_ADVANCED / PHYSICAL_EXECUTION_STILL_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Purpose

Close the sole coefficient-level gap isolated by `2026-08-16_Background3C5_G5_Full_Operator_Identity_Audit_v0.1.md` without fitting, convention guessing or importing a second gauge normalization.

The target identity is the coefficient in

`P_x = -Gamma_Sigma * exp(4A) * s_hat^2 * w / ell`,

where

`P = exp(4A) Z_F a_chi_x / ell`.

## 2. Provenance chain

The canonical repository sources already fix the relevant normalization.

### 2.1 SCI-001/SCI-002 canonical core

`sci-001-002-parent-closure-v0.1.html` defines the canonical Maxwell sector as

`L_F = -1/4 Z_F(phi) F^2`

and the bulk equation

`nabla_A[Z_F F^(AB)] = 0`.

There is no independent `1/g6^2` coefficient in this canonical action.

### 2.2 C-PHYS ParentActionOperatorEntry

`registry/2026-08-03_MD2S_R1_C_PHYS_ParentActionOperatorEntryContract_v0.1.json` freezes the same operator normalization,

`... -1/4 Z_F(phi) F^2 ...`,

and explicitly records

`Maxwell_normalization = FROZEN_BY_SCI_001_V0_1`.

This contract is a direct dependency of the later C-PHYS function and convention freezes.

### 2.3 M1 function/charge freeze

`registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json` fixes

`x = M6*r`,

`ell = M6*L`,

`varphi = phi/M6^2`,

`a_chi = A_chi/M6`,

`q_ref = q_hat/M6`,

and states that gauge-field rescaling has already been removed by the Maxwell normalization together with `Z_F(0)=1`.

### 2.4 Finite-thickness charge lattice

`2026-08-15_Background3C5_Normalization_Closure_v0.2.md` proves within the frozen U(1) bundle convention

`gSigma = m_layer*q_ref = m_layer*q_hat/M6`,

with `m_layer` a fixed positive integer within one Jacobian branch.

Therefore define the dimensionless charged-layer coupling

`g_hat_Sigma := M6*gSigma = m_layer*q_hat`.

## 3. Source-local g6 notation is not an additional M1 coupling

`2026-08-15_Background3C5_Equation_Freeze_Audit_v0.2.md` recovered a separate source-local representation containing

`-Z_F F^2/(4 g6^2)`.

That representation cannot be carried simultaneously into the already-frozen executable C-PHYS M1 convention, because the canonical SCI-001/ParentActionOperatorEntry normalization used by M1 is explicitly

`-Z_F F^2/4`.

Keeping an additional `g6` in the M1 Maxwell equation after adopting the canonical field normalization would reintroduce a gauge-field rescaling that the M1 Function Freeze explicitly declares removed.

Accordingly, the `g6 <-> q_ref` question in the source-local representation is a notation/field-normalization reconciliation issue, not an independent missing coefficient in the canonical M1 operator.

This v0.2 closure supersedes only the `Gamma_Sigma`-open conclusion of G5 v0.1. It does not erase the source-local record or identify its gauge potential with the M1 gauge potential without an explicit field redefinition.

## 4. Exact dimensionless derivation

Use the frozen finite-thickness field

`Sigma = s(r)/sqrt(2) * exp(i n chi)`

with

`w = n - gSigma*A_chi`.

The canonical phase kinetic term gives

`E_chi = 1/2 s^2 w^2/L^2`.

Varying the canonical Maxwell plus phase sector with respect to `A_chi` yields

`d/dr [ exp(4A) Z_F A_chi'/L ] = - exp(4A) gSigma s^2 w/L`.

Now substitute the M1 dimensionless variables:

`x = M6*r`, hence `d/dr = M6*d/dx`,

`L = ell/M6`,

`A_chi = M6*a_chi`, hence `A_chi' = M6^2*a_chi_x`,

`s = M6^2*s_hat`,

`gSigma = g_hat_Sigma/M6`.

The left-hand side becomes

`M6^4 * d/dx [ exp(4A) Z_F a_chi_x/ell ]`.

The right-hand side becomes

`-M6^4 * g_hat_Sigma * exp(4A) s_hat^2 w/ell`.

Canceling the common nonzero factor `M6^4` gives

`P_x = -g_hat_Sigma * exp(4A) s_hat^2 w/ell`,

with

`P = exp(4A) Z_F a_chi_x/ell`.

Therefore

`Gamma_Sigma = g_hat_Sigma = M6*gSigma = m_layer*q_hat`.

## 5. Dimensional check

`[gSigma] = M^-1`, `[M6] = M`, hence

`[Gamma_Sigma] = [M6*gSigma] = 1`.

Also `q_hat` and `m_layer` are dimensionless, so

`[m_layer*q_hat] = 1`.

Both sides of

`Gamma_Sigma = m_layer*q_hat`

are dimensionless as required.

## 6. Factor-of-two audit

The quarantined implementation

`2026-08-15_hzt_background3c5_finite_thickness_operator_v0.1.py`

used a factor `2*gSigma` in its current source, but that operator was independently falsified for direct Background3C5 binding by `2026-08-15_Background3C5_Operator_Variable_Consistency_Audit_v0.1.md`.

For the frozen amplitude convention

`Sigma = s/sqrt(2) exp(i theta)`

one has the phase kinetic term

`-1/2 s^2 (D theta)^2`.

Its variation produces exactly one power of `gSigma`, not `2*gSigma`. Thus no factor two survives in `Gamma_Sigma`.

## 7. Operator consequence

The G5 executable candidate must not accept `Gamma_Sigma` as an independent caller-supplied physical parameter.

It is derived internally from the fixed charge sector:

`Gamma_Sigma = sector.m_layer * sector.q_hat`.

The corrected conservative residual is

`E_flux = P_x + (m_layer*q_hat) exp(4A) s_hat^2 w/ell`.

The layer-off limit remains exact:

`s_hat -> 0  =>  P_x -> 0  =>  P = q_s`.

## 8. Status and remaining gates

**Provenance result:** `GAMMA_SIGMA = m_layer*q_hat` — **PROVENANCE_CLOSED_WITHIN_CANONICAL_C_PHYS_M1**.

This is a coefficient identity inside the already-defined M1 model. It is not a derivation of M1 from a deeper 6D UV completion and is not physical evidence.

Still required before any physical Background3C5 execution:

- full symbolic constraint-propagation/Bianchi identity for the coefficient-fixed finite-thickness operator;
- independent parent-equivalence regression of all coefficient-fixed residual blocks;
- global regular BVP existence/convergence and branch checks;
- existing authorization firewalls;
- only after those gates, the 41-job physical response-rank program.

Therefore:

`MAXWELL_CURRENT_DIMENSIONLESS_COEFFICIENT = PASS_PROVENANCE_CLOSED`

`G5_COEFFICIENT_BLOCKER = CLOSED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

`PHYSICAL_EVIDENCE_EFFECT = NONE`
