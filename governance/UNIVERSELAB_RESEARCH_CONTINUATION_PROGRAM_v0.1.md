# UniverseLab Research Continuation Program v0.1

**Datum:** 2026-08-01  
**Owner:** Stefan Hasselmeyer  
**Governance:** MD-0 v3.1.1  
**Architektur:** HPVS → HZT-M0-S6 / HZT-M0-P5 → HZT-Full  
**Status:** ACTIVE / GOVERNANCE AND RECOVERY PHASE  
**Evidenzwirkung:** NONE

## 1. Zweck

Dieses Programm führt die wissenschaftliche Weiterentwicklung der 6D-Hyperzeit-Arbeit und den Ausbau von UniverseLab in einem gemeinsamen, prüfbaren Arbeitsstrom zusammen.

UniverseLab ist dabei nicht selbst die Theorie. Es ist die operative Integrationsschicht für:

1. Theorie und Wirkungsprinzip,
2. mathematische Herleitung,
3. numerische Lösung,
4. Stabilitäts- und Constraintprüfung,
5. 6D→4D-Reduktion,
6. Forward Map,
7. Observablen und Likelihoods,
8. Provenienz, Dokumentation und Veröffentlichung.

## 2. Nicht verhandelbare Evidenzregeln

- Technische Ausführbarkeit ist keine physikalische Identifikation.
- Numerische Stabilität ist keine Ghostfreiheit.
- Ein guter Fit ist keine Theoriebestätigung.
- Parameteranpassung ist keine Herleitung aus dem 6D-Sektor.
- Literaturkompatibilität ist keine Ableitung.
- Gauge-Fixing folgt der Constraintanalyse und ersetzt sie nicht.
- Negative Resultate gelten nur für den präzise getesteten Mechanismus.
- Chattexte sind Provenienz, aber keine primäre Source of Truth für freigegebene Physik.

## 3. Kanonische Forschungsreihenfolge

6D-Parentwirkung
→ regulärer Hintergrund
→ Rand- und Junction-Bedingungen
→ Constraintalgebra
→ physische Freiheitsgrade
→ quadratische Skalar-/Vektor-/Tensorwirkung
→ Ghost-/Gradient-/Tachyonprüfung
→ kontrollierte 6D→4D-EFT
→ Forward Map
→ Observablen
→ Likelihood
→ Modellvergleich.

Eine Umkehrung dieser Kette ist unzulässig.

## 4. Verbindliche Statuslage

| Objekt | Status |
|---|---|
| HPVS | OPEN RESEARCH PROGRAM / methodisch tragfähig |
| HZT-M0-S6 | RETAINED AND INCOMPLETE |
| HZT-M0-P5 | CONDITIONAL CONTROL BRANCH |
| HZT-Full | NOT CONSTRUCTED |
| K1-D | NOT RELEASED |
| K1-E | NOT ADMISSIBLE |
| diagnostische Dry-Runs | EVIDENCE EFFECT: NONE |
| SCI-001 | PARTIAL |
| SCI-002 | PARTIAL |
| MD-2S reproduzierbarer Solver | MISSING / RECOVERY REQUIRED |
| B1.4O Rangaudit | FORMALLY SPECIFIED / NOT EXECUTABLE |

## 5. Arbeitsprogramme

### WP-1 — Chat-, Dokument- und Artefaktkanonisierung

Ziel: Jede relevante Behauptung, Entscheidung, Rechnung, Datei und Softwareversion erhält eine eindeutige ID, einen Status und eine Provenienzkette.

Akzeptanzkriterien:

- Chat-/Exportquellen sind inventarisiert.
- Dubletten und Nachfolger sind als SUPERSEDED markiert.
- Primärquelle, Sekundärquelle und reine Provenienz sind getrennt.
- Keine kanonische Behauptung besitzt ausschließlich einen Chat als Primärquelle.

### WP-2 — MD-2S Artifact Recovery

Ziel: Wiederherstellung oder reproduzierbarer Neuaufbau des MD-2S-Hintergrundsolvers.

Akzeptanzkriterien:

- Parentwirkung, Konventionen und Feldgleichungen versioniert.
- vollständiger Parametersatz und Randbedingungen dokumentiert.
- Solver, Toleranzen, Softwareversion und Seeds erfasst.
- publizierte A0-Benchmarks innerhalb deklarierter Toleranzen reproduziert.
- einseitige Randdaten und orientierte Normalen exportiert.
- Residuen- und Hash-Manifeste erzeugt.

### WP-3 — B1.4O Rang- und Identifizierbarkeitsaudit

Ziel: Bestimmung von Rang, Nullrichtungen und Kondition der Response-Matrix.

J_ai = ∂y_a/∂c_i

mit Kontrollvektor c und Ziel-/Residualvektor y.

Akzeptanzkriterien:

- numerischer Rang mit dokumentierter Schwelle,
- vollständiges Singulärwertspektrum,
- Konditionszahl,
- Nullraum und Parameterkorrelationen,
- Robustheit gegen Diskretisierung, Regulator und Normierung,
- physische Zulässigkeitsprüfung.

### WP-4 — UniverseLab Registry und P0-Verifier

Ziel: Status, Claims, Dokumente, Runs, Daten und Releases werden maschinenlesbar und automatisch geprüft.

### WP-5 — Quadratischer Störungs- und Ghostaudit

Startbedingung: WP-2 und Hintergrund-/Junction-Gate bestanden.

### WP-6 — Kontrollierte Forward Engine

Startbedingung: physische Freiheitsgrade und stabile EFT bestimmt.

### WP-7 — Beobachtungsinferenz

Startbedingung: freigegebene Forward Map. Erst dann DESI, Pantheon+, KiDS/DES, RSD, SPARC und GW-Likelihoods.

## 6. Parallelstrategie Forschung ↔ Software

Jeder wissenschaftliche Arbeitsschritt erzeugt zugleich ein UniverseLab-Objekt:

- Spezifikation → Registry-Eintrag,
- Gleichungssystem → versioniertes Modellprofil,
- Solverlauf → RUN_ID und Manifest,
- Resultat → Residual-/Benchmarkdatei,
- Gate-Entscheidung → Claim-/Evidence-Update,
- Visualisierung → abgeleitete Ansicht ohne eigene Statushoheit.

## 7. Aktueller kritischer Pfad

R0: vorhandene Archive nach Solver-, CSV-, JSON-, Residuen- und Manifestdateien durchsuchen.

R1: falls R0 scheitert, MD-2S-BVP neu aufbauen und A0-Benchmarks reproduzieren.

R2: einseitige Randwerte und Normalen exportieren.

R3: SCI-001/SCI-002-v0.2-Gates vollständig ausführen.

R4: B1.4O-Rang- und Konditionsaudit durchführen.

## 8. Blockierte Abkürzungen

Bis zur Erfüllung des kritischen Pfads werden nicht als Evidenz gewertet:

- neue kosmologische Proxy-Fits,
- MOND-/RAR-Anpassungen ohne 6D-Mapping,
- reine Visualisierungen,
- aus globalen Benchmarks geschätzte Junction-Daten,
- Stabilitätsclaims ohne quadratische Wirkung,
- HZT-Full-Claims ohne konsistente Mehrzeit-Constraintstruktur.

## 9. Unmittelbare nächste Entscheidung

Der nächste wissenschaftliche Output ist kein neuer Phänomenkatalog, sondern ein reproduzierbares MD-2S-Recovery-Paket. UniverseLab wird parallel so erweitert, dass dieses Paket als erstes vollständig registriertes End-to-End-Forschungsobjekt dient.
