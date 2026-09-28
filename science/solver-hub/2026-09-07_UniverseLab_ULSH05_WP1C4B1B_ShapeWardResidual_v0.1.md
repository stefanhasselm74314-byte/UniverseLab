# ULSH-05 / WP1C4B1B — Shape-Ward residual and passive-equation preflight v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Status:** `DERIVED_CONDITIONAL_REDUNDANCY / COMPONENT SHAPE RESIDUAL OPEN`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Ziel

Nach WP1C4B1A ist die Kinematik bewegter regionaler Integrationsgebiete bis zur zweiten Ordnung eingefroren. Offen blieb, ob die normale Einbettungsvariation der Kappe ein unabhängiger Euler-Lagrange-Kanal ist oder aus den übrigen Feld- und Junction-Gleichungen folgt.

WP1C4B1B beantwortet nur diese Strukturfrage. Es veröffentlicht **noch keine** komponentenweise passive Kraftgleichung.

## 2. Erste Variationsstruktur

Schreibe die vollständige erste Variation der Parentwirkung schematisch als

\[
DS[\delta\Phi]
=
\sum_{s=N,S}\int_{\mathcal M_s}
\left(
\mathcal E_{g,s}:\delta g_s
+\mathcal E_{\phi,s}\,\delta\phi_s
+\mathcal E_{A,s}\cdot\delta A_s
\right)
+
\int_\Sigma \mathcal B.
\]

Der Interface-Anteil wird in unabhängige Paarungen zerlegt:

\[
\mathcal B
=
\frac12\mathcal R_h^{ab}H_{ab}
+\mathcal R_\phi\,\Phi_\Sigma
+\mathcal R_A^a a_{\Sigma a}
+\mathcal R_\sigma s
+\mathcal R_\perp\,\xi.
\]

Diese Gleichung fixiert hier nur die **Kanalstruktur**. Die endgültige komponentenweise Normierung von \(\mathcal R_\perp\) wird erst im Folgeblock eingefroren.

## 3. Gemeinsame normale Diffeomorphismusvariation

WP1C3/C4B0 benutzen den doubly-covariant Vertrag

\[
\delta_\zeta g=-\mathcal L_\zeta\bar g,
\qquad
\delta_\zeta\phi=-\mathcal L_\zeta\bar\phi,
\qquad
\delta_\zeta A=-\mathcal L_\zeta\bar A,
\]

während die Einbettung gleichzeitig transformiert:

\[
z^A\rightarrow z^A+\zeta^A.
\]

Für eine normale Transformation

\[
\zeta^A=\beta N^A
\]

ist \(\beta\) ein einziger physischer Gaugeparameter. Wegen

\[
N=n_N=-n_S
\]

wird er regional als

\[
\beta_N=+\beta,
\qquad
\beta_S=-\beta
\]

dargestellt.

Die vollständige Parentwirkung aus EH+GHY+Skalar+Maxwell+Kappe ist unter dieser gemeinsamen Transformation invariant.

## 4. Off-shell Ward-Identität

Diffeomorphismusinvarianz erzwingt daher für beliebiges kompakt getragenes \(\beta\)

\[
\boxed{
\int_\Sigma \beta\,\mathcal R_\perp
+
\mathfrak N_\perp
\left[
\mathcal E_g,
\mathcal E_\phi,
\mathcal E_A,
\mathcal R_h,
\mathcal R_\phi,
\mathcal R_A,
\mathcal R_\sigma;
\beta
\right]
=0.
}
\]

\(\mathfrak N_\perp\) ist der orientation-safe lineare Funktional, der nach partieller Integration der regionalen Diffeomorphismusvariation entsteht. WP1C4B1B friert **nicht** voreilig eine komponentenreduzierte Formel dafür ein.

Damit gilt der zentrale Satz:

\[
\boxed{
\mathcal E_{g,s}=\mathcal E_{\phi,s}=\mathcal E_{A,s}=0
\quad\land\quad
\mathcal R_h=\mathcal R_\phi=\mathcal R_A=\mathcal R_\sigma=0
\quad\Longrightarrow\quad
\mathcal R_\perp=0.
}
\]

