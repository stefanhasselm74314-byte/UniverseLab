# UniverseLab G0 — Governance-, Track- und Register-Audit v1.0

**Datum:** 2026-08-03  
**Block:** G0  
**Governance:** MD-0 v3.1.1 nach Projektdeklaration  
**Primärer Arbeits-Track:** `MD2S-R1-C-PHYS`  
**Status:** `PROVEN` für die Governance-Synchronisation  
**Evidenzwirkung:** `GOVERNANCE_ONLY`  
**Physikalische Evidenzwirkung:** `NONE`

## 1. Auditgegenstand

Der Audit prüft und synchronisiert:

- Projektarchitektur,
- historische MD-2S-Rekonstruktion,
- aktuellen physikalischen Neuaufbau,
- C1-Verifikationszweig,
- Decision Log,
- Claim Register,
- Research-Continuation-Manifest,
- R1 Model Freeze Gate,
- Session Checkpoint,
- Issue #3,
- offene Alt-Pull-Requests,
- read-only Validatoren.

Es wurden keine neuen Hintergrundlösungen, Predictor-Schritte, zweiten Ableitungen, Root-Solves, Stabilitätsanalysen oder Forward Maps berechnet.

## 2. Verbindliche Zielarchitektur

```text
HPVS
→ HZT-M0
  → HZT-M0-S6
  → HZT-M0-P5
→ HZT-Full
```

Die MD-2S-Arbeit ist ab G0 in drei getrennte Tracks zerlegt:

```text
MD2S-R1-L       historical legacy reproduction
MD2S-R1-C-PHYS  current canonical physical rebuild
HZT-M0-S6-C1-V  manufactured verification sandbox
```

Kein Ergebnis darf ohne explizite, versionierte Modellidentitäts- oder Verification-to-Physics-Brücke zwischen den Tracks migrieren.

## 3. Drift-Matrix

