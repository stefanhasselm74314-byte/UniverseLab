# ULSH-01 / C-PHYS — Background3C5 G3.7 Dimensionless Boundary Residual Normalization & Functional-Jacobian QA v0.1

**Architecture:** HPVS -> HZT-M0 -> S6 -> C-PHYS -> ULSH-01  
**Status:** DIMENSIONAL_NORMALIZATION_PASS / FUNCTIONAL_JACOBIAN_QA_CONTRACT_DEFINED / ACTUAL_RANK_OPEN / PHYSICAL_EXECUTION_BLOCKED  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## 1. Scope

This block continues G3.6. It fixes the row and column normalization required to assess the 10x10 boundary Jacobian without mixing physical dimensions, unit choices, numerical equilibration, conditioning and exact rank.

No nonlinear BVP is solved and no physical Jacobian is evaluated in this block.

## 2. Parent-level dimensions

Use mass dimension `M` and the canonical C-PHYS conventions

- `[M6]=M`, `[r]=[rho_s]=M^-1`,
- `[phi]=M^2`, `[A]=1`, `[L]=M^-1`,
- `[A_chi]=M`, `[Q_s]=M^3`, `[K4]=M^2`,
- `[s]=M^2`,
- `s_s(r)=c_s r^|n_s|+...`, hence `[c_s]=M^(2+|n_s|)`.

For the ten boundary residuals of G3.6:

- `[R_A]=1`,
- `[R_L]=M^-1`,
- `[R_phi]=M^2`,
- `[R_patch]=M`,
- `[R_4d]=M^5`,
- `[R_chi]=M^5`,
- `[R_scalar]=M^3`,
- `[R_gauge^FT]=M^4`,
- `[R_s]=M^2`,
- `[R_s_flux]=M^3`.

Every term in each residual has the displayed common dimension. This is a dimensional consistency condition, not a numerical rank result.

## 3. Dimensionless continuous variables

For the fixed discrete branch `(N_F,m_layer,n_S)` with `n_N=n_S+m_layer*N_F`, define

`u_hat = D_U^(-1) U10`

with diagonal physical scales

`D_U = diag(M6^2, M6^3, 1, M6^2, M6^3, M6^-1, M6^-1, M6^2, M6^(2+|n_N|), M6^(2+|n_S|))`.

Thus explicitly

- `phi_N0_hat=phi_N0/M6^2`,
- `Q_N0_hat=Q_N0/M6^3`,
- `A_S0_hat=A_S0`,
- `phi_S0_hat=phi_S0/M6^2`,
- `Q_S0_hat=Q_S0/M6^3`,
- `rho_N_hat=M6*rho_N`,
- `rho_S_hat=M6*rho_S`,
- `K4_hat=K4/M6^2`,
- `c_N_hat=c_N/M6^(2+|n_N|)`,
- `c_S_hat=c_S/M6^(2+|n_S|)`.

The winding-dependent powers in the last two entries are mandatory. Using one common `M6^2` scale for both Frobenius amplitudes would be dimensionally wrong when `|n_s|>0`.

## 4. Dimensionless residual vector

Define

`R_hat = D_R^(-1) B10`

with

`D_R = diag(1, M6^-1, M6^2, M6, M6^5, M6^5, M6^3, M6^4, M6^2, M6^3)`.

Equivalently,

- `R_A_hat=R_A`,
- `R_L_hat=M6*R_L`,
- `R_phi_hat=R_phi/M6^2`,
- `R_patch_hat=R_patch/M6`,
- `R_4d_hat=R_4d/M6^5`,
- `R_chi_hat=R_chi/M6^5`,
- `R_scalar_hat=R_scalar/M6^3`,
- `R_gauge_hat=R_gauge^FT/M6^4`,
- `R_s_hat=R_s/M6^2`,
- `R_s_flux_hat=R_s_flux/M6^3`.

## 5. Canonical dimensionless Jacobian

The functional Jacobian used for rank assessment is

`J_hat = dR_hat/du_hat = D_R^(-1) J10 D_U`.

Because `D_R` and `D_U` are diagonal and nonsingular for finite positive `M6`,

`rank(J_hat)=rank(J10)` exactly.

The normalization therefore cannot create or remove an exact null direction. It only removes units and fixes a reproducible physical scale convention.

## 6. Separation from numerical equilibration

Three objects must remain distinct:

1. `J10`: dimensional parent Jacobian;
2. `J_hat`: canonical physically dimensionless Jacobian;
3. `J_eq = E_R J_hat E_U`: optional numerically equilibrated matrix with finite nonsingular diagonal row/column scalings.

Exact rank is invariant under all finite nonsingular scalings, but singular values and condition numbers are not.

Therefore:

