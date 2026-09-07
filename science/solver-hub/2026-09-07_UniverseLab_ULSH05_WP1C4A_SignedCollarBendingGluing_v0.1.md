# ULSH-05 / WP1C4A — Signed-Collar Two-Side Bending Gluing v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `91c2f2bc089f41f1e3168bf46d7b69f727e4a6a2`  
**Status:** `DERIVED_EXPLICIT_SIGNED_COLLAR_TWO_SIDE_BENDING_GLUING_FULL_MOVING_BOUNDARY_DYNAMICS_OPEN`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Ziel

WP1C3 hat die bewegte Hyperflächengeometrie eingefroren, aber bewusst nicht geraten, ob die beiden lokal definierten Bending-Skalare `xi_N` und `xi_S` gleich oder entgegengesetzt sind. Der Grund ist korrekt: Beide regionalen Radialkoordinaten wachsen jeweils vom Pol zur Kappe und beide lokalen outward normals besitzen die Komponente `+partial_r`.

WP1C4A schließt genau diese **Darstellungsfrage** durch eine explizite gemeinsame signed-normal Collar-Koordinate. Keine Hintergrundgleichung und kein Solver werden benutzt.

## 2. Eingefrorene regionale Orientierung

Auf der Nordregion:

\[
r_N:0\to\rho_N,
\qquad
n_N=+\partial_{r_N}.
\]

Auf der Südregion:

\[
r_S:0\to\rho_S,
\qquad
n_S=+\partial_{r_S}.
\]

Diese Aussagen stammen aus dem kanonischen C-PHYS-Konventionsvertrag.

## 3. Gemeinsame signed-normal Collar-Koordinate

Definiere in einer Umgebung der gemeinsamen Kappe eine einzige Koordinate `u` mit Interface `u=0`:

Nordseite:

\[
\boxed{r_N=\rho_N+u},\qquad u\le0,
\]

Südseite:

\[
\boxed{r_S=\rho_S-u},\qquad u\ge0.
\]

Daraus:

\[
\partial_u=\partial_{r_N}\quad(N),
\]

\[
\partial_u=-\partial_{r_S}\quad(S).
\]

Setze

\[
\nu\equiv\partial_u,
\]

wobei `nu` von Nord nach Süd zeigt. Dann folgen die lokalen outward normals automatisch als

\[
\boxed{n_N=+\nu},
\]

\[
\boxed{n_S=-\nu}.
\]

Dies löst keinen physikalischen Freiheitsgrad; es ist eine explizite Interface-Identifikationskonvention.

## 4. Ein einziges bewegtes Interface

Schreibe die physische Grenzfläche in diesem Collar als Graph

\[
\boxed{u=\epsilon\zeta(y)}.
\]

Dann folgt aus der Koordinatenabbildung unmittelbar

\[
\delta r_N=+\epsilon\zeta,
\qquad
\delta r_S=-\epsilon\zeta.
\]

Die in WP1C3 relativ zu den **lokalen outward normals** definierten Bending-Skalare sind daher

\[
\boxed{\xi_N=+\zeta},
\qquad
\boxed{\xi_S=-\zeta}.
\]

Somit

\[
\boxed{\xi_N+\xi_S=0}.
\]

`[BEWIESEN IM DEKLARIERTEN COLLAR]`

Diese Gleichung ist keine gauge-invariante Observable. Sie sagt lediglich, wie **ein und dieselbe geometrische Interfaceverschiebung** in den beiden regionalen outward-normal Basen dargestellt wird.

## 5. Kompatible Bulk-D-Gauge

Sei `beta` die Normalkomponente eines einzigen glatten D-Gauge-Generators entlang `nu` auf dem Interface.

Dann lauten seine regionalen outward-normal Komponenten

\[
\beta_N=+\beta,
\qquad
\beta_S=-\beta.
\]

Mit WP1C3

\[
\xi_s\to\xi_s+\beta_s
\]

folgt

\[
(\xi_N+\xi_S)'
=(\xi_N+\xi_S)+(\beta_N+\beta_S)
=0.
\]

Für zwei separat gewählte regionale Gaugegeneratoren ist daher die Kompatibilitätsbedingung

\[
\boxed{\beta_N+\beta_S=0}.
\]

Lokal kann man mit

\[
\beta=-\zeta
\]

beide regionalen Bending-Skalare gleichzeitig auf null setzen:

\[
\xi_N'=0,
\qquad
\xi_S'=0.
\]

Dies beweist nur eine **lokale Collar-Gauge**. Eine globale Erweiterung bis zu beiden Polen unter Erhaltung aller Regularitäts- und U(1)-Patchbedingungen bleibt offen.

## 6. Erste Fundamentalform

WP1C3 liefert je Region

\[
H^{(s)}_{ab}
=p^{(s)}_{ab}
+2\xi_sK^{(s)}_{ab}
+2D_{(a}\tau^{(s)}_{b)}.
\]

Setze die signed-collar Relation ein:

\[
H^{(N)}_{ab}
=p^{(N)}_{ab}+2\zeta K^{(N)}_{ab}+2D_{(a}\tau^{(N)}_{b)},
\]

\[
H^{(S)}_{ab}
=p^{(S)}_{ab}-2\zeta K^{(S)}_{ab}+2D_{(a}\tau^{(S)}_{b)}.
\]

