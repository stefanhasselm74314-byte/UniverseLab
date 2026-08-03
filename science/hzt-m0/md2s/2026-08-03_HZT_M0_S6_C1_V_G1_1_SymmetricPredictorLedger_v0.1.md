# HZT-M0-S6-C1-V — G1.1 Symmetric Predictor Ledger v0.1

**Datum:** 2026-08-03  
**Track:** `HZT-M0-S6-C1-V`  
**Modellklasse:** `MANUFACTURED_VERIFICATION_MODEL`  
**Block:** `G1.1`  
**Run-ID:** `C1V-G1.1-20260803-001`  
**Primärer Status:** `NUMERICALLY_CONFIRMED`  
**Qualifier:** `DIAGNOSTIC`  
**Phasenergebnis:** `PASS_DIAGNOSTIC`  
**Evidenzwirkung:** `DISCRETE_PREDICTOR_QA_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Fragestellung

Geprüft wurde ausschließlich, ob der unkorrigierte lokale Predictor

\[
X_{\mathrm{pred}}(\delta)=X_0+\delta X'(0)
\]

für den dimensionslosen Parameter

\[
p=\widehat{\lambda}_0
\]

im deklarierten diskreten C1-V-Residualmap ein sichtbares quadratisches Zwischenregime besitzt:

\[
\|R(X_{\mathrm{pred}}(\delta),p_0+\delta)\|_\infty=O(\delta^2).
\]

Es wurde kein nichtlinearer Korrektor verwendet.

## 2. Präregistrierung

Vor jeder Predictor-Auswertung wurden fixiert:

```text
signed steps:
±0.08, ±0.04, ±0.02, ±0.01, ±0.005, ±0.0025, ±0.00125

large-step probe:
0.08

quadratic fit window:
0.04, 0.02, 0.01, 0.005

small-step floor probe:
0.0025, 0.00125
```

Das Fitfenster wurde nach Sichtung der Resultate nicht verändert.

Präregistrierungshash:

```text
f70bb585a0bd91b196deaaafae64976dffdd0c930b3258184a99eef2fd4e45d2
```

## 3. Backends und Auflösungen

### Referenzbackend

```text
Methode: fixed-step RK4
Tangent: forward-mode AD
Schritte je Region: 400, 800
```

### Unabhängiger numerischer Backend

```text
Methode: implicit midpoint
Ordnungserhöhung: Richardson endpoint extrapolation
Tangent: symmetric finite differences
Basis-Schritte je Region: 50, 100
```

Die Backendübereinstimmung ist nur ein numerischer Crosscheck und keine unabhängige physikalische Bestätigung.

## 4. Tangenten-Crosscheck

Referenztangent:

```text
[0,
 0.4250000000000119,
 0,
 0,
 -0.4250000000000119,
 -0.4572501756126084,
 -0.45725017561283865,
 0.0479166666666657]
```

Unabhängiger Tangent:

```text
[0,
 0.42500000006888516,
 0,
 0,
 -0.42500000006888516,
 -0.4572501759648402,
 -0.4572501763291433,
 0.04791666664995769]
```

Ergebnis:

```text
relative tangent difference    = 9.097179491887701e-10
linear closure infinity norm   = 1.1102230246251565e-16
```

Beide präregistrierten Grenzwerte wurden bestanden.

## 5. Numerischer Floor

Gemessene Anker-Floors:

| Backend | Auflösung | Floor |
|---|---:|---:|
| RK4/AD | 400 | `6.22606480260101e-12` |
| RK4/AD | 800 | `3.8990772416312213e-13` |
| Midpoint/Richardson | 50 | `9.560929730164828e-09` |
| Midpoint/Richardson | 100 | `5.976472921013429e-10` |

Der kleinste Abstand eines **Fitpunkts** zum jeweiligen Floor betrug:

```text
748.1326597445042
```

Damit lagen alle vier vorab fixierten Fitmagnituden deutlich über dem verlangten Faktor 100.

Der kleinste Small-Step-Probe-Abstand betrug beim gröberen unabhängigen Backend:

```text
47.22430577411399
```

Damit zeigt der Lauf zugleich den erwarteten Beginn des numerischen Floor-Übergangs: `|delta|=0.00125` ist beim unabhängigen 50-Schritt-Backend nicht mehr fit-eligible. Dieser Punkt lag außerhalb des präregistrierten Fitfensters und wurde nicht nachträglich in die Ordnungsbestimmung aufgenommen.

## 6. Quadratische Fits

| Backend | Auflösung | Vorzeichen | Log-Log-Slope | Halbierratios | Ergebnis |
|---|---:|---:|---:|---|---|
| RK4/AD | 400 | − | `2.0096468206` | `4.04698148, 4.02324507, 4.01156079` | PASS |
| RK4/AD | 400 | + | `2.0003024170` | `4.00157171, 4.00068212, 4.00031412` | PASS |
| RK4/AD | 800 | − | `2.0096470057` | `4.04698156, 4.02324538, 4.01156202` | PASS |
| RK4/AD | 800 | + | `2.0003026021` | `4.00157179, 4.00068242, 4.00031535` | PASS |
| Midpoint/Richardson | 50 | − | `2.0093437629` | `4.04685413, 4.02273991, 4.00955023` | PASS |
| Midpoint/Richardson | 50 | + | `2.0000000310` | `4.00144696, 4.00018199, 3.99831129` | PASS |
| Midpoint/Richardson | 100 | − | `2.0096281197` | `4.04697373, 4.02321404, 4.01143639` | PASS |
| Midpoint/Richardson | 100 | + | `2.0002836832` | `4.00156392, 4.00065104, 4.00019020` | PASS |

Gesamtbereiche:

```text
slope minimum = 2.0000000309710653
slope maximum = 2.0096470056832327
ratio minimum = 3.9983112940859806
ratio maximum = 4.046981559180092
```

Damit liegen sämtliche acht Fits innerhalb der vorab fixierten Korridore

\[
1.8\le s\le2.2
\]

und

\[
3.2\le\frac{\|R(\delta)\|}{\|R(\delta/2)\|}\le4.8.
\]

## 7. Symmetrie-, Auflösungs- und Backendchecks

```text
maximum signed-pair relative asymmetry
= 0.022519410170857505