- any physical/functional rank verdict must be based on `J_hat` plus an uncertainty estimate tied to the derivative construction;
- `J_eq` may be used for linear-solver conditioning diagnostics or preconditioning only;
- a PASS obtained only after equilibration is not admissible as a physical-rank PASS;
- both `kappa_2(J_hat)` and, if used, `kappa_2(J_eq)` must be reported separately.

## 7. Functional derivative QA

For a future candidate background, construct `J_hat` by one of two provenance-declared methods:

### A. Analytic/automatic differentiation

The derivative implementation must be tested against directional finite differences on the same fixed discrete branch.

### B. Central finite differences

For each dimensionless variable direction `e_j`, use symmetric perturbations

`J_hat[:,j;h] = [R_hat(u_hat+h_j e_j)-R_hat(u_hat-h_j e_j)]/(2 h_j)`

at at least three nested step levels `h`, `h/2`, `h/4`.

No perturbation may change `(N_F,m_layer,n_N,n_S)` or cross a pole-regularity/topology branch.

## 8. Derivative uncertainty and rank separation

Define a matrix uncertainty estimate from the disagreement of independently converged derivative levels, for example

`epsilon_J = max(||J_h-J_h2||_2, ||J_h2-J_h4||_2)`

after all matrices are expressed in the same canonical dimensionless normalization.

The exact numerical formula and safety multiplier for a later executable rank gate must be separately frozen before physical use; this block does not invent a numerical threshold.

A future rank-10 claim requires at minimum:

- derivative convergence/plateau in the fixed branch;
- finite `J_hat` with no nonfinite entries;
- `sigma_10(J_hat)` demonstrably separated from the derivative/noise uncertainty by a preregistered margin;
- stability of the conclusion under the declared derivative refinement;
- explicit reporting of the full singular spectrum and `kappa_2(J_hat)`.

A small but nonzero singular value is not by itself evidence of a robust rank-10 operator if it is comparable to derivative uncertainty.

## 9. Schur-complement QA in the normalized basis

Partition `J_hat` with the same `8+2` split as G3.6:

`J_hat = [[J8_hat,B_hat],[C_hat,D_hat]]`.

If `J8_hat` is nonsingular,

`S_hat = D_hat-C_hat J8_hat^(-1) B_hat`

and

`det(J_hat)=det(J8_hat) det(S_hat)`.

A future QA report must distinguish:

- inherited near-null directions in `J8_hat`,
- raw amplitude-transfer weakness in `D_hat`,
- backreaction-induced near-null directions in `S_hat`,
- global near-null directions visible only in the full SVD of `J_hat`.

The Schur complement is diagnostic decomposition, not a replacement for the full 10x10 SVD.

## 10. Fail-closed conditions

No rank verdict is allowed if any of the following occurs:

- discrete patch/winding sector changes across derivative samples;
- a perturbed trajectory leaves the regular pole branch;
- one or more required BVP evaluations fails or is nonfinite;
- derivative levels do not converge sufficiently to define an uncertainty estimate;
- normalization uses a zero/nonfinite scale;
- rank appears only after undocumented adaptive rescaling/equilibration;
- the boundary operator differs from the frozen G3.6/G3.5 parent contract.

## 11. What is proven

**[BEWIESEN]** The displayed row and column scales make all ten residuals and all ten continuous variables dimensionless.

**[BEWIESEN]** `J_hat=D_R^-1 J10 D_U` has exactly the same mathematical rank as `J10` for finite positive `M6`.

**[BEWIESEN]** Frobenius-amplitude scaling depends on `|n_N|,|n_S|`.

**[BEWIESEN]** numerical equilibration can change singular values/conditioning but not exact rank; therefore it must be separated from the canonical physical normalization.

**[OFFEN]** actual derivative convergence, singular values, condition number and rank at a physical solution.

## 12. Verdict

`G3_7_DIMENSION_TABLE = PASS`

`G3_7_CANONICAL_ROW_NORMALIZATION = PASS_ANALYTIC`

`G3_7_CANONICAL_COLUMN_NORMALIZATION = PASS_ANALYTIC`

`G3_7_DIMENSIONLESS_JACOBIAN = J_hat=D_R^-1*J10*D_U`

`G3_7_EXACT_RANK_INVARIANCE_UNDER_CANONICAL_SCALING = PASS_ANALYTIC`

`G3_7_EQUILIBRATION_FIREWALL = FROZEN`

`G3_7_FUNCTIONAL_JACOBIAN_QA_METHOD = DEFINED_NO_PHYSICAL_EVALUATION`

`ACTUAL_10x10_JACOBIAN_RANK = OPEN_NOT_EVALUATED`

`PHYSICAL_EXECUTION_AUTHORIZED = FALSE`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`

No physical evidence claim follows from this normalization/QA block.