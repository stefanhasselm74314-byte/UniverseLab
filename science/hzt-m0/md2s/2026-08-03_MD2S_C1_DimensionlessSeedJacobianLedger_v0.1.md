# HZT-M0-S6-C1 — Dimensionslose Gleichungen, exakter Anker und AD-Jacobian v0.1

**Datum:** 2026-08-03  
**Status:** `DIAGNOSTIC_JACOBIAN_PREFLIGHT_PASS_EXECUTION_BLOCKED`  
**Evidenzwirkung:** `NONE`  
**Historische A0-Identität:** `NOT_CLAIMED`  
**Solver:** `NOT_AUTHORIZED`

## 1. Zweck und Evidenzgrenze

Dieser Block schließt für den neu definierten Kandidatenzweig `HZT-M0-S6-C1` vier formale Lücken:

1. eine eindeutige dimensionslose Variablenabbildung,
2. einen vorab festgelegten normierten Residualvektor,
3. einen exakt lösbaren analytischen C1-Anker,
4. einen tatsächlichen, durch Forward-Mode-Automatic-Differentiation erzeugten `8 x 8`-Jacobian der diskretisierten IVP-zu-Randresiduum-Abbildung.

Der Block enthält **keinen Nullstellensolver**, keine Parametersuche und keine physikalische Freigabe. Ein voller Rang des diskretisierten Jacobians am Anker ist weder ein Existenzbeweis für weitere Lösungen noch ein Stabilitäts- oder Ghostfreiheitsnachweis.

## 2. Referenzskala

Aus

\[
[\kappa_6^2]=M^{-4}
\]

wird die positive Referenzskala

\[
\mu_6=(\kappa_6^2)^{-1/4}
\]

definiert. Damit gilt

\[
\kappa_6^2\mu_6^4=1.
\]

Die dimensionslosen Variablen lauten

\[
x=\mu_6 r,
\qquad
\ell=\mu_6 L,
\qquad
\varphi=\frac{\phi}{\mu_6^2},
\]

\[
q=\frac{Q}{\mu_6^3},
\qquad
a_\chi=\frac{A_\chi}{\mu_6},
\qquad
k_4=\frac{\mathcal K_4}{\mu_6^2}.
\]

Für die Modellparameter gilt

\[
\hat\Lambda=\frac{\Lambda_{\rm geom}}{\mu_6^2},
\quad
u_0=\frac{U_0}{\mu_6^6},
\quad
m^2=\frac{m_\phi^2}{\mu_6^2},
\quad
\varphi_\star=\frac{\phi_\star}{\mu_6^2},
\]

\[
\hat\lambda_0=\frac{\lambda_0}{\mu_6^5},
\quad
\hat\lambda_1=\frac{\lambda_1}{\mu_6^3},
\quad
z_\sigma=\frac{Z_{\sigma0}}{\mu_6^3},
\quad
\hat q_0=\mu_6 q_0.
\]

## 3. Dimensionslose C1-Gleichungen

Das Potential ist

\[
u(\varphi)=u_0+\frac12m^2(\varphi-\varphi_\star)^2.
\]

Mit

\[
\widehat{\mathcal M}=q^2e^{-8A}
\]

folgt aus der internen Einstein-Gleichung

\[
A_{xx}
=
\frac{-10A_x^2+6k_4e^{-2A}-\hat\Lambda-rac12\varphi_x^2-u+rac12\widehat{\mathcal M}}{4}.
\]

Die externe Einstein-Gleichung liefert

\[
\ell_{xx}
=
\ell\left[
-3A_{xx}-6A_x^2-3A_x\frac{\ell_x}{\ell}
+3k_4e^{-2A}-\hat\Lambda-rac12\varphi_x^2-u-rac12\widehat{\mathcal M}
\right].
\]

Die skalare Gleichung lautet

\[
\varphi_{xx}
=
-\left(4A_x+\frac{\ell_x}{\ell}\right)\varphi_x
+m^2(\varphi-\varphi_\star).
\]

Das Maxwell-Erstintegral wird als erste Ordnung für das Patchpotential geschrieben:

\[
a_{\chi,x}=q\ell e^{-4A}.
\]

Der nicht als zusätzliche Randbedingung gezählte Constraint ist

\[
\mathcal C_{rr}
=
6A_x^2+4A_x\frac{\ell_x}{\ell}
-6k_4e^{-2A}+\hat\Lambda
-\frac12\varphi_x^2+u-rac12\widehat{\mathcal M}.
\]

## 4. Reguläre Polentwicklung

Nahe einem glatten Pol wird bei `Delta_chi=2 pi` angesetzt:

\[
A=A_0+a_2x^2+O(x^4),
\]

\[
\ell=x\left(1+c_2x^2+O(x^4)\right),
\]

\[
\varphi=\varphi_0+p_2x^2+O(x^4),
\]

\[
a_\chi=\frac12q e^{-4A_0}x^2+O(x^4).
\]

Mit

