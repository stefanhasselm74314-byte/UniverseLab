# MD-2S Oriented Cap and Junction Ledger v0.1

**Datum:** 2026-08-03  
**Zweig:** HZT-M0-S6 / MD-2S / canonical rebuild track  
**Status:** DERIVED_CONDITIONAL / MODEL FREEZE INCOMPLETE  
**Evidenzwirkung:** NONE  
**Solverfreigabe:** FALSE

## 1. Zweck und Geltungsgrenze

Dieses Ledger leitet das vollständig orientierte lokale Junction-System für den gegenwärtigen Einstein-Maxwell-Skalar-Kern und die bereits registrierte minimale Kappen-/Wicklungsstruktur her. Es friert die **Form** der Gleichungen ein, nicht die noch fehlenden Funktionen oder Zahlenwerte.

Nicht festgelegt werden hier:

- die konkreten Funktionen `lambda(phi)` und `Z_sigma(phi)`,
- die numerische Ladungsnormalisierung `q_sigma`,
- die globale Fluxquantisierung,
- zusätzliche lokalisierte Krümmungs-, Chern-Simons- oder höhere Ableitungsterme,
- die Identität mit der historischen A0-Kappenwirkung.

Daher bleiben MF-001 und MF-002 nur partiell geschlossen und ein offizieller Solver bleibt unzulässig.

## 2. Bulk- und GHY-Struktur

Für jede an die Kappe angrenzende Region `s` gilt

```text
S_bulk,s = integral_Ms d6x sqrt(|g|) [
  (R - 2 Lambda6)/(2 kappa6^2)
  - 1/2 Z_phi(phi) (partial phi)^2
  - V(phi)
  - 1/4 Z_F(phi) F_AB F^AB
],

S_GHY,s = M6^4 integral_Sigma d5x sqrt(|h|) K_s,
M6^4 = 1/kappa6^2.
```

`K_s` wird mit der **aus der jeweiligen Region herausweisenden** Einheitsnormalen `n_s^A` gebildet. Die Outward-Sum-Konvention vermeidet eine stillschweigende Vermischung von Sprung- und Summenschreibweisen.

## 3. Minimale lokalisierte Wirkung

Die bereits registrierten metrischen, skalaren und Gauge-Junctionformeln werden genau durch

```text
S_Sigma = - integral_Sigma d5x sqrt(|h|) [
  lambda(phi)
  + 1/2 Z_sigma(phi) h^ab D_a sigma D_b sigma
],

D_a sigma = partial_a sigma - q_sigma A_a
```

erzeugt.

Für einen axialen Wicklungszweig

```text
sigma = n sigma_chi,
D_mu sigma = 0,
D_chi sigma = d_chi = n - q_sigma A_chi,
X_sigma = h^ab D_a sigma D_b sigma = d_chi^2/L_Sigma^2,
Y_sigma = Z_sigma X_sigma.
```

`n` ist bei kompakter Phase ganzzahlig. Die genaue Normierung von `n`, `q_sigma` und `A_chi` bleibt Teil des offenen globalen Gauge-/Fluxvertrags.

## 4. Oberflächenstress

Aus der lokalisierten Wirkung folgt

```text
S^a_b = -lambda delta^a_b
        + Z_sigma (D^a sigma D_b sigma - 1/2 delta^a_b X_sigma).
```

Im axialen Hintergrund:

```text
S^mu_nu = -(lambda + Y_sigma/2) delta^mu_nu,
S^chi_chi = -lambda + Y_sigma/2.
```

Damit ist die Wicklungsenergie eine kontrollierte anisotrope Oberflächenquelle. `Z_sigma >= 0` und `X_sigma >= 0` implizieren `Y_sigma >= 0`.

## 5. Extrinsische Krümmung

Für

```text
ds6^2 = exp(2A) gbar_munu dx^mu dx^nu + dr^2 + L^2 dchi^2
```

und eine radiale Normalenkomponente `n_s^r = +/-1` gilt auf jeder Seite:

```text
K^mu_nu|s = n_s^r A'_s delta^mu_nu,
K^chi_chi|s = n_s^r L'_s/L_s,
K_s = 4 n_s^r A'_s + n_s^r L'_s/L_s.
```

Definiere die orientierten Summen

```text
A_Sigma = sum_s n_s^r A'_s,
L_Sigma = sum_s n_s^r L'_s/L_s.
```

Die Werte `A'_s`, `L'_s` müssen echte einseitige Grenzwerte sein. Eine zentrale Differenz über die Junction ist unzulässig.

## 6. Israel-Gleichung in Outward-Sum-Form

Die verwendete Konvention lautet

```text
M6^4 sum_s (K^a_b - K delta^a_b)_s = S^a_b.
```

Daraus folgen zwei unabhängige metrische Komponenten.

### EQ-MD2S-JNC-001 — externe 4D-Komponente

```text
-M6^4 (3 A_Sigma + L_Sigma) = -lambda - Y_sigma/2,
```

oder

```text
lambda = M6^4 (3 A_Sigma + L_Sigma) - Y_sigma/2.
```

### EQ-MD2S-JNC-002 — interne chi-Komponente

```text
-4 M6^4 A_Sigma = -lambda + Y_sigma/2,
```

oder

```text
lambda = 4 M6^4 A_Sigma + Y_sigma/2.
```

## 7. Anisotropieschluss und reine Spannung

Die Differenz der metrischen Gleichungen liefert exakt

