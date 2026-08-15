# ULSH-01 / C-PHYS — Physical Response-Rank Gate v1.0

Status: **SPECIFICATION / NOT YET PHYSICALLY EXECUTED**  
Architecture: `HPVS → HZT-M0 → S6 → C-PHYS → ULSH-01`  
Governance: `K1-D = NOT_RELEASED`, `K1-E = NOT_ADMISSIBLE`

## 0. Decision boundary

The finite-thickness flux-winding layer has already passed the **local structural** audits (`rank B_stress = 3`, structural control rank `rank S = 4`). This document defines the missing **global physical BVP response-rank** gate. A PASS here is necessary for Background-3C5 authorization, but is not sufficient for ghost freedom, dynamical stability, phenomenological viability, or K1-D release.

## 1. Fixed branch and variables

Hold the discrete branch labels fixed during every Jacobian evaluation:

- winding integer `n`: fixed;
- flux integer `N`: fixed.

They are branch labels, not Jacobian columns.

Canonical continuous controls at fixed `(n,N)`:

`c = (Λ6/Λref, Λlayer/Λref, mΣ²/mref², gΣ, λΣ)`.

Canonical four-component target/output vector:

`y = (δβ/β, δΞ, δUumb, δm0² Rcap²)`.

with `Ξ = ρcap/RK` and `Uumb = A' - L'/L` as defined by the C-PHYS cap audit.

The physical response matrix is

`R_ai = ∂y_a/∂c_i`,

so `R ∈ R^(4×5)`. The required row rank is 4.

## 2. Central finite differences

For each continuous control `c_i`, with unit vector `e_i`, solve the full nonlinear BVP at

`c0 ± h_i e_i`, `c0 ± (h_i/2)e_i`, `c0 ± (h_i/4)e_i`.

Then

`R_ai(h_i) ≈ [y_a(c0+h_i e_i) - y_a(c0-h_i e_i)]/(2 h_i)`.

For a smooth branch the truncation error is `O(h_i²)`. BVP/roundoff noise is amplified approximately as `O(ε_BVP/h_i)`. Consequently `h → 0` is **not** automatically better; the valid regime is an intermediate convergence plateau.

### Richardson consistency

For a central difference,

`R*_i ≈ [4 R_i(h/2) - R_i(h)]/3`.

In the asymptotic second-order regime the successive differences should satisfy approximately

`||R(h)-R(h/2)|| / ||R(h/2)-R(h/4)|| → 4`.

Failure of this ratio to approach the second-order regime is a diagnostic warning, not by itself a rank FAIL.

## 3. Mandatory dimensionless normalization

A raw SVD of a dimensioned/scaled Jacobian is not invariant under a change of units. Therefore the gate is evaluated on a fixed dimensionless Jacobian.

Define diagonal scale matrices

`Sc = diag(s_c,1,…,s_c,5)` and `Sy = diag(s_y,1,…,s_y,4)`

with scales frozen before the run. Define

`ĉ = Sc^(-1)(c-c0)`, `ŷ = Sy^(-1)(y-y0)`.

Then

`J = ∂ŷ/∂ĉ = Sy^(-1) R Sc`.

Preferred scales are physical admissibility/tolerance scales. If such scales are not yet physically fixed, use documented characteristic reference scales and perform a scale-sensitivity audit. A formal full rank that disappears under reasonable pre-declared scale choices is **INCONCLUSIVE**, not PASS.

## 4. SVD and uncertainty-aware rank

Compute

`J = U Σ V^T`, `Σ = diag(σ1,…,σ4)`, `σ1 ≥ … ≥ σ4 ≥ 0`.

Formal row rank 4 requires `σ4 > 0`, but floating-point arithmetic requires an uncertainty-aware criterion. Let `δJ` denote the empirical Jacobian uncertainty estimated from step refinement and solver-tolerance refinement. Use

`ε_J = ||δJ||_2`.

Weyl's bound implies that each singular value can shift by at most `ε_J`. Therefore a defensible numerical separation requires

`σ4 > q ε_J`,

where `q` is a governance safety factor frozen before inspecting the final result. Recommended default for this gate: `q = 5` (conservative engineering criterion; not a theorem).

Also report

`κ2(J) = σ1/σ4`.

The historical provisional gate `κ ≤ 10^6` is retained as a conditioning guardrail, but it is evaluated on **J**, not the raw dimensioned `R`.

## 5. Branch-continuity firewall

Every `±h` solution must remain on the same physical branch as the baseline. Required checks:

