# UniverseLab — RC-VALIDATION-16: Widerrufssichere Freigabestrategie und Routinebetrieb

**Stand:** 2026-11-03  
**Status:** `DRAFT — POLICY DECISION REQUIRED — NO INSTALLATION`  
**Betroffener Entwurf:** Draft-PR #264, ohne Änderung an `main` oder PR #263  
**Nachweismatrix:** `drafts/2026-11-03_UniverseLab_RC16_AuthorizationAlternatives_v1.0_DRAFT.json`  
**Nicht installierter Simulator:** `tools/2026-11-03_UniverseLab_RC16_AuthorizationModel_v1.0.py`

## 1. Kernresultat — formaler Gegenfall zum bisherigen Kommentar-Gate

Der bisherige Kandidat liest einen authentifizierten GitHub-Issue-Kommentar zu einem konkreten PR, Head-SHA und Scope und meldet nach erfolgreicher CI `SUCCESS`. Diese Einmalprüfung hat **keine garantierte Dauerhaftigkeit**:

- `t₀`: Passender Eigentümerkommentar existiert.
- `t₁`: Release-Guard bestätigt ihn, GitHub-Check wird grün.
- `t₂`: Kommentar wird bearbeitet oder entfernt, ohne den PR-Head zu ändern.
- `t₃`: Der bisherige grüne Check kann weiter zum selben Commit sichtbar bleiben; ein neues `pull_request_target`-Ereignis ist **nicht garantiert**.

Damit wird die benötigte Sicherheitsinvariante

`MERGE_ZULÄSSIG ⇒ AKTUELLE_GÜLTIGE_EIGENTÜMERFREIGABE`

durch das Kommentar-Gate **nicht nachgewiesen**. Noch mehr Negativtests bei der *Durchführung* des Checks beheben diese zeitliche Lücke nicht. Auch ein vor PASS ausgeführtes erneutes Lesen des Kommentars verhindert einen Widerruf **nach** PASS nicht.

**Entscheidung für RC16: Das Kommentar-Gate darf nicht als gleichwertig widerrufssichere Merge-Autorisierung gelten.** Dieser Befund wird dokumentiert; der bestehende RC13-Guard wird *noch nicht* auf eine der neuen Betriebsvarianten umgestellt.

## 2. Die sachlich unterschiedlichen Alternativen

| Modus | Alltäglicher, rein nichtoperativer Draft | Wissenschaftlicher, öffentlicher oder sicherheitsrelevanter PR | Zwingende Voraussetzung |
|---|---|---|---|
| **RC16-A — Native unabhängige GitHub-Review** | Technische Required Checks, kein individueller Kommentar pro neuem Draft | Native verpflichtende Genehmigung eines **anderen berechtigten Reviewers**, veraltete Approvals zurückweisen, Required CI | Wirklich vorhandener unabhängiger Reviewer und aktiviertes, erprobtes Ruleset |
| **RC16-B — Ein-Personen-HOLD** | Technische Required Checks für exakt abgegrenzte nichtkanonische Draft-JSONs | Standardmäßig **HOLD** bis gesondert autorisierter, technisch verifizierter Ausnahme-/Releaseprozess | Keine implizite Selbstgenehmigung; Eigentümer wählt ausdrücklich die Betriebsregel |
| **RC16-C — Bestehender Kommentaransatz** | Hoher Aufwand mit Kommentar bei jeder Änderung | Einmalige Kommentarprüfung vor grünem CI | **Nicht als sicherer Ersatz empfohlen**; Post-Green-Widerruf offen |

Der Vergleich entscheidet **nicht** stellvertretend für den Eigentümer. Varianten A und B sind derzeit ebenfalls nicht produktiv installierbar.

### Enger Routine-Fall für einen späteren Ein-Personen-Betrieb

Ein optionaler, **noch nicht genehmigter** Ausnahmevertrag erlaubt nur das *Hinzufügen* von `drafts/YYYY-MM-DD_UniverseLab_..._DRAFT.json` und ausschließlich dann, wenn der maschinenlesbare Status `DRAFT` trägt, `physical_gate_effect=NONE`, `physical_evidence_effect=NONE` und keine Canon-/Solver-Promotion behauptet wird.

Nicht zulässig als Routinedraft: Änderungen existierender Dateien, Markdown/HTML/JS, GitHub-Workflows, Registry, Manifest, Alias, öffentliche Seiten, Bilder/Skripte oder gemischte PRs. Solche Änderungen bleiben REVIEW/HOLD. Alle Checks müssen weiterhin aus vertrauenswürdiger Basis stammen und *GitHub-nativ* Required Checks sein.

Ein grüner Routinedraft-Check besagt nur `NONCANONICAL TECHNICAL QA`, niemals `SCIENTIFIC VALIDITY`.

## 3. GitHub-native Merge-Policy statt Check-Erinnerung

GitHub-Rulesets können `Require a pull request before merging`, `Require status checks to pass`, nötigenfalls `Dismiss stale pull request approvals` und `Require approval of the most recent reviewable push` kombinieren. **Ein unabhängiger Reviewer** muss dabei tatsächlich verfügbar sein; die Selbstfreigabe eines alleinigen PR-Autors darf nicht stillschweigend als erfüllt gelten. Diese Regeln sind *plattformseitige* Merge-Voraussetzungen, nicht ein Kommentar, den ein Skript einmal liest.

