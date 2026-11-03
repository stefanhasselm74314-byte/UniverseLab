# UniverseLab — RC-VALIDATION-14: Adversarialer Sicherheits- und Bypass-Audit v1.0

Datum: 2026-11-03  
Ziel: Separater Draft-PR #264, **keine** Änderung an `main` oder PR #263.  
Scope: kontrollierte Inspektion und Gegenproben gegen das vorgeschlagene `pull_request_target`-Release-Gate.  
**Befundklasse:** `TECHNICAL_ADVERSARIAL_REVIEW_WITH_RELEASE_BLOCKERS`  
**Keine Behauptung unabhängiger externer Prüfung:** Die Review-Analyse und die Tests wurden im selben AI-unterstützten Arbeitsgang durchgeführt; eine externe menschliche Sicherheitsfreigabe steht aus.

## 1. Angreifermodell und Vertrauensgrenzen

Ein Angreifer darf den Pull-Request-Head, dessen Dateien und Inhalte, unsichere Dateinamen, PR-Metadaten und GitHub-Ereignisse unter den ihm zustehenden Rechten beeinflussen. Er darf **nicht** voraussetzen, im Namen des Repository-Inhabers einen über die GitHub-API authentifizierten Kommentar verfassen oder die geschützte `main`-Basis verändern zu können. Eine kompromittierte Owner-Identität oder GitHub-Administration liegen außerhalb der zugesicherten Schutzdomäne.

Der spätere vertrauenswürdige Guard läuft nur in der auf `main` installierten Version; er checkt niemals PR-Code aus. Mit `contents: read`, `pull-requests: read`, `issues: read` wird ausschließlich der GitHub-REST-API-Datenpfad verwendet. Der bisherige Kandidaten-Selbsttest ist dagegen selbst Bestandteil des zu prüfenden PRs.

## 2. Reproduzierte Bypass-Risiken und Gegenmaßnahmen

| ID | Kritikalität | Vorheriger Angriffsweg | RC14-Gegenmaßnahme | Status |
|---|---|---|---|---|
| S14-01 | HOCH | Änderungen an `index.html`, `navigator.html`, README oder public assets waren nicht als sensitive Pfade klassifiziert. | `PUBLIC_SURFACE` zwingt exakte Eigentümer-Acknowledgment-Bindung. | IM DRAFT IMPLEMENTIERT |
| S14-02 | HOCH | Unbekannte Dateien unter `registry/` oder beliebige Quell-/Datenpfade konnten als normales PR ohne eigene Ownerprüfung durchlaufen. | Fail-closed Default `CONTROL_PLANE`; kein leerer Scope mehr erlaubt. | IM DRAFT IMPLEMENTIERT |
| S14-03 | HOCH | Trotz `K1-D=NOT_RELEASED` hätte ein PR z. B. `scientific_open_state.full_ghost_freedom=PROVEN` setzen können. | Vollständiger Vergleich erklärter Wissenschafts-/Claim- und Statusfelder gegen Baseline sowie Top-Level-Differenz-Allowlist. | IM DRAFT IMPLEMENTIERT |
| S14-04 | HOCH | In HTML-Seiten waren zusätzliche Behauptungen und in GlobalShell zusätzliche JavaScript-Befehle möglich, sofern die Pointers stimmten. | Exakter Vergleich mit durch zugelassene Pointer-/Version-Ersetzungen transformierter Baseline; keine sonstigen Text-/JS-Änderungen. | IM DRAFT IMPLEMENTIERT |
| S14-05 | HOCH | Checkpoint `active_block`, `confirmed_defects` und `entry_points` konnten das wissenschaftliche Evidenzbild verfälschen. | Nur festgelegter G11-Governance-Übergang und vereinbarte Eintrags-Pointer zugelassen; wissenschaftliche Gaps/Claim-Felder bleiben fest. | IM DRAFT IMPLEMENTIERT |
| S14-06 | HOCH | Der im Lauf zunächst gültige Owner-Kommentar oder Required-Check-Ruleset konnte vor der finalen Entscheidung zurückgezogen werden. | Erneute Lesekontrolle beider Artefakte unmittelbar vor PASS; fehlende Bindung führt zu FAIL. | IM DRAFT IMPLEMENTIERT |
| S14-07 | HOCH | Ruleset mit User-Bypass, Main-Exclusion, falscher GitHub-App oder nicht-striktem Required Check wäre als geschützt fehlinterpretiert worden. | Validiert `current_user_can_bypass=never`, keine Bypass-Actors, Main-Include ohne Exclude, strikt an GitHub Actions gebundener Check. | IM DRAFT IMPLEMENTIERT |
| S14-08 | MITTEL | Nach einem neu geposteten Owner-Kommentar wurde nicht automatisch eine erneute PR-Prüfung ausgelöst. | `labeled`-Ereignis für explizites Recheck; auch Ready-For-Review/Edited bleibt möglich. | IM DRAFT IMPLEMENTIERT |

### Explizite zusätzliche Negativfälle

Mocked-GitHub-API-Fälle testen veränderte Head-/Base-SHAs, nicht passende Owner-Entscheidung, deaktivierte/falsch konfigurierte Rulesets, Gate-Promotion, manipulierte wissenschaftliche/Claim-Ledger, gefälschte Checkpoint-Verläufe, zusätzliche HTML-/JS-Inhalte, vorzeitige Zeitstempel, unvollständige Alias-/Manifest-/Site-Verweise und Änderungen während einer laufenden Prüfung.

