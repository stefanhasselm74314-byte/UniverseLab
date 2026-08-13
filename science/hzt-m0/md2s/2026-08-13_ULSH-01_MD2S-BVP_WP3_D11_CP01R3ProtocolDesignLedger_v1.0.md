# ULSH-01 / MD2S-BVP — WP3-D11 CP01R3 Protocol Design Ledger v1.0

Date: 2026-08-13  
Architecture: HPVS → HZT-M0 → HZT-Full  
Scope: protocol design only; no physical backend import, residual/Jacobian evaluation, solver execution, grant or result

## 1. Why a new run identity is mandatory

WP3-D10 diagnosed two interacting numerical-path effects in CP01R2:

1. the frozen seed family remains far from the exact combined junction manifold;
2. the Jacobian-equilibrated trust coordinate produces an extreme mesh-dependent step squeeze while all trials remain locally acceptable.

Changing either seed construction or trust-region metric changes the numerical experiment. Therefore D11 reserves a new immutable identity:

`HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3`

CP01R1 and CP01R2 remain immutable negative numerical outcomes. CP01R3 does not supersede or reinterpret them.

## 2. Physical identity remains frozen

CP01R3 is designed to keep unchanged:

- M1 physical parameters, including `a_F=1/4` and `lambda_hat=1`;
- topological sector;
- alpha_H;
- physical ODEs;
- all eight boundary residual equations;
- physical acceptance thresholds;
- node counts 24, 32, 48, 64, 96;
- seven seed multipliers;
- CP01R2 progress-continuation criterion;
- 120-iteration and 12-step stagnation rules.

Only initialization and trust geometry are redesigned.

## 3. BJP-01 exact boundary derivative projection

The frozen junction residuals are

`R_4D = -3 A_sum - ell_sum + lambda_hat + 0.5 Y_sigma`

`R_chi = -4 A_sum + lambda_hat - 0.5 Y_sigma`.

For a supplied seed, hold the brane field values fixed. Then `ell_sigma` and `Y_sigma` remain fixed during the projection. Define

`A_sum* = (lambda_hat - 0.5 Y_sigma)/4`

and

`ell_sum* = -3 A_sum* + lambda_hat + 0.5 Y_sigma`.

These are exactly the values required for `R_chi=0` and `R_4D=0` at the initialization boundary.

Let

`Delta A_sum = A_sum* - A_sum_0`

`Delta ell_sum = ell_sum* - ell_sum_0`.

### 3.1 A-derivative basis

For each region use

`delta u_A^s(tau) = c_A^s (tau - 1)`.

Because the physical warp field is `A=A0+tau u_A`, this deformation vanishes at both the pole in physical A and at the brane value. At `tau=1`, however,

`delta A_x^s = 2 c_A^s / rho_s`.

Choose

`c_A^N = rho_N Delta A_sum / 4`

`c_A^S = rho_S Delta A_sum / 4`.

Each region contributes one half of the required change, so the total shift is exactly `Delta A_sum`.

### 3.2 ell-derivative basis

Use

`delta u_ell^s(tau) = c_ell^s (tau - 1)`.

Since `Lhat=1+tau u_ell`, the pole condition `Lhat(0)=1` is preserved and the brane value `ell_sigma` is unchanged. At the brane,

`delta ell_x^s = 2 c_ell^s`.

Choose

`c_ell^N = c_ell^S = ell_sigma Delta ell_sum / 4`.

Then

`delta[(ell_x^N+ell_x^S)/ell_sigma] = Delta ell_sum`.

### 3.3 Exact initialization invariants

Because the deformation vanishes in `A`, `ell` and `a_chi` at the brane and changes neither scalar field nor gauge field, the projection leaves unchanged at the projection instant:

- `R_A`;
- `R_ell`;
- `R_varphi`;
- `R_patch`;
- `R_scalar`;
- `R_gauge`;
- `ell_sigma`;
- `Y_sigma`.

Only `R_4D` and `R_chi` change, and they become exactly zero in exact arithmetic.

BJP-01 is **not** a solved background. The deformation changes radial profiles and can increase bulk residuals. It is only a deterministic initialization transform derived from the frozen equations.

