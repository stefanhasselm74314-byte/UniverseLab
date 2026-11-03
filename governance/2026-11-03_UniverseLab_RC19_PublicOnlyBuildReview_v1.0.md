# UniverseLab — RC-VALIDATION-19: Public-Only-Pages-Build (isolierter Kandidat)

**Datum:** 2026-11-03  
**Status:** `LOCAL_CANDIDATE_QA_PASS / INSTALLATION_NOT_AUTHORIZED / PRODUCTION_DEPLOY_UNCHANGED`  
**Architektur:** RC16-B — Ein-Personen-Betrieb, automatische technische QA, gesperrte kritische Freigaben.  
**Quellen:** verifizierter `main`-Commit `51bcc8fccb092c104ac0fca5fc98a5b996dcb914`, Tree `65f423f04bbb2f1462f120a6b31073644cdc28cc`; RC18-Publikationsaudit; produktiver Workflow `.github/workflows/deploy-pages.yml`.  
**Realisierung:** `tools/2026-11-03_UniverseLab_RC19_PublicOnlyBuild_v1.0.py`, explizites `governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json`, isolierte PR-QA und 27 Negativ-/Positivtests.

## 1. Befund und Entscheidung

**[BESTÄTIGT]** Der derzeitige `main`-Pages-Workflow lädt den Checkout über `actions/upload-pages-artifact@v4` mit `path: .` hoch. Dadurch ist die Auslieferungsgrenze an den gesamten nicht-versteckten Repository-Baum statt an einen geprüften Web-Build gebunden. RC18 belegte 1.157 getrackte Dateien sowie die prinzipielle Gefahr bei künftigem `drafts/`-Merge. Die genaue Anzahl der aktuell *tatsächlich ausgelieferten* Pages-Dateien wurde nicht durch einen Artefakt-Download verifiziert. Nach dokumentierter GitHub-Action-Konvention werden versteckte Dateien standardmäßig ausgeschlossen; die `.github`-Wurzel ist daher nicht mit einem nachgewiesenen Pages-Leak gleichzusetzen.

**[KONDITIONAL]** RC19 setzt dem eine isolierte exakte Pfad-Allowlist mit SHA-256-Bindung entgegen. Aus dem geprüften Main-Baum wurden **446 bestehende Pfade** aufgenommen; der Prototyp kopierte **4.932.132 Bytes** (ohne optionales Deployment-Metadatum) in ein neues, separates Verzeichnis. Die Auswahl ist ein vorläufiger, auf Main fixierter technischer Kompatibilitätsvorschlag, **keine redaktionelle Freigabe sämtlicher darin enthaltenen Forschungs- oder Registry-Daten**.

| Staging-Segment | Exakt aufgenommene Pfade |
|---|---:|
| Root (bestehende HTML-/JS-/CSS-/JSON-/MD-/CSV-/Text-Webdateien) | 146 |
| `assets/` | 28 |
| `registry/` (einschließlich `decision-log.jsonl`) | 269 |
| `schemas/` | 3 |
| **Summe** | **446** |

Gegenüber 1.157 Main-Git-Blobs bleiben 711 getrackte Dateien außerhalb der RC19-Stagingliste. Dies ist eine **Quellbaumauswahl**, kein gemessener Unterschied zwischen zwei realen Pages-Artefakten.

**Bewusst nicht enthalten:** neue Draft-Dateien, `.github/`, `governance/`, `science/`, `tests/`, `tools/`, `prompts/`, `recovery/`, `reproducibility/`, `requirements/`, Python-Programme und neue, bislang nicht ausdrücklich gelistete Web-/Registry-Dateien. Die genannten Verzeichnisse bleiben auf öffentlichen GitHub-Branches sichtbar; RC19 erzeugt **keine Vertraulichkeit** für das öffentliche Repository.

## 2. Durchgesetzte technische Eigenschaften des Kandidaten