maximum RK4 400→800 relative difference
= 4.084570885803319e-07

maximum independent 50→100 relative difference
= 0.0006276802969871953

maximum fine-backend relative difference
= 4.175883538687651e-05
```

Alle Werte liegen deutlich innerhalb der präregistrierten Obergrenzen.

## 8. Belastbare Aussage

Für das deklarierte C1-V-Verifikationsmodell, den hergestellten Anker, die fixierte Residualskalierung, die präregistrierten symmetrischen Schritte und die getesteten endlichen Diskretisierungen gilt:

> Der unkorrigierte lokale `lambda0_hat`-Predictor besitzt ein sichtbares quadratisches Zwischenregime der normalisierten Residualnorm.

Primärer Status:

```text
NUMERICALLY_CONFIRMED
Qualifier: DIAGNOSTIC
Evidence effect: DISCRETE_PREDICTOR_QA_ONLY
```

## 9. Was nicht bewiesen wurde

- keine endliche nichtlineare Lösung,
- keine lokale oder globale nichtlineare Branch-Existenz,
- keine Eindeutigkeit,
- kein Turning Point,
- kein Kontinuums-IFT,
- keine Invertierbarkeit des Kontinuumsoperators,
- keine perturbative Stabilität,
- keine Ghostfreiheit,
- kein Self-Tuning,
- keine historische A0-Identität,
- keine physikalische C1-Identität,
- keine physikalische Evidenz.

## 10. Gate-Wirkung

```text
G1.1                     = PASS_DIAGNOSTIC
C1-V3                    = PARTIAL
C1-V4                    = NOT_STARTED
nonlinear solution family = NOT_ESTABLISHED
continuum BVP Jacobian   = NOT_PROVEN
perturbative stability   = OPEN
ghost freedom            = OPEN
R1.1                     = BLOCKED
official MD-2S solver    = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical evidence effect = NONE
```

## 11. Artefakte und Hashes

```text
result contract:
registry/2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorResult_v0.1.json

evaluation table:
science/hzt-m0/md2s/2026-08-03_HZT_M0_S6_C1_V_G1_1_SymmetricPredictorEvaluations_v0.1.csv

workflow run:
30849219480

workflow artifact:
8869907449

workflow artifact ZIP SHA-256:
efa1fab69b56ba7073f1d73a7b56e739aed91965298e8e29962632fea94c24aa

full run JSON SHA-256:
b0c3f72a207a5e2581c334f77c89092cf5e9f1439797e385ab5c4329fe5b8269

evaluator code SHA-256:
39eea878699558c48ff7e7daf5829e50301a253062f54f6ee2584e27fb3a38e1

reference code SHA-256:
bb270082d8e19684eaaefd305c78b0e5184535251bcf604c4ec1e9167c68c947

independent code SHA-256:
685322f556eab3aa0045497605575f912d13a284fe860fd5184cadfd1caa2dbd

parameter SHA-256:
d23a01b6f024858bff071edd6b258df7a5e97441f887514b58369a9293ff73ce

evaluation CSV SHA-256:
50eef27f5a59617a98e890927ef67d72bfab7c055fcd6a6e3402a37fd8c1e917
```

## 12. Standardisierter Blockabschluss

### A. Was wurde gemacht?

Der präregistrierte symmetrische Predictor-only-Test wurde mit zwei numerisch verschiedenen Backends und je zwei Auflösungen ausgeführt.

### B. Was wurde tatsächlich bestätigt?

Ein sichtbares quadratisches Residualregime im fixierten Zwischenfenster wurde für beide Vorzeichen, beide Backends und alle registrierten Auflösungen bestätigt.

### C. Was wurde nicht bewiesen?

Keine nichtlineare Lösung, kein Kontinuumsresultat und keine physikalische Aussage.

### D. Bearbeiteter Track

```text
HZT-M0-S6-C1-V
```

### E. Gate-Wirkung

Nur `G1.1 = PASS_DIAGNOSTIC`; alle physischen und Release-Gates bleiben unverändert.

### F. Neue Artefakte

Präregistrierungsvertrag, Evaluator, Workflow, Resultatvertrag, vollständige Evaluationstabelle und dieses Ledger.

### G. Exakt nächster zulässiger Block

```text
G1.2 — LOCAL_SECOND_ORDER_DISCRETE_RESPONSE_DIAGNOSTIC
```

Dieser Block darf ausschließlich zwei unabhängige lokale zweite Ableitungsmethoden vergleichen. Er darf keine endliche Fortsetzung oder physikalische Branch-Aussage enthalten.