| Artefakt | Deklarierter Ist-Status vor G0 | Tatsächlich implementierter Stand | Konflikt | Erforderliche und ausgeführte Korrektur |
|---|---|---|---|---|
| `project-manifest.json` | HPVS → HZT-M0-S6/HZT-M0-P5 → HZT-Full | Kontrollierte Zweige vorhanden, aber keine übergeordnete HZT-M0-Ebene und keine Tracktrennung | Architektur- und Forschungsphasen vermischt | Programmchain `HPVS → HZT-M0 → HZT-Full`, kontrollierte Zweige und drei Research Tracks ergänzt |
| Dual-Track-Governance | kein kanonisches Artefakt gefunden | Legacy-Rekonstruktion und aktueller Neuaufbau wurden praktisch gemeinsam geführt; C1 kam später hinzu | fehlende formale Identitätsfirewall | Drei-Track-Vertrag v1.0 ratifiziert; `UL-DEC-0014` vorgesehen |
| `registry/decision-log.jsonl` | bis `UL-DEC-0013` | C1 als Kandidat und lokaler numerischer Zweig dokumentiert | keine formale Drei-Track-Entscheidung | append-only `UL-DEC-0014` mit Migrationsfirewall ergänzt |
| `registry/claim-register-v0.1.json` | `MD2S-BG-001 = NUMERICALLY_CONFIRMED` | historische Gleichungen, Originalsolver und vollständiges Runpaket fehlen | Evidenzstatus zu stark | kanonischer Nachtrag setzt Status auf `OPEN`, Label `REPORTED_NOT_INDEPENDENTLY_REPRODUCED` |
| Claim Register, C1 | keine zentralen C1-Claims | exakter hergestellter Anker, zwei diskrete Jacobians und lokaler Tangent liegen vor | numerische QA nicht zentral klassifiziert | vier C1-V-Claims mit Status, Evidenzwirkung, Gültigkeit, Dependencies und Forbidden Inference ergänzt |
| `registry/research-continuation-manifest-v0.1.json` | R1.0–R1.3 als eine Kette | C1-Jacobians liefen parallel, obwohl R1.1/R1.2 blockiert blieben | C1-Verifikation erschien als Teil der physischen R1-Kette | Manifest v0.2 trennt R1.0–R1.3 von C1-V0–C1-V4 |
| `governance/UNIVERSELAB_RESEARCH_CONTINUATION_PROGRAM_v0.1.md` | Recovery/Rebuild als gemeinsamer WP-2-Pfad | neue C1-Verifikation nicht abgebildet | veraltete Programmstruktur | v0.2 mit Drei-Track-Programm, Prioritätsordnung und Standardabschluss erstellt |
| `science/hzt-m0/md2s/R1_MODEL_FREEZE_GATE_v0.1.json` | ein gemeinsamer R1-Rebuild mit A0-Zielen | historische Rekonstruktion, aktueller Neuaufbau und C1-Testmodell sind nicht identisch | Modellidentität und Reproduktionsziel vermischt | Drei-Track-Gate v1.0 ersetzt den alten Gate-Stand kanonisch |
| `registry/2026-08-03_MD2S_C1_ModelContract_v0.1.json` | `CANDIDATE_MODEL_DEFINED_NOT_RELEASED` | Funktionen und Parameter wurden gezielt für einen exakten Testanker definiert | „Candidate“ kann physikalische Identität suggerieren | Nachfolger `HZT-M0-S6-C1-V`, `MANUFACTURED_VERIFICATION_MODEL` |
| C1-Anker | `EXACT_CONTINUUM_BACKGROUND_DERIVED` | exakte Lösung der deklarierten C1-Gleichungen mit `k4=1/4` | physikalischer/IR-Kontext nicht ausreichend abgegrenzt | `EXACT_MANUFACTURED_VERIFICATION_BACKGROUND`; GR-artige Niedrigkrümmungsinterpretation verboten |
| C1-Ladungsidentität | `q_sigma=q_ref=q0` als C1-Postulat | keine Herleitung aus einer Eichgruppe oder Minimalladung | Gefahr der Migration in C-PHYS | als `C1_V_SIMPLIFICATION_NOT_DERIVED` markiert; Transfer verboten |
| C1-Jacobian-Vertrag v0.1 | diskreter Rang 8, Kontinuumsrang offen | numerisch korrekt innerhalb des deklarierten diskreten Maps | keine explizite C1-V-Phasenzuordnung | Nachfolger v0.2: `C1-V1 = PASS_DIAGNOSTIC`, Evidenz `DISCRETE_QA_ONLY` |
| C1-Backend-/Tangent-Vertrag v0.1 | unabhängiger Backend und lokaler Tangent | zwei numerisch verschiedene Implementierungen stimmen lokal überein | „independent“ kann physikalische Bestätigung suggerieren | Nachfolger v0.2: `C1-V2 PASS_DIAGNOSTIC`, `C1-V3 PARTIAL`, nur Backend-QA |
| `session-checkpoint-latest.json` | nächster Schritt: Predictor und zweite Ableitung | Governance-Drift hatte höhere Priorität | technischer Anschluss vor Governance-Korrektur | Checkpoint v1.7 setzt G0-Stand und erlaubt als Nächstes ausschließlich G1.1 |
| Issue #3 | ein gemeinsames WP-2-Recovery/Rebuild-Programm | Kommentare enthalten historische Suche, C-PHYS-Teile und C1-Rechnungen im selben Strom | Aufgabenbesitz unklar | bestehende Aufgaben bleiben; drei Unterprogramme werden sichtbar ergänzt |
| PR #1 | offene Architekturgrundlage | 293 Commits hinter `main`; nützliche Evidenz- und Visualisierungsregeln, aber veraltete L0–L5-Governance | darf nicht still kanonisch bleiben | Entscheidung `SUPERSEDE`; nützliche Regeln in v0.2 migriert; Alt-PR wird geschlossen |
| PR #2 | offene MVP-0.5-Numerikhärtung | 290 Commits hinter `main`, basiert nicht auf `main`, verändert aktuelle Runtime-Dateien | direkter Merge wäre gefährlich | Entscheidung `REBASE_AND_REPLACE`; alter PR wird geschlossen; spätere Neuimplementierung nur von aktuellem `main` |
| K1-D/K1-E | `NOT_RELEASED` / `NOT_ADMISSIBLE` | keine physikalische Forward Map oder Likelihood-Freigabe | kein sachlicher Änderungsgrund | unverändert und durch Validator geschützt |
| official MD-2S solver | `NOT_AUTHORIZED` | nur Verifikationswerkzeuge, kein physikalischer Solver | C1-Rechnung darf keine Freigabe erzeugen | unverändert und durch Validator geschützt |

