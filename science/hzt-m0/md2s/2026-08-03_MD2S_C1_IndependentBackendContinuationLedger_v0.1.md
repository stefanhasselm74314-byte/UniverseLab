# HZT-M0-S6-C1 — unabhängiger Backend- und linearer Fortsetzungs-Preflight v0.1

**Datum:** 2026-08-03  
**Status:** `INDEPENDENT_BACKEND_AND_LINEAR_TANGENT_PREFLIGHT_PASS_EXECUTION_BLOCKED`  
**Evidenzwirkung:** `NONE`  
**Historische A0-Identität:** `NOT_CLAIMED`  
**Offizieller Solver:** `NOT_AUTHORIZED`

## 1. Prüfziel

Der vorherige C1-Block zeigte an einem exakten analytischen Hintergrund einen schrittweitenkonvergenten, vollrangigen `8 x 8`-Jacobian der festschrittigen RK4-Residualabbildung. Dieser Befund musste mit einem numerisch und differenziell unabhängigen Pfad geprüft werden.

Der vorliegende Block verwendet deshalb:

1. keine RK4-Integration,
2. keine Dualzahlen und keine Forward-Mode-AD-Sensitivitäten,
3. keine Wiederverwendung des Referenz-Residualevaluators,
4. keinen BVP-Root-Solver.

Er prüft ausschließlich den bekannten analytischen Anker und leitet anschließend genau einen lokalen linearen Fortsetzungstangenten ab.

## 2. Unabhängiger Integrationsbackend

Die dimensionslosen C1-Gleichungen werden erneut separat implementiert. Jede Region startet bei

\[
\varepsilon=10^{-5}
\]

mit der regulären Polentwicklung.

Für einen Schritt von \(x_n\) nach \(x_{n+1}=x_n+h\) wird die implizite Mittelpunktregel verwendet:

\[
y_{n+1}=y_n+h\,f\!\left(\frac{y_n+y_{n+1}}{2}\right).
\]

Die interne Schrittlösung erfolgt durch Newton-Iteration auf

\[
F(z)=z-y_n-hf\!\left(\frac{y_n+z}{2}\right)=0.
\]

Der dabei benötigte Zustands-Jacobian wird symmetrisch finit differenziert. Diese lokale Newton-Iteration löst nur die implizite Einzelschrittgleichung; sie ist **kein** Newton-Korrektor des globalen Randwertproblems.

Die Grundmethode ist zweiter Ordnung. Zur unabhängigen Ordnungsanhebung werden zwei Endpunktlösungen mit \(N\) und \(2N\) Schritten kombiniert:

\[
y^{[4]}=\frac{4y_{2N}-y_N}{3}.
\]

Am glatten C1-Anker ergibt dies die erwartete vierte Ordnung.

## 3. Unabhängiger Sensitivitäts-Jacobian

Der vollständige unabhängige Residualvektor

\[
\widetilde R(X)
\]

wird mit derselben vorab fixierten Residualreihenfolge und denselben lösungsunabhängigen Skalen ausgewertet wie der Referenzblock. Die Implementierung der Abbildung ist jedoch separat.

Jede Spalte des unabhängigen Jacobians wird durch symmetrische Differenzen erzeugt:

\[
J^{\rm IM}_{ij}
=
\frac{\widetilde R_i(X+h_je_j)-\widetilde R_i(X-h_je_j)}{2h_j},
\]

mit

\[
h_j=2\times10^{-6}\max(1,|X_j|).
\]

Damit ist die Sensitivitätsmethode unabhängig von der Forward-Mode-AD-Pipeline des RK4-Referenzbackends.

## 4. Präregistrierte Backend-Toleranzen

Vor der Ausführung wurden festgelegt:

- maximales Ankerresiduum bei Basisauflösung \(N=50\): `<= 1e-8`,
- maximales Ankerresiduum bei Basisauflösung \(N=100\): `<= 1e-9`,
- relative Jacobianänderung von \(N=50\) auf \(N=100\): `<= 5e-8`,
- relative Frobeniusabweichung zum RK4-AD-Referenzjacobian: `<= 2e-8`,
- maximale relative Abweichung des Singularwertspektrums: `<= 2e-7`,
- unabhängiger Rang: acht,
- Konditionswarnung ab \(10^6\),
- diagnostische Blockierung ab \(10^{10}\).

## 5. Unabhängige Resultate

Für die Richardson-extrapolierte implizite Mittelpunktmethode gilt:

| Basis-Schritte je Region | feine Schritte | \(\max|\widetilde R|\) |
|---:|---:|---:|
| 50 | 100 | `9.560929730164828e-09` |
| 100 | 200 | `5.976472921013429e-10` |

Das Verhältnis liegt nahe \(16\) und entspricht der erwarteten vierten Ordnung.

Die relative Änderung des unabhängigen Jacobians zwischen den beiden Auflösungen beträgt

\[
\frac{\|J^{\rm IM}_{100}-J^{\rm IM}_{50}\|_F}
{\|J^{\rm IM}_{100}\|_F}
=
1.2005132839301583\times10^{-8}.
\]

Der Vergleich mit dem 800-Schritt-RK4-AD-Jacobian ergibt

\[
\frac{\|J^{\rm IM}_{100}-J^{\rm RK4-AD}_{800}\|_F}
{\|J^{\rm RK4-AD}_{800}\|_F}
=
7.406169931198177\times10^{-10}.
\]

