# MD-2S Bulk, Localized Action and Junction Ledger v0.1

**Datum:** 2026-08-03  
**Zweig:** HZT-M0-S6 / MD-2S / canonical rebuild track  
**Status:** PARTIAL_CONDITIONAL / MODEL FREEZE NOT COMPLETE  
**Evidenzwirkung:** NONE  
**Solverfreigabe:** FALSE

## 1. Zweck und Geltungsgrenze

Dieses Ledger fixiert die Vorzeichen-, Dimensions-, Normalen- und Variationsstruktur des aktuellen kanonischen Einstein-Maxwell-Skalar-Zweigs mit einer codimension-1-Kappe. Es ersetzt weder die fehlende historische A0-Wirkung noch bestimmt es die noch offenen Funktionen `U(phi)`, `Z_phi(phi)`, `Z_F(phi)`, `lambda(phi)` und `Z_sigma(phi)`.

Die folgenden Aussagen sind deshalb **strukturgenau, aber funktional konditional**. Eine numerische Implementierung des vollständigen MD-2S-Randwertproblems bleibt verboten, bis alle offenen Funktionen, Parameter, Winkel- und Fluxkonventionen sowie die zweite Seite vollständig fixiert sind.

## 2. Symboltrennung gegen Lambda-Doppelzählung

Zur Vermeidung der bisherigen Mehrdeutigkeit werden zwei verschiedene Größen verwendet:

```text
Lambda_geom : geometrische kosmologische Konstante im Einstein-Hilbert-Sektor,
U(phi)      : skalare 6D-Energiedichte im Materiesektor.
```

Die kanonische Bulkwirkung lautet in jeder glatten Region `M_s`

```text
S_bulk,s = integral_Ms d6x sqrt(|g|) [
  (R - 2 Lambda_geom)/(2 kappa6^2)
  - 1/2 Z_phi(phi) (partial phi)^2
  - U(phi)
  - 1/4 Z_F(phi) F_AB F^AB
].
```

Damit besitzt die konstante Vakuumenergiedichte die Kombination

```text
rho_vac,total(phi) = Lambda_geom/kappa6^2 + U(phi).
```

Die historische Schreibweise `V(phi)=Lambda6+beta phi^2` darf nicht identifiziert werden, solange nicht geklärt ist, ob das historische `Lambda6` eine Krümmung `M^2`, eine Energiedichte `M^6` oder bereits eine reskalierte dimensionslose Größe bezeichnet.

## 3. GHY- und Kappenwirkung

Für jede Region wird der Gibbons-Hawking-York-Term mit der nach außen gerichteten spacelike Normalen `n_s^A` verwendet:

```text
S_GHY,s = (1/kappa6^2) integral_Sigma d5x sqrt(|h|) K_s,
K_s = h^{ab} K_ab^(s),
K_ab^(s) = h_a^A h_b^B nabla_A n_B^(s).
```

Die minimale aktuelle Kappenwirkung wird strukturell fixiert als

```text
S_Sigma = - integral_Sigma d5x sqrt(|h|) [
  lambda(phi) + 1/2 Z_sigma(phi) X_sigma
],

X_sigma = h^{ab} D_a sigma D_b sigma,
D_a sigma = partial_a sigma - q_sigma A_a.
```

Für den statischen Wicklungsansatz

```text
sigma = n chi,
D_chi sigma = n - q_sigma A_chi,
X_sigma = (n - q_sigma A_chi)^2/L^2.
```

Die Funktionen und Parameter bleiben offen, aber ihre Rollen und Dimensionen sind fixiert:

```text
[lambda] = M^5,
[Z_sigma] = M^3,
[sigma] = 1,
[q_sigma] = M^-1,
[X_sigma] = M^2,
Y_sigma := Z_sigma X_sigma = M^5.
```

## 4. Oberflächenstress

Mit

```text
S_ab = -2/sqrt(|h|) delta S_Sigma / delta h^{ab}
```

folgt

```text
S_ab = -lambda h_ab
       + Z_sigma [D_a sigma D_b sigma - 1/2 h_ab X_sigma].
```

