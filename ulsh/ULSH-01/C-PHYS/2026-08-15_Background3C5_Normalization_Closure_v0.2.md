# ULSH-01 / C-PHYS — Background-3C5 Normalization Closure v0.2

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** NORMALIZATION_BRIDGES_CLOSED / RESPONSE_CONTROL_AMENDMENT_REQUIRED / PHYSICAL_EXECUTION_STILL_BLOCKED  
**Governance:** K1-D = NOT_RELEASED; K1-E = NOT_ADMISSIBLE; physical_evidence_effect = NONE

## 1. Purpose

This artifact closes the two normalization bridges left open by `Background3C5_Equation_Freeze_Audit_v0.2` using only already-frozen C-PHYS contracts on `main`.

## 2. Scalar normalization — CLOSED

The canonical M1 Function Freeze Contract fixes:

- `[phi] = M^2`,
- `varphi = phi / M6^2`,
- canonical scalar kinetic normalization `Z_phi = 1`,
- `U(phi) = 0.5*mhat_phi_sq*M6^6*varphi^2`,
- `Z_F(phi) = exp(-2*a_F*varphi)`.

Therefore the correct notation bridge is

`varphi = phi/M6^2`, equivalently `phi = M6^2 varphi`.

No additional scalar field `Phi` is required in the executable M1 convention. Any prior notation using a dimensionful `Phi` is to be identified with the canonical dimensionful field `phi` only after checking source-local notation.

The scalar redundancy is already removed by `Z_phi=1`, the unique minimum of `U` at `phi=0`, and `Z_F(0)=1`.

**Verdict:** `SCALAR_NORMALIZATION_BRIDGE = PASS_FROZEN`.

## 3. Gauge normalization — CLOSED AT THE U(1) LATTICE LEVEL

The Global Convention Freeze Contract fixes

`Delta_chi = 2*pi`,

`Lambda_NS(chi) = (N_F/q_ref) chi`,

and single-valuedness

`q_ref [Lambda_NS(chi+2*pi)-Lambda_NS(chi)] = 2*pi N_F`.

It also fixes the charge lattice

`q_sigma = m_sigma q_ref`, `m_sigma in Z_{>0}`,

while the M1 Function Freeze Contract fixes

`q_ref = q_hat/M6`, `q_hat>0`,

and states that gauge-field rescaling has already been removed by the Maxwell normalization together with `Z_F(0)=1`.

For the finite-thickness charged phase

`D_chi theta_Sigma = partial_chi theta_Sigma - gSigma A_chi`,

with `theta_Sigma = n chi`, global U(1) bundle consistency requires the phase factor of Sigma to be single-valued under the frozen patch transition. Hence

`gSigma [Lambda_NS(chi+2*pi)-Lambda_NS(chi)] in 2*pi Z`.

Using the frozen transition function gives

`(gSigma/q_ref) N_F in Z` for every admissible flux sector. To place the field on the same minimal charge lattice independently of the chosen admissible `N_F`, the canonical charge assignment is

`gSigma = m_layer q_ref`, `m_layer in Z`.

Choosing the positive-charge representative gives `m_layer in Z_{>0}`. Therefore

`gSigma = m_layer*q_hat/M6`.

This is not a new continuous coupling independent of the charge lattice.

**Verdict:** `GAUGE_NORMALIZATION_BRIDGE = PASS_LATTICE_CONSTRAINED`.

## 4. Consequence for the response-rank control vector

The v0.3 finite-thickness control list used `gSigma` as a continuous control. After imposing the already-frozen U(1) charge lattice, that notation must be interpreted carefully.

At fixed discrete charge sector `m_layer`, a continuous finite-difference response may vary the underlying model parameter `q_hat` across explicitly labelled neighboring model instances, with

`delta gSigma/gSigma = delta q_hat/q_hat`.

It is NOT admissible to vary `gSigma` independently while keeping `q_hat`, patch transition, and charge lattice fixed.

Therefore the canonical continuous control vector should be represented as

`c = (Lambda6/Lambda_ref, Lambda_layer/Lambda_ref, mSigma2/mref2, q_hat/qhat_ref, lambdaSigma/lambda_ref)`

with the derived coupling

`gSigma = m_layer*q_hat/M6`.

Discrete labels held fixed during the Jacobian scan include at least

`(n, N_F, m_layer)`

and any additional topological integers required by the selected branch.

## 5. Dimensional consistency

The M1 Function Freeze Contract fixes

`a_chi = A_chi/M6`,

so `[A_chi]=M` for the angular component in the dimensionless-chi convention. Since `[q_ref]=M^-1`,

`[gSigma A_chi] = 1`,

as required for

`w = n - gSigma A_chi`.

Thus `[gSigma]=M^-1` and the lattice identification `gSigma=m_layer*q_hat/M6` is dimensionally consistent.

## 6. What is closed and what remains open

### Closed

- canonical scalar normalization `varphi=phi/M6^2`;
- canonical scalar kinetic normalization `Z_phi=1`;
- Maxwell/gauge-field rescaling redundancy;
- minimal charge unit `q_ref=q_hat/M6`;
- finite-thickness charge assignment `gSigma=m_layer*q_ref`;
- interpretation of the continuous gauge-response direction as a `q_hat` model-parameter variation at fixed integer charge sector.

### Still open

- physical finite-thickness Background-3C5 BVP solution;
- continuum response rank of the full coupled system;
- stability/ghost gates;
- whether the selected finite-thickness branch admits a nonempty globally regular solution for generic M1 parameters;
- K1-D and K1-E.

## 7. Authorization disposition

`BACKGROUND3C5_NORMALIZATION_FREEZE = PASS`

`BACKGROUND3C5_RESPONSE_CONTROL_VECTOR = REQUIRES_LATTICE_AMENDMENT`

`BACKGROUND3C5_PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

The remaining block is no longer scalar/gauge normalization. The next admissible implementation action is to amend the ULSH-01 RunSpec/runner so the fourth continuous control is `q_hat` with derived `gSigma`, then bind the physical finite-thickness equation kernel and pass the existing authorization gates before any physical run.
