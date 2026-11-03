# UniverseLab — RC-VALIDATION-15: Installationsreife und Betrieb des Trusted Release Gate

**Stand:** 2026-11-03 · **Geltung:** separater Draft-PR #264 · **Urteil:** `NOT_READY_FOR_INSTALLATION`  
**Audit-Basis:** `main@51bcc8fccb092c104ac0fca5fc98a5b996dcb914`  
**Verweis:** `drafts/2026-11-03_UniverseLab_RC15_InstallationReadinessEvidence_v1.0_DRAFT.json`

## A. Gesicherte Erkenntnisse versus ausstehende Nachweise

**[BESTÄTIGT]** Das aktive Ruleset `UniverseLab-main-Basisschutz` (ID `24417933`) gilt für `main` und enthält nur `deletion` und `non_fast_forward`. Weder der erforderliche PR-Zwang noch der Required Check `trusted-release-gate` sind in den lesbaren Regeln konfiguriert.

**[BESTÄTIGT]** Das letzte überprüfte Kandidaten-CI `rc13-candidate-selftest` ist von der GitHub-Actions-App mit `integration_id=15368` erzeugt worden. **Daraus folgt NICHT**, dass der später zu installierende *andere* Job `trusted-release-gate` bereits als Required Check auf einem PR-Head oder Merge-Test-Commit existiert. Tatsächlich wurde dieser Job auf PR #264 noch nicht gefunden.

**[KONDITIONAL]** GitHub dokumentiert `pull_request_target` als zulässiges Ereignis für Required-Check-Auswertung. GitHub verlangt dennoch eine erfolgreiche Prüfung auf dem jeweils maßgeblichen Head- oder Test-Merge-SHA; eine eindeutige Job-/App-Quellidentität ist zu verifizieren. Dies erfordert einen echten Probe-PR **nach** kontrollierter Guard-Installation. Frühere Mock-Tests ersetzen dies nicht.

**[OFFEN / HOCH]** Der Guard verwendet einen GitHub-authentifizierten Owner-**Kommentar** als Freigabe für einen exakten PR/Head/Scope. Entfernen oder Bearbeiten des Kommentars *nach* einem grünen Check führt ohne eigenes PR-Ereignis nicht automatisch zur Ungültigkeit dieses bestehenden grünen Statuschecks. Die Prüfung unmittelbar vor PASS schließt dieses zeitliche Fenster nicht vollständig. GitHub-native Required Reviews mit »Dismiss stale approvals« können stärkere Semantik für einen vorhandenen unabhängigen Reviewer liefern, würden aber ohne weiteren berechtigten Reviewer einen Ein-Personen-Ablauf blockieren. Eine spätere Installation darf Kommentar-Autorisierung deshalb nicht als zeitlich unaufhebbares Sicherheitsmerkmal darstellen.

**[OFFEN / HOCH]** GitHub weist darauf hin, dass doppelte Jobnamen in unterschiedlichen Workflows Required-Check-Ergebnisse mehrdeutig machen und das Mergen blockieren können. Die Herkunft »GitHub Actions« (App 15368) allein beweist nicht, welcher Workflow den Check erzeugt hat. Für `trusted-release-gate` ist ein eigenständiger Eindeutigkeits-/Canary-Nachweis erforderlich.

**[OFFEN]** Ein unabhängig handelnder menschlicher Sicherheitsprüfer hat den Python-Code und die Workflow-Konfiguration nicht freigegeben. Die 44 negativen Mocks und die bisherigen 9 Unittest-Methoden belegen lediglich die implementierten Simulationsfälle; sie bilden weder sämtliche API-Races noch einen Real-Merge-Schutz ab.

## B. Betriebsmodell, das ausdrücklich akzeptiert werden müsste

RC14 ordnet absichtlich **jeden geänderten Dateipfad** als `CONTROL_PLANE`, `PUBLIC_SURFACE` oder `STATE_RELEASE` ein. Eine unbekannte Registry-, Script- oder Datendatei ist nicht automatisch harmlos. Selbst gewöhnliche README-, Website- und Entwicklungsänderungen verlangen damit einen GitHub-Owner-Kommentar, der PR-Nummer, exakten 40-Zeichen-Head-SHA und die *vollständigen* Scopes bindet.

Ein solcher Kommentar ist eine GitHub-Kontobindung, keine kryptografische Attestierung des menschlichen Eigentümers und keine wissenschaftliche Evidenz. Nach jeder Änderung des PR-Heads muss die Entscheidung erneuert werden. Nach Erstellung eines Kommentars wäre ein neues `labeled`- oder `ready_for_review`-Ereignis notwendig, weil der bloße Kommentar die aktuelle `pull_request_target`-Prüfung nicht erneut startet.