1. **Exact path:** Kein Verzeichnis-Glob, kein `*`/`?`, keine Platzhalter, kein implizites Mitnehmen künftig ergänzter Dateien. Nur im Manifest einzeln aufgeführte Pfade dürfen ins Staging.
2. **Content pinning:** Jeder erlaubte Pfad hat einen SHA-256-Digest seines vorhandenen Main-Inhalts. Geänderte Dateien, geänderte Manifeste und neue Site-Versionen verlangen neue Prüfung; ein reines Schema-PASS reicht nicht.
3. **Deny envelope:** Verzeichnispräfixe wie `drafts`, `governance`, `science`, `.github`, `tools` und `tests` sind unabhängig vom Manifest blockiert. Verzeichnisausbruch, %-Kodierung, Windows-Backslashes, versteckte Pfade und ungeeignete Dateiendungen führen zu HOLD.
4. **Source safety:** Fehlende oder ausführbare Dateien und Symlinks im genehmigten Pfad führen zu HOLD. Kopierte Dateien werden erneut gehasht; das Zielverzeichnis muss vorher fehlen und wird nicht wiederverwendet.
5. **Linkprüfung:** Statische Literalverweise aus HTML-Attributen, CSS `url(...)` sowie einfachem `fetch(...)`/`importScripts(...)` werden geprüft. Bestehende lokale Zielpfade, die im Manifest fehlen, lösen HOLD aus.
6. **Kontrolliertes `deploy-meta.json`:** Kann nach bestehender Source-SHA-Attestierung optional als einziges dynamisches Deployment-Dokument hinzugefügt werden; Schema, Felder, SHA und `workflow_run_attempt=1` werden geprüft.
7. **Keine Release-Seiteneffekte:** Der PR-QA-Workflow hat ausschließlich `contents: read`; er lädt **kein** Pages-Artefakt hoch, ruft **kein** `deploy-pages` auf und editiert weder `main` noch Rulesets.

## 3. Erhaltene Website-Pfade / verbleibende Abhängigkeitslücken

**[LOKAL NUMERISCH BESTÄTIGT]** Der echte RC19-Build auf dem RC18-Head (ohne Änderungen an Main-Webdateien) hat folgende lokale Diagnose geliefert:

```text
RC19_CANDIDATE_BUILD_PASS_NOT_RELEASE
file_count                         = 446
staged_bytes                       = 4932132
existing_literal_links_excluded    = 0
missing_literal_link_targets       = 0
dynamic_runtime_link_closure       = NOT_PROVEN
pages_deployment_changed           = FALSE
```

**Wesentliche Begrenzung:** Die Linkprüfung erfasst nur statische Literalformen, nicht alle dynamisch konstruierten JavaScript-Pfade, per JSON zusammengestellte Links, Service-Worker-Verhalten, Redirects, Drittanbieterzugriffe, Deep-Links und Browser-Navigationszustände. Aus `0` statischen Lücken folgt **nicht** eine vollständige Laufzeit-Verträglichkeit. Auch die bestehenden öffentlichen wissenschaftlichen Quell- und Registry-URLs sind vor einer Migration einzeln auf ihre beabsichtigte Veröffentlichung zu prüfen.

## 4. Negative Tests (lokal)

**[LOKAL NUMERISCH BESTÄTIGT]** `python tests/2026-11-03_test_UniverseLab_RC19_PublicOnlyBuild_v1.0.py` ergab **27/27 PASS**. Darunter:

- synthetischer Draft-Canary außerhalb der Website, kein Kopieren neuer unfreigegebener Registry- oder Workflow-Dateien;
- Digest-Manipulation, fehlender Pfad, Symlink, ausführbare Quelle;
- Traversal, Glob, %-Kodierung, Duplikate, doppelte JSON-Felder, falsches Manifeststatusfeld;
- verweigerte Überschreibung bestehender Ausgabe;
- vorhandene lokale Linkziele außerhalb der Allowlist lösen HOLD aus;
- korrektes dynamisches Metadatum als kontrollierter Einzelfall; falsche Source-SHA, zweiter Lauf, ungeeignete Ref, boolescher Laufnummer-Typ und fremde Felder werden abgelehnt.

