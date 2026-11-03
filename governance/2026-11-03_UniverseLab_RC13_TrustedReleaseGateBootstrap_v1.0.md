# UniverseLab — RC-VALIDATION-13: Vertrauenswürdiger Release-Gate-Bootstrap v1.0

Datum: 2026-11-03  
Status: **DRAFT / INSTALLATION CANDIDATE / NO CANONICAL AUTHORITY**  
Basis für Bootstrap: `main@51bcc8fccb092c104ac0fca5fc98a5b996dcb914`.  
Release-Status: **HOLD**, kein Solver, keine wissenschaftliche Gate-Promotion.

## 1. Konkrete Vertrauensgrenze

Der neue Workflow `.github/workflows/2026-11-03_UniverseLab_RC13_TrustedReleaseGate_v1.0.yml` verwendet `pull_request_target`, **keinen Checkout oder Import des untrusted PR-Heads**. Nach einer gesondert autorisierten Aufnahme in `main` würde er den dort geprüften Guard `tools/2026-11-03_UniverseLab_RC13_TrustedReleaseGuard_v1.0.py` laden.

- `permissions: contents: read, pull-requests: read, issues: read`.
- Ausschließlich GitHub-REST-GET; kein externer Netzhost, keine Head-Code-Ausführung, keine Schreibrechte.
- Kein Workflow-Pfadfilter, keine Job-`if`-Auslassung: der Check `trusted-release-gate` muss bei jedem relevanten Pull-Request-Ereignis erscheinen.
- Bei API-Ausfall, Race zwischen PR-Head und Event, Drift von `main` oder fehlendem Eigentümerentscheid: **FAIL CLOSED**.
- Die Prüfung ist bis zur tatsächlichen Installation auf `main` **nicht unabhängig durchsetzbar**. Die `pull_request`-QA dieses PR ist ausdrücklich nur ein Kandidaten-Selbsttest.

## 2. Risikoklassen

**Andere PR-Dateien (konservativer RC14-Entwurf):** Kein beliebiger Pfad darf unkontrolliert als harmlos gelten. Alle Nicht-Release-Dateien werden mindestens als `PUBLIC_SURFACE` (insbesondere HTML/JS/Markdown/Assets) oder `CONTROL_PLANE` (einschließlich unbekannter Registry-/Daten-/Quellpfade) eingestuft. Damit ist **jeder PR vorläufig owner-acknowledgment-pflichtig**; das ist eine potenziell erhebliche Einschränkung für Routinearbeit. Eine spätere Ausnahmeliste erfordert eigene ausdrückliche Policy-Entscheidung und Tests.

**Control Plane / Public Surface:** Änderungen an Workflows, Skripten, Tests, Registry-Daten und sonstigen Quellen erfordern `CONTROL_PLANE`; alle öffentlichen HTML-, JavaScript-, Markdown- und Assetänderungen erfordern `PUBLIC_SURFACE`. Beides verlangt einen **expliziten GitHub-Owner-Kommentar**, der PR, den exakten Head-SHA und sämtliche betroffenen Scopes fest bindet. Kein allgemeines `Go`. Diese Prüfung bestätigt nur technische Kontrollhoheit, nicht die physikalische Wahrheit veröffentlichter Aussagen.

**State Release:** Änderungen am aktiven Manifest, Checkpoint-Alias, State/Checkpoint/SiteState in `registry/`, den DE/EN-Forschungsstatusseiten oder der GlobalShell erfordern:

1. PR nicht Draft; aktuelle Live-API-Bindung von `main`, PR-Base und PR-Head.
2. **Expliziter** owner-authentifizierter GitHub-Kommentar mit PR-Nummer, exaktem Head-SHA und gesamtem Scope.
3. Tatsächlich aktives `main`-Ruleset mit `pull_request` **und** `required_status_checks` einschließlich `trusted-release-gate`.
4. Ausschließlich acht zusammenhängende Release-Dateien im PR: neuer datierter CurrentState, Checkpoint, SiteState und Änderungen am aktiven Manifest, Checkpoint-Alias, DE/EN-Statusseiten und der GlobalShell.
5. Byteidentischer Checkpoint-Alias, kanonisch konsistente Status-/Manifest-Pointer, valide **echte** und zeitlich konsistente Releasezeitstempel, verifizierter Baseline-Git-Tree.
6. Keine physikalische Gate-/Evidenzänderung: `FM-G0=OPEN`, `K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`, kein behaupteter etablierter Hintergrund oder Response-Rank.
7. Gesamtscan des getrackten HTML-/JS-Baums des PR-Heads auf alle bisherigen aktiven Snapshot-Verweise, ohne PR-Code auszuführen. Bei unvollständigem Scan: **HOLD**.
8. RC14-Negativprüfung: nicht-poin­termäßige Änderungen an Wissenschafts-/Claim-/Evidenzfeldern, G11-Checkpoint-Verlauf, HTML-Fließtext und GlobalShell-JavaScript-Code sind auch bei unveränderten K1-D/K1-E-Werten **BLOCKIERT**. Die öffentliche Migration darf außer konkreten Pfaden, den bekannten Versionsbezeichnungen und der GlobalShell-Versionsnummer keine stillen Publikationsänderungen enthalten.

Dieser Guard testet technische Invarianten. Selbst ein vollständig bestandener Release-Test ist **kein unabhängiger mathematischer Beweis, keine empirische Bestätigung und keine Ghostfreiheitsprüfung**.

## 3. Wie der GitHub-Eigentümer später ausdrücklich ratifiziert

Der Guard akzeptiert keinen Freitext wie `Go`. Für einen sensiblen PR ist auf **dessen GitHub-PR-Seite** ein eigener Kommentar des Repo-Owners nötig:

```text
UniverseLab RC13 RELEASE-AUTHORIZATION
PR: #<EXAKTE_PR_NUMMER>
HEAD: <EXAKTER_40_ZEICHEN_SHA>
SCOPE: <CONTROL_PLANE,PUBLIC_SURFACE,STATE_RELEASE — ALLE BETROFFENEN SCOPES KOMMAGETRENNT UND ALPHABETISCH>
DECISION: APPROVE THIS EXACT HEAD
```

Die tatsächlichen konkreten Werte werden erst nach der vollständigen Quellenprüfung und **ausdrücklichen Entscheidung des Owners** eingesetzt. Wird der PR-Head geändert, verfällt die SHA-Bindung; der Nutzer muss die Entscheidung gegen den neuen Head neu treffen. Ein nachträglich hinzugefügter Owner-Kommentar triggert selbst **keinen** `pull_request_target`-Check; ein neues PR-Label (`labeled`), ein `ready_for_review`-Ereignis oder eine kontrollierte Wiederholung des Checks ist für den erneuten Lauf erforderlich. Der GitHub-Required-Check-Kontext ist anschließend tatsächlich in der PR-Oberfläche zu kontrollieren. Dies ist GitHub-authentifizierte Kontozuordnung, **keine kryptographische Personen-/Geräte-Attestierung**. Ein grünes Release-Gate ersetzt darüber hinaus keinen unabhängigen Code-/Wissenschaftsreview.

Ein Owner-Kommentar wird **nicht** durch eine Antwort `Go` in einem Chat erstellt und ist ausdrücklich nicht Gegenstand dieses RC13-Bootstraps.

## 4. Vertrauenswürdige Installationsreihenfolge — ausdrücklich noch nicht freigegeben

