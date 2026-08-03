# HZT-M0-S6-C-PHYS-M1 — Operator-2B Function-Space and Trace Ledger v0.1

**Datum:** 2026-08-04  
**Track:** `MD2S-R1-C-PHYS`  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Block:** `C-PHYS-R1.0-OPERATOR-2B`  
**Klassifikation:** `FORMAL_FUNCTION_SPACE_AND_TRACE_CONTRACT_NO_BACKGROUND_SOLVE`  
**Evidenzwirkung:** `FORMAL_FUNCTIONAL_ANALYTIC_STRUCTURE_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

---

## 1. Ziel und harte Grenze

OPERATOR-2A hat die spezialisierte M1-Differentialexpression, die exakte Constraint-Fortpflanzung, die höheren Polreihen und den Hauptteil der Profil-Transmission geschlossen.

OPERATOR-2B beantwortet die nächste, davon logisch getrennte Frage:

> In welchen präzisen Banachräumen wird der polreguläre, auf feste Intervalle transformierte M1-Operator formuliert, und wie sieht der vollständige parameteraugmentierte linearisierte Randtrace **als Template** aus?

Der Block berechnet ausdrücklich nicht:

- eine Hintergrundlösung,
- einen numerischen Trace-Rang,
- Kernel oder Kokernel,
- einen Fredholmindex,
- einen Kontinuums-Jacobian,
- oder eine Stabilitätsmatrix.

---

## 2. Warum das rohe \(x\)-Chart nicht genügt

In jeder Region liegt der glatte Pol bei \(x_s=0\), während der Kap bei der unbekannten Position \(x_s=\rho_s\) liegt. Gleichzeitig enthält die rohe Differentialexpression Quotienten wie

\[
\frac{\ell_s'}{\ell_s},
\qquad
\frac{\ell_s''}{\ell_s},
\]

obwohl

\[
\ell_s(x_s)\sim x_s
\]

am Pol gilt.

Die Quotienten sind auf der glatten Paritätsklasse endlich, erscheinen im ungefilterten Chart aber regulär-singulär. Zusätzlich bewegen sich die Endpunkte mit den unbekannten Größen \(\rho_N,\rho_S\).

Wir fixieren daher

\[
x_s=\rho_s y,
\qquad
0\le y\le1,
\]

und anschließend

\[
\boxed{\tau=y^2\in[0,1]}.
\]

Damit gilt

\[
\frac{d}{dx_s}
=
\frac{2\sqrt\tau}{\rho_s}\frac{d}{d\tau}.
\]

Das Quadratkoordinaten-Chart kodiert die gerade Polparität direkt.

---

## 3. Affines polreguläres Chart

Für jede Seite \(s\in\{N,S\}\) setzen wir

\[
A_s(\tau)=A_{s0}+\tau u_{A,s}(\tau),
\]

\[
\ell_s(\tau)
=
\rho_s\sqrt\tau\,\widehat L_s(\tau),
\qquad
\widehat L_s(\tau)=1+\tau u_{\ell,s}(\tau),
\]

\[
\varphi_s(\tau)
=
\varphi_{s0}+\tau u_{\varphi,s}(\tau),
\]

\[
a_{\chi,s}(\tau)
=
\tau u_{g,s}(\tau).
\]

Die bereits fixierte Nord-Framebedingung lautet

\[
A_{N0}=0.
\]

Die Größen

\[
\varphi_{N0},\quad A_{S0},\quad \varphi_{S0}
\]

bleiben Teil des augmentierten Parametervektors.

Diese Darstellung erzwingt automatisch

\[
A_s'(0)=0,
\qquad
\ell_s(0)=0,
\qquad
\ell_s'(0)=1,
\qquad
\varphi_s'(0)=0,
\qquad
a_{\chi,s}(0)=0.
\]

Sie ist eine funktionalanalytische Koordinatenwahl auf der glatten Polklasse, keine numerische Startvorschrift.

---

## 4. Little-Hölder-Räume

Wir fixieren einen Exponenten

\[
0<\alpha_H<1.
\]

Dabei ist \(\alpha_H\) ausschließlich ein Regularitätsexponent und keine Modellkopplung.

Wir verwenden die little-Hölder-Räume

\[
h^{k,\alpha_H}([0,1]),
\]

definiert als Abschluss von \(C^\infty([0,1])\) in der \(C^{k,\alpha_H}\)-Norm.

Der Grund für diese Wahl ist wesentlich:

- Es entsteht ein Banachraum.
- Glatte Funktionen bilden einen dichten Kern.
- Multiplikation und glatte Kompositionen sind auf dem kompakten Intervall kontrolliert.
- Die Dichteaussage wird nicht fälschlich aus dem großen Hölderraum übernommen.

Pro Region definieren wir

\[
\boxed{
X_s
=
\bigl(h^{2,\alpha_H}\bigr)^3
\times h^{1,\alpha_H}
}
\]

in der Reihenfolge

\[
(u_A,u_\ell,u_\varphi,u_g).
\]

Der Bulk-Zielraum ist

\[
\boxed{
Y_s
=
\bigl(h^{0,\alpha_H}\bigr)^4
}.
\]

Als gemeinsamer Profil-Ambientraum verwenden wir

\[
Z_s
=
\bigl(h^{0,\alpha_H}\bigr)^4.
\]

Global:

\[
X_{\rm prof}=X_N\times X_S,
\]

\[
Y_{\rm bulk}=Y_N\times Y_S,
\]

\[
Z_{\rm prof}=Z_N\times Z_S.
\]

Der gemeinsame glatte Kern liefert eine kontinuierliche dichte Einbettung

\[
X_{\rm prof}\hookrightarrow Z_{\rm prof}.
\]

---

## 5. Augmentierter Parameterraum

Der kontinuierliche BVP-Vektor bleibt

\[
p=
(\varphi_{N0},q_N,A_{S0},\varphi_{S0},q_S,\rho_N,\rho_S,k_4).
\]

Wir schreiben

\[
P
=
\mathbb R^5\times\mathbb R_{>0}^2\times\mathbb R,
\]

wobei die beiden positiven Faktoren \(\rho_N,\rho_S\) sind.

Die sechs M1-Modellformparameter bleiben externe Koeffizienten. Sie werden nicht stillschweigend zu Shooting-Unbekannten erhoben.

Ebenso bleiben

\[
N_F,\quad N_\sigma,\quad m_\sigma
\]

fixierte diskrete Sektorlabels.

---

## 6. Admissible offene Menge

Wir definieren

\[
\mathcal U_{\rm adm}
\subset
X_{\rm prof}\times P
\]

durch

\[
\rho_N>0,
\qquad
\rho_S>0,
\]

und

\[
\widehat L_s(\tau)
=1+\tau u_{\ell,s}(\tau)>0
\quad
\forall\tau\in[0,1].
\]

Da \([0,1]\) kompakt ist, definiert die strikt positive Minimaldistanz von \(\widehat L_s\) zu null eine offene Bedingung in der Supremums- und damit in der Hölder-Topologie.

Insbesondere gilt am Kap

\[
\ell_s(1)=\rho_s\widehat L_s(1)>0.
\]

---

## 7. Regularisierte Ableitungsidentitäten

Aus dem Chart folgen

\[
A_x
=
\frac{2\sqrt\tau}{\rho}
\left(u_A+\tau u_{A,\tau}\right),
\]

\[
A_{xx}
=
\frac{2}{\rho^2}
\left(
 u_A+5\tau u_{A,\tau}
 +2\tau^2u_{A,\tau\tau}
\right).
\]

Für den Skalar gilt dieselbe Struktur:

\[
\varphi_x
=
\frac{2\sqrt\tau}{\rho}
\left(u_\varphi+\tau u_{\varphi,\tau}\right),
\]

\[
\varphi_{xx}
=
\frac{2}{\rho^2}
\left(
 u_\varphi+5\tau u_{\varphi,\tau}
 +2\tau^2u_{\varphi,\tau\tau}
\right).
\]

Mit

\[
\ell=\rho\sqrt\tau\widehat L
\]

folgt

\[
\ell_x
=
\widehat L+2\tau\widehat L_{,\tau},
\]

\[
\frac{\ell_{xx}}{\ell}
=
\frac{2}{\rho^2}
\frac{3\widehat L_{,\tau}+2\tau\widehat L_{,\tau\tau}}
{\widehat L}.
\]

Auch die scheinbar singulären Mischterme werden regulär:

\[
A_x\frac{\ell_x}{\ell}
=
\frac{2}{\rho^2}
\frac{
(u_A+\tau u_{A,\tau})
(\widehat L+2\tau\widehat L_{,\tau})
}{\widehat L},
\]

\[
\varphi_x\frac{\ell_x}{\ell}
=
\frac{2}{\rho^2}
\frac{
(u_\varphi+\tau u_{\varphi,\tau})
(\widehat L+2\tau\widehat L_{,\tau})
}{\widehat L}.
\]

Für den Gauge-Transport erhalten wir nach Division durch \(\sqrt\tau\)

\[
\frac{E_{\rm gauge}}{\sqrt\tau}
=
\frac{2}{\rho}
\left(u_g+\tau u_{g,\tau}\right)
-q\rho\widehat L
\exp(-4A+2a_F\varphi).
\]

Es verbleibt keine negative Potenz von \(\tau\).

---

## 8. Regularisierter Bulk-Operator

Pro Region definieren wir

\[
F_{A,s}=E_{A,s},
\]

\[
F_{\ell,s}=\frac{E_{\ell,s}}{\ell_s},
\]

\[
F_{\varphi,s}=\frac{E_{\varphi,s}}{\ell_s},
\]

\[
F_{g,s}=\frac{E_{{\rm gauge},s}}{\sqrt\tau},
\]

jeweils mit der durch das Chart bestimmten stetigen Fortsetzung nach \(\tau=0\).

Damit entsteht

\[
F_{\rm bulk}:\mathcal U_{\rm adm}
\longrightarrow
Y_{\rm bulk}.
\]

Auf der positiven \(\widehat L\)-Menge bestehen die Residuals ausschließlich aus

- stetigen Ableitungsabbildungen,
- Produkten,
- Division durch die positive Funktion \(\widehat L\),
- und glatten Exponentialkompositionen.

Folglich ist

\[
\boxed{F_{\rm bulk}\in C^\infty(\mathcal U_{\rm adm},Y_{\rm bulk})}.
\]

Der regularisierte Constraint

\[
\frac{C_{rr}}{\ell}
\]

besitzt ebenfalls eine stetige Polfortsetzung, bleibt aber gemäß OPERATOR-2A ein QA-Kanal und wird nicht als neunte Bulk- oder Randgleichung gezählt.

---

## 9. Kap-Trace

Für jede Region sammeln wir

\[
\Gamma_s=
\left(
A_s,
A_{s,x},
\ell_s,
\ell_{s,x},
\varphi_s,
\varphi_{s,x},
a_{\chi,s}
\right)_{\tau=1}.
\]

Die expliziten Charttraces sind

\[
A_s(1)=A_{s0}+u_{A,s}(1),
\]

\[
A_{s,x}(1)
=
\frac2{\rho_s}
\left[u_{A,s}(1)+u_{A,s,\tau}(1)\right],
\]

\[
\ell_s(1)=\rho_s\widehat L_s(1),
\]

\[
\ell_{s,x}(1)
=
\widehat L_s(1)+2\widehat L_{s,\tau}(1),
\]

\[
\varphi_s(1)
=
\varphi_{s0}+u_{\varphi,s}(1),
\]

\[
\varphi_{s,x}(1)
=
\frac2{\rho_s}
\left[u_{\varphi,s}(1)+u_{\varphi,s,\tau}(1)\right],
\]

\[
a_{\chi,s}(1)=u_{g,s}(1).
\]

Wert- und Erstderivativtraces sind auf \(h^{2,\alpha_H}\) stetig; der Gauge-Werttrace ist auf \(h^{1,\alpha_H}\) stetig. Daher ist

\[
\Gamma_{\rm cap}:X_{\rm prof}\times P
\longrightarrow
\mathbb R^{14}
\]

stetig.

---

## 10. Nichtlinearer Randoperator

Die bereits eingefrorene Residualreihenfolge lautet

\[
B=
(R_A,R_\ell,R_\varphi,R_{\rm patch},
R_{4d},R_\chi,R_{\rm scalar},R_{{\rm gauge,local}}).
\]

Damit

\[
B:\mathcal U_{\rm adm}\longrightarrow\mathbb R^8.
\]

Für M1 sind \(\lambda\) und \(Z_\sigma\) skalarunabhängig. Deshalb enthält der Hauptteil des skalaren Kapresiduals nur

\[
\delta\varphi_{N,x}+\delta\varphi_{S,x}.
\]

Die Patch- und globale Fluxbedingung bleiben gemäß Freeze-1A eine einzige Bedingung.

Der vollständige nichtlineare Operator ist

\[
\boxed{
\mathcal G=(F_{\rm bulk},B):
\mathcal U_{\rm adm}
\longrightarrow
Y_{\rm bulk}\times\mathbb R^8
}.
\]

Er ist auf \(\mathcal U_{\rm adm}\) glatt. Daraus folgt nicht, dass

\[
\mathcal G^{-1}(0)\ne\varnothing.
\]

---

## 11. Parameteraugmentiertes lineares Trace-Template

Sei

\[
W_\star=(u_\star,p_\star)
\in\mathcal U_{\rm adm}
\]

ein später separat deklarierter Kandidatenhintergrund.

Erst wenn zusätzlich

\[
\mathcal G(W_\star)=0
\]

unter festgelegten Toleranzen beziehungsweise exakt gilt, darf die numerische Trace-Auswertung beginnen.

Wir definieren den augmentierten Kapvektor

\[
z_{\rm cap}
=
\left(
\Gamma_{\rm cap}(\delta u,\delta p),
\delta p
\right)
\in\mathbb R^{22}.
\]

Dann besitzt die Randlinearisation die Form

\[
\boxed{
D B[W_\star](\delta u,\delta p)
=
M_B[W_\star]\,z_{\rm cap}
}
\]

mit

\[
M_B[W_\star]\in\mathbb R^{8\times22}.
\]

Dies ist ein strukturelles Template, keine bereits ausgewertete Matrix.

Der aus OPERATOR-2A bekannte metrische Derivativhauptblock lautet

\[
\begin{pmatrix}
-3 & -1/\ell_{\rm cap}\\
-4 & 0
\end{pmatrix},
\]

mit

\[
\det=-\frac4{\ell_{\rm cap}}.
\]

Für \(\ell_{\rm cap}>0\) ist dieser Hauptblock invertierbar. Diese Aussage ersetzt nicht den Rang des vollständigen parameteraugmentierten Traces.

---

## 12. Linearisiertes Operator-Template

Nach Fixierung eines zulässigen Kandidatenhintergrunds definieren wir

\[
L_\star
=
D\mathcal G[W_\star]:
X_{\rm prof}\times\mathbb R^8
\longrightarrow
Y_{\rm bulk}\times\mathbb R^8.
\]

Zwischen den deklarierten Banachräumen ist \(L_\star\) beschränkt. Daher besitzt es als beschränkte Abbildung einen geschlossenen Graphen.

Diese eingeschränkte Aussage ist nicht gleichbedeutend mit

- einer geschlossenen unbeschränkten Realisierung auf einem einzigen Ambientraum,
- Fredholm-Eigenschaft,
- Index null,
- kompaktem Resolvent,
- oder Invertierbarkeit.

---

## 13. Dichte- und Closedness-Audit

Durch die little-Hölder-Definition ist der glatte polreguläre Kern dicht in den Profilräumen. Insbesondere ist

\[
X_{\rm prof}
\]

dicht in

\[
Z_{\rm prof}.
\]

Für ein fixes \(W_\star\) ist die beschränkte Abbildung \(L_\star:X\to Y\) graphgeschlossen.

Offen bleibt eine gegebenenfalls spätere unbeschränkte Realisierung

\[
\mathfrak L:D(\mathfrak L)\subset Z\to Y
\]

mit einem eigenständigen Graphnorm- und Fredholmtheorem.

---

## 14. Kernel-/Kokernel-Protokoll

Nach Vorliegen eines separat akzeptierten Kandidatenhintergrunds sind mindestens folgende Schritte erforderlich:

1. \(W_\star\), M1-Parameter und diskreten Sektor unveränderlich fixieren.
2. \(L_\star\) in zwei numerisch unabhängigen Darstellungen implementieren.
3. Das homogene Problem
   \[
   L_\star\delta W=0
   \]
   lösen und die Kerndimension auf Auflösungskonvergenz prüfen.
4. Eine zur deklarierten Paarung kompatible Dual- oder Adjungiertendarstellung konstruieren.
5. Die Kokerneldimension auf Konvergenz prüfen.
6. Erst danach
   \[
   \operatorname{ind}L_\star
   =\dim\ker L_\star-\dim\operatorname{coker}L_\star
   \]
   berichten.
7. Die Singularwerte des nach Bulk-Elimination verbleibenden augmentierten Endpoint-Traces ausweisen.

Eine quadratische Residualzählung genügt für keinen dieser Schritte.

---

## 15. Geschlossene Ergebnisse

```text
fixed tau pole chart                  = FROZEN
little-Holder profile spaces          = FROZEN
bulk target spaces                    = FROZEN
ambient profile spaces                = FROZEN
positive admissible set               = FROZEN
regularized bulk operator             = DEFINED C-infinity
pole and cap trace continuity         = PROVEN
nonlinear operator template           = DEFINED
linearized boundary trace template    = DEFINED NOT EVALUATED
bounded linearized operator template  = DEFINED
smooth-core density                    = PROVEN BY SPACE DEFINITION
kernel/cokernel protocol              = FROZEN NOT EXECUTED
```

---

## 16. Offene Ergebnisse

```text
candidate M1 background               = NOT ESTABLISHED
numeric M_B                           = NOT CONSTRUCTED
full trace rank                       = NOT PROVEN
kernel and cokernel                   = NOT COMPUTED
Fredholm property                     = NOT PROVEN
continuum Jacobian                    = NOT PROVEN
existence and uniqueness              = NOT PROVEN
conditioning                          = OPEN
perturbative stability                = OPEN
ghost freedom                         = OPEN
official solver                       = NOT AUTHORIZED
```

---

## 17. Gate-Wirkung

```text
R1.0                                  = ACTIVE_BACKGROUND_PREREQUISITE_AND_FREDHOLM_ANALYSIS_REMAINING
R1.1                                  = BLOCKED
R1.2                                  = BLOCKED
continuum BVP operator                = FUNCTION_SPACE_AND_TRACE_TEMPLATE_DEFINED
weighted function spaces              = FROZEN
full linearized trace template        = DEFINED NOT EVALUATED
full linearized trace rank            = NOT PROVEN
Fredholm property                     = NOT PROVEN
continuum BVP Jacobian                = NOT PROVEN
physical background                  = NOT ESTABLISHED
official MD-2S solver                 = NOT AUTHORIZED
K1-D                                  = NOT RELEASED
K1-E                                  = NOT ADMISSIBLE
physical evidence effect              = NONE
```

---

## 18. Exakt nächster Primärblock

```text
C-PHYS-R1.0-BACKGROUND-3A
```

Dieser Block darf ausschließlich ein Kandidatenhintergrund-Verfahren präregistrieren:

- feste M1-Parameter und diskreter Sektor,
- feste numerische Methode,
- feste Residualnormen,
- Pol- und Kap-Chart-Implementierung,
- Constraint-QA,
- Auflösungs- und Backend-Konvergenz,
- fail-closed Akzeptanzkriterien.

Er darf noch keine Existenz, Eindeutigkeit, Stabilität oder physikalische Bestätigung behaupten.
