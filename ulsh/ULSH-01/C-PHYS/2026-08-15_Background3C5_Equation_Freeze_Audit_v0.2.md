# ULSH-01 / C-PHYS — Background-3C5 Equation Freeze Audit v0.2

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** PARTIAL_FREEZE_ADVANCED / NORMALIZATION_BRIDGE_OPEN / PHYSICAL_EXECUTION_BLOCKED  
**Governance:** K1-D = NOT_RELEASED; K1-E = NOT_ADMISSIBLE; physical_evidence_effect = NONE

## 0. Correction to v0.1

v0.1 stated too strongly that the canonical `Z_F` function, Einstein-Hilbert normalization, cosmological-term placement, and `M6^4 <-> kappa6^-2` relation had not been recovered.

The canonical C-PHYS restart package and the surviving July 2026 project-status action recover the following:

- `M6^4 = kappa6^-2`,
- gravitational bulk term `M6^4/2 (R6 - 2 Lambda6)`,
- scalar-Maxwell bulk structure,
- frozen M1 potential `U(phi)=1/2*mhat_phi^2*M6^6*phi^2`,
- frozen M1 gauge kinetic function `Z_F(phi)=exp(-2*a_F*phi)`,
- `Delta chi = 2*pi`, flux orientation and charge lattice,
- `lambda=lambdahat*M6^5`, `Z_sigma=zhat_sigma*M6^3`, `q_ref=qhat/M6`, `q_sigma=m_sigma*q_ref`.

Therefore the v0.1 blocker is narrowed rather than removed.

## 1. Recovered SCI-001 bulk action in dimensionful-scalar convention

The surviving bulk-action record is

`S_bulk = integral d^6X sqrt(-g6) [ M6^4/2 (R6 - 2 Lambda6) - 1/2 g^(AB) d_A Phi d_B Phi - V6(Phi) - Z_F(Phi)/(4 g6^2) F_AB F^(AB) ]`.

Dimensions in that record:

- `[M6]=M`,
- `[Lambda6]=M^2`,
- `[Phi]=M^2`,
- `[V6]=M^6`,
- `[g6^2]=M^-2`,
- `[Z_F]=1`.

This fixes the dimensionful Euler-Lagrange equations associated with that convention.

## 2. Frozen M1 functions in dimensionless-phi convention

The canonical restart package separately freezes

`U(phi)=1/2*mhat_phi^2*M6^6*phi^2`,

`Z_F(phi)=exp(-2*a_F*phi)`,

with active domain `mhat_phi^2>0`, `a_F>0`, `zhat_sigma>0`, `qhat>0`.

The restart package does NOT, in the recovered text currently available to this audit, explicitly state the field redefinition between the dimensionful July variable `Phi` and the M1 variable `phi`, nor the exact kinetic prefactor in the M1 notation.

The dimensionally natural candidate bridge

`Phi = M6^2 * phi`

would map the canonical dimensionful scalar kinetic term to

`- M6^4/2 * (partial phi)^2`

and maps the quadratic potential to the frozen M1 form. However this bridge remains **CANDIDATE_NOT_RATIFIED** until independently provenance-bound from the M1 spec/canonical state.

## 3. Geometry — exact and convention-fixed

Metric:

`ds6^2 = exp(2A(r)) gbar_mn dx^m dx^n + dr^2 + L(r)^2 dchi^2`,

`gbar_R_mn = 3 K4 gbar_mn`.

Define

`B = L'/L`, `k4 = K4*exp(-2A)`.

The mixed Einstein tensor components are

`G^mu_nu = [3 A'' + 6 A'^2 + 3 A' B + L''/L - 3 k4] delta^mu_nu`,

`G^r_r = 6 A'^2 + 4 A' B - 6 k4`,

`G^chi_chi = 4 A'' + 10 A'^2 - 6 k4`.

These are geometric identities for the frozen ansatz, not fitted equations.

Given the recovered gravitational action, Einstein's equation in the dimensionful-SCI-001 convention is

`M6^4 (G^A_B + Lambda6 delta^A_B) = T^A_B`.

## 4. Finite-thickness layer — frozen

`Sigma = s(r)/sqrt(2) exp(i n chi)`

`D_A thetaSigma = partial_A thetaSigma - gSigma A_A`

`w(r)=n-gSigma*A_chi(r)`

`V_Sigma = Lambda_layer(phi) + 1/2 mSigma^2(phi) s^2 + lambdaSigma/4 s^4`

`mSigma^2(phi)=mSigma0^2+etaSigma*(phi-phi_star)`.

The layer amplitude equation is

`s'' + (4A'+L'/L)s' - (w^2/L^2)s - mSigma^2(phi)s - lambdaSigma*s^3 = 0`.

Layer thickness remains DERIVED_NOT_FREE.

## 5. Exact Maxwell equation conditional on the recovered SCI-001 gauge convention

From

`L_F = - Z_F/(4 g6^2) F^2`

plus the finite-thickness phase term, variation with respect to `A_chi` gives

`nabla_A[(Z_F/g6^2) F^(A chi)] = - gSigma s^2 D^chi thetaSigma`.

For the radial ansatz `F_rchi=A_chi'`, `D^chi thetaSigma=w/L^2`:

`d/dr [ exp(4A) (Z_F/g6^2) A_chi'/L ] = - exp(4A) gSigma s^2 w/L`.