**Operative Folge:** sehr hoher Review- und Wartungsaufwand. Kein allgemeines Chat-`Go` kann diese konkrete Governance-Policy-Erweiterung oder ihre Installation ratifizieren. Erst nach ausdrücklicher Entscheidung ist sinnvoll zu prüfen, ob eine überprüfte Ausnahmeliste für unverfängliche Alltagsänderungen sinnvoller wäre.

## C. Kontrollierte Installation — *nur* nach gesondertem Eigentümerentscheid

### Phase 0 — Jetzt

1. PR #263 und PR #264 Draft und ungemergt lassen. Keine Änderungen an `registry/`, `project-manifest.json`, öffentlichen Seiten oder am aktiven Ruleset.
2. Einen **externen oder unabhängig agierenden menschlichen Security-Reviewer** mit Zugang zum Diff von PR #264 für Code-, Policy- und Event-Review hinzuziehen, soweit verfügbar.
3. Die Workflow-Identität `trusted-release-gate`, GitHub-API-Leserechte, Statuscheck-SHA-Zuordnung, Post-Green-Kommentarrückzug und den All-PR-Reviewzwang als offene High-Risk-Fragen behandeln.
4. Keine tatsächliche Installation aus `RC15` oder aus einem einfachen `Go` ableiten.

### Phase 1 — Eigentümerentscheidung über den *Kontrollmechanismus*

Der Repository-Inhaber entscheidet **explizit und begrenzt** über zwei getrennte Gegenstände: (a) Akzeptanz der All-PR-Acknowledgment-Regel; (b) Erlaubnis zur rein nichtoperativen Installation der in PR #264 vorliegenden Workflow-/Guard-Version. Eine solche Genehmigung wäre **keine** Freigabe von PR #263 und **keine** physikalische oder wissenschaftliche Statusänderung.

Der Inhaber kann stattdessen »Nicht installieren; zunächst Routine-Ausnahmen und technische Freigabefehler überarbeiten« entscheiden. Bis zu dieser Wahl: `HOLD`.

### Phase 2 — Erst nach Freigabe: isolierter Merge und Positivprobe

1. Kontrolle, dass PR #264 nur die überprüften Governance-, Tool-, Test-, Workflow- und Draft-Auditartefakte enthält.
2. Den finalen PR-Head erneut auf gegenstandsbezogene Freigabe und unabhängige technische Reviews prüfen. Bei neuem Commit ist die ältere Freigabe nicht automatisch übertragbar.
3. Nur nach ausdrücklicher Installationsfreigabe PR #264 isoliert nach `main` übernehmen; **nicht** zeitgleich den Forschungsstand ändern.
4. Mit einem harmlosen Probe-PR einen echten **vom Basisbranch** geladenen `pull_request_target`-Lauf auslösen. Verifizieren, dass `trusted-release-gate` im GitHub-PR-Merge-Bereich auftaucht, welches GitHub-App-/Workflow-/Commitobjekt ihn erzeugt und ob seine Source/Context-Zuordnung eindeutig ist. Diesen Nachweis mit Run-ID, Check-Run-ID, Check-Head-SHA und PR-Head-SHA festhalten.
5. Falls die Zuordnung nicht eindeutig oder nicht der von GitHub für Required Checks verwendete Commit ist: **HOLD**, keine Ruleset-Aktivierung unter der Behauptung einer vorhandenen Schutzwirkung.

### Phase 3 — GitHub-Regelkonfiguration durch den Inhaber

Im Repository: `Settings → Rules → Rulesets → UniverseLab-main-Basisschutz` (`24417933`).

1. Bestehenden Lösch- und Force-Push-Schutz beibehalten.
2. `Require a pull request before merging` ergänzen.
3. `Require status checks to pass` ergänzen; `trusted-release-gate` nur **nach echtem beobachtetem Check-Run** aus dem Live-Selector wählen, Quelle **GitHub Actions**, streng `Require branches to be up to date before merging`. Die App-ID 15368 ist für den bisherigen Kandidaten-Selbsttest bestätigt; ihre Anwendung auf den Trusted-Check ist später separat zu bestätigen.
4. Zusätzliche stets laufende Jobs (`validate-file-names`, `platform-governance`) nur mit tatsächlich beobachteten eindeutigen Statuskontexten aufnehmen; pfadgefilterte Tests nicht blind global verpflichtend setzen.
5. Approving-Reviews nur dann verpflichtend konfigurieren, wenn unabhängige Reviewer tatsächlich verfügbar sind.
6. Bypass-Actors und andere Ausnahmen gesondert prüfen und nicht aus Effizienzgründen stillschweigend aktivieren.

