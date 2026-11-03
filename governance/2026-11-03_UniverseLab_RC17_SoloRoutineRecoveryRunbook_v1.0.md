# UniverseLab — RC-VALIDATION-17: Routinedraft-Grenzen und Recovery

**Datum:** 2026-11-03  
**Status:** `DRAFT — TECHNISCHER VORSCHLAG — NICHT INSTALLIERT`  
**Zielarchitektur:** RC16-B, Ein-Personen-Betrieb / automatische nichtoperative QA / kritische Änderungen `HOLD`  
**Repository:** `stefanhasselm74314-byte/UniverseLab` · **Arbeits-PR:** #264 (Draft)  
**Maßgebliche Vorlage:** `drafts/2026-11-03_UniverseLab_RC17_SoloRoutineSafetyContract_v1.0_DRAFT.json`  
**Prüfskript:** `tools/2026-11-03_UniverseLab_RC17_RoutineDraftValidator_v1.0.py` (nicht installiert)

## 1. Präziser Geltungsbereich

RC17 entwickelt eine **technische Routine-Ausnahme**, keine Delegation der wissenschaftlichen oder kanonischen Freigabe. Sie umfasst ausschließlich neu erzeugte, reguläre Git-Dateien nach dem Muster:

`drafts/YYYY-MM-DD_UniverseLab_<slug>_vX.Y_DRAFT.json`

Ein Routine-PR muss ausschließlich solche neuen Dateien enthalten. Zulässige Menge in dieser Modellversion: **1 bis 12 Dateien je PR**, jede maximal **32 KiB**. Binärdateien, Symlinks, Submodule, ausführbare Dateien, geänderte bestehende Dateien, umbenannte Pfade, HTML, Markdown, JS, GitHub-Workflows, `registry/`, `project-manifest.json` und öffentliche Statusseiten sind **nicht** Teil dieser Ausnahme.

Vor einer späteren technischen Integration sind **Git-Modus `100644`**, Typ `blob`, SHA des genauen Blobinhalts, Übereinstimmung mit dem aktuellen verifizierten `main`-Commit sowie das vollständige GitHub-PR-Dateiinventar aus der **vertrauenswürdigen** Quelle abzugleichen. Die aktuelle RC17-Pythonfunktion führt selbst keine GitHub-Netzabfragen aus; das ist absichtlich ein vorgeschalteter Vertrag für einen späteren, separat überprüften Base-Trusted-Adapter.

### 1.1 Striktes Dokumentenformat

Erlaubt sind nur die Felder `schema`, `status`, `date`, `title`, `basis_main_commit`, `physical_gate_effect`, `physical_evidence_effect`, `authority_status`, `publication_status`, `scientific_evidence_status`, `solver_execution` und `notes`.

Der Validator verlangt:

- `schema = universelab.rc17.routine-note.v1`
- `status = DRAFT_NONCANONICAL`
- `physical_gate_effect = NONE`
- `physical_evidence_effect = NONE`
- `authority_status = NO_AUTHORITY`
- `publication_status = NOT_PUBLISHED`
- `scientific_evidence_status = NOT_VALIDATED`
- `solver_execution = NOT_AUTHORIZED`
- `date` stimmt mit dem Dateinamen überein, `basis_main_commit` mit `main`.
- `notes` enthält 1–16 kurze Klartextnotizen, ohne frei definierbare maschinenlesbare Ergebnis-/Gate-Strukturen. Doppelte JSON-Felder, ungültiges JSON, NaN/Infinity, Kontrollzeichen und übergroße Dateien führen zu `HOLD`.

**Wichtiger Vorbehalt:** Auch Klartextnotizen können falsche wissenschaftliche Aussagen enthalten. Die Routineprüfung beglaubigt daher nicht deren Wahrheit und darf nicht als Evidenz oder Canon importiert werden. Noch nicht verifiziert ist, ob ein bereits auf `main` vorhandener Verbraucher den Ordner `drafts/` indirekt automatisch ausliest oder veröffentlicht. **Bis zum vollständigen Datenfluss-/Autodiscovery-Audit bleibt die tatsächliche GitHub-Merge-Ausnahme gesperrt.**

### 1.2 Zwei grundsätzlich verschiedene Testergebnisse

`ROUTINE_QA_PASS_NOT_MERGE_AUTHORIZATION` bedeutet nur: Die konkrete Notizdatei ist technisch strukturell plausibel. Dieser Test darf bereits im **Draft-PR** laufen.

`CONDITIONAL_ROUTINE_MERGE_ELIGIBLE_NEVER_AUTO_MERGE` wird im reinen RC17-**Simulationsmodell** ausschließlich erreicht, wenn `main` den unabhängig geprüften Guard installiert hat, GitHub erforderliche PR- und strikte Check-Regeln tatsächlich erzwingt, der aktuelle Head/Base nachweislich übereinstimmt, keine Bypass-Regeln gelten, die GitHub-Actions-Ereignisrichtlinie zulässig ist, der Eigentümer die enge Ausnahme ausdrücklich ratifiziert hat und ein echter negativer Canary-PR die Mergeblockade bewiesen hat.

**Aktuell erfüllt UniverseLab diese Installations- und Regelvoraussetzungen nicht.** Deshalb gilt bei jedem echten Release-/Mergeversuch weiterhin `HOLD`, selbst wenn der Modelltest ein theoretisches positives Ergebnis zeigt.

## 2. Störungs- und Wiederherstellungsverfahren