\[
k_c=k_4e^{-2A_0},
\qquad
M_0=q^2e^{-8A_0}
\]

gilt

\[
a_2=rac{6k_c-\hat\Lambda-u(\varphi_0)+\frac12M_0}{8},
\]

\[
c_2=rac{u(\varphi_0)}{12}-\frac{5M_0}{24}-k_c+\frac{\hat\Lambda}{12},
\]

\[
p_2=\frac{m^2(\varphi_0-\varphi_\star)}{4}.
\]

## 5. Residualvektor und feste Normierung

Der Schießvektor ist

\[
X=
(\varphi_{N0},q_N,A_{S0},\varphi_{S0},q_S,\rho_N,\rho_S,k_4).
\]

Der rohe Randresidualvektor ist

\[
R=(R_A,R_L,R_\varphi,R_{\rm patch},R_{4D},R_\chi,R_{\rm scalar},R_{\rm gauge}).
\]

Für Off-Shell-Auswertungen werden die Kappenwerte in lokalisierten Termen symmetrisch gemittelt:

\[
\bar A=\frac{A_N+A_S}{2},
\quad
\bar\ell=\frac{\ell_N+\ell_S}{2},
\quad
\bar\varphi=\frac{\varphi_N+\varphi_S}{2}.
\]

Der Wicklungsinvariant wird im Nordpatch ausgewertet:

\[
d_\chi=N_\sigma-\hat q_0 a_{\chi,N},
\qquad
Y_\sigma=z_\sigma\frac{d_\chi^2}{\bar\ell^2}.
\]

Die acht Residuen sind

\[
R_A=A_N-A_S,
\qquad
R_L=\ell_N-\ell_S,
\qquad
R_\varphi=\varphi_N-\varphi_S,
\]

\[
R_{\rm patch}=a_{\chi,N}-a_{\chi,S}-\frac{N_F}{\hat q_0},
\]

\[
R_{4D}=-(3A_\Sigma+L_\Sigma)+\hat\lambda+\frac12Y_\sigma,
\]

\[
R_\chi=-4A_\Sigma+\hat\lambda-\frac12Y_\sigma,
\]

\[
R_{\rm scalar}=\varphi_{x,N}+\varphi_{x,S}+\hat\lambda_1,
\]

\[
R_{\rm gauge}
=
\frac{e^{-4\bar A}}{\bar\ell}(q_N+q_S)
-\hat q_0z_\sigma\frac{d_\chi}{\bar\ell^2}.
\]

Dabei

\[
A_\Sigma=A_{x,N}+A_{x,S},
\qquad
L_\Sigma=\frac{\ell_{x,N}}{\ell_N}+\frac{\ell_{x,S}}{\ell_S},
\]

\[
\hat\lambda=\hat\lambda_0+\hat\lambda_1(\bar\varphi-\varphi_\star).
\]

Die Normierung ist vor der Jacobian-Auswertung fixiert:

\[
S=(1,1,1,1,1,1,1,2),
\qquad
\widetilde R_i=R_i/S_i.
\]

Lösungsabhängige Skalen sind verboten, weil sie selbst zusätzliche Ableitungen in den Jacobian einführen und den Rangvergleich verschleiern würden.

## 6. Exakter analytischer C1-Anker

Es wird gesetzt:

\[
\hat\Lambda=1,
\quad
u_0=\frac58,
\quad
m^2=1,
\quad
\varphi_\star=0,
\]

\[
\hat\lambda_0=0,
\quad
\hat\lambda_1=0,
\quad
z_\sigma=1,
\quad
\hat q_0=2,
\]

\[
N_\sigma=1,
\qquad
N_F=2.
\]

Der Schießvektor lautet

\[
X_\star=
\left(0,\frac12,0,0,-\frac12,\frac\pi2,\frac\pi2,\frac14\right).
\]

Die exakten Profile sind

\[
A_N=A_S=0,
\qquad
\varphi_N=\varphi_S=0,
\]

\[
\ell_N=\ell_S=\sin x,
\]

\[
a_{\chi,N}=\frac12(1-\cos x),
\qquad
 a_{\chi,S}=-\frac12(1-\cos x).
\]

An der Kappe `x=pi/2` gilt

\[
\ell=1,
\quad
\ell_x=0,
\quad
A_x=0,
\quad
\varphi_x=0,
\]

\[
a_{\chi,N}=\frac12,
\qquad
 a_{\chi,S}=-\frac12.
\]

Damit folgen gleichzeitig

\[
R_{\rm patch}=\frac12-\left(-\frac12\right)-\frac22=0,
\]

\[
d_\chi=1-2\cdot\frac12=0,
\]

\[
A_\Sigma=L_\Sigma=Y_\sigma=\hat\lambda=0.
\]

Somit verschwinden alle acht Randresiduen exakt. Geometrisch ist dies eine glatte Einheits-Zweikugel in zwei regulären Gauge-Patches; die gemeinsame Kappe ist am Anker eine spannungsfreie Matchingfläche.

