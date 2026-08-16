# UniverseLab / GSRA-01 — Chat Naming & Status Audit v1.0

**Datum:** 2026-08-16  
**Klasse:** COORDINATION / NAMING / WORKSTREAM GOVERNANCE ONLY  
**Physische Evidenzwirkung:** NONE

## Ziel

Alle wichtigen Arbeitschats erhalten einen eindeutigen Statuspräfix und eine Funktionsbezeichnung. Die ChatGPT-Titel selbst müssen in ChatGPT manuell umbenannt werden; dieses Dokument definiert die kanonischen Soll-Namen und ihre Zuständigkeit.

## Statuspräfixe

- `ACTIVE` — aktiver Arbeitsstrang
- `UTILITY` — Hilfs-/Zentralfunktion, keine Theorieentwicklung
- `AUDIT` — technische Prüfung, Fehleranalyse, QA
- `CLOSED` — abgeschlossen; keine weitere Ausführung aus diesem Strang
- `ARCHIVE` — historische Referenz / ersetzt
- `BLOCKED` — fachlich aktiv, aber durch ein definiertes Gate gesperrt

## Soll-Namen

| Bisheriger Titel | Neuer Soll-Titel | Status / Funktion |
|---|---|---|
| Forschungsplattform Architektur | `ACTIVE — UniverseLab Forschungsplattform` | Plattform, SiteState, Governance, Navigation |
| Analyse der 17 Dateien | `ACTIVE — ULSH-01 C-PHYS Solverentwicklung` | Primärer wissenschaftlicher Solverpfad |
| Aktive wichtige Links | `UTILITY — UniverseLab Wichtige Links` | Link-Zentrale / Workstream-Zuordnung |
| CP01R2 D8 Laufwache | `CLOSED — CP01R2-D8 Laufwache` | Einmaliger historischer Run-Watch, nicht replaybar |
| HZT-M0-S6-C1 Theorie | `ARCHIVE — HZT-M0-S6-C1 Theorie — Vorgänger` | Vorgängerchat; Referenz nach Längenlimit |
| HZT-M0-S6-C1 Restart | `ACTIVE — HZT-M0-S6-C1 Continuation — Solverplanung` | Kanonische Fortsetzung ohne C2-Sprung |
| ULSH Master Build Order | `ACTIVE — ULSH Master Build Order — 14 Solver` | Gesamtplanung der 14 Solver |
| Technischer Neben-/Analysechat: UniverseLab Fehleranalyse | `AUDIT — UniverseLab Fehleranalyse` | Repo-/CI-/Integrations-Audits |
| Hyperzeit Projektstatus Update | `ARCHIVE — Hyperzeit Projektstatus Update — Übergabestand` | Historischer Status-/Strategiestand |
| Bauplan Hyperzeit Raumschiff | `ACTIVE — Generationsschiff Sagittarius A* — Systemarchitektur` | Eigenständiges GSRA-01-Systemengineering |

## GSRA-01 Trennvertrag

Der Generationsschiff-Chat ist ein **eigenständiger Projektstrang**. Er gehört organisatorisch in dieselbe persönliche Projektübersicht, aber technisch nicht in das UniverseLab-Repository.

Kanonische Ziele:

- `GSRA-01-Generation-Ship` — technisches Hauptrepository
- `GSRA-01-Control-Center` — öffentliche Projektzentrale

UniverseLab darf später nur über definierte Schnittstellen Daten, Referenzen oder Visualisierungen konsumieren. Nicht bestätigte Hyperzeit-/HZT-Mechanismen dürfen als Forschungsoptionen untersucht werden, aber nicht als etablierte Antriebs- oder Engineering-Technologie behandelt werden.

## Governance-Regel

Ein Chatstatus (`ACTIVE`, `CLOSED`, `ARCHIVE` usw.) ist **nur Koordinationsmetadatum**. Er verändert keine wissenschaftlichen Gates, keine Solverfreigabe und keine Evidenzklassifikation.