## 4. Korrigierte Statusarchitektur

```text
Architecture:
HPVS -> HZT-M0 -> HZT-Full

MD2S-R1-L:
BLOCKED_BY_MISSING_PRIMARY_SOURCES
historical A0 benchmarks = REPORTED_NOT_INDEPENDENTLY_REPRODUCED

MD2S-R1-C-PHYS:
MODEL_FREEZE_INCOMPLETE

HZT-M0-S6-C1-V:
MANUFACTURED_VERIFICATION_MODEL
C1-V0 = PASS
C1-V1 = PASS_DIAGNOSTIC
C1-V2 = PASS_DIAGNOSTIC
C1-V3 = PARTIAL
C1-V4 = NOT_STARTED

Historical A0 identity     = NOT_ESTABLISHED
C1 physical identity       = NOT_ESTABLISHED
Continuum BVP Jacobian      = NOT_PROVEN
Nonlinear solution family  = NOT_ESTABLISHED
Perturbative stability     = OPEN
Ghost freedom              = OPEN
K1-D                       = NOT_RELEASED
K1-E                       = NOT_ADMISSIBLE
Physical evidence effect   = NONE
```

## 5. Alte Pull Requests

### PR #1 — `SUPERSEDE`

Begründung:

- 293 Commits hinter `main`,
- alte L0–L5-Projektgliederung ist nicht die heutige MD-0-/HPVS-/HZT-Architektur,
- nützliche Regeln zu Visualisierungsautorität, Numerikmetadaten und Evidenzgrenzen wurden in v0.2 migriert,
- kein direkter Merge.

### PR #2 — `REBASE_AND_REPLACE`

Begründung:

- 290 Commits hinter `main`,
- basiert auf `agent/mvp-0.4-cosmic-epochs`, nicht auf `main`,
- verändert `index.html`, `sw.js`, README und alte Modulpfade,
- wissenschaftlich nützliche Numerikideen dürfen nur in einem neuen, aktuellen und separat geprüften PR wiederaufgenommen werden.

## 6. Neue und geänderte Artefakte

| Artefakt | Datum/Version | Modell-/Trackbezug | Primärquellen | Hash/Teststatus |
|---|---|---|---|---|
| `registry/2026-08-03_UniverseLab_ThreeTrackContract_v1.0.json` | 2026-08-03 / v1.0 | alle drei Tracks | MD-0, Projektmanifest, R1- und C1-Verträge | read-only G0-Vertrag |
| `registry/2026-08-03_UniverseLab_ClaimRegister_G0_v1.0.json` | 2026-08-03 / v1.0 | L und C1-V | Baseregister, Recovery-Audit, C1-Verträge | read-only G0-Vertrag |
| `registry/2026-08-03_UniverseLab_ResearchContinuationManifest_v0.2.json` | 2026-08-03 / v0.2 | alle drei Tracks | Programm v0.1, R1-Gate, C1-Verträge | read-only G0-Vertrag |
| `science/hzt-m0/md2s/2026-08-03_MD2S_R1_ThreeTrackGate_v1.0.json` | 2026-08-03 / v1.0 | L / C-PHYS / C1-V | R1-Gate v0.1, Drei-Track-Vertrag | read-only G0-Vertrag |
| `registry/2026-08-03_HZT_M0_S6_C1_V_ModelContract_v0.2.json` | 2026-08-03 / v0.2 | C1-V | C1 v0.1 und G0 | Parameterhash `d23a01b6f024858bff071edd6b258df7a5e97441f887514b58369a9293ff73ce` |
| `registry/2026-08-03_HZT_M0_S6_C1_V_DimensionlessJacobianContract_v0.2.json` | 2026-08-03 / v0.2 | C1-V1 | C1-Jacobian v0.1 | diskrete QA, keine neue Rechnung |
| `registry/2026-08-03_HZT_M0_S6_C1_V_BackendTangentContract_v0.2.json` | 2026-08-03 / v0.2 | C1-V2/V3 | Backendvertrag v0.1 | Backend-QA, keine neue Rechnung |
| `governance/2026-08-03_UNIVERSELAB_RESEARCH_CONTINUATION_PROGRAM_v0.2.md` | 2026-08-03 / v0.2 | Governance | v0.1, PR #1, G0-Auftrag | manuell und CI-geprüft |
| `tools/2026-08-03_validate_g0_three_track_sync_v1.0.py` | 2026-08-03 / v1.0 | Governance | zentrale Register | SHA-256 `b89ced5a6ed58fb73cdc159f198143888c06c2670f2ff2e644239ebc753f6704` |
| `tests/2026-08-03_test_g0_three_track_sync_v1.0.py` | 2026-08-03 / v1.0 | Governance | G0-Validator | SHA-256 `8b768adc7c6309046712429c552f90dfae6c815f8045bb94de606936af0f31f8` |
| `registry/2026-08-03_UniverseLab_SessionCheckpoint_v1.7.json` | 2026-08-03 / v1.7 | alle drei Tracks | G0-Artefakte | Alias muss identisch sein |
| `project-manifest.json` | Release 2.2 | gesamtes Projekt | MD-0 und G0 | grandfathered stable path |
| `registry/decision-log.jsonl` | append-only | Governance | `UL-DEC-0014` | grandfathered stable path |