1. same discrete `(n,N)`;
2. same node/topology class of `s(r)` and gauge profile;
3. smooth center preserved: `L(0)=0`, `L'(0)=1`, `A'(0)=0`, `φ'(0)=0`, and for `n≠0`, `s(0)=0`;
4. no conical rescue mode;
5. simultaneous metric/scalar/gauge outer matching;
6. flux quantization preserved;
7. continuation/homotopy trace does not jump to a disconnected solution branch.

A derivative formed across two different branches is invalid and cannot contribute to rank.

## 6. Local linearity diagnostic

For each control define

`Q_i(h) = y(c0+h e_i) + y(c0-h e_i) - 2 y(c0)`.

A dimensionless nonlinearity indicator is

`η_i(h) = ||Sy^(-1) Q_i(h)||_2 / max(||Sy^(-1)[y(c0+h e_i)-y(c0-h e_i)]||_2, ε_floor)`.

For a smooth locally linear response, `η_i(h) = O(h)` and decreases under step halving. Persistent or increasing `η_i` flags a nonlinear/branch regime in which the first-order rank interpretation is not reliable.

## 7. Gate outcomes

### PASS — `PHYSICAL_RESPONSE_RANK_4_CONFIRMED`

All conditions must hold simultaneously:

- all baseline and perturbed BVPs satisfy regularity/matching physics gates;
- fixed discrete branch throughout;
- derivatives reach a stable step-refinement plateau;
- verdict is stable under at least one stricter BVP tolerance/regulator setting;
- dimensionless `J` has row rank 4;
- `σ4 > q ε_J`;
- `κ2(J) ≤ 10^6`;
- no singular-value/rank verdict changes under step halving;
- smallest-singular-direction is stable under refinement (principal-angle check);
- `m0² ≥ 0`, reduced kinetic matrix positive, off-shell tube valid.

### BLOCKED — `PHYSICAL_RESPONSE_RANK_DEFICIENT`

Use only when a converged, branch-consistent calculation robustly yields row rank `<4`, e.g. `σ4` collapses toward the numerical uncertainty floor under refinement. This blocks the finite-thickness candidate as the missing global control channel at that benchmark/branch.

### INCONCLUSIVE — `NUMERICAL_OR_BRANCH_RESOLUTION_INSUFFICIENT`

Use when the BVP does not converge reproducibly, branch continuity fails, derivative convergence is absent, or `σ4` is not separated from `ε_J`. **INCONCLUSIVE must never be relabeled as rank deficiency.**

## 8. Inverse-function interpretation

If the relevant 4×4 response submap has nonzero determinant and the BVP solution map is `C¹`, the inverse-function theorem gives a **local** inverse near the benchmark. For the 4×5 map, full row rank implies local surjectivity onto the four target directions (submersion theorem). It does not imply global uniqueness of controls.

Thus a PASS establishes only:

`local physical controllability of the four target directions on the tested branch`.

It does **not** establish:

- global existence/uniqueness;
- ghost freedom;
- nonlinear dynamical stability;
- observational fit;
- 6D→4D physical identifiability;
- K1-D or K1-E release.

## 9. Asymptotic regimes

- **Large h:** nonlinear/truncation error dominates; central derivative biased by curvature of the solution map.
- **Intermediate h:** desired convergence plateau; `O(h²)` behavior visible and BVP noise subdominant.
- **Small h:** cancellation and BVP tolerance noise dominate as `~ε_BVP/h`; apparent rank can fluctuate or collapse.
- **σ4/σ1 → 0:** formally near-degenerate control map; even if algebraic rank is four, practical controllability/identifiability becomes poor.

## 10. Required evidence bundle

A Background-3C5 authorization review must archive:

- baseline control vector and branch labels;
- solver version/commit and numerical tolerances;
- all `±h`, `±h/2`, `±h/4` run manifests;
- raw outputs `y` and physics-gate flags;
- raw `R(h)` matrices;
- frozen `Sc`, `Sy` scales and rationale;
- normalized `J(h)` matrices;
- singular values, condition numbers, left-nullspace and right-singular directions;
- step/refinement and solver-tolerance uncertainty estimate `ε_J`;
- branch-continuity evidence;
- final machine-readable verdict.

Until this evidence bundle exists, status remains:

`GLOBAL BVP RESPONSE RANK = OPEN`  
`K1-D = NOT_RELEASED`  
`K1-E = NOT_ADMISSIBLE`
