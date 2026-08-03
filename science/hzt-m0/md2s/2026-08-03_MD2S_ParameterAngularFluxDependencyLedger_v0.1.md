# MD-2S Parameter, Angular, Flux and Dependency Ledger v0.1

**Datum:** 2026-08-03  
**Zweig:** HZT-M0-S6 / MD-2S / canonical rebuild track  
**Status:** PARTIAL_STRUCTURAL_FREEZE  
**Evidenzwirkung:** NONE  
**Solverfreigabe:** FALSE

## 1. Zweck und Geltungsgrenze

Dieses Ledger fixiert die Dimensions-, Bereichs-, Winkel-, Wicklungs-, Flux- und Abhängigkeitsstruktur des aktuellen MD-2S-Canonical-Rebuild-Zweigs. Es bestimmt keine bislang quellenmäßig unbelegte konkrete Form von

```text
U(phi), Z_phi(phi), Z_F(phi), lambda(phi), Z_sigma(phi).
```

Es ersetzt weder die fehlende historische A0-Wirkung noch einen Randwertsolver. Sein Zweck ist, MF-006 von `OPEN` auf `PARTIAL_STRUCTURAL_FREEZE` anzuheben und exakt auszuweisen, welche Eingaben vor einem symbolischen Abhängigkeitsaudit und vor jeder offiziellen Solverimplementierung noch fehlen.

## 2. Koordinaten- und Einheitenvertrag

Es gelten natürliche Einheiten mit `[L]=M^-1`. Der axialsymmetrische Hintergrund lautet

```text
ds6^2 = exp(2A(r)) gbar_munu dx^mu dx^nu + dr^2 + L(r)^2 dchi^2.
```

Die Koordinatenkonvention ist

```text
[r] = M^-1,
chi dimensionslos,
chi ~ chi + Delta_chi,
Delta_chi > 0,
[L] = M^-1,
[A] = 1.
```

Da `chi` dimensionslos ist, tragen koordinatenbasierte Komponenten andere Massendimensionen als orthonormale Komponenten:

```text
[A_chi] = M,
[F_rchi] = M^2,
[F_rchi/L] = M^3,
[Q] = M^3,
```

mit

```text
Q = exp(4A) Z_F F_rchi/L.
```

Damit besitzt das Maxwell-Invariant `F_AB F^AB` weiterhin Dimension `M^6`.

## 3. Parameter- und Funktionsklassen

### 3.1 Fundamentale Bulkgrößen

```text
kappa6_squared : M^-4,  kappa6_squared > 0,
Lambda_geom    : M^2,   reell,
K4             : M^2,   reell,
U(phi)         : M^6,
Z_phi(phi)     : 1,
Z_F(phi)       : 1,
phi            : M^2.
```

Für den minimal gesunden Hintergrundzweig gilt im gesamten Integrationsgebiet

```text
Z_phi(phi) > 0,
Z_F(phi) > 0.
```

Die Hintergrundgleichungen benötigen mindestens `C^1`-Funktionen. Ein späteres lineares Stabilitäts- oder Jacobian-Audit benötigt grundsätzlich mindestens `C^2`, sofern zweite Funktionsableitungen auftreten.

`Lambda_geom` und `U(phi)` bleiben verschiedene Größen. Die historische Bezeichnung `V(phi)=Lambda6+beta phi^2` darf ohne Dimensions- und Wirkungsidentitätsnachweis nicht in diesen Vertrag eingesetzt werden.

### 3.2 Lokalisierte Größen

```text
lambda(phi)    : M^5,
Z_sigma(phi)   : M^3,
sigma          : 1,
q_sigma        : M^-1,
N_sigma        : ganze Zahl.
```

Für den minimalen positiven Wicklungszweig gilt

```text
Z_sigma(phi) >= 0.
```

Die konkrete Form von `lambda(phi)` und `Z_sigma(phi)`, die Normierung von `q_sigma` und die Frage, ob der Kappensektor weitere lokalisierte Terme enthält, bleiben offen.

### 3.3 Geometrische und regionale Größen

```text
rho_cap        : M^-1,
A0             : 1,
phi0           : M^2,
Q_s            : M^3 pro glatter Region s,
n_s^r          : +1 oder -1,
Delta_chi      : 1 und > 0.
```

Die additive Konstante von `A` ist erst nach Wahl eines vierdimensionalen Frames fixiert. `A0` darf daher nicht gleichzeitig als freier physikalischer Parameter und als Framekonvention gezählt werden.

## 4. Periodische Wicklung