## 7. Standardisierter Blockabschluss

### A. Was wurde gemacht?

Die Architektur, Trackkennungen, Evidenzlabels, R1-Phasen, C1-Verifikationsphasen, zentrale Claims, Checkpointstruktur und Alt-PR-Dispositionen wurden synchronisiert. Ein fail-closed read-only Validator wurde angelegt.

### B. Was wurde tatsächlich bewiesen oder bestätigt?

- Die zuvor gemeinsam geführten Aufgaben sind governance-seitig in drei nicht übertragbare Tracks zerlegt.
- Der historische A0-Status war gegenüber der vorhandenen Quellenlage zu stark und wurde korrigiert.
- C1 ist nach seiner Konstruktion ein hergestelltes Verifikationsmodell.
- Die vorhandenen C1-Zahlen bleiben diskrete QA-Ergebnisse; ihre numerischen Werte wurden durch G0 nicht verändert.

### C. Was wurde nicht bewiesen?

- keine historische A0-Reproduktion,
- keine Identität zwischen A0, C-PHYS und C1-V,
- keine Kontinuumsinvertierbarkeit,
- keine endliche Lösungsfamilie,
- keine Hintergrundexistenz außerhalb des hergestellten Ankers,
- keine perturbative Stabilität,
- keine Ghostfreiheit,
- keine 6D→4D-Forward Map,
- keine physikalische Evidenz.

### D. Welcher Track wurde bearbeitet?

```text
MD2S-R1-C-PHYS
```

G0 bearbeitet dort die Governance- und Modellidentitätsvoraussetzungen. `MD2S-R1-L` und `HZT-M0-S6-C1-V` wurden ausschließlich reklassifiziert; in ihnen wurde keine neue wissenschaftliche Rechnung ausgeführt.

### E. Gate-Wirkung

```text
K1-D                     = unchanged / NOT_RELEASED
K1-E                     = unchanged / NOT_ADMISSIBLE
R1.1                     = unchanged / BLOCKED
official MD-2S solver    = unchanged / NOT_AUTHORIZED
physical evidence effect = NONE
```

### F. Artefakt- und Teststatus

Der Merge ist nur zulässig, wenn G0-Vertrag, Dateinamenvertrag, Memory-/Privacy-Vertrag und bestehende Research Contracts vollständig grün sind. Die endgültigen Run- und Merge-IDs werden im Abschlussbericht und Issue #3 dokumentiert.

### G. Exakt ein nächster Forschungsblock

```text
G1.1 — Symmetrischer predictor-only Residualordnungstest
Track: HZT-M0-S6-C1-V
```

Vor Ausführung müssen Schrittgrößen, Auflösungen, Norm, Rundungsgrenze, Akzeptanzkorridor und Fitfenster präregistriert werden. Kein Korrektor, kein Branch-Tracking und keine physikalische Interpretation.
