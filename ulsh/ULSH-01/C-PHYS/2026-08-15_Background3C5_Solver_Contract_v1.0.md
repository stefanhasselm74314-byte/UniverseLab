# ULSH-01 / Background-3C5 Solver Contract v1.0

Status: `L1_IMPLEMENTATION_ONLY / SOFTWARE_QA_NO_PHYSICS`

## Zweck

Dieser Vertrag trennt den Response-Orchestrator strikt vom noch separat zu ratifizierenden physikalischen 6D-BVP-Kern. Technische Ausführbarkeit erzeugt keine physikalische Evidenz.

## Solver-Aufruf

Der Orchestrator ersetzt in `solver_command` die Platzhalter `{input}` und `{output}`. Der Solver muss die JSON-Eingabedatei lesen und genau eine JSON-Ausgabedatei schreiben.

### Input-Schema

`ulsh01.background3c5.solver-input.v1`

Pflichtinhalt: fixer diskreter Branch `(winding_n, flux_N)`, fünf kontinuierliche Kontrollen, Felder `A,L,phi,s,A_chi`, Center-/Outer-Boundary-Contract und Solver-Toleranzklasse.

### Output-Schema

`ulsh01.background3c5.solver-output.v1`

Pflichtfelder:

- `job_id`, `input_sha256`, `branch`
- vier Outputs `delta_beta_over_beta`, `delta_Xi`, `delta_U_umb`, `delta_m0sq_Rcap2`
- boolesche Gates: Konvergenz, glattes Zentrum, simultanes Metric/Scalar/Gauge-Matching, gleiche Profil-Knotenklasse, Continuation-Trace, kein konischer Rescue-Mode, positive reduzierte kinetische Matrix, gültige Off-Shell-Tube
- Diagnostik: endliches `m0_squared`, endliche `residual_norm`
- `synthetic=true|false`

Branchdrift oder fehlende/nonfinite Werte führen fail-closed zum Abbruch.

## Response-Läufe

Für jede der fünf Kontrollen werden `+/-`-Läufe bei `h`, `h/2`, `h/4` erzeugt: insgesamt 30 Perturbationen plus Baseline. Zusätzlich werden die zehn `h/4`-Perturbationen mit strengerer Solver-Toleranz wiederholt, damit die Solver-Komponente der Jacobian-Unsicherheit separat bestimmt werden kann.

Die Schrittamplitude ist

`Delta_i = h * perturbation_scale_i`.

Die Skalen müssen vor einem autorisierten Lauf physikalisch begründet und eingefroren werden.

## Evidenz-Firewall

`SYNTHETIC_SMOKE_ONLY` und `SOFTWARE_QA_ONLY` setzen immer `rank_claim_allowed=false` und `evidence_effect=NONE_SYNTHETIC_OR_QA`.

Nur `AUTHORIZED_PHYSICAL_RUN` mit `synthetic=false` und bestandenen Job-Gates darf Rohmatrizen erzeugen, die anschließend vom unabhängigen Response-Rank-Auditor geprüft werden. Auch dann gilt weiterhin: kein automatisches K1-D/K1-E-Promoting.

## Noch offener physikalischer Kern

Der vorhandene Theorie-Stand spezifiziert den Finite-Thickness-Layer und Teile seiner Feldgleichungen, aber der Repository-Stand enthält noch keinen ratifizierten vollständigen nonlinear Background-3C5-Kernel mit allen gekoppelten Einstein-, Stabilisator-, Maxwell- und Layer-Gleichungen samt normalisierten Randbedingungen. Dieser Vertrag erfindet diese fehlenden Terme ausdrücklich nicht.
