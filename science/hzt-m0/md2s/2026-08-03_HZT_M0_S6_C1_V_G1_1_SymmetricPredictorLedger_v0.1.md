# HZT-M0-S6-C1-V — G1.1 Symmetric Predictor Ledger v0.1

**Datum:** 2026-08-03  
**Track:** `HZT-M0-S6-C1-V`  
**Modellklasse:** `MANUFACTURED_VERIFICATION_MODEL`  
**Block:** `G1.1`  
**Run-ID:** `C1V-G1.1-20260803-001`  
**Status vor Ausführung:** `PREREGISTERED_NOT_EXECUTED`  
**Evidenzwirkung:** `DISCRETE_PREDICTOR_QA_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Fragestellung

Geprüft wird ausschließlich, ob der unkorrigierte lokale Predictor

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

Es wird kein nichtlinearer Korrektor verwendet.

## 2. Vorab fixierte symmetrische Schritte

Für jede Magnitude werden beide Vorzeichen ausgewertet:

```text
±0.08
±0.04
±0.02
±0.01
±0.005
±0.0025
±0.00125
```

Die Fenster werden vor Ausführung festgelegt:

```text
large-step probe:       0.08
quadratic fit window:   0.04, 0.02, 0.01, 0.005
small-step floor probe: 0.0025, 0.00125
```

Das Fitfenster darf nach Sichtung der Resultate nicht ausgetauscht werden.

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

## 4. Residualnorm und numerischer Floor

Primäre Norm:

\[
\|R\|_\infty
=
\max_i |R_i^{\rm normalized}|.
\]

Sekundär wird die euklidische Norm berichtet.

Für jeden Backend und jede Auflösung wird der Floor definiert als

\[
\epsilon_{\rm floor}
=
\max\!\left(\|R(X_0,p_0)\|_\infty,10^{-13}\right).
\]

Ein Fitpunkt ist nur zulässig, wenn

\[
\|R(\delta)\|_\infty
\ge 100\,\epsilon_{\rm floor}.
\]

## 5. Vorab fixierter Akzeptanzkorridor

Der Test gilt nur als bestanden, wenn sämtliche Bedingungen erfüllt sind:

```text
log-log slope                         ∈ [1.8, 2.2]
R(delta)/R(delta/2)                   ∈ [3.2, 4.8]
max. +delta/-delta norm asymmetry     ≤ 0.20
max. same-backend resolution drift   ≤ 0.10
max. fine-backend norm difference    ≤ 0.10
tangent relative difference          ≤ 1e-7
linear closure infinity norm         ≤ 1e-10
fit magnitudes above floor            = all four
```

Die vier präregistrierten Fitmagnituden müssen zusammenhängend bestehen.

## 6. Zulässige Aussage bei PASS

```text
The uncorrected local C1-V lambda0_hat predictor exhibits a visible
quadratic normalized-residual regime for the preregistered finite
discretizations and fit window.
```

Status:

```text
NUMERICALLY_CONFIRMED
Qualifier: DIAGNOSTIC
Evidence effect: DISCRETE_PREDICTOR_QA_ONLY
```

Auch bei PASS bleibt:

```text
C1-V3                    = PARTIAL
C1-V4                    = NOT_STARTED
nonlinear solution family = NOT_ESTABLISHED
continuum BVP Jacobian   = NOT_PROVEN
R1.1                     = BLOCKED
official MD-2S solver    = NOT_AUTHORIZED
K1-D                     = NOT_RELEASED
K1-E                     = NOT_ADMISSIBLE
physical evidence effect = NONE
```

## 7. Verbotene Schlussfolgerungen

- keine endliche nichtlineare Lösung,
- keine Branch-Existenz oder Eindeutigkeit,
- kein Turning Point,
- kein Kontinuums-IFT,
- keine Stabilität oder Ghostfreiheit,
- kein Self-Tuning,
- keine historische A0-Identität,
- keine physikalische C1-Identität,
- keine Gate-Freigabe.

## 8. Noch nicht ausgeführt

Zum Zeitpunkt dieser Präregistrierung wurden keine Predictor-Residualwerte berechnet. Ergebnisse, Codehashes, Fitparameter und Gateentscheidung werden erst nach dem unveränderten Lauf ergänzt.
