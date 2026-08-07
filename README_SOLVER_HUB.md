# UniverseLab Solver Hub (ULSH) v1.0

## Zweck

Der UniverseLab Solver Hub ist die gemeinsame numerische Infrastruktur für Hyperzeit/HPVS. Er ersetzt keine physikalische Herleitung. Jeder Solver muss seine Annahmen, Konventionen, Residuen, Toleranzen und Provenienz explizit exportieren.

## Governance

- K1-D = NOT RELEASED
- K1-E = NOT ADMISSIBLE
- physical evidence effect = NONE
- numerische Stabilität != Ghostfreiheit
- technische Ausführbarkeit != physikalische Identifikation
- guter Fit != Theoriebestätigung
- Branch-Transfer nur nach vollständiger Neuberechnung
- Planungsstatus != Solverfreigabe
- Downstream-Ausführung nur nach Upstream-Gate

## Solver Development Program v1.0

Seit 2026-08-07 besitzt jeder der 14 kanonischen Solver eine eigene versionierte Roadmap.

Dashboard:

`2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html`

Maschinenlesbare Registry:

`registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json`

Jede Roadmap enthält denselben Entwicklungsvertrag:

1. wissenschaftliches Ziel
2. aktueller Baseline-Status
3. Upstream-Abhängigkeiten
4. fehlende Theorie-/Vertragsarbeit
5. Implementierungspakete
6. Kontroll- und Manufactured Tests
7. Pflicht-Outputs
8. Freigabegate
9. Downstream-Abhängigkeiten

Die Readiness-Matrix verwendet bewusst keine pseudo-genauen Prozentwerte. Die Zustände `DEFINED`, `PARTIAL`, `MISSING`, `BLOCKED` und `NOT_APPLICABLE` beschreiben Planungs- und Implementierungsreife, nicht wissenschaftliche Evidenz.

## Kanonischer erster Solver

`HZT-M0-S6_MD-2S_Background_BVP_Solver_v1.0`

Ziel: Rekonstruktion beziehungsweise Wiedergewinnung des MD-2S-Hintergrund-Randwertproblems für

- A(r)
- L(r)
- phi(r)
- A_chi(r)

und Export der einseitigen Kappendaten für SCI-001/SCI-002 v0.2.

## Solver-Vertrag

Jeder Solver erhält mindestens:

1. Parametervektor
2. Konventions-ID
3. Einheiten/Normierung
4. numerische Toleranzen
5. Provenienz

und erzeugt mindestens:

1. Lösung
2. Residuen
3. Randexport oder sektorspezifischen Pflicht-Output
4. Solverdiagnostik
5. Provenienz/Hashes
6. expliziten Status

## MD-2S Pflicht-Outputs

An r = r_sigma müssen mindestens ausgegeben werden:

- A'_bulk, A'_cap
- L_bulk, L_cap
- L'_bulk, L'_cap
- phi'_bulk, phi'_cap
- A_chi_bulk, A_chi_cap
- Q_bulk, Q_cap
- Z_F_bulk, Z_F_cap
- orientierte Normalen n^r_bulk, n^r_cap

Daraus folgen

A_Sigma = sum_s n_s^r A'_s

L_Sigma = sum_s n_s^r L'_s/L_s

Y_sigma_required = M6^4 (L_Sigma - A_Sigma)

und das Pure-Tension-Gate A_Sigma = L_Sigma.

## Kanonische Module und Roadmap-IDs

- ULSH-01 · MD2S-BVP
- ULSH-02 · MD2S-JUNCTION
- ULSH-03 · MD2S-RANK / B1.4O
- ULSH-04 · CONSTRAINT
- ULSH-05 · PERTURBATION
- ULSH-06 · GHOST
- ULSH-07 · KK
- ULSH-08 · RADION
- ULSH-09 · FLUX
- ULSH-10 · COSMO
- ULSH-11 · LIKELIHOOD
- ULSH-12 · BARYO
- ULSH-13 · GW
- ULSH-14 · MOND/RAR

Nur die ersten drei Blöcke besitzen derzeit konkrete Solver-Vorarbeiten. Einige spätere Blöcke besitzen konzeptionelle oder Datenpipeline-Vorarbeiten, bleiben aber als Solver physisch nicht freigegeben.

## Abhängigkeitsphasen

1. Hintergrund: ULSH-01
2. Rand und Rang: ULSH-02/03
3. Dynamik und Stabilität: ULSH-04 bis ULSH-09
4. Phänomenologie: ULSH-10, ULSH-12, ULSH-13, ULSH-14
5. Daten: ULSH-11 erst nach freigegebenem K1-D

## Nächster Freigabeschritt

Der nächste harte Gate bleibt die reproduzierbare MD-2S-Hintergrundlösung mit vollständigem einseitigem Randexport. Erst danach sind das Zwei-Junction-Urteil und der B1.4O-Rankaudit physisch numerisch ausführbar.

Das Solver Development Program ändert diesen Status nicht; es verhindert lediglich, dass Downstream-Solver ohne ihre notwendigen Upstream-Grundlagen begonnen oder überinterpretiert werden.