Die PR-QA ergänzt zwei Canary-Dateien ausschließlich im temporären Runner-Checkout, erstellt ein isoliertes Staging sowie eine **simulierte `.tar.gz`-Pages-Dateiliste** und prüft, dass weder Dateien noch Canary-Marker darin auftauchen. Dieser CI-Lauf ist erst nach dem Speichern der Kandidaten-Dateien auf einem PR-Branch beobachtbar; ein **echter** GitHub-Pages-Upload ist bewusst nicht Teil von RC19.

## 5. Installationsvorschlag – keine autorisierte Änderung

Erst nach dokumentiertem gesonderten Review könnte ein **eigener** späterer PR die produktive `.github/workflows/deploy-pages.yml` gezielt so ändern, dass nach bestehendem GitHub-Checkout und Source-Check erst ein Public-Only-Staging gebaut wird und `actions/upload-pages-artifact@v4` **ausschließlich `path: _site`** bekommt. Die bestehende `deploy-meta.json`-Erzeugung muss vor dem Build erfolgen; alle Main-Head-/Rerun-/Post-Deploy-Attestierungen sind zu erhalten. Bei geänderter Main-Basis sind die Digestpins und sämtliche Guards neu zu validieren.

Anschließend müssen mindestens diese unabhängigen Nachweise vorliegen:

1. Besitzerentscheid zur öffentlichen Pfad-Auswahl **einschließlich jeder Registry-Datei**; Datenschutz-/Secret-Prüfung auf die wirkliche Veröffentlichungsmenge, unabhängig vom RC18-Scanner.
2. Vollständige Browser-/Netzwerk-Smoketests auf Desktop und Android sowie über DE/EN-Einstiegsseiten, Navigator, Solver Hub, wissenschaftliche Statusseiten, JSON-Fetches, Service Worker und Ausdruck/Export.
3. Artefaktinventar des echten zukünftigen `upload-pages-artifact`-Laufs, nicht nur des simulierten Tarballs; negative Synthetic-Canary-Probe ohne vertrauliche Daten.
4. GitHub-Branch-Protection/Required-Checks tatsächlich aktiv und als **echte** Merge-Blockade getestet; Trusted-Workflow-Scope der RC13–RC17-Governance separat freigegeben.
5. Eigentümerfreigabe für **genau** diesen Installationsumfang. Allgemeine Chat-Aufforderungen wie »Go« sind keine Ratifikation einer Produktions-/Kanonisierungsfreigabe.

## 6. Status und Abhängigkeiten

```text
RC19_LOCAL_BUILD                 = PASS_446_FILES
RC19_LOCAL_UNIT_TESTS            = PASS_27_OF_27
RC19_SIMULATED_ARTIFACT_CI       = PENDING_BRANCH_RUN
RC19_BROWSER_RUNTIME_PARITY      = NOT_VERIFIED
RC19_PUBLIC_CONTENT_OWNER_REVIEW = NOT_RATIFIED
RC19_MAIN_INSTALLATION           = NOT_AUTHORIZED
RC18_PUBLICATION_BLOCKER         = OPEN_ON_MAIN
RC17_ROUTINE_AUTO_MERGE          = BLOCKED
PR263                            = DRAFT_UNMERGED
PR264                            = DRAFT_UNMERGED
CANONICAL_PROMOTION              = BLOCKED
PHYSICAL_GATE_EFFECT             = NONE
PHYSICAL_EVIDENCE_EFFECT         = NONE
```

**Urteil:** Ein sicherheitsbewusst konstruiertes, isoliertes Publikationsstaging ist lokal technisch ausführbar. Es beweist weder eine gefahrlos installierbare reale GitHub-Pages-Migration noch wissenschaftliche Gültigkeit der veröffentlichten Daten. Der RC18-Blocker bleibt bis zur separaten Installation und realen Negativprüfung **offen**.