Für die 4D-isotropen Komponenten und die Kreisrichtung:

```text
S_mu^nu = (-lambda - Y_sigma/2) delta_mu^nu,
S_chi^chi = -lambda + Y_sigma/2.
```

Eine reine Spannung ist der Spezialfall `Y_sigma=0`.

## 5. Orientierter Israel-Vertrag

Die Normalen sind auf **jeder Seite nach außen aus ihrer jeweiligen Region** gerichtet. Die kanonische Junction-Gleichung lautet

```text
sum_s [K_ab^(s) - K_s h_ab] = kappa6^2 S_ab.
```

Für den MD-2S-Ansatz

```text
ds6^2 = exp(2A_s(r_s)) gbar_munu dx^mu dx^nu
        + dr_s^2 + L_s(r_s)^2 dchi^2
```

werden die orientierten Größen definiert als

```text
A_Sigma = sum_s n_s^r A_s'(rho_s),
L_Sigma = sum_s n_s^r L_s'(rho_s)/L_s(rho_s).
```

Die induzierte Geometrie muss vor Anwendung der Junctiongleichung stetig sein:

```text
A_+|Sigma = A_-|Sigma,
L_+|Sigma = L_-|Sigma > 0,
phi_+|Sigma = phi_-|Sigma,
A_chi,+|Sigma = A_chi,-|Sigma modulo gauge.
```

## 6. Metrische Junctiongleichungen

Die beiden unabhängigen Komponenten lauten

```text
-(3 A_Sigma + L_Sigma)
  = kappa6^2 (-lambda - Y_sigma/2),

-4 A_Sigma
  = kappa6^2 (-lambda + Y_sigma/2).
```

Äquivalent:

```text
lambda_from_4d
  = (3 A_Sigma + L_Sigma)/kappa6^2 - Y_sigma/2,

lambda_from_chi
  = 4 A_Sigma/kappa6^2 + Y_sigma/2.
```

Die gemeinsame Lösung ist

```text
Y_sigma,required = (L_Sigma - A_Sigma)/kappa6^2,

lambda_required = (7 A_Sigma + L_Sigma)/(2 kappa6^2).
```

Damit gilt für eine positive Wicklungsenergie `Z_sigma>=0`, `X_sigma>=0` die notwendige Bedingung

```text
L_Sigma - A_Sigma >= 0.
```

Der reine-Spannungs-Test lautet

```text
Y_sigma = 0  <=>  A_Sigma = L_Sigma.
```

Ein einzelner effektiver Spannungswert kann die beiden metrischen Junctiongleichungen nur dann gleichzeitig erfüllen, wenn diese Umbilizitätsbedingung erfüllt ist oder ein anisotroper Kappensektor vorhanden ist.

## 7. Skalares Matching

Die Variation des Bulk-Skalarterms und der Kappenwirkung ergibt

```text
sum_s Z_phi,s n_s^r phi_s'
+ lambda_,phi
+ 1/2 Z_sigma,phi X_sigma
= 0.
```

Das zu exportierende Residuum ist

```text
R_scalar = sum_s Z_phi,s n_s^r phi_s'
           + lambda_,phi
           + 1/2 Z_sigma,phi X_sigma.
```

Die häufig verwendete Form ohne `Z_phi` ist nur für `Z_phi=1` zulässig.

## 8. Gauge- und Fluxmatching

Die Variation nach `A_a` liefert

```text
sum_s n_A^(s) Z_F,s F_s^{A b}
= q_sigma Z_sigma D^b sigma.
```

Für `b=chi`:

```text
sum_s n_s^r Z_F,s F_s^{r chi}
- q_sigma Z_sigma (n - q_sigma A_chi)/L^2
= 0.
```

Mit dem regionalen Maxwell-Erstintegral

```text
Q_s = exp(4A_s) Z_F,s F_rchi,s/L_s
```

folgt bei stetigem `A` und `L`