Offizielle Grundlagen:
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets
- https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches

**[KONDITIONAL]** Nur bei aktivem Ruleset, eindeutig gebundenem erforderlichem Job, tatsächlich aktuellem Review und erfolgreichem Negativ-PR kann die GitHub-native Merge-Sicherung als implementiert bezeichnet werden. Ein Mock, eine API-Abfrage und eine grüne selbstgelieferte PR-CI sind dafür nicht ausreichend.

## 4. Neue RC16-Gefahr: GitHub-Actions-Ereignisrichtlinie

Die aktuelle GitHub-Dokumentation beschreibt für öffentliche Repositories eine standardmäßige `pull_request_target`-Sperre, die zunächst im **Evaluate-Modus** ausgegeben und am **2. Dezember 2026** für betroffene Repositories durchgesetzt werden soll. Ob UniverseLab eine konkret erlaubende Richtlinie hat, konnte über den verbundenen GitHub-Zugriff **nicht festgestellt** werden: Die separate Actions-Policy-Schnittstelle war dort nicht aufrufbar; nach GitHubs Dokumentation benötigt die REST-Policy-Verwaltung administrative Berechtigungen.

Weder "Richtlinie vorhanden" noch "Richtlinie fehlt" darf ohne belegte Repositorydaten behauptet werden.

**Konsequenz:** Ein später über `pull_request_target` laufender Pflichtcheck könnte nach GitHub-Policy-Änderung gar nicht gestartet werden. Er muss als **HOLD / MISSING REQUIRED CHECK** wirken, nicht als stillschweigend bestanden. Vor Installation die GitHub-Actions-Policies unter den Repository-Einstellungen persönlich prüfen; sicherere Alternativarchitektur auf `pull_request` mit **separat geschützter Policy-/Codebasis** erwägen. Dabei darf keine ungeprüfte PR-Version des Freigabeskripts den vertrauenswürdigen Status selbst berechnen.

Quellen:
- https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target
- https://docs.github.com/en/actions/concepts/about-actions-policies
- https://docs.github.com/en/rest/actions/policies

## 5. Reproduzierbarer Testumfang

Der separate RC16-**Modell**test zeigt, dass ein nachträglich gelöschter Kommentar keine vorzeitige Freigabe von `PUBLIC_SURFACE`, `CONTROL_PLANE` oder `STATE_RELEASE` auslösen kann, **wenn** die Autorisierung allein auf GitHub-nativer Reviewpflicht (RC16-A) oder einem dauerhaften Sensitiv-HOLD (RC16-B) beruht. Er prüft außerdem technische Required Checks, bekannte und unbekannte Pfade, Misch-PRs und die enge nichtoperative Draft-Ausnahme.

Das ist lediglich eine **formale Testmodellierung mit künstlichen Eingaben**, kein Beleg, dass das konkrete GitHub-Repository diese Regeln erzwingt. Das vorhandene RC13/RC14-Produktionskandidaten-Skript bleibt daher bis zu einer gesonderten Policyentscheidung bewusst unverändert und weiterhin **NICHT INSTALLATIONSREIF**.

## 6. Entscheidungsvorlage und zusätzliche Blocker

Vor einer tatsächlichen GitHub-Installation sind separat zu entscheiden:

1. **RC16-A oder RC16-B?** Existiert ein anderer berechtigter Reviewer, der dauerhaft mitprüfen soll, oder soll ein strikter Ein-Personen-HOLD gelten?
2. Ist die vorgeschlagene **Routine-Ausnahme für ausschließlich neue nichtkanonische Draft-JSONs** im Projekt zulässig?
3. Soll `pull_request_target` überhaupt verwendet werden? Dafür die **Actions Event Policy** am konkreten Repository prüfen. Keine stillschweigende Sicherheitsausnahme.
4. Welcher verbindliche GitHub-Required-Check-Kontext ist auf welchem SHA tatsächlich wirksam? Doppelbenannte Checks und mögliche `skipped`/`neutral`-Bewertungen sind mit einer Canary-Prüfung zu klären.
5. Wie kann ein abgebrochener/gesperrter Security-PR im Ein-Personen-Betrieb wieder kontrolliert geöffnet werden, **ohne** pauschalen Admin-Bypass oder ungesicherte Direkt-Merges?
6. Unabhängige Code- und Security-Reviews vor Installation; Eigentümerratifikation nur für den exakt angegebenen Gegenstand.
7. Ein gesonderter, technisch validierter achtteiliger Statusrelease **darf** keine physikalische Theorie- oder Evidenzfreigabe bewirken.

```text
RC16_COMMENT_BASED_REVOKABILITY = FALSIFIED_AS_DURABLE_AUTHORIZATION
RC16_MODEL_ALTERNATIVES = PREPARED_NOT_SELECTED
RC16_GITHUB_ACTIONS_EVENT_POLICY = UNKNOWN_REQUIRES_OWNER_VERIFICATION
RC16_NATIVE_GITHUB_REQUIRED_REVIEWS = NOT_CONFIGURED
RC16_ROUTINE_DRAFT_EXEMPTION = NOT_RATIFIED
RC16_EXTERNAL_SECURITY_REVIEW = NOT_PERFORMED
PR263 = DRAFT_UNMERGED
PR264 = DRAFT_UNMERGED
GUARD_INSTALLED_ON_MAIN = NO
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