1. Diesen **isolierten** Kandidaten-PR in Draft belassen. Seine unabhängigen Python-Fixtures und GitHub-CI prüfen nur die technische Ausführbarkeit.
2. Dokumentation, Code, GitHub-Sicherheitsmodell und Negativtests in einem **separaten Review** überprüfen.
3. Vor dem Merge ausdrückliche sachbezogene Owner-Freigabe nur für die nichtoperative **Installation des Guards** einholen; keine implizite Eigentümerratifikation.
4. Erst danach diesen kleinen Kontrollplane-PR (ohne Forschungsdaten / ohne aktive Snapshot-Änderung) in `main` integrieren.
5. Einen gewöhnlichen **Probe-PR** erstellen. Nachweisen, dass der aus `main` stammende `pull_request_target`-Job wirklich auf dem PR-Head in der Merge-UI erscheint, und den exakten Jobkontext `trusted-release-gate` im GitHub-Selector verifizieren. Nicht aufgrund des Workflow-Namens raten.
6. Unter `Settings → Rules → Rulesets → UniverseLab-main-Basisschutz` (`24417933`) zusätzlich `Require a pull request before merging` und `Require status checks to pass` aktivieren; `trusted-release-gate` als Required Check mit **strict / Require branches to be up to date** und Quelle **GitHub Actions (integration_id 15368)** konfigurieren. Ungebundene Quelle (`any source`), falscher App-Kontext, fehlende Strictness oder Bypass-Actors bleiben im Guard gesperrt. Außerdem die vorhandenen stets laufenden `validate-file-names` und `platform-governance` nach Live-Prüfung erwägen.
7. Einen kontrollierten **Negativ-PR** mit kritischem Pfad, fehlender Owner-Autorisierung oder fehlerhaftem Snapshot testen. Nachweis der tatsächlichen GitHub-UI-Mergeblockade dokumentieren.
8. Regeln und tatsächliche Herkunft der Required Checks anschließend nochmals lesend abrufen; nur dann `PROTECTED_MAIN_REQUIRED_CHECKS_VERIFIED` feststellen.

**ACHTUNG:** Der vor dem Bootstrap beobachtete Basisschutz enthält ausschließlich `deletion` und `non_fast_forward`, keine erzwungenen PR-/Statuscheck-Regeln. Die App konnte den alten Branch-Protection-Detailendpunkt nicht auslesen (HTTP 403); diese Grenze bleibt offen.

## 5. Bekannte Restrisiken

- Die Kontrollplane ist erst *nach* Merge auf `main` vertrauenswürdige Quellbasis. Der PR-Kandidat allein ist nicht unabhängig.
- Single-Owner-GitHub-Kommentar ist technisch authentifiziert, aber kein separater unabhängiger Reviewer; keine globale kryptographische Autorisierung.
- Der vollständige HTML-/JS-Scan kann bei Repositorywachstum an begrenzten API-/Dateigrößen scheitern und blockiert dann konservativ.
- GitHub-Branchregeln werden **nicht** durch eine Workflow-Datei erzeugt. Ohne Required-Check-Ruleset kann ein grüner Job weiterhin umgangen werden.
- Ein GitHub-konfigurierter Schutz kann durch Eigentümer/Admin geändert werden. Er ist keine unaufhebbare physikalische oder kryptographische Schranke.
- Die Release-Gate-Validierung deckt technische Zustands-/Pointer-Konsistenz ab, nicht die wissenschaftliche Bedeutung der Inhalte.
- Bei aktiviertem Merge-Queue-Verfahren sind besondere `merge_group`-Prüfpfade nötig; dieser v1-Kandidat beansprucht keine Merge-Queue-Unterstützung. Kein Merge-Queue-Ruleset aktivieren, bevor dieser Pfad angepasst und auditiert ist.
- Ein fehlender oder von GitHub nicht zuordenbarer Statuscheck muss als **Blocker** gelten, nicht als grüner Ersatzcheck.

## 6. Aktuelle Entscheidung

```text
RC13_CANDIDATE = PREPARED_FOR_REVIEW
PR13_BOOTSTRAP_MERGE = NOT_AUTHORIZED
PR263_STATUS = DRAFT_UNMERGED
ACTIVE_MAIN_POLICY_CHANGES = NONE
OWNER_SCOPED_RELEASE_RATIFICATION = NOT_REQUESTED
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
