# ULSH-01 / C-PHYS — Background3C5 G5 Full Operator Identity Audit v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** PARTIAL_DERIVATION_PASS / MAXWELL_SOURCE_NORMALIZATION_OPEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Purpose

Derive the full finite-thickness residual structure from the frozen parent sector without silently identifying unresolved gauge normalizations. This audit supersedes neither the G2 closure nor the normalization closure; it narrows G5 to the remaining coefficient-level identity.

## 2. Canonical variables

Use

`x=M6*r`, `ell=M6*L`, `varphi=phi/M6^2`, `s_hat=s/M6^2`, `a_chi=A_chi/M6`,

with

`Z_F=exp(-2*a_F*varphi)`, `gSigma=m_layer*q_hat/M6`, and dimensionless winding

`w=n-(m_layer*q_hat)*a_chi`.

The layer potential is

`Vhat_layer = Lambda_hat_layer(varphi) + 1/2*mhatSigma^2(varphi)*s_hat^2 + 1/4*lambdahatSigma*s_hat^4`.

Define

`E_r_hat = 1/2*(d_x s_hat)^2`,

`E_chi_hat = 1/2*s_hat^2*w^2/ell^2`.

## 3. Exact layer stress insertion into Einstein residuals

The frozen dimensionful stress basis is

`Tmu_layer = -E_r - E_chi - V_layer`,

`Tr_layer = +E_r - E_chi - V_layer`,

`Tchi_layer = -E_r + E_chi - V_layer`.

The existing canonical bulk residuals are respectively the chi-chi Einstein equation (`E_A`), the mu-mu equation multiplied by `ell` (`E_ell`), and the rr constraint.

Therefore the finite-thickness additions are fixed algebraically:

`Delta E_A = +E_r_hat - E_chi_hat + Vhat_layer`,

`Delta E_ell = ell*(E_r_hat + E_chi_hat + Vhat_layer)`,

`Delta rr_constraint = -E_r_hat + E_chi_hat + Vhat_layer`.

These signs are not fitted. They follow directly from `G-T=0` and the frozen stress tensor.

## 4. Scalar residual

The canonical bulk scalar residual contains the frozen bulk potential and gauge-kinetic source. The layer adds

`Delta E_varphi = -ell * d_varphi Vhat_layer`.

Thus any `varphi` dependence of `Lambda_hat_layer` or `mhatSigma^2` is a genuine scalar source and must not be omitted.

For the affine mass model,

`mhatSigma^2(varphi)=mhatSigma0^2 + etaSigma*(varphi-varphi_star)`,

one has

`d_varphi Vhat_layer = d_varphi Lambda_hat_layer + 1/2*etaSigma*s_hat^2`.

## 5. Layer-amplitude residual

The dimensionless amplitude equation is closed:

`E_s = s_hat_xx + (4*A_x + ell_x/ell)*s_hat_x - (w^2/ell^2)*s_hat - d_s Vhat_layer = 0`,

with

`d_s Vhat_layer = mhatSigma^2(varphi)*s_hat + lambdahatSigma*s_hat^3`.

Its regular-axis Frobenius limit is `s_hat ~ x^abs(n)` for `n!=0`, already closed by G2.

## 6. Maxwell equation in conservative flux form

The bulk-control first integral implies the natural dimensionless flux variable

`P = exp(4*A)*Z_F*a_chi_x/ell`.

In the layer-free limit, `P=q_s=constant`, exactly reproducing the frozen bulk gauge equation

`a_chi_x = q_s*ell*exp(-4*A+2*a_F*varphi)`.

With the charged finite-thickness layer the parent variation requires

`P_x = -Gamma_Sigma * exp(4*A) * s_hat^2 * w / ell`,

where `Gamma_Sigma` is the dimensionless coefficient obtained after converting the dimensionful Maxwell normalization and charged phase current into the frozen M1 gauge convention.

The **functional form, sign, geometry, winding dependence and s_hat^2 dependence are fixed**. The surviving frozen contracts available to this audit do not yet provide an independent coefficient identity that proves the numerical value of `Gamma_Sigma` in terms of `(q_hat,m_layer)` without reintroducing the source-local `g6` convention.

Therefore:

`MAXWELL_CURRENT_STRUCTURE = PASS_DERIVED`

`MAXWELL_CURRENT_DIMENSIONLESS_COEFFICIENT = OPEN_PROVENANCE_IDENTITY`

No value for `Gamma_Sigma` may be guessed.

## 7. Constraint consistency

The rr constraint including the layer is

`C_rr_full = C_rr_bulk - E_r_hat + E_chi_hat + Vhat_layer`.

For an exact Euler-Lagrange solution the radial Bianchi identity implies propagation of this constraint once the independent Einstein, scalar, Maxwell and layer equations hold. A numerical implementation must nevertheless monitor `C_rr_full` independently. G4 remains open until this identity is checked symbolically/numerically for the complete coefficient-fixed operator.

## 8. Mandatory limits

### Layer-off limit

For `s_hat -> 0` and `Vhat_layer -> 0`:

- all layer stress additions vanish;
- `Delta E_varphi -> 0`;
- Maxwell current vanishes;
- `P_x -> 0`, hence `P=q_s`;
- the exact G2-tested bulk operator v0.2 is recovered.

### Zero-winding local limit

For `w -> 0`, `E_chi_hat -> 0` and the Maxwell current vanishes locally, while radial-gradient and potential stresses can remain nonzero.

### Thin-gradient-free local condensate

For `s_hat_x -> 0`, `E_r_hat -> 0`; the remaining local anisotropy is carried by `E_chi_hat` and the gauge sector. This does not reproduce the full finite-thickness rank-3 stress space unless radial gradients are present somewhere in the profile.

## 9. G5 verdict

Established:

- canonical variable set;
- full layer stress insertions into all three Einstein channels;
- scalar layer source;
- amplitude equation;
- conservative Maxwell-current structure;
- exact bulk-control limit.

Still open:

- coefficient-level provenance identity for `Gamma_Sigma` in the frozen M1 gauge convention;
- complete symbolic constraint-propagation identity after that coefficient is fixed;
- numerical parent-equivalence regression of the fully coupled operator.

Therefore:

`G5_OPERATOR_IDENTITY = PARTIAL_PASS_COEFFICIENT_BLOCKED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

No physical BVP run is authorized by this audit.