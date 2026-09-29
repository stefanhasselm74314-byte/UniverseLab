# ULSH-01 / C-PHYS — Background3C5 G2 Regular Center Closure v0.4

**Supersedes:** v0.3 status only; derivations remain append-only.  
**Status:** PASS_ANALYTIC_AND_SOFTWARE_REGRESSION_QA  
**Physical evidence effect:** NONE  
**K1-D:** NOT_RELEASED  
**K1-E:** NOT_ADMISSIBLE

## Ratified G2 state

The following are now jointly established for the canonical-variable development path:

- regular north-axis variables: `x=M6*r`, `ell=M6*L`, `varphi=phi/M6^2`, `a_chi=A_chi/M6`;
- frozen frame `A(0)=0` and regular angular slope `ell_x(0)=1`;
- Frobenius exponent `s_hat ~ x^abs(n)` for `n!=0`;
- six-dimensional layer amplitude normalization `[s]=M^2`, hence `s_hat=s/M6^2`;
- `mSigma_hat^2=mSigma^2/M6^2`, `lambdaSigma_hat=lambdaSigma*M6^2`, `Lambda_layer_hat=Lambda_layer/M6^6`;
- exact bulk-control pole coefficients `(a2,f2,g2,l3)`;
- local free-data budget `(f0,g2,s_p)` at fixed `k4` for `n!=0`, or `(f0,g2,s0)` for `n=0`;
- no continuous conical-rescue parameter.

## Observed executable QA

GitHub Actions workflow:

`ULSH-01 Background3C5 canonical operator v0.2 QA`

Run ID: `31927952864`

Job ID: `95118325800`

Conclusion: `success`.

The observed successful steps include:

- Python compilation;
- G2 regression suite;
- fail-closed governance enforcement.

This validates implementation consistency of the G2 candidate library; it does not establish a global nonlinear background.

## Remaining operator-identity gate

G2 is no longer the critical blocker. The next blocker is G5/full finite-thickness parent equivalence, including:

1. exact dimensionless Maxwell current coefficient for the evolving internal flux;
2. full finite-thickness contributions to the three Einstein equations;
3. scalar source induced by any `phi` dependence of `Lambda_layer` and `mSigma^2`;
4. constraint propagation for the complete coupled residual system;
5. bulk-control regression when the layer is removed;
6. proof that the numerical residual vector is algebraically the Euler-Lagrange system of the frozen parent action.

## Gate disposition

`G2_REGULAR_CENTER = PASS_ANALYTIC_AND_SOFTWARE_REGRESSION_QA`

`G3_OUTER_MATCHING = OPEN`

`G4_CONSTRAINT_PROPAGATION = OPEN`

`G5_OPERATOR_IDENTITY = OPEN_CRITICAL`

`PHYSICAL_BACKGROUND = NOT_ESTABLISHED`

`PHYSICAL_RESPONSE_RANK_R = NOT_EXECUTED`

`K1-D = NOT_RELEASED`

`K1-E = NOT_ADMISSIBLE`
