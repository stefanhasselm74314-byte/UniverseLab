# MD-2N through MD-2Q Package Rigor Audit v0.1

**Date:** 2026-08-01  
**Source archive:** `MD2N.zip`  
**Source SHA-256:** `28f91e7081cc3dca0f1e225c6e203e2d66af53298a4202f956fae69322dadba3`  
**Governance:** MD-0 / HPVS  
**Status:** AUDIT COMPLETED / PHYSICAL RELEASE UNCHANGED  
**Evidence effect:** NONE

## 1. Executive decision

The archive is a substantial and useful recovery of the HZT-M0 K1 bridge-development chain. It contains executable diagnostic code, numerical outputs, reports and nested predecessor packages covering MD-2A through MD-2Q, with two important provenance gaps: MD-2J is present only as a reported-status stub, and the original rejected MD-2P artifact is absent.

The package supports the following statements:

1. The MD-2N reduced effective mapping is technically executable and its recorded raw Jacobian condition number `1.8957468008439005` is reproducible.
2. The later claim of a condition number near `89575` is unsupported for MD-2N and was correctly rejected by MD-2O.
3. The corrected MD-2P-corr bounded amplitude formula has the stated asymptotic behavior and the MD-2Q numerical values are reproducible from that formula.
4. MD-2Q is a one-control trajectory through an effective ansatz. Its condition number of `1.0` is algebraically automatic for any nonzero one-column Jacobian and carries no multi-parameter identifiability content.
5. The archive does not close the fundamental physical map `P_phys -> P_mod`, does not release K1-D, and does not supply evidence for HZT-M0.

Canonical gate state remains:

```text
K1-D = NOT RELEASED
K1-E = NOT ADMISSIBLE
MD-2N = QUARANTINED TECHNICAL BASELINE
MD-2Q = QUARANTINED EFFECTIVE-CANDIDATE DRY RUN
Evidence effect = NONE
```

## 2. Archive structure and provenance

### 2.1 Recovered chain

The nested packages recover:

```text
MD-2A -> MD-2B -> MD-2C -> MD-2D -> MD-2E
      -> MD-2F -> MD-2G -> MD-2H -> MD-2I
      -> [MD-2J status stub] -> MD-2K -> MD-2L
      -> MD-2M -> MD-2N -> MD-2O
      -> [MD-2P original absent/rejected]
      -> MD-2P-corr -> MD-2Q -> [MD-2R absent]
```

The chain is scientifically valuable because it preserves negative and quarantine decisions instead of silently promoting diagnostic outputs.

### 2.2 Semantic duplication

The archive includes exact content duplicates under different wrapper/root names for MD-2N, MD-2O and MD-2Q. The long-name and short-name MD-2P-corr cores are likewise content-identical. These duplicates should be replaced by one canonical package plus an alias table in a future archive normalization pass.

### 2.3 Provenance gaps

- **MD-2J:** only `MD2J_reported_status_input.md` exists. The full bridge-contract artifact is absent.
- **MD-2P original:** only the rejected formula and rejection reason are preserved in MD-2P-corr.
- **MD-2R:** named as the successor of MD-2Q but not included.

Consequently, MD-2K may rely on the reported MD-2J status operationally, but the full MD-2J contract content is not independently auditable from this archive.

## 3. MD-2N numerical audit

## 3.1 Mapping

MD-2N uses the locked effective mapping

```text
k_c = m_eff / omega_c_eff,
A(k) = exp[-(k/k_c)^s],
mu_red(k) = 1 + eta_eff A(k),
Sigma_red(k) = 1 + 0.5 eta_eff A(k),
P_mod/P_phys = mu_red(k).
```

with

```text
m_eff = 0.055 Mpc^-1,
omega_c_eff = 1,
s = 2,
eta_eff = 0.08.
```

The run contains no data vector, covariance, likelihood or posterior. It is therefore a mapping smoke test.

## 3.2 Analytic derivatives

Let

```text
z = (k omega_c/m)^s,
A = exp(-z),
P = 1 + eta A.
```

For fixed `omega_c` and `s`,

```text
partial P / partial eta = A,
partial P / partial m = eta A s z / m.
```

The delivered finite-difference Jacobian agrees with these derivative structures.

## 3.3 Recomputed singular values

For the delivered 128-point logarithmic `k` grid, the raw two-column Jacobian has

```text
sigma_1 = 7.30945429,
sigma_2 = 3.85571232,
kappa_2(J) = sigma_1/sigma_2
           = 1.8957468008439005.
```

This reproduces the MD-2N package and validates MD-2O's provenance correction.

However, the condition number is not invariant under parameter redefinition. The same columns yield approximately