If `g6` is constant, the expanded form is

`A_chi'' + (4A' - L'/L + Z_F'/Z_F) A_chi' = - (g6^2 gSigma/Z_F) s^2 w`.

For the frozen M1 function `Z_F(phi)=exp(-2 a_F phi)` this becomes, conditional on the M1 field bridge,

`A_chi'' + (4A' - L'/L - 2 a_F phi') A_chi' = - g6^2 gSigma exp(2 a_F phi) s^2 w`.

**Status:** algebraically derived from recovered action; executable normalization remains blocked until `g6 <-> q_ref/q_sigma/gSigma` convention mapping is ratified.

## 6. Scalar equation in recovered dimensionful convention

Variation of the recovered SCI-001 action gives

`Box_6 Phi - d_Phi V6 - (d_Phi Z_F)/(4 g6^2) F^2 - d_Phi V_Sigma = 0`.

For radial fields and `F^2=2 A_chi'^2/L^2`:

`Phi'' + (4A'+L'/L) Phi' - d_Phi V6 - (d_Phi Z_F)/(2 g6^2) A_chi'^2/L^2 - d_Phi V_Sigma = 0`.

This is exact in the dimensionful `Phi` convention. Conversion to the frozen M1 `phi` notation is **BLOCKED_ONLY_BY_FIELD_NORMALIZATION_BRIDGE**.

## 7. Stress tensor in recovered dimensionful convention

Define

`E_Phi = 1/2 Phi'^2`,

`E_r = 1/2 s'^2`,

`E_chi = 1/2 s^2 w^2/L^2`,

`rho_F = Z_F/(2 g6^2) * A_chi'^2/L^2`,

`V_tot = V6(Phi) + V_Sigma`.

Then

`T^mu_mu = -E_Phi - E_r - E_chi - V_tot - rho_F`,

`T^r_r = +E_Phi + E_r - E_chi - V_tot + rho_F`,

`T^chi_chi = -E_Phi - E_r + E_chi - V_tot + rho_F`.

The finite-thickness stress sub-basis retains exact local rank 3. This is structural, not a global-response result.

## 8. Candidate closed Einstein ODE system in the dimensionful convention

Let `B=L'/L`, `k4=K4 exp(-2A)`. Then

`3A'' + 6A'^2 + 3A'B + L''/L - 3k4 + Lambda6 = T^mu_mu/M6^4`,

`6A'^2 + 4A'B - 6k4 + Lambda6 = T^r_r/M6^4`,

`4A'' + 10A'^2 - 6k4 + Lambda6 = T^chi_chi/M6^4`.

The middle equation is the radial Einstein constraint; it must be monitored independently rather than treated as an extra freely satisfiable boundary condition.

**Status:** exact consequence of the recovered dimensionful SCI-001 action and frozen metric ansatz; M1 executable form awaits only the normalization bridge described below.

## 9. Remaining normalization bridge — sole theory blocker for the executable kernel

The surviving sources currently do not independently expose the referenced `06_CPHYS_M1_SPEC.md` / canonical-state entries that would settle all of:

1. exact field redefinition `Phi <-> phi`,
2. M1 scalar kinetic prefactor,
3. exact map between `g6` and the frozen charge quantities `q_ref`, `q_sigma`, and the v0.3 layer notation `gSigma`,
4. whether the v0.3 shorthand `rho_F = Z_F F_rchi^2/(2L^2)` has absorbed `1/g6^2`, or simply suppresses it notationally.

No solver implementation may choose among these alternatives implicitly.

## 10. Boundary, branch and junction conditions

Still frozen without change:

- `L(0)=0`, `L'(0)=1`, `A'(0)=0`, `phi'(0)=0`, and `s(0)=0` for `n != 0`;
- simultaneous outer layer decay, bulk matching, gauge regularity and flux quantization;
- fixed discrete branch `(n,N)` during a continuous Jacobian scan;
- two metric junction equations and `Y_sigma=M6^4(L_Sigma-A_Sigma)`;
- no conical rescue mode;
- no free layer thickness;
- no free radion boundary mass unless derived from the local parent sector.

## 11. Revised freeze verdict

### FROZEN / RECOVERED

- EH normalization and cosmological-term placement,
- `M6^4=kappa6^-2`,
- dimensionful scalar-Maxwell bulk action,
- frozen M1 `U(phi)` and `Z_F(phi)`,
- metric Einstein tensor and dimensionful Einstein ODEs,
- dimensionful scalar ODE,
- Maxwell equation structure and action-normalized coefficient,
- finite-thickness layer action and amplitude ODE,
- branch, regularity, junction and response-rank governance.

### STILL OPEN

- `Phi <-> phi` field-normalization bridge,
- M1 scalar kinetic prefactor as an independently provenance-bound statement,
- `g6 <-> q_ref/q_sigma/gSigma` normalization bridge,
- reconciliation of the v0.3 `rho_F` shorthand with the explicit SCI-001 `1/g6^2` factor.

## 12. Authorization status

`BACKGROUND3C5_EQUATION_FREEZE = ADVANCED_PARTIAL`

`BACKGROUND3C5_PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`REASON = M1_FIELD_AND_GAUGE_NORMALIZATION_BRIDGE_NOT_YET_PROVENANCE_BOUND`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical background, rank-R, stability, ghost or phenomenology claim follows from this audit.
