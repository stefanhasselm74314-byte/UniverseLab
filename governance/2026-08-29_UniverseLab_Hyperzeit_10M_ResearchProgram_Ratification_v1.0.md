# UniverseLab / Hyperzeit — 10-Monats-Arbeits- und Forschungsprogramm v1.0 — Ratifikation

**Datum:** 2026-08-29  
**Programm-ID:** `UL-HZT-10M-2026-2027`  
**Status:** `ACTIVE_RATIFIED_RESEARCH_PROGRAM`  
**Zeitraum:** 2026-09-01 bis 2027-06-30  
**Klassifikation:** Theorie-, Methoden-, Daten-, QA- und Dokumentationsprogramm; CP01R4 fail-closed.

## 1. Ratifikationsentscheidung

Mit der ausdrücklichen Nutzerfreigabe **„Go“ vom 2026-08-29** wird das zuvor als `VORGESCHLAGEN` geführte Dokument **UniverseLab / Hyperzeit 10-Monats-Arbeits- und Forschungsprogramm v1.0** als Arbeits- und Forschungsprogramm ratifiziert.

Planungsquelle: `UniverseLab_Hyperzeit_10M_Arbeits_und_Forschungsprogramm_v1.0.docx`  
SHA-256: `cbf6cdd7f96a6aff74655aeda6729f6bec1153486367a06a20890a46ab2bd09d`

Die Ratifikation macht **das Arbeitsprogramm**, seine Workstreams, Gates, WIP-Regeln und den CP01R4-Hold kanonisch. Sie ratifiziert **keine neue Physik**, keinen Solverlauf und keine Evidenzhochwertung.

## 2. Harte CP01R4-Firewall

Während des gesamten Programmhorizonts gelten unverändert:

- `ULSH-01-WP1 = CLOSED_TARGET_FROZEN_NO_EXECUTION`
- `ULSH-01-WP2 = READY_FOR_SEPARATE_AUTHORIZATION_DECISION_NOT_AUTHORIZED`
- `CP01R4 = METHOD_FROZEN_NO_EXECUTION`
- operativer `AuthorizationDecision = NOT_CREATED`
- operativer `SingleUseGrant = NOT_CREATED`
- Backendimport = `FALSE`
- Solverlauf = `FALSE`
- `physical background = NOT_ESTABLISHED`
- `physical rank R = NOT_EXECUTED`
- `WP3 = NOT_STARTED`
- `WP4 = BLOCKED_NOT_AUTHORIZED`
- `K1-D = NOT_RELEASED`
- `K1-E = NOT_ADMISSIBLE`
- `physical evidence effect = NONE`

Wiederaufnahmeanker:

- Release subject: `d8890b9ef47936edf8bb7e758b882c898241b314`
- Target: `237c4b5e08a2106e13e985c4af7925f1899e2ae2e4b7253c7ab73cc2db5f1823`
- CP01R4 payload: `8e5976a22c4be78b5e4fe7834c9947de8a4acea7781363c7aeb83aa73982ac8c`
- 16-file release package: `1d6f45725a66b145d2907943ddc7fe3a989411e5ccfe6c0f29053c91253c7621`

**Keine** operative CP01R4-Decision/Grant-Erzeugung, kein physischer Backendimport, kein CP01R4-Lauf und kein automatischer WP3/WP4-Start sind Teil dieses Programms.

## 3. Programmarchitektur

Primärer wissenschaftlicher Pfad:

`HZT-M0 Forward Map → MOND/RAR → Kosmologie/Growth/Lensing → Identifizierbarkeit → Likelihoods → Falsifikationsatlas`

Kritische Arbeitskette:

`FM-0 → FM-1 → RAR-0 → COS-0 → ID-0 → DATA-0 → FALS-0`

Paralleler Theoriepfad:

`Ghost/Stability/Constraints → KK/GW-Vorbereitung → frühes Universum / Phasenübergänge`

Infrastrukturpfad:

`Dissertation/Monographie + Tafelwerk + Quellen/Provenienz + UniverseLab nur material-change-getrieben`

WIP-Regel: maximal **zwei aktive wissenschaftliche Kern-Work-Packages**; ein dritter Slot ist nur für Dokumentation/QA zulässig.

