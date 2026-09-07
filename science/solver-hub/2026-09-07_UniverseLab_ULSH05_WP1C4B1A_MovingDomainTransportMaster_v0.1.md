# ULSH-05 / WP1C4B1A — Moving-domain transport master v0.1

**Datum:** 2026-09-07  
**Modell:** `HZT-M0-S6-C-PHYS-M1`  
**Basis-main:** `2dec38781b453a6688f4f5ef0be08b57943ea012`  
**Status:** `DERIVED KINEMATIC DOMAIN TRANSPORT / DYNAMICAL SHAPE RESIDUAL OPEN`  
**Physical gate effect:** `NONE`  
**Physical evidence effect:** `NONE`

## 1. Warum B1A vor der bewegten Boundary-Hesse nötig ist

WP1B hat die EH+GHY-Variation für eine feste Referenzgrenze formuliert. WP1C3/C4A haben die bewegte Interface-Geometrie und die linearen Junction-Preflights eingefroren. WP1C4B0 hat die zweite Pullback-Kinematik und die off-shell Pfadabhängigkeit fixiert.

Was bisher noch fehlt, ist die Variation des **Integrationsgebiets selbst**. Für eine bewegte Kappe ändern sich die beiden regionalen Bulkdomänen. Die vollständige erste oder zweite Wirkungsvariation darf deshalb nicht nur die lokalen Bulk-/GHY-/Cap-Dichten variieren; sie muss zusätzlich den Transport der Domain berücksichtigen.

B1A friert ausschließlich diese geometrische Transportidentität ein. Eine physische Normal-Kraftgleichung beziehungsweise Shape-EOM wird hier noch nicht erzeugt.

---

## 2. Regionaler Domain-Flow

Für jede Region `M_s` sei

\[
\mathcal M_s(\epsilon)=F_{s,\epsilon}(\mathcal M_s)
\]

und

\[
\frac{dF_{s,\epsilon}}{d\epsilon}
=v_{s,\epsilon}\circ F_{s,\epsilon}.
\]

Wie in C4B0 definieren wir

\[
z_s=v_{s,\epsilon}|_0,
\qquad
w_s=\left.\frac{dv_{s,\epsilon}}{d\epsilon}\right|_0.
\]

`w_s` ist ein zweiter Lie-Generator, nicht ohne weitere Konvention die rohe Koordinatenbeschleunigung der Kappe.

Die regionale Lagrange-Topform sei

\[
\mathbf L_s(\epsilon)
=\bar{\mathbf L}_s
+\epsilon\mathbf L_{1,s}
+\frac12\epsilon^2\mathbf L_{2,s}
+O(\epsilon^3).
\]

In sechs Dimensionen ist jede 6-Form automatisch geschlossen:

\[
d\mathbf L_s=0.
\]

---

## 3. Erste Transportvariation

Schreibe die bewegte Wirkung auf der festen Referenzregion:

\[
I_s(\epsilon)
=\int_{\mathcal M_s}F_{s,\epsilon}^*\mathbf L_s(\epsilon).
\]

Dann folgt aus der ersten Pullback-Ableitung

\[
\boxed{
I_{1,s}
=\frac{dI_s}{d\epsilon}\Big|_0
=\int_{\mathcal M_s}
\left(
\mathbf L_{1,s}
+\mathcal L_{z_s}\bar{\mathbf L}_s
\right).
}
\]

Mit Cartans Formel

\[
\mathcal L_z=d\,i_z+i_zd
\]

und `d Lbar_s=0` ergibt sich

\[
\boxed{
I_{1,s}
=\int_{\mathcal M_s}\mathbf L_{1,s}
+\int_{\partial\mathcal M_s}i_{z_s}\bar{\mathbf L}_s.
}
\]

Der erste Term ist die Eulerian Variation der Dichte auf der festen Referenzregion. Der zweite ist der reine Domain-Transportterm.

Diese Zerlegung ist **Bookkeeping**, kein separat beobachtbarer Gauge-invarianter Kraftkanal.

---

## 4. Zweite Transportvariation

Aus dem in C4B0 eingefrorenen zweiten Pullback folgt

