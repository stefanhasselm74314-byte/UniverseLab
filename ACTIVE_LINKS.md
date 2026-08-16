# UniverseLab — Canonical Active Links

**Status:** ACTIVE · CANONICAL  
**Letzte Pflege:** 2026-08-16  
**Zweck:** Single Source of Truth für aktuell wichtige und verwendbare Projektlinks sowie die Zuordnung aktiver Arbeitsstränge.

> Regel: Nur aktive, aktuelle oder ausdrücklich als Arbeitslink benötigte Ziele gehören in dieses Register. Ersetzte oder historische Ziele werden aus dem aktiven Bereich entfernt bzw. unter `ARCHIV / ERSETZT` verschoben.

## Statuslegende

- **CANONICAL** — maßgeblicher aktueller Einstieg
- **ACTIVE** — aktuell funktionsfähig und relevant
- **WORKING** — temporärer aktiver Arbeitslink, z. B. offener PR
- **PRIVATE** — nur mit berechtigtem GitHub-Zugang erreichbar
- **COMPLETED** — Arbeitsstrang abgeschlossen; Ergebnis bleibt als Provenienz relevant
- **ARCHIVE / ERSETZT** — nicht mehr als primärer Einstieg verwenden

---

## 1. UniverseLab

### UniverseLab Live
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/

### UniverseLab Wissenschafts-Navigator
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/navigator.html

### UniverseLab GitHub Repository
**CANONICAL · ACTIVE**  
https://github.com/stefanhasselm74314-byte/UniverseLab

### UniverseLab Solver Hub
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/solver-hub.html

### UniverseLab Audit 2026-07-31
**ARCHIVED_REFERENCE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/universelab-audit-2026-07-31.html?v=1

---

## 2. UniverseLab Solver Hub — ULSH

### Solver Hub README / Governance
**CANONICAL · ACTIVE**  
https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/README_SOLVER_HUB.md

### Solver Workbench v1.1
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html

### Master Build Order v1.0
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/2026-08-10_ULSH_MasterBuildOrder_v1.0.html

### ULSH-01 / C-PHYS — PR #137
**WORKING · ACTIVE**  
https://github.com/stefanhasselm74314-byte/UniverseLab/pull/137

**Primärer Solver:** `HZT-M0-S6_MD-2S_Background_BVP_Solver_v1.0`  
**Kennung:** `ULSH-01 · MD2S-BVP`

### Governed Site State
**CANONICAL · ACTIVE · MACHINE_READABLE**  
https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/registry/2026-08-16_UniverseLab_SiteState_v1.0.json

---

## 3. Aktive Arbeitsstränge / Chat-Zuordnung

> Diese Zuordnung ist eine **Koordinationsschicht**, keine wissenschaftliche Evidenzquelle. Chat-Inhalte werden nicht als kanonische Physik zitiert. Kanonisch werden Ergebnisse erst über versionierte GitHub-Artefakte, Registries, Tests, PRs und Merge-Commits. Private ChatGPT-URLs und Konversations-IDs werden bewusst nicht öffentlich gespeichert.

### Forschungsplattform Architektur
**ACTIVE · PLATFORM / GOVERNANCE**  
**Aufgabe:** UniverseLab als Forschungsplattform: globale Navigation, SiteState, Reproduzierbarkeit, Plattform-Governance, Statusachsen und UI-/Registry-Integration.  
**Kanonische Ausgaben:** PR #139 / #140 sowie nachfolgende Reproduzierbarkeitsintegration #141–#143.  
https://github.com/stefanhasselm74314-byte/UniverseLab/pull/140

### Analyse der 17 Dateien
**ACTIVE · SCIENCE / SOLVER · CRITICAL PATH**  
**Aufgabe:** `ULSH-01 → C-PHYS → Background3C5`; Response-Rank-Gate, Finite-Thickness-Operator, Regular-Center-Gates und anschließend vollständige Operatoridentität.  
**Aktueller Auftrag:** `G5 — FULL FINITE-THICKNESS OPERATOR IDENTITY`.  
**Kanonischer Arbeitslink:** PR #137.  
https://github.com/stefanhasselm74314-byte/UniverseLab/pull/137

### Aktive wichtige Links
**ACTIVE · LINK GOVERNANCE**  
**Aufgabe:** zentrale Pflege aller aktiven, kanonischen und temporären Projektlinks; tote oder ersetzte Links aussortieren.  
**Kanonische Ausgaben:** `links.html`, `ACTIVE_LINKS.md` und Workstream-Registry.  
https://stefanhasselm74314-byte.github.io/UniverseLab/links.html

### CP01R2 D8 Laufwache
**COMPLETED · RUN WATCH / PROVENANCE**  
**Aufgabe:** einmaligen CP01R2-D8-Lauf überwachen, verifizieren, korrekt beenden und Artefakt-/Grant-Zustand sichern.  
**Abschlussstatus:** Lauf `completed / success`; Grant einmalig verbraucht (`SPENT / NON-REPLAYABLE`, `replay_permitted=false`); kein akzeptierter Kandidat.  
**Regel:** kein erneuter Lauf aus diesem Arbeitsstrang ohne neuen expliziten Grant/Vertrag.

