# UniverseLab Research Continuation Program v0.2

**Datum:** 2026-08-03  
**Owner:** Stefan Hasselmeyer  
**Governance:** MD-0 v3.1.1 nach Projektdeklaration  
**Architektur:** HPVS → HZT-M0 → HZT-Full  
**Kontrollierte Zweige:** HZT-M0-S6, HZT-M0-P5  
**Status:** ACTIVE / G0 SYNCHRONIZED  
**Physikalische Evidenzwirkung:** NONE  
**Ersetzt:** `governance/UNIVERSELAB_RESEARCH_CONTINUATION_PROGRAM_v0.1.md`

## 1. Zweck

UniverseLab ist die operative Integrations-, Prüf- und Dokumentationsschicht des Hyperzeit-Forschungsprogramms. UniverseLab ist nicht selbst die physikalische Theorie und besitzt keine eigene Evidenzhoheit.

Der Forschungsstrom wird ab dieser Version in drei wissenschaftlich getrennte Tracks zerlegt:

1. historische Rekonstruktion,
2. kanonischer physikalischer Neuaufbau,
3. hergestellte numerische Verifikation.

Kein Ergebnis darf zwischen diesen Tracks wandern, solange keine explizite, versionierte Modellidentitäts- oder Verification-to-Physics-Brücke vorliegt.

## 2. Nicht verhandelbare Evidenzregeln

- Technische Ausführbarkeit ist keine physikalische Identifikation.
- Numerische Stabilität ist keine Ghostfreiheit.
- Ein guter Fit ist keine Theoriebestätigung.
- Parameteranpassung ist keine Herleitung aus dem 6D-Sektor.
- Diskreter Jacobianrang ist keine Invertierbarkeit des Kontinuumsoperators.
- Ein lokaler Tangent ist keine endliche nichtlineare Lösungsfamilie.
- Hintergrundregularität ist keine perturbative Stabilität.
- Die Übereinstimmung zweier Backends ist keine unabhängige physikalische Bestätigung.
- Visualisierung besitzt keine Status- oder Modellautorität.
- Chattexte sind Provenienz, aber keine alleinige Freigabequelle.

## 3. Drei verbindliche Tracks

### 3.1 MD2S-R1-L — Historical legacy reproduction

**Status:** `BLOCKED_BY_MISSING_PRIMARY_SOURCES`

Ziel ist die möglichst originalgetreue Rekonstruktion des historischen A0- und B1.4N/B1.4O-Modells. Zulässig sind nur historisch belegte Quellen mit nachvollziehbarer Provenienz.

Historische Benchmarkwerte werden bis zur identischen Rekonstruktion ausschließlich bezeichnet als:

```text
REPORTED_NOT_INDEPENDENTLY_REPRODUCED
```

Fehlende historische Gleichungen, Normalisierungen oder Solverparameter dürfen nicht durch Annahmen des heutigen Modells oder durch C1-V ersetzt werden.

### 3.2 MD2S-R1-C-PHYS — Current canonical physical rebuild

**Status:** `MODEL_FREEZE_INCOMPLETE`

Dieser Track ist der zukünftige physikalische Hauptpfad. Er beginnt bei der aktuellen SCI-001/SCI-002-Parentwirkung und folgt zwingend:

```text
Parentwirkung
→ Variation
→ Randterme
→ Hintergrundgleichungen
→ Randwertproblem
→ Hintergrundfamilie
→ Perturbationen
→ 4D-Reduktion
→ Observablen
```

Historische Benchmarks dürfen erst nach nachgewiesener Gleichungs-, Konventions- und Normalisierungsidentität als Reproduktionsziele dieses Tracks verwendet werden.

### 3.3 HZT-M0-S6-C1-V — Manufactured verification sandbox

**Klassifikation:** `MANUFACTURED_VERIFICATION_MODEL`

C1-V prüft Gleichungsimplementierung, Dimensionsskalierung, Polserien, Patchkonventionen, Residuen, Integratoren, Sensitivitäten, diskrete Jacobians, Nullmoden und lokale numerische Antworten.

Der exakte Hintergrund

```text
A = 0
ell(x) = sin(x)
varphi = 0
```

wird als `EXACT_MANUFACTURED_VERIFICATION_BACKGROUND` geführt.

Mit `k4 = 1/4` liegt er nicht in einem parametrisch schwach gekrümmten Regime. Eine realistische GR-artige IR-Interpretation ist unzulässig.

Leitsatz:

> **C1 prüft zunächst unsere Werkzeuge, nicht die Natur.**

## 4. Getrennte Phasen

### 4.1 Historischer und physikalischer R1-Pfad