## 7. Diskretisierung und Automatic Differentiation

Der Referenzevaluator startet bei

\[
\varepsilon=10^{-5}
\]

mit der Polserie und integriert jede Region mit klassischem festem RK4. Es wird **keine** Nullstellensuche ausgeführt.

Der Jacobian

\[
J_{ij}=\frac{\partial\widetilde R_i}{\partial X_j}
\]

wird durch Forward-Mode-Automatic-Differentiation erzeugt. Jede Schießgröße trägt einen achtkomponentigen Tangentialvektor; sämtliche RK4-Stufen, Mittelpunktbildungen und Randresiduen propagieren diese Ableitungen algebraisch. Dies ist der tatsächliche Jacobian der vollständig diskretisierten IVP-zu-Residual-Abbildung.

Er ist nicht identisch mit einem analytisch bewiesenen Kontinuums-Jacobian. Deshalb ist Schrittweitenkonvergenz verpflichtend.

## 8. Präregistrierte Toleranzen

Vor Ausführung gelten:

- analytische geschlossene Residuen: `<= 1e-13`,
- RK4-Ankerresiduum bei 200 Schritten: `<= 2e-10`,
- RK4-Ankerresiduum bei 400 Schritten: `<= 2e-11`,
- relative Jacobianänderung von 400 auf 800 Schritte: `<= 1e-9`,
- Rangschwelle:
  \[
  \tau_{\rm rank}=\max(10^{-12},10^{-10}\sigma_{\max}),
  \]
- Konditionswarnung ab `1e6`,
- diagnostische Blockierung ab `1e10`.

Diese Grenzwerte autorisieren keinen Solver. Sie gelten ausschließlich für den Anker- und Jacobian-Preflight.

## 9. Numerische Referenzergebnisse

Der maximale normierte Residualbetrag ist

| RK4-Schritte je Region | `max |R_tilde|` |
|---:|---:|
| 100 | `1.5936623892532058e-09` |
| 200 | `9.960994876036197e-11` |
| 400 | `6.226068272047963e-12` |
| 800 | `3.899701742082573e-13` |

Die Singularwerte des 800-Schritt-Jacobians sind

\[
(15.4457519447776,
3.31627063848449,
2.56270218844830,
2.04698274226254,
1.89502299802529,
0.995037171340217,
0.473464262246708,
0.0695893845582763).
\]

Damit

\[
\operatorname{rank}(J_{800})=8
\]

unter der präregistrierten Schwelle und

\[
\kappa_2(J_{800})
=\frac{\sigma_{\max}}{\sigma_{\min}}
=221.95557616755255.
\]

Die relative Frobeniusänderung zwischen 400 und 800 Schritten beträgt

\[
\frac{\|J_{800}-J_{400}\|_F}{\|J_{800}\|_F}
=2.863079188994937\times10^{-12}.
\]

Der diskretisierte Jacobian ist am analytischen Anker somit vollrangig und deutlich unterhalb der Konditionswarnung.

## 10. Nullrichtungsregression

Auf der bereits analytisch identifizierten Fläche

\[
m^2=0,
\qquad
\hat\lambda_1=0
\]

ist eine gemeinsame konstante Verschiebung von `varphi_N0` und `varphi_S0` eine exakte Symmetrie. Der AD-Jacobian reproduziert

\[
\operatorname{rank}(J)=7
\]

mit genau einem verschwindenden Singularwert. Dies ist ein wichtiger Positivtest dafür, dass die Rangdiagnostik bekannte Nullrichtungen nicht künstlich entfernt.

## 11. Zulässige Schlussfolgerung

Zulässig ist:

> Der C1-Anker ist eine exakte analytische Hintergrundlösung. Die fest definierte diskretisierte IVP-zu-Residual-Abbildung besitzt dort einen schrittweitenkonvergenten, durch Forward-Mode-AD berechneten Jacobian mit Rang acht und moderater Konditionszahl.

Nicht zulässig sind:

- historische A0-Identität,
- Existenz einer nichttrivialen C1-Lösungsfamilie,
- globale Eindeutigkeit,
- Solverrobustheit außerhalb des Ankers,
- perturbative Stabilität oder Ghostfreiheit,
- K1-D- oder K1-E-Freigabe.

## 12. Gate-Status

```text
C1 exact analytic anchor          = DERIVED
C1 dimensionless equations        = FROZEN_FOR_DIAGNOSTIC_PREFLIGHT
C1 discretized AD Jacobian rank   = 8 AT ANALYTIC ANCHOR
C1 continuum BVP Jacobian rank    = NOT_PROVEN
C1 nonlinear continuation         = NOT_EXECUTED
C1 root solver                    = NOT_IMPLEMENTED
C1 official solver                = NOT_AUTHORIZED
historical A0 identity            = NOT_CLAIMED
R1.1                              = BLOCKED
K1-D                              = NOT_RELEASED
K1-E                              = NOT_ADMISSIBLE
```