Die unabhängigen Singularwerte sind

\[
\begin{aligned}
(&15.445751940961904,
3.316270636392083,
2.562702188610960,
2.046982741055011,\\
&1.895022997669581,
0.995037170437595,
0.473464262185980,
0.0695893845775842).
\end{aligned}
\]

Damit gilt unter der registrierten Rangschwelle:

\[
\boxed{\operatorname{rank}(J^{\rm IM}_{100})=8}
\]

und

\[
\boxed{\kappa_2(J^{\rm IM}_{100})=221.95557605113822.}
\]

Der unabhängige Pfad bestätigt somit den Rang-8- und Konditionsbefund des RK4-AD-Backends am exakten Anker.

## 6. Wahl des Fortsetzungsparameters

Als einziger Fortsetzungsparameter wird der konstante dimensionslose Kappenspannungsanteil

\[
p=\hat\lambda_0
\]

festgelegt.

Die Wahl ist bewusst konservativ:

- \(p\) verändert bei festem Schießvektor nicht die Bulk-Differentialgleichungen,
- die diskreten Wicklungs- und Fluxsektoren bleiben unverändert,
- \(p\) tritt linear in genau den beiden metrischen Kappenresiduen auf,
- dadurch wird zunächst ausschließlich die lokale Grenzflächenantwort geprüft.

Am Anker gilt

\[
\frac{\partial\widetilde R}{\partial\hat\lambda_0}
=
(0,0,0,0,1,1,0,0)^T.
\]

Diese Ableitung wird im unabhängigen Backend zusätzlich mit symmetrischer Parameterdifferenz und Schritt \(10^{-6}\) reproduziert.

## 7. Linearer impliziter Tangent

Für

\[
\widetilde R(X(p),p)=0
\]

folgt formal am Anker

\[
J_X\frac{dX}{dp}+R_p=0.
\]

Der registrierte lokale Tangent ist deshalb

\[
\boxed{
\frac{dX}{d\hat\lambda_0}
=-J_X^{-1}R_{\hat\lambda_0}
}.
\]

In der Schießreihenfolge

\[
X=(\varphi_{N0},q_N,A_{S0},\varphi_{S0},q_S,\rho_N,\rho_S,k_4)
\]

liefert der unabhängige Backend:

\[
\frac{dX}{d\hat\lambda_0}
\approx
\begin{pmatrix}
0\\
0.425000000068885\\
4.93\times10^{-18}\\
0\\
-0.425000000068885\\
-0.457250175964840\\
-0.457250176329143\\
0.047916666649958
\end{pmatrix}.
\]

Der RK4-AD-Referenzjacobian liefert

\[
\frac{dX}{d\hat\lambda_0}
\approx
\begin{pmatrix}
0\\
0.424999999892648\\
-2.86\times10^{-17}\\
0\\
-0.424999999892648\\
-0.457250175582988\\
-0.457250175595161\\
0.047916666675221
\end{pmatrix}.
\]

Die relative Vektordifferenz beträgt

\[
9.77747552550672\times10^{-10}.
\]

Die lineare Abschlussprüfung ergibt

\[
\left\|
J^{\rm IM}\frac{dX}{d\hat\lambda_0}
+R_{\hat\lambda_0}
\right\|_\infty
=
1.1102230246251565\times10^{-16}.
\]

Die erwartete Nord-Süd-Symmetrie wird reproduziert:

\[
\frac{dq_S}{dp}=-\frac{dq_N}{dp},
\qquad
\frac{d\rho_S}{dp}=\frac{d\rho_N}{dp},
\]

während die skalaren Zentralwerte und der südliche Warp-Offset im linearen symmetrischen Modus verschwinden.

## 8. Aussagegrenze

Zulässig ist:

> Zwei numerisch und sensitivitätsseitig verschiedene Backends stimmen am exakten C1-Anker im Residualvektor, im vollständigen `8 x 8`-Jacobian, im Singularwertspektrum, in der Konditionszahl und im linearen \(\hat\lambda_0\)-Tangenten innerhalb präregistrierter Toleranzen überein.

Nicht zulässig ist:

- aus dem Tangenten einen endlichen Parameterschritt als Lösung auszugeben,
- einen nichtlinearen Lösungszweig zu behaupten,
- das Kontinuums-IFT ohne funktionalanalytischen Nachweis als bewiesen zu behandeln,
- Existenz oder Eindeutigkeit außerhalb des Ankers zu folgern,
- Stabilität oder Ghostfreiheit abzuleiten,
- C1 mit dem historischen A0-Modell zu identifizieren,
- R1.1, K1-D oder K1-E freizugeben.

## 9. Gate-Status

```text
C1 independent integration backend = NUMERICALLY_CONFIRMED_DIAGNOSTIC
C1 independent sensitivity backend = NUMERICALLY_CONFIRMED_DIAGNOSTIC
C1 backend Jacobian agreement       = PASS
C1 lambda0 linear tangent           = NUMERICALLY_CONFIRMED_DIAGNOSTIC
continuum implicit-function theorem = NOT_PROVEN
nonlinear continuation              = NOT_EXECUTED
root corrector                       = NOT_IMPLEMENTED
official C1 solver                  = NOT_AUTHORIZED
historical A0 identity              = NOT_CLAIMED
R1.1                                = BLOCKED
K1-D                                = NOT_RELEASED
K1-E                                = NOT_ADMISSIBLE
```