\[
\boxed{
I_{2,s}
=\frac{d^2I_s}{d\epsilon^2}\Big|_0
=\int_{\mathcal M_s}
\left[
\mathbf L_{2,s}
+2\mathcal L_{z_s}\mathbf L_{1,s}
+(\mathcal L_{w_s}+\mathcal L_{z_s}^2)\bar{\mathbf L}_s
\right].
}
\]

Erneute Anwendung von Cartan/Stokes liefert

\[
\boxed{
I_{2,s}
=\int_{\mathcal M_s}\mathbf L_{2,s}
+\int_{\partial\mathcal M_s}
\left[
2i_{z_s}\mathbf L_{1,s}
+i_{w_s}\bar{\mathbf L}_s
+i_{z_s}\mathcal L_{z_s}\bar{\mathbf L}_s
\right].
}
\]

Hierbei wurde verwendet:

\[
[\mathcal L_z,i_z]=i_{[z,z]}=0.
\]

Die drei Randstücke besitzen klare Rollen:

1. `2 i_z L1`: Kopplung von erster Dichtevariation und erster Grenzbewegung;
2. `i_w Lbar`: zweiter Generator/zweite Pfadtangente;
3. `i_z L_z Lbar`: konvektiver quadratischer Beitrag derselben ersten Grenzbewegung.

Diese Formel ist eine **Transportidentität**, keine bereits assemblierte HZT-Grenzhessianformel.

---

## 5. Interne Kappe: erster Ordnung

Regional sei

\[
z_s=\xi_s n_s+\tau^ae_a.
\]

Da `Lbar_s` eine 6-Form ist und die Kappe nur fünf unabhängige Tangentialrichtungen besitzt, gilt für einen rein tangentialen Vektor

\[
\bar X_s^*(i_\tau\bar{\mathbf L}_s)=0.
\]

Damit

\[
\boxed{
\bar X_s^*(i_{z_s}\bar{\mathbf L}_s)
=\xi_s\,\bar X_s^*(i_{n_s}\bar{\mathbf L}_s).
}
\]

WP1C4A liefert

\[
\xi_N=+\xi,
\qquad
\xi_S=-\xi.
\]

Die **kanonische orientationssichere** zweiseitige Schreibweise bleibt daher

\[
\boxed{
\sum_{s=N,S}
\bar X_s^*(i_{z_s}\bar{\mathbf L}_s).
}
\]

Erst wenn zusätzlich eine gemeinsame Orientierung der beiden regional geerbten 5-Formen festgelegt wurde, darf man dies zu einer skalaren Differenzform

\[
\xi(\ell_N^{\rm out}-\ell_S^{\rm out})\,\mathrm{vol}_\Sigma
\]

reduzieren.

B1A friert diese zusätzliche Orientierung **nicht stillschweigend** ein.

---

## 6. Interne Kappe: zweite Ordnung

C4B0 liefert für den zweiten Generator

\[
w_s=\chi_s n_s+\nu^ae_a,
\]

mit

\[
\chi_N=+\chi,
\qquad
\chi_S=-\chi.
\]

Die regionale zweite Domain-Randform lautet damit weiterhin invariant

\[
\boxed{
2i_{z_s}\mathbf L_{1,s}
+i_{w_s}\bar{\mathbf L}_s
+i_{z_s}\mathcal L_{z_s}\bar{\mathbf L}_s.
}
\]

Eine komponentenreduzierte Formel erfordert zusätzlich:

- gemeinsame Orientation Map;
- deklarierte regionale Extension von `z_s`;
- deklarierte regionale Extension von `w_s`;
- Behandlung etwaiger Ecken/Ränder der Kappe.

Diese Angaben werden nicht geraten.

---

## 7. Bewegte GHY- und Kappenintegrale

Ist `B_s(epsilon)` eine 5-Form auf der regionalen Kappe, gilt direkt aus C4B0:

\[
Q_1[B_s]=B_{1,s}+\mathcal L_{z_s}\bar B_s,
\]

\[
Q_2[B_s]
=B_{2,s}+2\mathcal L_{z_s}B_{1,s}
+(\mathcal L_{w_s}+\mathcal L_{z_s}^2)\bar B_s.
\]

Diese Regel gilt sowohl für die GHY-5-Form jeder Region als auch für die lokalisierte Kappen-5-Form.