Die Shape-Gleichung ist also **bedingt redundant im vollständigen Gleichungssystem**.

## 5. Was daraus nicht folgt

Insbesondere gilt nicht

\[
\mathcal R_h=0\quad\Longrightarrow\quad\mathcal R_\perp=0.
\]

Die Israel-Gleichung allein schließt den passiven Normal-Kanal nicht.

Ebenso darf off shell nicht gesetzt werden

\[
\mathcal R_\perp=0,
\]

denn `PHYSICAL_BACKGROUND=NOT_ESTABLISHED` und die regionalen Bulkresiduen sind nicht als physisch erfüllt freigegeben.

Für einen asymmetrischen Zwei-Seiten-Shell ist genau diese Trennung zwischen aktiver Israel-Wirkung und passiver Normalbewegung auch aus der allgemeinen Brane-Literatur bekannt. Diese Literatur dient ausschließlich als mathematischer Cross-check; der UniverseLab-Parentvertrag bleibt autoritativ.

## 6. Minimaler unabhängiger Algebra-Kontrollfall

Betrachte

\[
S(q,X)=\frac12(q-X)^2.
\]

Unter gemeinsamer Translation

\[
q\to q+a,
\qquad
X\to X+a
\]

ist die Wirkung invariant. Die Residuen sind

\[
E_q=q-X,
\qquad
E_X=-(q-X),
\]

und daher identisch

\[
E_q+E_X=0.
\]

Setzt man das Feldresiduum \(E_q=0\), folgt \(E_X=0\). Off shell kann \(E_X\neq0\) sein.

Ein zweiter Kontrollvektor modelliert explizit den verbotenen Israel-only-Schluss: Ein Interface-Metrikresiduum kann null sein, während ein Bulkresiduum durch die Ward-Identität einen nichtverschwindenden Shape-Residual erzwingt.

## 7. Warum die komponentenweise passive Gleichung noch offen bleibt

Für C-PHYS-M1 müssen noch in einer einzigen gemeinsamen Orientierung zusammengeführt werden:

1. regionale Einsteinresiduen und Hamilton-/Momentumprojektionen,
2. Skalar- und Maxwellresiduen,
3. Israel-Residual,
4. Skalar-Normalfluss-Junction,
5. Gauge-Normalfluss-Junction,
6. Phasengleichung,
7. Moving-cap-Stress und Moving-GHY-Beiträge,
8. die C4A/C4B0 Vorzeichen- und Extensionkonventionen.

Erst dann ist ein projekt-spezifischer Ausdruck für \(\mathcal R_\perp\) zulässig.

## 8. Ergebnis

**[BEWIESEN]** Die vollständige Diffeomorphismusinvarianz liefert eine off-shell Ward-Identität, welche den normalen Shape-Residual an Bulk- und Junction-Residualen bindet.

**[BEWIESEN]** Sind sämtliche Bulk- und Interfacegleichungen erfüllt, verschwindet der Shape-Residual.

**[BEWIESEN]** Israel allein genügt dafür nicht.

**[OFFEN]** Projekt-spezifische gemeinsame Komponentenform der passiven Gleichung.

**[OFFEN]** Vollständige bewegte Boundary-Hesse.

## 9. Unveränderte Firewalls

```text
WP1_full_shape_residual         NOT_ASSEMBLED_COMPONENTWISE
WP1_full_boundary_hessian       NOT_CLOSED
WP1_full_quadratic_action       NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM       NOT_RELEASED
PHYSICAL_BACKGROUND             NOT_ESTABLISHED
FM-G0                           OPEN
AuthorizationDecision           NOT_CREATED
SingleUseGrant                  NOT_CREATED
BACKEND_IMPORT                  NOT_EXECUTED
SOLVER_EXECUTION                NOT_EXECUTED
PHYSICAL_RESPONSE_RANK          NOT_EXECUTED
K1-D                            NOT_RELEASED
K1-E                            NOT_ADMISSIBLE
physical_gate_effect            NONE
physical_evidence_effect        NONE
```

## 10. Nächster Block

`ULSH-05/WP1C4B1C — Project-specific component shape residual and Gauss-Codazzi/Bianchi reduction`.