## 4. New seed identity

The seven CP01R2 multiplier directions are retained, but BJP-01 is applied after constructing each seed. Because this changes the seed states, the new seed set must receive a new identity and hash:

`M1-BG3B-CP01R3-BJP01-SEEDS-01`

The actual source digest and `seed_spec_sha256` remain deliberately `PENDING_D12_IMPLEMENTATION_FREEZE`. D11 must not fabricate a digest before code exists.

## 5. ETRN-02: separate linear preconditioning from trust geometry

CP01R2 uses row/column Jacobian equilibration to obtain an SVD direction and also clips the equilibrated coordinate vector `z` by the trust radius. D10 showed that at N=96 the unconstrained `z` norm reaches O(1e8) while the frozen radius is 64, producing an active fraction O(1e-7).

ETRN-02 keeps row/column equilibration **only for the linear solve**. The recovered original-variable direction `dx` is instead measured in an explicit state metric that does not depend on the Jacobian column norms.

### 5.1 Mesh-normalized field blocks

For each of the eight field blocks of length N, freeze at stage initialization

`s_b = max(1, RMS(seed_block))`.

For a trial direction define

`m_b^2 = mean_j[(delta x_b,j / s_b)^2]`.

Using a mean rather than a raw Euclidean sum prevents the same smooth perturbation from acquiring an artificial `sqrt(N)` growth merely because the collocation mesh is refined.

### 5.2 Global parameter blocks

For each of the eight global parameters freeze

`s_p = max(1, abs(seed_p))`

and use

`m_p^2 = (delta p / s_p)^2`.

### 5.3 Combined trust metric

`||delta x||_M = sqrt(sum_b m_b^2 + sum_p m_p^2)`.

The unconstrained original-variable Newton direction is clipped by

`alpha = min(1, Delta / ||dx||_M)`

`dx_trial = alpha dx`.

The Jacobian equilibration therefore cannot by itself redefine the physical/state-space notion of step size.

## 6. Frozen D11 candidate trust constants

Because the state metric is dimensionless and block normalized, D11 proposes the following candidate constants for manufactured validation:

- initial radius: 0.25
- minimum radius: 1e-8
- maximum radius: 2.0
- rho accept: 0.10
- rho shrink threshold: 0.25
- rho expand threshold: 0.75
- expansion factor: 2

The rho acceptance definition remains based on the original unscaled residual equations.

These are **design constants, not authorized physical settings**. D12 must test them on analytic/manufactured systems. Failure of those controls requires a new design revision before any physical binding.

## 7. What intentionally does not change yet

To keep the future CP01R3 experiment diagnostically attributable, D11 leaves unchanged:

- physical thresholds;
- 120 iterations per mesh;
- 12 accepted-step stagnation window;
- 1e-4 relative stagnation floor;
- the 10% progress-continuation rule.

This means CP01R3 initially tests only two hypotheses: boundary-aware initialization and decoupled trust geometry.

## 8. Required manufactured controls before physical binding

D12 must implement and pass six control families:

1. exact algebraic junction projection;
2. pole/patch invariant preservation;
3. mesh-normalized state metric across N=24…96;
4. separation of linear equilibration from trust clipping;
5. a manufactured stiff boundary/bulk system with known root;
6. nonfinite/admissibility fail-closed behavior.

No real CP01R3 physical residual or Jacobian is allowed in D12.

## 9. Release sequence

The earliest admissible path is:

`D12 implementation + manufactured controls`

→ `D13 independent implementation review`

→ `D14 exact CP01R3 run-input/seed/source freeze`

→ `D15 physical release eligibility review`

Only a later separately authorized one-shot block could execute CP01R3.

## 10. Governance

- WP3: `OPEN_CP01R3_PROTOCOL_DESIGNED_IMPLEMENTATION_AND_MANUFACTURED_CONTROLS_PENDING`
- WP4: `BLOCKED_NO_ACCEPTED_BACKGROUND_EXPORT`
- ULSH-02: blocked pending ULSH-01 release gate
- K1-D: `NOT_RELEASED`
- K1-E: `NOT_ADMISSIBLE`
- physical evidence effect: `NONE`

D11 itself contains no physical execution capability.