Die lokalisierte Phase ist modulo `2 pi` definiert. Für eine Kreisperiode `Delta_chi` gilt

```text
sigma(chi + Delta_chi) - sigma(chi) = 2 pi N_sigma,
N_sigma in Z.
```

Damit lautet der konstante Wicklungsgradient

```text
partial_chi sigma = 2 pi N_sigma/Delta_chi.
```

Die gaugeinvariante Kombination ist

```text
d_chi = 2 pi N_sigma/Delta_chi - q_sigma A_chi.
```

Daraus folgen

```text
X_sigma = d_chi^2/L^2,
Y_sigma = Z_sigma X_sigma.
```

Dimensionsprüfung:

```text
[d_chi] = 1,
[X_sigma] = M^2,
[Y_sigma] = M^5.
```

Die frühere Kurzschreibweise `sigma=n chi` ist nur dann eindeutig, wenn die verwendete Winkelperiode und die Definition von `n` gleichzeitig angegeben werden. Bei `Delta_chi=2 pi` gilt `partial_chi sigma=N_sigma`.

## 5. Reparametrisierungsinvarianz der Winkelkoordinate

Unter einer reinen Koordinatenumbenennung

```text
chi_new = c chi,
c > 0,
```

transformieren

```text
Delta_chi_new = c Delta_chi,
L_new = L/c,
A_chi_new = A_chi/c,
F_rchi_new = F_rchi/c,
d_chi_new = d_chi/c.
```

Damit bleiben invariant:

```text
X_sigma_new = X_sigma,
F_rchi_new/L_new = F_rchi/L,
Q_new = Q,
Phi_F,new = Phi_F.
```

Jede numerische Datei muss deshalb die tatsächlich verwendete `Delta_chi` ausweisen. Werte für `L`, `A_chi` oder `F_rchi` sind ohne diese Konvention nicht vollständig interpretierbar.

## 6. Lokales Gauge-Matching

Mit nach außen gerichteten Normalen jeder Region lautet das lokale Gauge-Residual

```text
R_gauge = sum_s n_s^r Z_F,s F_s^(r chi)
          - q_sigma Z_sigma D^chi sigma.
```

Für den axialen Ansatz und stetiges induziertes `A` und `L` kann es mit dem regionalen Maxwell-Erstintegral geschrieben werden als

```text
R_gauge = exp(-4A)/L sum_s n_s^r Q_s
          - q_sigma Z_sigma d_chi/L^2.
```

Diese Gleichung erlaubt im Allgemeinen unterschiedliche regionale Konstanten `Q_s`, falls die Kappe eine lokalisierte Gaugequelle trägt. Sie ist keine globale Fluxquantisierung.

## 7. Globale Fluxquantisierung

Der gesamte interne Flux ist

```text
Phi_F = integral_internal F
      = sum_s integral_Is dr integral_0^Delta_chi dchi F_rchi^(s).
```

Für axialsymmetrische Profile folgt

```text
Phi_F = Delta_chi sum_s integral_Is dr F_rchi^(s)
      = Delta_chi sum_s integral_Is dr
        [Q_s L_s exp(-4A_s)/Z_F,s].
```

Mit dimensionslosem `chi` gilt

```text
[Phi_F] = M.
```

Eine globale U(1)-Quantisierung besitzt strukturell die Form

```text
q_ref Phi_F = 2 pi N_F,
N_F in Z,
```

wobei

```text
[q_ref] = M^-1.
```

`q_ref` ist die Referenz- beziehungsweise Minimalladung des globalen U(1)-Bündels. Die Identifikation `q_ref=q_sigma` ist nur zulässig, wenn nachgewiesen ist, dass die lokalisierte Phase die minimale Ladung trägt. Diese Identität ist im aktuellen Quellenstand offen.

Das zu exportierende globale Residuum lautet

```text
R_flux = q_ref Phi_F - 2 pi N_F.
```

Eine Aussage über Fluxquantisierung ist erst zulässig, wenn zusätzlich Gauge-Patches, Übergangsfunktion und Ladungsnormalisierung festgelegt sind.

## 8. Glatter Pol und Winkelperiode

An einem glatten Pol gilt

```text
Delta_chi L'(r_pole) = 2 pi
```

mit der entsprechend nach außen oder entlang der gewählten radialen Koordinate orientierten Ableitung. Der lokale Defizitwinkel ist

```text
delta = 2 pi - Delta_chi |L'(r_pole)|.
```

Die Betragsform trennt die lokale Glattheit von der Wahl, ob die radiale Koordinate zum Pol hin oder vom Pol weg wächst. Für einen konkreten Solver muss die Vorzeichenkonvention pro Pol ausdrücklich angegeben werden.