Der positive achtteilige Release-Fixture-Test belegt ausschließlich, dass ein eng begrenzter, konstruiert konsistenter Kontrollfall vom Kandidaten angenommen wird. Er belegt nicht die Sicherheit eines zukünftigen konkreten Release-Bundles.

## 3. Verbleibende, nicht aufgelöste Risiken und Freigabeblocker

1. **Keine installierte Trusted Base:** Die `pull_request_target`-Workflow-Datei und das Sicherheitsprogramm existieren nur in PR #264 und nicht im geschützten `main`. Die CI des Kandidaten ist keine unabhängige Installations- oder Release-Autorität.
2. **Keine verpflichtenden Required Checks:** Das zuletzt ausgelesene aktive Ruleset `UniverseLab-main-Basisschutz` (#24417933) enthält `deletion` und `non_fast_forward`, aber weder `pull_request` noch `required_status_checks`. Alte Branch-Protection-Detailabfragen ergaben im Connector HTTP 403. Eine tatsächliche Merge-Blockade ist daher nicht bewiesen.
3. **GitHub-Statuscheck-Identität:** `trusted-release-gate`, `integration_id=15368` und die strikte Up-to-date-Regel müssen nach Installation in GitHubs Required-Check-Auswahl und an einem realen Negativ-PR unabhängig bestätigt werden. Die Regeln im Mock ersetzen den Nachweis nicht. `pull_request_target` zählt laut GitHub-Dokumentation zu den für PR-Required-Checks geeigneten Ereignissen; die tatsächliche Bindung im spezifischen Repository ist dennoch offen.
4. **Owner-Acknowledgment ist keine unabhängige wissenschaftliche Validierung.** Das GitHub-Konto verbürgt nicht die physikalische Richtigkeit einer Behauptung. Verbindliche Owner-Ratifikation für wissenschaftliche Statusänderungen bleibt separat und gegenstandsbezogen.
5. **Strenger Arbeitsmodus:** Der RC14-Klassifikator ordnet absichtlich **alle** PR-Dateien einer genehmigungspflichtigen Risikoklasse zu. Das erschwert Routine-PRs erheblich. Eine Ausnahmeliste darf nicht ohne eigene Sicherheitsreview geschaffen werden; der Inhaber muss die operative Tragweite vor Installation ausdrücklich akzeptieren.
6. **Zeit- und Versionensemantik:** Der Kandidat ist auf die konkrete September→November-Zustandsmigration zugeschnitten; ein späterer Nachfolger erfordert erneute Kontrolle des zulässigen Versionierungs- und Zeitmodells. Eine sachliche Unbedenklichkeit des gesamten 298-Commit- und 39-Quellen-Korpus ist nicht nachgewiesen.
7. **Admin-/Plattform-Vertrauen:** Ein Repository-Admin kann ein Ruleset künftig verändern oder den zu prüfenden Guard austauschen. Das Tool kann keinen irreversiblen Root of Trust erzeugen.
8. **Keine umfassende unabhängige Sicherheitsprüfung:** Es wurden keine externen Pentests, kein alternativer unabhängiger Reviewer und keine Live-Attestierung des späteren Release-PRs durchgeführt.
9. **Kein laufender physikalischer Solver / keine Evidenz:** `FM-G0=OPEN`, `K1-D=NOT_RELEASED`, `K1-E=NOT_ADMISSIBLE`, `PHYSICAL_BACKGROUND=NOT_ESTABLISHED`, `PHYSICAL_RESPONSE_RANK=NOT_EXECUTED` bleiben unangetastet.
10. **Merge Queue nicht unterstützt:** Kein erforderliches `merge_group`-Ereignis und kein Nachweis bei aktivierter Merge Queue; ein solches Ruleset darf deshalb nicht ohne spätere Anpassung als kompatibel behauptet werden.

## 4. Nachweisansprüche und Grenzziehung

- **[NUMERISCH/TECHNISCH BESTÄTIGT]** Nach erfolgreichem Kandidaten-CI-Lauf: reproduzierbare Python-Unittests inklusive adversarialer Mock-Szenarien und Prüfung der No-Head-Checkout-Vertrauensgrenze.
- **[KONDITIONAL]** Für einen späteren PR gelten die Aussagen nur bei tatsächlich installierter Base-Version, read-only Token, wirksamer Ruleset-Required-Check-Pflicht und nachgewiesener Owner-Authentifizierung.
- **[OFFEN]** Effektive GitHub-Merge-Blockade, Umgehungsmöglichkeiten durch administrative Änderung, externe Security-Attestierung sowie zeitlich aktuelle Release-Metadaten.
- **[NICHT HERGELEITET]** Mathematische Konsistenz der vollständigen 6D-Theorie, Ghostfreiheit, empirische Signaturen, Forward-Map-Vollständigkeit und wissenschaftliche Evidenz.

## 5. Konsequenz

**RC14 ist eine zusätzliche adversariale Kandidatenprüfung, keine Installationsfreigabe.** PR #264 muss Draft bleiben; PR #263 bleibt davon unabhängig Draft. Weder Repository-Ruleset noch `main` dürfen aufgrund eines grünen Kandidaten-Selbsttests automatisch geändert werden.

```text
RC14_ADVERSARIAL_CANDIDATE_QA = RUN_RESULTS_REQUIRED
EXTERNAL_SECURITY_AUDIT = NOT_PERFORMED
TRUSTED_MAIN_GATE_INSTALLED = NO
REQUIRED_CHECK_ENFORCED = NO
OWNER_POLICY_ACCEPTANCE_FOR_ALL_PR_ACK = NOT_RECORDED
RELEASE_OWNER_RATIFICATION = NOT_REQUESTED
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```