Kontinuität desselben Interface-Tensors verlangt

\[
\boxed{
\begin{aligned}
0={}&H^{(N)}_{ab}-H^{(S)}_{ab}\\
={}&p^{(N)}_{ab}-p^{(S)}_{ab}
+2\zeta\left(K^{(N)}_{ab}+K^{(S)}_{ab}\right)\\
&+2D_{(a}\left(\tau^{(N)}_{b)}-\tau^{(S)}_{b)}\right).
\end{aligned}
}
\]

In einem gemeinsamen intrinsischen Tangentialchart mit `tau_N=tau_S` reduziert sich dies auf

\[
\boxed{
p^{(N)}_{ab}-p^{(S)}_{ab}
+2\zeta\left(K^{(N)}_{ab}+K^{(S)}_{ab}\right)=0.
}
\]

## 7. Skalar-Pullback-Kontinuität

Hintergrundkontinuität lautet

\[
\bar\phi_N(\rho_N)=\bar\phi_S(\rho_S).
\]

Für dasselbe bewegte Interface:

\[
\delta_\Sigma\phi_N
=\varphi_N+\zeta\,\partial_{r_N}\bar\phi_N,
\]

\[
\delta_\Sigma\phi_S
=\varphi_S-\zeta\,\partial_{r_S}\bar\phi_S.
\]

Daher

\[
\boxed{
\varphi_N-\varphi_S
+\zeta\left(
\partial_{r_N}\bar\phi_N
+\partial_{r_S}\bar\phi_S
\right)=0.
}
\]

Wichtig: Wir setzen **nicht** die Hintergrund-Skalar-Junction als gelöste Gleichung ein. `PHYSICAL_BACKGROUND=NOT_ESTABLISHED` bleibt bestehen. Der Klammerterm darf also nicht stillschweigend auf null gesetzt werden.

## 8. Gauge-Patch-Sektor bleibt offen

Der Hintergrund besitzt die gefrorene Patchrelation

\[
A_{\chi,N}-A_{\chi,S}=\frac{N_F}{q_{\rm ref}}.
\]

Für die Perturbation kann die regionale U(1)-Gauge jedoch auch die perturbierte Übergangsfunktion verändern. WP1C4A setzt deshalb **nicht**

\[
a_{\chi,N}^\Sigma-a_{\chi,S}^\Sigma=0
\]

ohne einen eigenen Moving-Patch-Vertrag.

Dieser Punkt wird nach WP1C4A zusammen mit den normalen Gauge-/Skalarflüssen behandelt.

## 9. Kontrollrechnungen

Der Repository-Test prüft unabhängig:

1. die Jacobis der zwei Collar-Abbildungen;
2. die Relation `n_N=+nu`, `n_S=-nu`;
3. die regionale Darstellung eines numerisch bewegten Interfacegraphs;
4. Erhaltung von `xi_N+xi_S=0` unter einem gemeinsamen Collar-D-Gauge;
5. gleichzeitiges lokales Gauge-Fixing `xi_N'=xi_S'=0`;
6. die first-fundamental-form Relation durch direkte finite Differenz zweier generischer linearer regionaler Interface-Metriken;
7. die Skalar-Pullback-Relation durch direkte finite Differenz zweier off-shell Skalarprofile mit **nichtverschwindender** Summe der radialen Hintergrundableitungen;
8. alle physischen und Autorisierungsfirewalls.

## 10. Ergebnis

`[BEWIESEN IM DEKLARIERTEN SIGNED COLLAR]`

- eine explizite gemeinsame Interface-Identifikationsabbildung;
- `xi_N=+zeta`, `xi_S=-zeta`;
- D-Gauge-Kompatibilitätsbedingung `beta_N+beta_S=0`;
- lokale simultane Fixed-Interface-Gauge;
- off-shell Kontinuitätsgleichung der ersten Fundamentalform;
- off-shell Skalar-Pullback-Kontinuität.

`[OFFEN/BLOCKIERT]`

- globale Erweiterbarkeit der Fixed-Interface-Gauge;
- perturbierte U(1)-Patchtransition;
- normale Skalar-/Gaugefluss-Junctions;
- Moving-Boundary-Hessian;
- vollständig assembliertes Perturbations-Junctionsystem;
- physischer Hintergrund;
- Ghostfreiheit/Stabilität;
- 6D→4D-Observablen.

## 11. Gate-Status

```text
WP1 signed-collar interface identification = DERIVED
WP1 two-side bending gluing               = DERIVED_IN_DECLARED_COLLAR
WP1 local simultaneous fixed-interface    = DERIVED_COLLAR_LOCAL_ONLY
WP1 global fixed-interface gauge          = NOT_PROVEN
WP1 full boundary Hessian                 = NOT_CLOSED
WP1 full quadratic action                 = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM                 = NOT_RELEASED
PHYSICAL_BACKGROUND                       = NOT_ESTABLISHED
FM-G0                                     = OPEN
AuthorizationDecision                     = NOT_CREATED
SingleUseGrant                            = NOT_CREATED
BACKEND_IMPORT                            = NOT_EXECUTED
SOLVER_EXECUTION                          = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK                    = NOT_EXECUTED
K1-D                                      = NOT_RELEASED
K1-E                                      = NOT_ADMISSIBLE
physical_gate_effect                      = NONE
physical_evidence_effect                  = NONE
```