## 9. Abhängigkeitsstufen

Der aktuelle symbolische Ablauf wird in folgende gerichtete Stufen zerlegt.

### Stufe P0 — Modellidentität und Funktionen

```text
kappa6_squared,
Lambda_geom,
U(phi), Z_phi(phi), Z_F(phi),
lambda(phi), Z_sigma(phi),
q_sigma, q_ref,
Delta_chi,
integer sectors N_sigma and N_F,
region count and topology.
```

### Stufe P1 — Rand- und Framekonventionen

```text
four-dimensional frame condition,
radial coordinate orientation,
outward normals,
pole regularity,
gauge patches,
cap positions,
continuity rules.
```

### Stufe P2 — Symbolische Gleichungssysteme

```text
radial Einstein-Maxwell-scalar equations,
centre series,
regional Maxwell first integrals,
metric junctions,
scalar junction,
local gauge junction,
phase equation,
global flux equation.
```

### Stufe P3 — Freie Daten und BVP-Zählung

```text
independent central data,
regional flux constants,
cap location or geometric replacement,
independent localized controls,
integer sectors,
constraint count,
gauge/frame removals.
```

Die konkrete Liste unabhängiger Schießparameter bleibt offen, bis P0 und P1 vollständig fixiert und die Gleichungsabhängigkeiten ranggeprüft sind.

### Stufe P4 — Numerische Lösung

```text
A_s(r), L_s(r), phi_s(r), A_chi,s(r),
one-sided derivatives,
constraint and matching residuals,
convergence diagnostics.
```

### Stufe P5 — Abgeleitete Größen

```text
Phi_F,
V_W,
M4_squared,
R_circle,
mode operators and spectra,
benchmark observables.
```

### Stufe P6 — Freigabebrücken

```text
physical identification,
6D-to-4D EFT map,
forward observables,
K1-D release audit,
K1-E admissibility audit.
```

## 10. Aktuelle Blocker des Graphen

Der Graph ist strukturell definiert, aber nicht ausführbar, weil mindestens folgende P0/P1-Knoten offen sind:

```text
exact U(phi),
exact Z_phi(phi),
exact Z_F(phi),
exact lambda(phi),
exact Z_sigma(phi),
q_sigma normalization,
q_ref and charge lattice,
Delta_chi adoption,
gauge-patch transition rule,
complete second-region geometry,
frame condition,
dimensionless solver variables,
residual tolerances.
```

Daher gilt:

```text
MF-006 = PARTIAL_STRUCTURAL_FREEZE,
R1.1 = BLOCKED,
MD2S_SOLVER = NOT_AUTHORIZED,
TWO_JUNCTION_VERDICT = NOT_EXECUTABLE.
```

## 11. Verbotene Schlussfolgerungen

- Ein ganzzahliger Wicklungssektor bestimmt nicht automatisch den globalen Fluxsektor.
- `q_sigma` darf nicht ohne Ladungsgitter-Nachweis mit `q_ref` identifiziert werden.
- Lokales Gauge-Matching ersetzt keine globale Fluxquantisierung.
- Eine Wahl `Delta_chi=2 pi` ist eine Koordinatenkonvention, kein physikalischer Messwert.
- Eine positive Wicklungsenergie beweist keine vollständige Stabilität.
- Ein azyklischer Abhängigkeitsgraph beweist keine Lösbarkeit des Randwertproblems.
- Ein technisch ausführbarer diagnostischer Evaluator besitzt keine Evidenzwirkung.
- K1-D und K1-E bleiben unverändert.

## 12. Freeze-Wirkung

Dieses Ledger aktualisiert den Stand zu

```text
MF-001 = PARTIAL_STRUCTURAL_FREEZE,
MF-002 = PARTIAL_STRUCTURAL_FREEZE,
MF-003 = PARTIAL_CONDITIONAL,
MF-004 = PARTIAL_CONDITIONAL,
MF-005 = PARTIAL_CONDITIONAL,
MF-006 = PARTIAL_STRUCTURAL_FREEZE,
MF-007 = PARTIAL.
```

Der nächste exakte Schritt ist nicht das Schreiben eines Solvers, sondern die quellenbasierte Entscheidung über die fünf offenen Funktionen, Ladungs- und Winkelkonventionen sowie die vollständige zweite Region. Danach kann ein formaler BVP-Freiheitsgrad- und Gleichungsrang-Audit entscheiden, ob R1.1 geöffnet werden darf.
