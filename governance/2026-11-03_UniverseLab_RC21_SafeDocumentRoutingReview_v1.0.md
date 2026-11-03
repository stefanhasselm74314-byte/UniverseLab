# UniverseLab — RC-VALIDATION-21: Manifestgebundener Dokumentenrouter

**Datum:** 2026-11-03  
**Status:** `LOCAL_AND_GITHUB_CI_CANDIDATE_QA_PASS / UNINSTALLED / RELEASE_HOLD`  
**Governance:** RC16-B, Ein-Personen-Betrieb, QA ohne automatische Freigabe.  
**Herkunft:** `main`-Basis `51bcc8fccb092c104ac0fca5fc98a5b996dcb914`; RC19-Draft-PR #265 → RC20-Draft-PR #266 → RC21 eigener gestapelter Draft.  
**RC19-Allowlist:** `governance/2026-11-03_UniverseLab_RC19_PublicFiles_v1.0_DRAFT.json`, 446 Einträge.  
**Manifest-SHA-256:** `b0b517002349fc158eddb0676fc764986c9a909fc873f5edf6bf75e42a57753b`.  
**Generator:** `tools/2026-11-03_UniverseLab_RC21_RenderSafeRouter_v1.0.py`.  
**Nichtinstallierter Kandidat:** `drafts/2026-11-03_UniverseLab_RC21_SafeDocumentRouter_v1.0_DRAFT.js`.  
**Router-SHA-256:** `1fdcdfe472832d600e5ad2232dec25e0df52e2a6651cdfd5fe66a95bb0f1d0e6`.  
**Provenienz:** `drafts/2026-11-03_UniverseLab_RC21_RouterProvenance_v1.0_DRAFT.json`.
**GitHub-CI:** Draft-PR #267, Head `93a0dfe96955fb60f21c6c7dd86b3b75cd821977`, Run `41675103974`, Job `126053496053`, Conclusion `SUCCESS`; die sechs fachlichen Workflow-Steps bestanden. Die dokumentarische Nachbindung dieses Runs ändert keine Public-Datei.

## 1. Kernergebnis und Geltungsbereich

**[NUMERISCH BESTÄTIGT — LOKALE CODE-/TESTUMGEBUNG]** Ein neuer Router-Kandidat beschränkt die automatische Umschreibung von Dokument-/Source-Links auf **77 zulässige, manifestgebundene exakte Dateipfade**. Alle 77 Dateien sind ein Teil der 446 Datei- und SHA-256-Einträge des RC19-Manifests. Der Generator verifiziert vor Ausgabe die RC19-Manifeststruktur, die 446 tatsächlich vorhandenen Public-Dateien, deren SHA-256 sowie die Existenz beider Viewer-HTML-Dateien. Der generierte Code enthält eine fest eingebettete Version dieser 77 Pfade und die Manifest-Provenienz.

**[KONDITIONAL — KANDIDAT, NICHT LIVE]** Bei GitHub- oder Pages-Links zu einer manifestierten Markdown-/Text-/Quelltextdatei wird lokal zu `DocumentViewer` beziehungsweise `SourceTextViewer` mit einem exakt aufgebauten `src` navigiert. Bei einem **nicht freigegebenen** GitHub-Pfad wird die Original-URL unverändert gelassen. Das verhindert im beabsichtigten Einbauzustand den von RC20 identifizierten lokalen 404 durch die bisherige pauschale Umschreibung; die tatsächliche Produktivwirkung ist ausdrücklich **nicht** festgestellt.

**[BESTÄTIGT — NICHTINSTALLATION]** Der aktive `assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js` wurde **nicht verändert**. Der Kandidat liegt nur unter `drafts/`, ist in keinem HTML-/Shell-/Service-Worker-Loader eingetragen und wird durch das RC19-Staging aus der Website ausgeschlossen. Weder `main` noch der Pages-Deployment-Workflow wurden verändert.

**[GITHUB-CI NUMERISCH BESTÄTIGT]** Im read-only PR-Runner bestätigten die 9 Python-Fälle, alle 1.095 JavaScript-VM-Assertions, die Bytegleichheit des generierten Routers, das weiterhin 446 Dateien umfassende RC19-Staging ohne RC21-Kandidat sowie den erneut erwarteten RC20-Exit-2 mit `release_gate=HOLD`. Die Tatsache, dass der Workflow erfolgreich abschloss, entspricht einem **erfolgreich nachgewiesenen HOLD**, nicht einer Freigabe.

## 2. Positive und negative Abdeckung

| Kontrollklasse | Fallzahl | Befund / Aussagegrenze |
|---|---:|---|
| Manifestierte lokale Dokument-/Quelltexte | 77 Pfade | Positiv umgeleitet (simulierter DOM) |
| Dieselben Pfade als GitHub-`blob/main`-Links | 77 Pfade | Positiv umgeleitet (simulierter DOM) |
| Statisch in RC20 gefundene ausgeschlossene Ziele | 3 verschiedene Pfade / 4 Linkvorkommen | GitHub-URL bleibt unverändert |
| Asynchron erzeugbare `solvers[*].roadmap_path`-Links | 14 | GitHub-URL bleibt unverändert |
| Angreifer-/Fehlkonfigurationstest | Domain- und Port-Spoof, andere Branches/Owner, unzulässige Pfade, codierte Trenner | Negativabweisung im VM-Test |
| Dynamische DOM-Ergänzung und `href`-Änderung | Vorhandene Links, verschachtelte spätere Links, MutationObserver, opt-out, idempotente Wiederholung, Wechsel auf unzulässige Ziele | Geprüft im VM-Test; kein echter Browser |

Die drei statisch unterschiedlichen ausgeschlossenen Ziele heißen:

1. `md2s_bvp_solver_v1_0.py`;
2. `science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md`;
3. `tools/2026-08-03_validate_public_repository_privacy_v1.0.py`.

Alle 14 weiteren Roadmaps liegen unter `science/solver-hub/` und **gehören nicht** zur Pages-Allowlist. Das Modellieren eines nachträglichen DOM-Linkeinsatzes reduziert ein RC20-Timingrisiko; es ist kein Beweis für eine konkrete Ausführung im Browser.

Lokale Testbefunde:

```text
RC21_GENERATOR_UNIT_TESTS = 9/9_PASS
RC21_JS_VM_ASSERTIONS = 1095_PASS
RC21_PUBLIC_MANIFEST = 446_SHA256_PINNED_FILES
RC21_ROUTABLE_SUBSET = 77_EXACT_PATHS
RC21_STATIC_EXCLUDED_UNIQUE_TARGETS = 3_PRESERVED
RC21_DYNAMIC_EXCLUDED_ROADMAP_TARGETS = 14_PRESERVED
RC21_BROWSER_RUNTIME = NOT_TESTED
RC21_REAL_ANDROID = NOT_TESTED
RC21_REAL_PAGES_ARTIFACT = NOT_TESTED
RC21_RELEASE = HOLD
```

## 3. Fail-closed-Eigenschaften, Restrisiken

- Jede lokale Umschreibung erfordert Mitgliedschaft im SHA-gebundenen exakten RC19-Dateisatz. Eine bloß existierende Datei außerhalb der Allowlist ist nicht ausreichend.
- Nur GitHub `https://github.com` ohne abweichenden Port, exakter Repository-/`blob/main`-Präfix oder derselbe Pages-Origin und `/UniverseLab/`-Präfix sind als Router-Eingang zugelassen. Dekodierte Punkt-/versteckte Segmente, nichtkanonische Trenner und fremde Hosts werden abgewiesen.
- Explizite Roh-/Download- und `data-ul-*`-Opt-outs bleiben unberührt. Ein DOM-Observer verarbeitet asynchron ergänzte Links und geänderte `href`-Attribute. Eigene `href`-Änderungen werden idempotent erkannt; bei einer späteren fremden `href`-Änderung werden nur vom Kandidaten gesetzte Metadaten entfernt.
- Die Path-Liste dient **allein der Navigation**, nicht als Zugriffskontrolle. Nicht auf Pages publizierte Dateien können weiterhin im **öffentlichen GitHub-Repository** sichtbar sein. Ein externer Original-Link legitimiert die Veröffentlichung seines Zielinhalts nicht.
- Query-Parameter werden in `src` eingebettet; ein ursprünglicher Anker-Fragmentteil `#…` wird wie beim bisherigen Router derzeit nicht in den Viewer übertragen. Semantische Ankerparität bleibt separat zu prüfen.
- Die RC19-Freigabe ist weiterhin `DRAFT_NOT_AUTHORIZED`. SHA-256 belegt Byteidentität, nicht semantische Datenschutzfreigabe. Der RC20-Musterscan mit null Treffern beweist keine vollständige Geheimnis-/Personenbezogenheitsfreiheit.
- Die Node-VM simuliert URL, DOM und MutationObserver, aber nicht Chromium/Samsung Internet, echte Netzwerkzugriffe, Service-Worker-Interzeption, HTML-Viewer-Rendering oder Android-Ausgabe.

## 4. Künftige Integrations- und Freigabeschranken

**Kein autonomer Installationsschritt in RC21.** Für eine separate Freigabe muss der Betreiber ausdrücklich entscheiden, ob der Kandidat die bisherige Routerdatei ersetzen darf. Danach wären mindestens erforderlich:

1. Ein gezielter Änderungenachweis der tatsächlich genutzten Routerdatei, erneute SHA-256-Bindung aller geänderten Public-Dateien und ein neues RC19-Staging-Audit; der alte SHA-Satz darf nicht stillschweigend weitergelten.
2. Echte Browser-/Netzwerkpfadtests im öffentlichen Pages-Prefix `/UniverseLab/` einschließlich erster Sitzung, bestehendem Service Worker, Offline-/Reset-Zuständen und dynamischen Registry-Links.
3. Android (Samsung Galaxy S24 Ultra) und Desktop mit Positiv- und Negativlinks, Viewer, Rücknavigation, Download, Druck/Export sowie DE/EN.
4. Erneuter Privacy-/Semantikreview sämtlicher neu oder geändert veröffentlichter Bytes und des vollständigen Deployment-Artefakts.
5. Wirklich erzwungene Required Checks und der gesonderte menschliche Freigabeschritt; grüne QA allein darf keine Freigabe erzeugen.

## 5. Entscheidungssatz

```text
RC21_CODE_CANDIDATE = LOCAL_TEST_PASS
RC21_CANDIDATE_INSTALLED = FALSE
RC21_ACTIVE_ROUTER_CHANGED = FALSE
RC21_RC19_MANIFEST_CHANGED = FALSE
RC21_PUBLIC_PAGES_CHANGED = FALSE
RC21_GITHUB_CI = SUCCESS_RUN_41675103974_JOB_126053496053
RC21_INHERITED_RC20_RELEASE_GATE = HOLD
RC21_AUTOMATIC_MERGE_OR_DEPLOY = FORBIDDEN
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```

**Urteil:** Der manifestgebundene, gegen Ausschlussziele getestete Codepfad liegt als reproduzierbarer, nichtoperativer Kandidat vor. Es entsteht **keine Release-, Governance-, mathematische oder empirische Bestätigung**. Die beiden Blocker *Integration in den wirklich geladenen Router* und *Browser-/Pages-Abnahme* bleiben offen.