| Auslöser | Erlaubte Reaktion | Nicht zulässig |
|---|---|---|
| Ungültiges JSON, doppelte Schlüssel, falsches Schema | Datei im **eigenen Branch** reparieren, neuen Commit bilden, alle Prüfungen wiederholen | Fehlertest als »ungefährlich« überspringen |
| Blob-Prüfsumme, Git-Modus oder PR-Dateiliste stimmen nicht | Exakte Head-Dateien/Tree erneut nur lesend abholen; Symlink/Submodule ersetzen oder gesondert prüfen | SHA ignorieren oder untrusted Inhalt ausführen |
| `main` ist inzwischen weitergelaufen | PR auf bestätigtem `main` aktualisieren und **alle** Checks an neuer Basis wiederholen | Altes grünes CI oder Owner-Entscheidung weiterverwenden |
| API 403, Timeout, Rate Limit, fehlender Statuscheck | `HOLD`; Zugriffsgrund untersuchen, nach Wiederherstellung auf identischer Basis neu prüfen | Fehler als erfolgreich deklarieren |
| Sensitiver Pfad, Misch-PR, öffentliches Dokument oder wissenschaftliche Aussagefreigabe | Routine-Ausnahme aufheben, in getrennten Reviewpfad verschieben | In `drafts/` umbenennen und als unkritisch tarnen |
| Auf `main` installierter Schutzmechanismus fehlerhaft | Gesonderter Reparatur-PR vom letzten bekannten, vertrauenswürdigen Stand, dokumentierter Incident, erneute Eigen-/Gegenprüfung | Required Checks stillschweigend deaktivieren oder ungeprüft direkt pushen |
| Sicherheitskritischer Notfall im Ein-Personen-Betrieb | Bewusste separate Eigentümerentscheidung über *konkreten* Recovery-Scope; bis dahin `HOLD` | Globale Admin-Bypass-Freigabe aus einem allgemeinen »Go« ableiten |
| Physikalische/empirische Evidenz oder Solver-Ausführung verlangt | An die getrennte HPVS → HZT-M0 → HZT-Full-Gate-Governance zurückgeben | Durch formalen JSON-Status `RATIFIED` / `RELEASED` erzwingen |

### 2.1 Zustandsmodell (Vorschlag)

`NEW_DRAFT → ROUTINE_QA_RUNNING → QA_PASS_NONCANONICAL` oder `QA_HOLD`.

Nach `QA_HOLD`: `FIX_BRANCH → VERIFY_CURRENT_MAIN → NEW_HEAD → RECHECK`. Kein Übergang direkt zu `MERGED` oder `CANONICAL`.

Bei einem technischen Guard-Defekt: `INCIDENT_HOLD → DIAGNOSTIC → SEPARATE_REPAIR_PR → REQUIRED_CHECK_REPLAY → OWNER_DECISION_IF_RESERVED`. Das ist ein Arbeitsplan, **kein freigegebener GitHub-Notfall-Bypass**.

## 3. Risiken, die bewusst nicht als geschlossen gelten

1. **Datenfluss:** Ein vorhandener Registry-/Website-Verbraucher könnte auch neue Draft-Dateien automatisch entdecken. Der RC17-Selbsttest prüft solche globalen Abhängigkeiten derzeit nicht.
2. **Ereignisrichtlinie:** Die Konfiguration der Actions-Policy für `pull_request_target` im konkreten Repository ist nicht ausgelesen und könnte künftige Trusted-Workflows beeinflussen.
3. **Tatsächliche Required-Check-Identität:** Kein `trusted-release-gate` auf `main` installiert; keine echte Mergeblockade bestätigt.
4. **Betriebspolitik:** Die Bevorzugung von RC16-B ist dokumentiert, aber die **konkrete Routine-Ausnahme einschließlich eventueller Recovery-Regeln** wurde noch nicht durch den Projektinhaber in Kraft gesetzt.
5. **Wissenschaft:** Keiner der Daten- oder Statusprüfer beweist mathematische Konsistenz, Ghostfreiheit, einen zulässigen Hintergrund oder empirische HZT-Unterstützung.
6. **Recovery bei einem einzigen Admin:** Ein unabhängiger Ersatz für kritische Reviews existiert noch nicht. Es ist zulässig, einen sensiblen PR deshalb gesperrt zu lassen.

## 4. Geplante Akzeptanztests vor jeder Installation

- GitHub-Statuskontext eindeutig, erforderliche Checks wirklich aktiv, GitHub-App/Head/Commit korrekt identifiziert.
- Mindestens ein einfacher positiver Routinedraft-PR in der echten GitHub-Oberfläche; **kein Auto-Merge**.
- Negative Canary-PRs mit geänderten existierenden Dateien, Misch-PR, gefälschtem Gate, Symlink, inkonsistentem Head/Main und fehlendem Owner-/Ruleset-Schutz. Der Merge muss im GitHub-UI tatsächlich blockiert sein.
- Vollständiger Datenfluss-/Autodiscovery-Scan von `drafts/` über bestehende Site-/Registry-/Tool-Verbraucher.
- Owner entscheidet ausdrücklich, ob die enge Ausnahme betrieblich tragbar ist; gesonderte Installation, Review und Aktivierung nötig.

## 5. Schlussstatus

```text
RC17_ROUTINE_DRAFT_QA = PROTOTYPE_NONINSTALLED
RC17_ROUTINE_MERGE_RIGHT = NOT_GRANTED
RC17_SOLO_RECOVERY = DRAFT_PROCEDURE_ONLY
RC16_B_PREFERRED = YES
RC17_EXCEPTION_POLICY_RATIFIED = NO
GITHUB_REQUIRED_GUARD_INSTALLED = NO
CANONICAL_PROMOTION = BLOCKED
PR263 = DRAFT_UNMERGED
PR264 = DRAFT_UNMERGED
MAIN = UNCHANGED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