```text
column-normalized kappa_2 = 1.77957819,
log-parameter kappa_2     = 2.42176593.
```

A physical K1 condition number would additionally require:

- a released physical parameter chart,
- parameter scales or priors,
- observable covariance/whitening,
- a defined inner product,
- and the complete `P_phys -> P_mod -> O` map.

Thus the MD-2N value is numerically correct but physically non-evidential.

## 4. MD-2P-corr mathematical audit

## 4.1 Candidate formula

The corrected candidate defines

```text
gamma = 2 alpha + 1/sigma_B^2,
R_chi = 4/(kappa_6^2 lambda_chi),
x = gamma R_chi^2
  = 16 gamma/(kappa_6^4 lambda_chi^2),
q = 1 - exp(-x),
eta_bulk = beta_0 q(1-q).
```

The filter and reduced responses are

```text
A(k) = exp[-(k/m_eff)^s],
mu_red = 1 + eta_bulk A(k),
Sigma_red = 1 + 0.5 eta_bulk A(k).
```

## 4.2 Dimensional contract

The expression is dimensionally consistent only under the explicit convention

```text
[kappa_6] = L^2,
[kappa_6^2] = L^4,
[lambda_chi] = L^-5,
[R_chi] = L,
[alpha] = L^-2,
[sigma_B] = L,
[gamma] = L^-2,
[x] = 1.
```

The package lists `kappa_6 = 1.0` in effective/model units while assigning Mpc units to the other quantities. This is insufficient for a physical unit contract. The numerical run is valid only in a declared nondimensionalized convention that is not fully supplied.

## 4.3 Exact asymptotics

For `lambda_chi -> infinity`,

```text
x -> 0,
q = x + O(x^2),
eta_bulk = beta_0 x + O(x^2)
         = 16 beta_0 gamma/(kappa_6^4 lambda_chi^2)
           + O(lambda_chi^-4).
```

For `lambda_chi -> 0`,

```text
x -> infinity,
1-q = exp(-x),
eta_bulk = beta_0[exp(-x) - exp(-2x)]
         ~ beta_0 exp(-x).
```

The amplitude is bounded:

```text
0 <= eta_bulk <= beta_0/4.
```

The maximum occurs at

```text
q = 1/2,
x = ln 2,
lambda_chi,* = 4 sqrt(gamma/(kappa_6^4 ln 2)).
```

For the MD-2Q locked values, this gives

```text
lambda_chi,* = 4.7911252431,
eta_bulk,max = 0.025.
```

The reported scan maximum `0.0249975319` near `lambda_chi = 4.8256651` is therefore a finite-grid approximation to the exact maximum.

## 4.4 Physical interpretation limit

The boundedness and asymptotics are mathematically correct. They do not derive the bridge from the 6D action.

In particular:

- `q=1-exp(-x)` is labelled a volume quotient, but no equality to a derived warp-volume or overlap integral is proved in this package.
- `eta_bulk=beta_0 q(1-q)` is a deliberately constructed bounded interpolant.
- `beta_0` remains an uncalibrated amplitude constant.
- the formula does not derive the observable normalization `N_4`.

Therefore the correct status is:

```text
EFFECTIVE BRIDGE ANSATZ WITH PHYSICAL SEMANTIC MOTIVATION
```

not a derived physical bridge.

## 5. MDS coverage audit

The MD-2P-corr/MD-2Q path does not close the MD-2I minimal derivation set.

| MDS | Required edge | Actual archive result | Status |
|---|---|---|---|
| MDS-01 | `R_chi -> m` | `m_eff=0.055 Mpc^-1` remains locked and is not derived from the candidate `R_chi` | OPEN |
| MDS-02 | `beta_tau,I_B,kappa_6 -> omega_c` | `omega_c` is removed/frozen effectively by using `A(k)=exp[-(k/m_eff)^s]` | OPEN / BYPASSED |
| MDS-03 | `a0,beta_tau,I_B -> eta` | replaced by candidate `lambda_chi,alpha,sigma_B,kappa_6,beta_0 -> eta_bulk` | ALTERNATIVE EFFECTIVE ANSATZ, NOT DERIVED |
| MDS-04 | `R_chi,beta_tau -> s` | `s=2` fixed | FIXED EFFECTIVE |
| MDS-05 | `kappa_6 -> N_4` | no 6D-to-4D Planck/observable normalization is derived | OPEN |

The `mds05_status` field in MD-2P-corr is therefore misleading. Dependence of an amplitude ansatz on `kappa_6` is not the same as deriving the 4D normalization bridge.

## 6. MD-2Q audit

## 6.1 Reproduction

For

