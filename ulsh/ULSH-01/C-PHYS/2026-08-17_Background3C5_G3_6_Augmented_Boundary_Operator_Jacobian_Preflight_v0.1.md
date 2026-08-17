# ULSH-01 / C-PHYS — Background3C5 G3.6 Augmented Boundary Operator & Jacobian Preflight v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** BOUNDARY_OPERATOR_10_DEFINED / JACOBIAN_SCHUR_PREFLIGHT_PASS / ACTUAL_RANK_OPEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This block continues the frozen G3.4/G3.5 development path

`SUPPLEMENTARY_BULK_LAYER_WITH_CANONICAL_CAP`.

It defines the complete ten-component global boundary operator for the two-region finite-thickness extension and derives exact algebraic conditions for local Jacobian invertibility. It performs no nonlinear BVP solve and proves no physical background.

## 2. Fixed discrete branch

The continuous BVP is defined only after fixing the discrete bundle sector

`(N_F, m_layer, n_S)`

with

`n_N = n_S + m_layer*N_F`.

Equivalently one may fix `(N_F,m_layer,n_N)` and derive `n_S`. The two local winding integers must not be varied independently inside one continuous Jacobian evaluation.

## 3. Continuous unknown vector

Use

`U10 = (phi_N0, Q_N0, A_S0, phi_S0, Q_S0, rho_N, rho_S, K4, c_N, c_S)`.

Here `Q_N0,Q_S0` denote pole/initial Maxwell momenta. With distributed finite-thickness current they are not region-wide constants.

`c_N,c_S` are the regular pole amplitudes defined by

`s_N(r_N)=c_N r_N^|n_N|+O(r_N^(|n_N|+2))`,

`s_S(r_S)=c_S r_S^|n_S|+O(r_S^(|n_S|+2))`.

The frame and regular local pole gauges remain

`A_N(0)=0`, `A_chi,N(0)=A_chi,S(0)=0`.

## 4. Cap traces and oriented derivative sums

At the common cap define the shared target traces after continuity:

`A_cap`, `L_cap`, `phi_cap`.

Before imposing continuity, retain regional endpoint values at `rho_N,rho_S`.

Use the canonical local-coordinate orientation

`n_N^r=n_S^r=+1`.

Define

`A_Sigma = A_N'(rho_N)+A_S'(rho_S)`,

`L_Sigma = L_N'(rho_N)/L_cap + L_S'(rho_S)/L_cap`,

`phi_Sigma_der = phi_N'(rho_N)+phi_S'(rho_S)`.

For the canonical cap winding sector

`d_chi = N_sigma - q_sigma*A_chi,cap`

in the `Delta_chi=2*pi` convention, with `A_chi,cap` understood in the canonical cap-patch convention, and

`X_sigma=d_chi^2/L_cap^2`, `Y_sigma=Z_sigma(phi_cap) X_sigma`.

For the finite-thickness Maxwell sector define the evolved endpoint momenta

`P_Ncap = exp(4A_N) Z_F(phi_N) A_chi,N'/L_N |_(rho_N)`,

`P_Scap = exp(4A_S) Z_F(phi_S) A_chi,S'/L_S |_(rho_S)`.

## 5. Complete augmented boundary operator

Define

`B10(U10) = (R_A,R_L,R_phi,R_patch,R_4d,R_chi,R_scalar,R_gauge^FT,R_s,R_s_flux)`.

The ten residuals are:

1. `R_A = A_N(rho_N)-A_S(rho_S)`.

2. `R_L = L_N(rho_N)-L_S(rho_S)`.

3. `R_phi = phi_N(rho_N)-phi_S(rho_S)`.

4. `R_patch = A_chi,N(rho_N)-A_chi,S(rho_S)-N_F/q_ref`.

5. `R_4d = M6^4*(-3*A_Sigma-L_Sigma)+lambda(phi_cap)+Y_sigma/2`.

6. `R_chi = -4*M6^4*A_Sigma+lambda(phi_cap)-Y_sigma/2`.

7. `R_scalar = phi_Sigma_der + lambda_,phi(phi_cap) + 0.5*Z_sigma_,phi(phi_cap)*X_sigma`.

8. `R_gauge^FT = exp(-4*A_cap)/L_cap*(P_Ncap+P_Scap) - q_sigma*Z_sigma(phi_cap)*d_chi/L_cap^2`.

9. `R_s = s_N(rho_N)-s_S(rho_S)`.

10. `R_s_flux = s_N'(rho_N)+s_S'(rho_S)`.

The last equation follows because no cap-localized coupling of `Sigma_FT` is present in the selected G3.4 path. Any future localized `Sigma_FT` interaction changes this residual and requires a new parent contract.

The two regional `rr` constraints are propagated QA channels and are not appended to `B10`.

The discrete relation `n_N-n_S=m_layer*N_F` is a branch condition, not an eleventh continuous residual.

## 6. Jacobian block decomposition

Let

`u=(phi_N0,Q_N0,A_S0,phi_S0,Q_S0,rho_N,rho_S,K4)`