Damit ist die kinematische Infrastruktur für B1B vorhanden. Was noch fehlt, ist die dynamische Assemblierung der Eulerian EH/Materie-Variation, der regionalen Domain-Flüsse, der bewegten GHY-Pullbacks und der Cap-Variation zu einem gemeinsamen First-Shape-Residual.

---

## 8. Zwei-Regionen-Kontrollmodell

Ein besonders harter Vorzeichentest ist

\[
I(\epsilon)
=\int_0^{y(\epsilon)}f_N(x,\epsilon)dx
+\int_{y(\epsilon)}^L f_S(x,\epsilon)dx,
\]

mit

\[
y(\epsilon)=y_0+\epsilon\xi+\frac12\epsilon^2\chi.
\]

Dann

\[
\boxed{
I_1
=\int_0^{y_0}f_{N,1}dx
+\int_{y_0}^{L}f_{S,1}dx
+\xi(f_{N,0}-f_{S,0})|_{y_0}.
}
\]

Die zweite Ableitung lautet

\[
\boxed{
\begin{aligned}
I_2={}&
\int_0^{y_0}f_{N,2}dx
+\int_{y_0}^{L}f_{S,2}dx\\
&+2\xi(f_{N,1}-f_{S,1})|_{y_0}\\
&+\chi(f_{N,0}-f_{S,0})|_{y_0}\\
&+\xi^2(f'_{N,0}-f'_{S,0})|_{y_0}.
\end{aligned}
}
\]

Dies ist exakt die gemeinsame-Koordinatenform der regionalen C4A/C4B0-Vorzeichenstruktur.

---

## 9. Gültigkeits- und Gaugegrenze

Die Summe aus Eulerian Variation und Domain-Transport ist die sinnvolle geometrische Größe. Die künstliche Zerlegung

```text
Eulerian piece | shape piece
```

hängt von der gewählten Referenzdomain und vom Gauge-/Pullback-Split ab.

Daher gilt ausdrücklich:

```text
regional transport term != physical brane force by itself
```

Ein physischer oder redundanter Shape-Residual kann erst nach Assemblierung der **gesamten** Parentwirkung und Prüfung der Diffeomorphismus-/Bianchi-/Junction-Identitäten beurteilt werden.

Eine mathematische Gegenprüfung an der allgemeinen Weiss-Variation bewegter GR-Grenzen bestätigt, dass bewegte allgemeine Grenzen zusätzliche Boundary-Beiträge tragen; diese Literatur dient ausschließlich als externer Cross-check und ist keine UniverseLab-Projekt-Autorität.

---

## 10. Noch offen

- vollständiger First-Shape-Residual von EH+GHY+Skalar+Maxwell+Kappe;
- Entscheidung, ob dessen Normalanteil unabhängig oder durch Bulk/Junction/Bianchi redundant ist;
- zweite bewegte GHY-Variation;
- zweite bewegte Kappenvariation;
- vollständige Boundary-Hesse;
- Konfigurationsraum-Verbindung;
- freigegebener pertubierter BVP-Operator;
- S/V/T und Constraint-Elimination;
- physischer Hintergrund;
- Ghostfreiheit/Stabilität;
- 6D→4D-Observablen.

Unverändert:

```text
WP1_full_shape_residual = NOT_ASSEMBLED
WP1_configuration_space_connection = NOT_FROZEN
WP1_full_boundary_hessian = NOT_CLOSED
WP1_full_quadratic_action = NOT_CLOSED
PERTURBED_JUNCTION_SYSTEM = NOT_RELEASED
PHYSICAL_BACKGROUND = NOT_ESTABLISHED
FM-G0 = OPEN
AuthorizationDecision = NOT_CREATED
SingleUseGrant = NOT_CREATED
BACKEND_IMPORT = NOT_EXECUTED
SOLVER_EXECUTION = NOT_EXECUTED
PHYSICAL_RESPONSE_RANK = NOT_EXECUTED
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
physical_gate_effect = NONE
physical_evidence_effect = NONE
```

## 11. Nächster Block

`ULSH-05/WP1C4B1B` muss den vollständigen ersten Shape-Residual der Parentwirkung assemblieren. Erst wenn dessen Status gegenüber Diffeomorphismus-/Bianchi-/Junction-Identitäten geklärt ist, darf `WP1C4B1C` die zweite moving-boundary Variation als Boundary-Hessian-Baustein aufbauen.
