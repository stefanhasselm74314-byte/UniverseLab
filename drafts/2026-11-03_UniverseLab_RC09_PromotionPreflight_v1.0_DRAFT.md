# UniverseLab — RC-VALIDATION-09 / Canonical Promotion Preflight v1.0
Datum: 2026-11-03
Status: DRAFT — NONCANONICAL — HOLD
Basis für Quellenaussagen: main commit `51bcc8fccb092c104ac0fca5fc98a5b996dcb914`
Verifizierter Git-Tree: `65f423f04bbb2f1462f120a6b31073644cdc28cc`
Änderungsziel: Governance-/Status-Synchronisierung, nicht physikalische Evidenz.

## 1. Verifizierte Vorarbeiten

- RC08: sechs festgepinnte Quellen, zwölf quellengebundene Feldentscheidungen, acht Negativkontrollen — GitHub Actions PASS.
- RC09: 39 Git-Blob-Provenienzen, 177 quellengebundene Feldprüfungen, acht Negativkontrollen — GitHub Actions PASS.
- Wichtig: Die 39 RC09-Quellen wurden hinsichtlich ihrer deklarierten Geltung und Statusgrenzen geprüft, nicht unabhängig mathematisch neu hergeleitet.
- Das Claimbuch führt 993 automatisch zugeordnete Kandidaten mit 251 `manual_review_required_count`. Automatisches Routing ist keine wissenschaftliche Bestätigung.

## 2. Vollständigkeit der Zustandskette

Die ursprüngliche Drei-Dateien-Trias reicht nicht aus. Die folgenden, gegenwärtig NICHT aktiven Draft-Kandidaten wurden vollständig aus ihren Vorgängern abgeleitet:

1. `drafts/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4_DRAFT.json`
2. `drafts/2026-11-03_UniverseLab_SessionCheckpoint_v1.35_DRAFT.json`
3. `drafts/2026-11-03_UniverseLab_SiteState_v1.5_DRAFT.json`
4. `drafts/2026-11-03_UniverseLab_ProjectManifest_v2.35_DRAFT.json`

DRAFT-Pointer dürfen nicht mit aktiven Canon-Pointern gleichgesetzt werden. Die Drafts bleiben im Ordner `drafts/`; gerade diese Trennung verhindert unbeabsichtigte Erkennung als neueste kanonische Registrysnapshots.

## 3. Nachzuweisende Freigabekette (nur Vorschlag)

Geplante, erst nach gesondertem Review zu erzeugende/aktivierende Ziele:

- neuer datierter `CurrentMainCanonicalState` in `registry/`;
- neuer datierter `SessionCheckpoint` in `registry/`;
- neuer datierter `SiteState` in `registry/`;
- aktives `project-manifest.json` mit konsistenten Canon-Pointern;
- `registry/session-checkpoint-latest.json` byteidentisch zum neuen datierten Checkpoint;
- `research-status.html` und `research-status-en.html`, einschließlich aller aktuellen wissenschaftlichen Statusverweise;
- `assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js` bzw. ein neuer versionierter Shell-Nachfolger einschließlich der öffentlichen Referenzverkettung;
- ein vollständiger Repository-Referenzscan über weitere Verbraucher, Weboberflächen und Tests.

Diese Zielpfade sind ein Releaseplan, keine Autorisierung zur Änderung.

## 4. Offene Blocker

1. Das im Draft geerbte `snapshot_timestamp` stammt vom September 2026 und darf nicht als November-Snapshot ausgegeben werden.
2. Im Checkpoint ist `canonical_snapshot` bis zum Release weiterhin ein historischer September-Pfad. Dieser darf nicht fälschlich als aktueller November-Canon bezeichnet werden.
3. Öffentliche DE/EN-Seiten und die aktuelle Shell referenzieren weiter die September-Kette. Quellprüfung am gepinnten Basis-Commit hat diese Referenzen bestätigt.
4. Der alte historische Claimcount von elf missing links und die September-G11-Reparatur mit null verbleibenden Governance-Provenienz-Gaps müssen zeitlich und im Geltungsbereich getrennt bleiben. Die zehn wissenschaftlichen Gaps sind nicht durch diese Governance-Reparatur geschlossen.
5. Die 39 fachlichen Quelldeklarationen sind nicht identisch mit unabhängigen Beweisen, empirischer Modellvalidierung oder vollständiger Prüfung sämtlicher 298 Commits.
6. Eine Owner-Ratifikation für eine spätere Beförderung zu `canonical`, `ratified` oder `released` ist ausdrücklich und gegenstandsbezogen erforderlich. Ein allgemeines `Go` zur Auditfortsetzung ist dafür nicht hinreichend.
7. Die üblichen G0-/Snapshot-/Dateinamens-/Privacy-/Gate-Checks müssen nach dem vollständigen Umbau auf dem exakten PR-Head bestehen. Grün auf einem vorgelagerten Draft ist keine aktive Freigabe.

## 5. Freigabevoraussetzungen

- Vollständiger Crosswalk neuer Statusfelder gegen relevante gemergte Quellen; unaufgelöste Konflikte müssen `HOLD` bleiben.
- Konsistenz `CurrentState ↔ Checkpoint ↔ SiteState ↔ Manifest ↔ Alias ↔ DE/EN-Seiten ↔ Shell`.
- Frische, klar definierte Snapshot-Semantik; keine fälschliche Gleichsetzung von Quellbasis-Commit, Git-Tree, Entwurfszeitpunkt und Release-Commit.
- Bytegleichheit des Checkpoint-Alias nach einem kontrollierten Release-PR.
- Keine positive Abweichung von `FM-G0=OPEN`, `K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`, `PHYSICAL_BACKGROUND=NOT_ESTABLISHED`, `PHYSICAL_RESPONSE_RANK=NOT_EXECUTED`.
- Adversariale Tests für veraltete Pointer, nicht passende SHAs und unzulässige Gate-/Evidenzbeförderung.
- Separater, überprüfter Release-PR; ausdrückliche Eigentümer-Ratifikation vor jeder reservierten positiven Statusänderung.

## 6. Auswirkung

```text
RC09_SOURCE_CONTRACT_QA = PASS
RC09_DRAFT_POINTER_INTEGRATION = PREPARATION_ONLY
CANONICAL_PROMOTION = BLOCKED
OWNER_RATIFICATION_FOR_RESERVED_PROMOTION = NOT_REQUESTED
SOLVER_EXECUTION = NOT_AUTHORIZED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