and

`c=(c_N,c_S)`.

Split the residuals as

`R8=(R_A,R_L,R_phi,R_patch,R_4d,R_chi,R_scalar,R_gauge^FT)`

and

`Rs=(R_s,R_s_flux)`.

Then the actual functional Jacobian at a candidate solution has block form

`J10 = dB10/dU10 = [[J8, B],[C,D]]`,

where

`J8 = dR8/du`,

`B = dR8/dc`,

`C = dRs/du`,

`D = dRs/dc`.

Because finite-thickness stress and current backreact on metric, scalar and Maxwell profiles, generally

`B != 0` and `C != 0`.

Therefore invertibility of the inherited 8x8 block and of the raw 2x2 layer block separately is not sufficient.

## 7. Exact Schur-complement criterion

If `J8` is nonsingular, block Gaussian elimination gives

`det(J10)=det(J8)*det(S_layer)`

with

`S_layer = D-C*J8^(-1)*B`.

Thus

`rank(J10)=10`

is equivalent, under `det(J8)!=0`, to

`det(S_layer)!=0`.

This isolates the finite-thickness rank question after accounting for relaxation of the eight inherited global variables.

Conversely, if `J8` itself is singular, the Schur formula with `J8^(-1)` is unavailable and full-rank assessment must be performed on `J10` directly; structural matching alone cannot rescue an inherited null direction.

## 8. Raw amplitude transfer block

At fixed inherited variables `u`, define the cap sensitivities

`a_N = partial s_N(rho_N)/partial c_N`,

`a_S = partial s_S(rho_S)/partial c_S`,

`b_N = partial s_N'(rho_N)/partial c_N`,

`b_S = partial s_S'(rho_S)/partial c_S`.

Regional locality at fixed `u` gives the raw layer block

`D = [[a_N,-a_S],[b_N,b_S]]`

and therefore

`det(D)=a_N*b_S+a_S*b_N`.

In the linearized zero-amplitude limit these sensitivities are the normalized regional transfer solutions and their cap derivatives. Hence

`a_N*b_S+a_S*b_N=0`

is an explicit raw layer rank-risk surface.

However the physical augmented BVP rank-risk surface is the Schur condition

`det(D-C*J8^(-1)*B)=0`,

not merely `det(D)=0`.

## 9. Rank-risk classes

The preflight identifies the following distinct failure classes:

- `RISK-J8`: inherited 8x8 functional Jacobian singular; includes the known scalar-shift surface and fixed-K4 overconstraint variants.
- `RISK-LAYER-RAW`: `a_N*b_S+a_S*b_N=0` at fixed inherited variables.
- `RISK-LAYER-SCHUR`: `det(D-C J8^(-1) B)=0` despite nonsingular `J8`; a genuine backreaction-induced augmented null direction.
- `RISK-POLE`: one regional Frobenius branch ceases to be regular or differentiable in its amplitude parameter.
- `RISK-PATCH`: branch drift or violation of `n_N-n_S=m_layer*N_F` invalidates the continuous Jacobian comparison.
- `RISK-CAP-IDENTITY`: introducing a cap-localized `Sigma_FT` interaction without updating `R_s_flux` changes the operator and invalidates this preflight.

## 10. Dimensions and normalization

Each residual must be normalized before numerical rank assessment; the present equations are the parent-level dimensional forms. Multiplication of any residual by a finite nonzero normalization factor leaves exact rank unchanged but changes conditioning and singular-value thresholds.

Therefore a later numerical Jacobian gate must operate on an explicitly dimensionless/scaled `J10` and must distinguish exact rank from conditioning.

## 11. What is proven

**[BEWIESEN]** The selected supplementary parent path defines a ten-component global boundary operator.

**[BEWIESEN]** The bundle compatibility relation removes independent continuous variation of the two local winding integers.

**[BEWIESEN]** The exact block determinant identity and Schur-complement rank criterion hold whenever `J8` is invertible.

**[BEWIESEN]** The raw 2x2 amplitude transfer determinant is `a_N*b_S+a_S*b_N` under fixed inherited variables.

**[NICHT BEWIESEN]** `det(J8)!=0` at a physical solution.

**[NICHT BEWIESEN]** `det(S_layer)!=0` at a physical solution.

**[NICHT BEWIESEN]** existence, uniqueness, convergence, conditioning, stability or ghost freedom.

## 12. Verdict

`G3_6_BOUNDARY_OPERATOR_DIMENSION = 10`

`G3_6_BOUNDARY_OPERATOR = PROVENANCE_DEFINED`

`G3_6_DISCRETE_PATCH_COMPATIBILITY = FROZEN`

`G3_6_JACOBIAN_BLOCK_FORM = PASS_ANALYTIC`

`G3_6_SCHUR_COMPLEMENT_CRITERION = PASS_ANALYTIC`

`G3_6_RAW_LAYER_RISK_DETERMINANT = a_N*b_S+a_S*b_N`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN_NOT_EVALUATED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence claim follows from this preflight.