### HZT-M0-S6-C1 Theorie
**ACTIVE REFERENCE / THEORY**  
**Aufgabe:** kanonischer C1/C-PHYS-Theoriestrang innerhalb `HPVS → HZT-M0 → HZT-Full`; Parent-Physik, Herleitungen, Gates und Theorieentscheidungen.  
**GitHub-Ziel:** versionierte C-PHYS-/MD2S-Artefakte und Registries auf `main`; Chat selbst ist keine kanonische Quelle.  
https://github.com/stefanhasselm74314-byte/UniverseLab/tree/main/science/hzt-m0/md2s

### HZT-M0-S6-C1 Restart
**ACTIVE CONTINUATION / HANDOFF**  
**Aufgabe:** kanonische Fortsetzung des wegen Chat-Längenlimit beendeten C1-Theoriestrangs; kein C2-Versionssprung. Zusätzlich Solver-Gesamtplanung und Übergabe in ULSH.  
**Kanonische Ausgabe:** ULSH Master Build Order / Solver Workbench.  
https://stefanhasselm74314-byte.github.io/UniverseLab/2026-08-10_ULSH_MasterBuildOrder_v1.0.html

### Technischer Neben-/Analysechat: UniverseLab Fehleranalyse
**ACTIVE · TECHNICAL AUDIT / QA**  
**Aufgabe:** technische Fehleranalyse, Repository-/CI-Audits, P0-Verifikation, SCI-001/SCI-002-Integrationsprüfung und technische Sonderprobleme.  
**Kanonischer Zielbereich:** Quellcode, Methoden/QA, Registries und Audit-Artefakte.  
https://stefanhasselm74314-byte.github.io/UniverseLab/source.html

### Trennregel für parallele Chats

`Theoriechat → Herleitung / physikalische Modellentscheidung`  
`Solverchat → numerische Implementierung / BVP / Rang / Konvergenz`  
`Plattformchat → SiteState / UI / Governance / Reproduzierbarkeit`  
`Fehleranalysechat → technische Audits / CI / Reparaturen`  
`Linkchat → ausschließlich aktive Zugänge und Zuordnungen`

**Keine automatische Statusübertragung zwischen diesen Arbeitssträngen.**

Maschinenlesbare Zuordnung:  
https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/registry/2026-08-16_UniverseLab_WorkstreamLinks_v1.0.json

---

## 4. GSRA-01 — Generation Ship

> GSRA-01 ist ein eigenständiges Projekt und bleibt technisch/repositorisch von UniverseLab getrennt. Die Links werden hier nur zentral referenziert.

### GSRA-01 Control Center — Live
**CANONICAL · ACTIVE · PUBLIC**  
https://stefanhasselm74314-byte.github.io/GSRA-01-Control-Center/

### GSRA-01 Control Center — GitHub
**CANONICAL · ACTIVE · PUBLIC**  
https://github.com/stefanhasselm74314-byte/GSRA-01-Control-Center

### GSRA-01 Generation Ship — Hauptrepository
**CANONICAL · ACTIVE · PRIVATE**  
https://github.com/stefanhasselm74314-byte/GSRA-01-Generation-Ship

---

## 5. Link-Zentrale selbst

### UniverseLab Link Hub — Live
**CANONICAL · ACTIVE**  
https://stefanhasselm74314-byte.github.io/UniverseLab/links.html

### Kanonisches Link-Register — GitHub
**CANONICAL · ACTIVE**  
https://github.com/stefanhasselm74314-byte/UniverseLab/blob/main/ACTIVE_LINKS.md

---

## ARCHIV / ERSETZT

Historische Zugänge werden nur aufbewahrt, wenn sie für Reproduzierbarkeit oder Provenienz benötigt werden. Der Audit vom 2026-07-31 ist ausdrücklich `ARCHIVED_REFERENCE` und kein aktueller kanonischer Projektstatus.

---

## Pflegevertrag

1. Ein neuer wichtiger Link wird zunächst auf Erreichbarkeit und Projektzuordnung geprüft.
2. Bestehende kanonische Ziele werden nicht stillschweigend dupliziert.
3. Ein ersetzter Link verliert `CANONICAL` und wird bei Bedarf in `ARCHIV / ERSETZT` verschoben.
4. Temporäre PR-/Issue-Links tragen `WORKING` und werden nach Abschluss neu bewertet.
5. `links.html` ist der bevorzugte mobile Einstieg; `ACTIVE_LINKS.md` ist die kanonische textuelle Quelle.
6. Chat-Arbeitsstränge erhalten eine eindeutige Zuständigkeit und einen GitHub-Ausgabeort; private Chat-URLs werden nicht veröffentlicht.
7. Chatstatus, technischer Status, Governance-Status und wissenschaftlicher Status dürfen nicht automatisch ineinander überführt werden.