```text
R_gauge = exp(-4A)/L * sum_s n_s^r Q_s
          - q_sigma Z_sigma (n - q_sigma A_chi)/L^2.
```

Diese lokale Gleichung ersetzt keine globale Fluxquantisierung. Zusätzlich bleibt erforderlich:

```text
integral_internal F = quantized flux,
```

mit einer noch zu fixierenden Ladungs-, Winkel- und Patchkonvention.

## 9. Phasengleichung

Die Kappenphase erfüllt

```text
D_a [Z_sigma D^a sigma] = 0.
```

Für den homogenen statischen Wicklungsansatz kann diese Gleichung automatisch erfüllt sein, sofern `Z_sigma`, `L`, `A_chi` und die induzierte Geometrie entlang `chi` konstant sind. Sie muss dennoch als eigener Gleichungskanal im vollständigen Vertrag geführt werden.

## 10. Junction-Residualvektor

Ein vollständiger zweiseitiger Export muss mindestens liefern:

```text
R_continuity = (Delta A, Delta L, Delta phi, Delta A_chi modulo gauge),
R_metric = (R_4d, R_chi),
R_scalar,
R_gauge,
R_phase,
R_flux_global,
R_rr_constraint,left,
R_rr_constraint,right.
```

mit

```text
R_4d = -(3 A_Sigma + L_Sigma)
       + kappa6^2 (lambda + Y_sigma/2),

R_chi = -4 A_Sigma
        + kappa6^2 (lambda - Y_sigma/2).
```

Jedes Residuum benötigt Rohwert, dimensionslose Normierung, Toleranz und PASS/FAIL.

## 11. Orientierungs-Firewall

Verboten sind:

1. ein unmarkierter Wechsel zwischen Sprungnotation und outward-sum-Notation,
2. die Verwendung derselben Normalenrichtung auf beiden Seiten ohne explizite Koordinatenabbildung,
3. zentrale Differenzen über die Kappe,
4. das Ersetzen der zwei metrischen Gleichungen durch einen einzelnen Spannungsfit,
5. das Ableiten eines globalen Fluxurteils allein aus dem lokalen Gauge-Matching.

Bei gemeinsamen globalen Koordinaten mit einer links/rechts-Junction kann die outward-sum-Form in eine Sprungform überführt werden. Diese Übersetzung muss jedoch separat mit den jeweiligen Normalenvorzeichen dokumentiert werden.

## 12. Dimensionshygiene

```text
[A_Sigma] = [L_Sigma] = M,
[1/kappa6^2] = M^4,
[lambda] = [Y_sigma] = M^5,
[R_metric before normalization] = M,
[R_scalar] = M^4,
[n_A Z_F F^{A chi}] = M^4 bei dimensionslosem chi.
```

Die dimensionslosen Residuen dürfen erst nach Fixierung einer Referenzskala definiert werden.

## 13. Freeze-Wirkung

Dieser Block verbessert den Status auf

```text
MF-001 bulk action structure = PARTIAL_STRUCTURAL_FREEZE,
MF-002 localized action structure = PARTIAL_STRUCTURAL_FREEZE,
MF-005 oriented junction system = PARTIAL_CONDITIONAL.
```

Weiter offen bleiben:

- konkrete Form und Normalisierung von `U`, `Z_phi`, `Z_F`,
- konkrete Form und Normalisierung von `lambda`, `Z_sigma`,
- Wert und Vorzeichenkonvention von `q_sigma`,
- Wicklungszahl und Gaugepatch-Konvention,
- Winkelperiode und globale Fluxquantisierung,
- zweite Region beziehungsweise Kappengeometrie,
- historische Modellidentität,
- dimensionslose Solvervariablen und Toleranzen.

Daher gilt weiterhin:

```text
R1.0 = ACTIVE,
R1.1 = BLOCKED,
OFFICIAL_SOLVER_IMPLEMENTATION = FORBIDDEN,
TWO_JUNCTION_VERDICT = NOT_EXECUTABLE,
K1-D = NOT_RELEASED,
K1-E = NOT_ADMISSIBLE.
```