```text
alpha = 0.15 Mpc^-2,
sigma_B = 1.2 Mpc,
kappa_6 = 1 effective unit,
beta_0 = 0.1,
lambda_chi = 4.25 Mpc^-5,
```

one obtains

```text
gamma = 0.9944444444444445,
x = 0.8808919646289889,
q = 0.5855868950525662,
eta_bulk = 0.024267488339526102.
```

These values and the analytic/finite-difference derivative agreement are reproducible.

## 6.2 One-column condition number

MD-2Q varies one control parameter and produces a Jacobian with shape `(128,1)`. For a nonzero matrix with one column, there is one nonzero singular value and

```text
kappa_2(J) = sigma_max/sigma_min = 1.
```

This is a linear-algebra identity, not a demonstration that the physical model is well conditioned.

The only defensible result is that the selected one-dimensional trajectory has a nonzero local response under the locked ansatz.

## 6.3 Identifiability boundary

MD-2Q cannot determine:

- rank of the full physical Jacobian,
- degeneracy between `lambda_chi`, `alpha`, `sigma_B`, `kappa_6`, `beta_0`, `m_eff` and `s`,
- covariance-weighted observability,
- global injectivity,
- or physical interpretation of the effective amplitude.

Its output is a quarantined one-control sensitivity test.

## 7. Reproducibility and package-integrity audit

### 7.1 Strengths

- Reports, status JSON, audit CSVs, source snippets and numerical output tables are preserved together.
- All 12 unique Python files compile.
- MD-2N and MD-2Q formula-level numerical outputs can be independently recomputed.
- The package explicitly forbids evidence and K1 release claims.

### 7.2 Defects

1. Module manifests contain paths and sizes but no SHA-256 hashes.
2. Several manifests list their own `MANIFEST.csv` size as zero although the file is nonzero.
3. Both MD-2P-corr manifests list large reference ZIPs that are absent from the delivered cores.
4. No environment lock specifies Python, NumPy or plotting/report-generation versions.
5. The included MD-2N and MD-2Q source files do not regenerate the complete delivered CSV/PNG/DOCX/PDF package.
6. No single run command and immutable run ID reconstructs all outputs.
7. Duplicate wrapper packages substantially inflate the archive and complicate source-of-truth selection.

Hence:

```text
formula-level reproducibility = PASS
selected numerical values     = PASS
end-to-end package rebuild    = FAIL / NOT PROVIDED
cryptographic provenance      = PARTIAL
```

## 8. Theory-skeleton assessment

### Postulates

The archive assumes a Gaussian spectral filter and later a bounded amplitude function. These are effective model choices, not consequences of the current 6D parent action.

### Dynamics

No bulk field equations, background solution or perturbation reduction is solved in MD-2N through MD-2Q.

### Observables

`mu_red(k)` and `Sigma_red(k)` are diagnostic response curves. They are not yet linked to a released cosmological perturbation system, matter species, gauge choice, initial conditions or survey likelihood.

### Tests and falsification

The dry runs test software finiteness, derivative consistency and local sensitivity. They do not test the physical 6D model against data.

## 9. Canonical disposition

### Retain

- MD-2A through MD-2Q as a valuable audit-history corpus.
- MD-2N as a technical baseline.
- MD-2O's correction of the false `89575` condition-number claim.
- MD-2P-corr as an explicitly heuristic bounded ansatz.
- MD-2Q as a verified one-control diagnostic.

### Downgrade or relabel

- `unified physical bridge` -> `bounded effective bridge candidate`.
- `volume quotient` -> `candidate bounded overlap/volume-response coordinate` until derived.
- MD-2Q `condition number = 1` -> `one-column identity; no conditioning conclusion`.
- `mds05_status` -> OPEN unless a true `kappa_6 -> N_4` reduction is supplied.

### Block

- K1-D release.
- K1-E ratification.
- data fitting as HZT-M0 evidence.
- use of MD-2Q to claim full physical identifiability.
- promotion of `beta_0`, `m_eff` or `s` to derived 6D quantities.

## 10. Required successor

Before any MD-2R release review, the successor must perform two separate audits:

1. **Bridge-origin audit**  
   Derive or explicitly classify each parameter entering `eta_bulk`, `m_eff`, `s` and the normalization.

2. **Multi-parameter rank audit**  
   Construct a dimensionless or prior-whitened Jacobian for every physically admissible control, report the complete singular spectrum and separate structural from observational rank.

The preferred research route remains the current parent-action and MD-2S recovery path:

```text
6D parent action
-> regular background and boundary closure
-> normalized mode spectrum and warp volume
-> physical bridge coefficients
-> released forward map
-> covariance-weighted K1 audit.
```