## 4. Ratifizierte Workstreams

- **WS1 — HZT-M0 Forward Map & Observables** · Lane A · Initialstatus `ACTIVE_FM0`
- **WS2 — Rigorose MOND-/RAR-Brücke** · Lane A · Initialstatus `QUEUED_AFTER_FM_G0`
- **WS3 — HPVS / K1–K7: Identifizierbarkeit, Robustheit und Falsifizierbarkeit** · Lane A · Initialstatus `QUEUED_PARALLEL_HPVS0`
- **WS4 — Beobachtungsdaten und Likelihood-Infrastruktur** · Lane A · Initialstatus `QUEUED_PARALLEL_DATA0`
- **WS5 — Kosmologie, Growth und Lensing** · Lane A · Initialstatus `QUEUED`
- **WS6 — Ghost Freedom, Constraint- und Stabilitätsanalytik** · Lane B · Initialstatus `QUEUED_PREPARATORY`
- **WS7 — ULSH-07 / Kaluza-Klein Spectrum Solver – Vorbereitung** · Lane B · Initialstatus `PREPARATORY_ONLY_PHYSICAL_RELEASE_BLOCKED`
- **WS8 — Gravitationswellen- und Polarisationssignaturen** · Lane B · Initialstatus `QUEUED_PREPARATORY`
- **WS9 — Frühes Universum, Phasenübergänge und stochastische GW** · Lane B · Initialstatus `QUEUED`
- **WS10 — Große kosmologische Rätsel – HZT-Relevanz- und No-Go-Audits** · Lane B · Initialstatus `BACKLOG_GATED`
- **WS11 — Dissertation, Monographie, Tafelwerk und wissenschaftliche Konsolidierung** · Lane C · Initialstatus `CONTINUOUS_SUPPORT`
- **WS12 — UniverseLab Forschungsplattform – Maintenance- und Integrationstrack** · Lane C · Initialstatus `MONITOR_DRIVEN_MAINTENANCE_ONLY`

## 5. Programmweite Qualitätsregeln

1. Kein Symbol ohne Definition, Dimension und Provenienzstatus.
2. Keine effektive Beziehung als 6D-Ableitung, wenn ein Zwischenschritt fehlt.
3. Negative Resultate/No-Gos werden eingefroren statt durch zusätzliche Freiheitsgrade verdeckt.
4. Daten-/Likelihood-Pipelines werden zunächst mit Referenz-/Mockfällen validiert, nicht durch HZT-Fits legitimiert.
5. Struktureller Rang bleibt strikt getrennt von physischem Response-/Jacobian-Rang.
6. Numerical stability ist keine Ghostfreiheit.
7. Green CI ist Software-/Governance-Evidenz, nicht automatisch physische Evidenz.
8. UniverseLab-Plattformarbeit bleibt supporting infrastructure und wird nur bei materiellem Forschungs-/Reproduzierbarkeitsnutzen priorisiert.

## 6. Unmittelbarer Start

Mit dieser Ratifikation wird **WS1 / FM-0 — Parameter-/Symbol-/Provenienz-Inventar** eröffnet.

Status: `ACTIVE_INITIALIZATION_PROVENANCE_INVENTORY`  
Gate: `FM-G0 = OPEN`

FM-0 darf ausschließlich vorhandene kanonische Definitionen, Units, Konventionen und Provenienz einsammeln und Lücken sichtbar machen. Es darf keine neue Parent→Reduced-Beziehung erfinden, keine Datenfits starten und keine background-abhängigen physikalischen Koeffizienten behaupten.

Maschinenlesbare Quellen:

- `registry/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgramManifest_v1.0.json`
- `registry/2026-08-29_HZT_M0_ForwardMap_FM0_Inventory_v0.1.json`

## 7. Wiederaufnahme nach der Haltephase

`aktueller kanonischer Stand → CP01R4-Vergleich → Toolchain/Environment-Revalidation → neuer Authorization Review → separate operative Entscheidung`

Es gibt **keine automatische Freigabe am Ende des 10-Monats-Zeitraums**.

## 8. Evidenzwirkung

`physical_gate_effect = NONE`  
`physical_evidence_effect = NONE`