| Phase | Inhalt | Status |
|---|---|---|
| R1.0 | Quellenrekonstruktion und Modell-Freeze | ACTIVE |
| R1.1 | symbolische physikalische Herleitung und Dependency Audit | BLOCKED |
| R1.2 | unabhängige physikalische BVP-Solver | BLOCKED |
| R1.3 | Benchmarkreproduktion nach Identitätsprüfung | BLOCKED |

### 4.2 C1-Verifikationspfad

| Phase | Inhalt | Status |
|---|---|---|
| C1-V0 | hergestellter analytischer Anker | PASS |
| C1-V1 | diskrete Residual- und Jacobian-Verifikation | PASS_DIAGNOSTIC |
| C1-V2 | unabhängige Backend-Verifikation | PASS_DIAGNOSTIC |
| C1-V3 | lokaler Predictor und Sensitivitätsprüfung | PARTIAL |
| C1-V4 | Kontinuumsoperator-Vergleich | NOT_STARTED |

C1-V-Phasen sind nicht Teil der Freigabekette R1.1–R1.3.

## 5. Numerischer Mindestvertrag

Jeder numerische Block dokumentiert vor Ausführung:

1. Modell- und Track-ID,
2. Gleichungen und unabhängige Variable,
3. Anfangs- und Randbedingungen,
4. Normierung und Einheiten,
5. Integrator und Schrittweitenregel,
6. Toleranzen und Rundungsgrenzen,
7. Referenz- oder Grenzlösung,
8. Residualnorm,
9. Code-, Parameter- und Quellenhashes,
10. Gültigkeitsbereich und verbotene Schlussfolgerungen.

Eine numerische Ausgabe ohne diese Metadaten ist kein kanonisches Forschungsergebnis.

## 6. Abhängigkeits- und Darstellungsregel

Die operative Software folgt der Richtung:

```text
Governance und Register
→ Modell- und Numerikmodule
→ Anwendung
→ Visualisierung
```

Visualisierung, DOM oder Canvas dürfen keine Modellparameter, Evidenzstatus oder Gate-Entscheidungen heimlich verändern.

## 7. Freigabekette des physikalischen Hauptpfads

```text
vollständige 6D-Parentwirkung
→ konsistente Variation und Randterme
→ regulärer physikalischer Hintergrund
→ Kontinuums-BVP und Constraintstruktur
→ quadratische Skalar-/Vektor-/Tensorwirkung
→ Ghost-/Gradient-/Tachyonprüfung
→ kontrollierte 6D→4D-Reduktion
→ Forward Map
→ Observablen
→ Likelihood
→ Modellvergleich
```

Eine Umkehrung dieser Kette ist unzulässig.

## 8. Gate-Status

```text
K1-D                         = NOT_RELEASED
K1-E                         = NOT_ADMISSIBLE
R1.1                         = BLOCKED
official MD-2S solver        = NOT_AUTHORIZED
physical evidence effect     = NONE
historical A0 identity       = NOT_ESTABLISHED
C1 physical identity         = NOT_ESTABLISHED
continuum BVP Jacobian       = NOT_PROVEN
nonlinear solution family    = NOT_ESTABLISHED
perturbative stability       = OPEN
ghost freedom                = OPEN
```

Diese Status dürfen nur durch eine versionierte, begründete Gate-Entscheidung geändert werden.

## 9. Prioritätsordnung

```text
Governance-Konsistenz
≫ Modellidentität
≫ mathematische Wohldefiniertheit
≫ Kontinuumsproblem
≫ Stabilität
≫ 4D-Reduktion
≫ Phänomenologie
≫ Datenfit
```

Ein technisch leichter numerischer Anschluss hat keine Priorität vor einem offenen höheren Gate.

## 10. Standardabschluss jedes Arbeitsblocks

Jeder Block berichtet:

- **A. Was wurde gemacht?**
- **B. Was wurde bewiesen oder bestätigt?**
- **C. Was wurde nicht bewiesen?**
- **D. Welcher Track wurde bearbeitet?**
- **E. Gate-Wirkung**
- **F. Neue Artefakte und Hashes**
- **G. Nächster blockergetriebener Schritt**

Jedes Resultat enthält genau einen primären Status aus dem kanonischen Statusvokabular sowie Evidenzwirkung, Gültigkeitsbereich, Abhängigkeiten, verbotene Schlussfolgerung und Upgrade- oder Falsifikationsbedingung.

## 11. Nächster zulässiger Block nach G0

Nach vollständiger G0-Synchronisation ist genau ein nächster Block empfohlen:

```text
G1.1 — symmetrischer predictor-only Residualordnungstest
Track: HZT-M0-S6-C1-V
```

Dabei bleiben nichtlinearer Korrektor, Branch-Tracking, physikalische C1-Interpretation und Solverfreigabe verboten.