```text
Y_sigma_required = M6^4 (L_Sigma - A_Sigma).
```

Danach ist

```text
lambda_required = (M6^4/2) (7 A_Sigma + L_Sigma).
```

Für reine Spannung `Y_sigma=0` gilt notwendig

```text
A_Sigma = L_Sigma,
lambda = 4 M6^4 A_Sigma.
```

Für einen gesunden minimalen Wicklungssektor folgt die Positivitätsbedingung

```text
L_Sigma - A_Sigma >= 0.
```

Ein negatives `M6^4(L_Sigma-A_Sigma)` kann durch einen positiven minimalen Wicklungsterm nicht realisiert werden.

## 8. Skalar-Junction

Bei konstantem `q_sigma` und ohne weitere lokalisierte Skalarableitungen ergibt die Variation von `phi`

```text
sum_s n_s^r Z_phi,s phi'_s
+ lambda_,phi
+ 1/2 Z_sigma,phi X_sigma
= 0.
```

Dies verallgemeinert die ältere Projektformel ohne `Z_phi`-Faktor. Die ältere Form ist nur im Spezialfall `Z_phi=1` gültig.

Falls `q_sigma`, zusätzliche Kappenterme oder nichtminimale Krümmungskopplungen von `phi` abhängen, entstehen zusätzliche Beiträge und dieses Ledger muss versioniert erweitert werden.

## 9. Gauge-Junction

Die tangentiale Gaugevariation liefert

```text
sum_s n_s^r Z_F,s F_s^{r chi}
- q_sigma Z_sigma D^chi sigma
= 0,

F^{r chi} = F_rchi/L^2,
D^chi sigma = d_chi/L_Sigma^2.
```

Mit dem Maxwell-Erstintegral jeder Region

```text
Q_s = exp(4A_s) Z_F,s F_rchi,s/L_s
```

wird am stetigen induzierten Hintergrund

```text
sum_s n_s^r Q_s exp(-4A_Sigma)/L_Sigma
- q_sigma Z_sigma d_chi/L_Sigma^2
= 0.
```

Diese Gleichung ersetzt keine globale Fluxquantisierung.

## 10. Phasengleichung

Die lokalisierte Phase erfüllt

```text
D_a (Z_sigma D^a sigma) = 0.
```

Für konstante axiale Hintergrundgrößen und `sigma=n chi` ist die lokale Differentialgleichung erfüllt. Die Ganzzahligkeit des Wicklungssektors und die Gauge-Patch-Konsistenz bleiben globale Bedingungen.

## 11. Induzierte Kontinuität

Vor Anwendung der Junction-Gleichungen müssen in einem gemeinsamen 4D-Frame gelten:

```text
[A]_Sigma = 0,
[L]_Sigma = 0,
[phi]_Sigma = 0,
```

sofern keine ausdrücklich zugelassenen Doppel- oder Schichtquellen vorliegen. Für `A_chi` ist die gauge-kovariante Patchbedingung maßgeblich; nicht der rohe Potentialwert allein.

Ein Mismatch der induzierten Metrik ist kein großer Junctionresidualwert, sondern ein ungültiges Kleben der beiden Regionen.

## 12. Residualvektor

Ein vollständiger Randexport muss mindestens liefern:

```text
R_cont_A,
R_cont_L,
R_cont_phi,
R_metric_4d,
R_metric_chi,
R_anisotropy,
R_scalar,
R_gauge,
R_phase_local,
R_flux_global,
R_normal_orientation.
```

Die beiden metrischen Residuen sind

```text
R_metric_4d = -M6^4(3A_Sigma+L_Sigma) + lambda + Y_sigma/2,
R_metric_chi = -4M6^4 A_Sigma + lambda - Y_sigma/2.
```

Die Anisotropiediagnostik ist

```text
R_anisotropy = Y_sigma - M6^4(L_Sigma-A_Sigma).
```

## 13. Dimensionshygiene

Mit dimensionslosem `chi` gilt:

```text
[M6^4] = M^4,
[A_Sigma] = [L_Sigma] = M,
[lambda] = [Y_sigma] = M^5,
[X_sigma] = M^2,
[Z_sigma] = M^3.
```

Die Dimension von `A_chi` als Komponente entlang einer dimensionslosen Koordinate ist separat von der kartesischen Komponentenangabe zu behandeln. Entscheidend ist, dass `d_chi=n-q_sigma A_chi` dimensionslos und gauge-invariant ist.

## 14. Action-Freeze-Wirkung

```text
MF-001 bulk action form = PARTIAL_CONDITIONAL
MF-002 localized action form = PARTIAL_CONDITIONAL
MF-005 oriented junction form = DERIVED_CONDITIONAL
MF-005 numerical executability = BLOCKED
```

Weiter offen:

- exakte Funktionen `V`, `Z_phi`, `Z_F`, `lambda`, `Z_sigma`,
- `Lambda6` gegen historische Potentialkonvention,
- zusätzliche lokalisierte Terme,
- Winkelperiode und Wicklungsnormalisierung,
- globale Fluxquantisierung,
- einseitige numerische Randdaten und Toleranzen.

Daher gilt weiterhin:

```text
R1.1 = BLOCKED_BY_R1.0
OFFICIAL_SOLVER_IMPLEMENTATION = FORBIDDEN
TWO_JUNCTION_VERDICT = NOT_EXECUTABLE
K1-D = NOT_RELEASED
K1-E = NOT_ADMISSIBLE
```