GitHub UI: https://github.com/stefanhasselm74314-byte/UniverseLab/rules/24417933

### Phase 4 — Negative Merge-Tests und echtes Betriebsprotokoll

- **Negativer Test A:** sensitiver Test-PR ohne Owner-Acknowledgment → Guard scheitert, GitHub-Merge-UI muss *nach Aktivierung der Rules* das Zusammenführen verweigern.
- **Negativer Test B:** Owner-Kommentar für alten statt aktuellen Head-SHA → nicht akzeptieren.
- **Negativer Test C:** falscher wissenschaftlicher Status / inkonsistenter Checkpoint-Alias im simulierten Zustandsrelease → Guard scheitert, Merge muss blockiert bleiben.
- **Negativer Test D:** doppelt benannter GitHub-Actions-Check `trusted-release-gate` aus einem anderen Test-Workflow → Jobzuordnung und erforderliches Check-Verhalten dokumentieren; *keinen* unbemerkten Status-Ersatz akzeptieren.
- **Negativer Test E:** GitHub-Owner-Kommentar nach einer grünen Prüfung entfernen, bearbeiten oder überarbeiten → **wie reagiert die native Merge-Policy tatsächlich?** Bis zu einem wirksamen Nachweis ist Post-Green-Widerruf als verbleibendes High-Risk-Problem zu behandeln. In der Zwischenzeit **kein Auto-Merge**, vor dem manuellen Merge Owner-/Head-/Ruleset-Bindung nochmals prüfen.
- **Negativer Test F:** Änderung von `main` oder Head vor Merge → Pflichtchecks müssen den neuen Git-Zustand erkennen und die Freigabe bis zur neuen Prüfung blockieren.

Jedes Ergebnis als echtes GitHub-Ereignis samt Logs, Run-ID, Check-Run-ID und beobachteter Merge-Blockade dokumentieren. Nur Unit-Test-Mocks oder ein grüner Kandidaten-PR reichen nicht.

## D. Betrieb und Recovery

**Bei unbekannten GitHub-API-Daten / 403 / Rate Limit:** nicht raten; `HOLD`, Datenzugriff und Berechtigungen prüfen, denselben Head erneut testen.

**Bei fehlendem Required Check:** nicht einen ähnlich klingenden Workflow wählen; echten Base-Trusted-Run auslösen, GitHub-Kontext prüfen, nichts mergen.

**Bei Duplicate Check-Namen:** zuerst eine eindeutige, von GitHub bestätigte Check-Identität herstellen. Ein weiterer grüner Job mit gleichem Namen ist kein Ersatz.

**Bei Owner-Freigabewiderruf:** Guard- und GitHub-UI-Status erneut überprüfen. Ein bereits grüner Check bleibt möglicherweise grün; kein manueller Merge ohne aktuelle Entscheidung. Der gegenwärtige Kandidat garantiert **nicht** automatischen Widerruf des alten Status.

**Bei Science- oder Governance-Änderung:** separate fachliche Review und gesonderte Ratifikation, auch wenn die Python-Tests sämtlich grün sind. Technische CI ist weder eine Herleitung aus 6D noch eine empirische Identifikation.

**Bei Inkompatibilität oder Fehlkonfiguration nach Installation:** keine automatische Abschaltung aller Schutzregeln. Separat autorisierten Korrektur-PR erstellen; Schutzregeln nur mit ausdrücklicher Eigentümerentscheidung ändern. Notfallbearbeitung erfordert dokumentierten Abweichungs- und Reparaturprozess.

## E. Momentanes Freigabeurteil

```text
RC15_INSTALLATION_READINESS = NOT_READY
CANDIDATE_MOCK_QA = PASS_SCOPED
GITHUB_ACTIONS_APP_ID_15368 = VERIFIED_FOR_CANDIDATE_ONLY
TRUSTED_RELEASE_CHECK_ON_PR_HEAD = NOT_OBSERVED
TRUSTED_GATE_ON_MAIN = NOT_INSTALLED
REQUIRED_CHECK_ENFORCEMENT = ABSENT
POST_GREEN_OWNER_REVOKE_WINDOW = OPEN
CHECK_CONTEXT_UNIQUENESS = NOT_VERIFIED
OWNER_ALL_PR_POLICY_DECISION = NOT_RECORDED
INDEPENDENT_HUMAN_SECURITY_REVIEW = NOT_PERFORMED
PR263 = DRAFT_UNMERGED
PR264 = DRAFT_UNMERGED
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
