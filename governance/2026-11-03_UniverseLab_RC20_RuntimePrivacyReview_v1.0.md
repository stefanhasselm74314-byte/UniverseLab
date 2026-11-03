# UniverseLab — RC-VALIDATION-20: Website-Laufzeitpfade, Quellenviewer und Datenschutz

**Datum:** 2026-11-03  
**Status:** `HOLD_CONFIRMED_STATIC_ROUTER_COMPATIBILITY / PRIVACY_PATTERN_QA_PASS / BROWSER_NOT_RUN`  
**Governance:** RC16-B Ein-Personen-Betrieb mit nichtoperativer automatischer QA und gesperrten kritischen Freigaben.  
**Main-Basis:** Commit `51bcc8fccb092c104ac0fca5fc98a5b996dcb914`, Tree `65f423f04bbb2f1462f120a6b31073644cdc28cc`.  
**RC19-Abhängigkeit:** Draft-PR #265, letzter geprüfter Head `81154e120ff5b64c28db43c0f1596c93d501ce3a`, exact-hash manifest mit 446 Dateien.  
**Maschinenlesbare Evidenz:** `drafts/2026-11-03_UniverseLab_RC20_RuntimePrivacyFindings_v1.0_DRAFT.json` und `drafts/2026-11-03_UniverseLab_RC20_HttpSmoke_v1.0_DRAFT.json`.  
**Auditor:** `tools/2026-11-03_UniverseLab_RC20_RuntimePrivacyAudit_v1.0.py`; Testfixture 21 Methoden; HTTP-Replay unter `/UniverseLab/`.

## 1. Kernergebnis

**[BESTÄTIGTER CODEPFAD, NOCH NICHT ALS BROWSERLAUF GEMESSEN]** RC19 kann die 446 technisch ausgewählten Dateien isoliert bereitstellen. Jedoch würde die unveränderte globale Dokumenten-Router-Logik GitHub-Quelllinks zu lokalen Viewern mit `?src=/UniverseLab/...` umschreiben, obwohl die betreffenden Ziele aus dem Public-Only-Staging ausgeschlossen sind. Das ist eine konkrete strukturelle Inkompatibilität, die der enge statische RC19-Literal-Linktest nicht erfassen konnte.

Es wurden **vier statische Linkvorkommen zu drei unterschiedlichen aktuell existierenden, aber aus RC19 ausgeschlossenen Repository-Dateien** gefunden:

| Quellseite | Ausgeschlossenes Ziel | Injektionsstatus |
|---|---|---|
| `solver-hub.html` | `md2s_bvp_solver_v1_0.py` | GlobalShell-Loader im HTML vorhanden |
| `solver-hub.html` | `science/solver-hub/2026-08-07_ULSH-01_MD2S-BVP_Roadmap_v1.0.md` | GlobalShell-Loader im HTML vorhanden |
| `source.html` | `tools/2026-08-03_validate_public_repository_privacy_v1.0.py` | GlobalShell-Loader im HTML vorhanden |
| `solver-hub-en.html` | `md2s_bvp_solver_v1_0.py` | Service-Worker-Injektion konditional |

Der Codepfad besteht aus `assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js` → `assets/2026-08-19_UniverseLab_SitePrintExportBootstrap_v1.0.js` → `assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js`, alternativ aus der HTML-Injektion über `2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js`. Die konkreten Browser-Timing-/Service-Worker-Zustände sind noch nicht experimentell geprüft.

**[KONDITIONAL, DATENGESTÜTZT]** Die öffentliche Registry `registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json` enthält **14 verschiedene `solvers[*].roadmap_path`-Ziele**, alle unter `science/solver-hub/` und alle außerhalb des RC19-Staging. Der zugehörige HTML-Renderer erzeugt daraus GitHub-Roadmaplinks. Ob ein nachladender Router diese erst asynchron erzeugten Links erfasst, hängt von der Reihenfolge von JSON-Fetch und Router-Initialisierung beziehungsweise der SW-Injektion ab. Diese 14 Kandidaten sind **kein zusätzlich gemessener 14-facher Laufzeitfehler**, aber ein materielles Risiko der Parität.

Für die 73 HTML-Dateien wurden im statischen Audit 16 Seiten mit unmittelbarem GlobalShell-Loader und elf passende dokument-/quellformatbezogene statische Links ermittelt. Externe ausführbare Script-/Style-Hosts wurden in statischen HTML-Tags nicht gefunden; dynamisch eingebrachte Dienste sind damit **nicht ausgeschlossen**.

## 2. Datenschutzprüfung der gesamten vorgesehenen Veröffentlichung

**[LOKAL NUMERISCH BESTÄTIGT]** Alle 446 RC19-Dateien / 4.932.132 Byte wurden in UTF-8 auf bekannte Muster gescannt. Das Verfahren erweitert den bisherigen öffentlichen Privacy-Validator auf den **tatsächlichen Manifestumfang** einschließlich bisher ausgelassener Root-, SVG-/XML-/CSV-/Webmanifest-Dateien. Auch verschachtelte JSON-Schlüssel, doppelte Schlüssel, NaN/Infinity, ungültige JSONL-Zeilen und fehlerhafte UTF-8-Dekodierung werden beurteilt.

```text
RC20_PUBLIC_FILE_SCAN = 446/446
RC20_PRIVACY_PATTERN_FINDINGS = 0
RC20_JSON_STRUCTURE_FINDINGS = 0
RC20_BYTES_SCANNED = 4_932_132
SEMANTIC_PERSONAL_DATA_REVIEW = NOT_PERFORMED
```

**Grenze:** Null Regex-/Schlüssel-Treffer beweisen nicht die Abwesenheit sämtlicher personenbezogenen Inhalte, indirekter Identifikatoren, Forschungsnotizen mit nicht offengelegter Provenienz, extern abgerufener Daten oder Geheimnisse ohne bekannte Muster. Das öffentliche Repository selbst ist unabhängig von Pages bereits öffentlich; ein privates Dokument gehört **nicht** auf einen öffentlichen PR-Branch.

## 3. HTTP-Transportreplay – keine Browserprüfung

**[LOKAL NUMERISCH BESTÄTIGT]** Mit einem frischen Python-HTTP-Testserver auf dem Pfad `/UniverseLab/` wurden sämtliche 446 Public-Dateien per HTTP 200 abgerufen und **bytegenau** gegen die Manifest-SHA-256-Werte verifiziert. Für alle **73 HTML-Seiten** wurde der HTTP-Abruf zusätzlich mit einem Galaxy-S24-Ultra-/Android-User-Agent wiederholt. Im selben lokalen Staging antworteten die drei ausgenommenen, vom Router adressierbaren Quellpfade und ein synthetischer Draft-Pfad mit **HTTP 404**.

```text
HTTP_DESKTOP_FILES_200_AND_SHA_MATCH = 446/446
HTTP_ANDROID_USER_AGENT_HTML_200 = 73/73
HTTP_EXCLUDED_ROUTER_TARGETS_404 = 3/3
HTTP_SYNTHETIC_DRAFT_404 = PASS
REAL_GITHUB_PAGES_ARTIFACT = NOT_TESTED
JAVASCRIPT_EXECUTION = NOT_TESTED
ANDROID_REAL_DEVICE = NOT_TESTED
CHROMIUM_RESPONSIVE_LAYOUT = NOT_TESTED
```

Ein HTTP-User-Agent ist **keine Android-Emulation**. Der Test belegt Routing und Byteidentität beim lokalen Server, aber nicht JS-Ausführung, Service-Worker-Kontrolle, visuelle Bedienbarkeit, Android-Druck/Export, Anmeldedialoge oder Live-Produktionsparität.

## 4. Behebungsarchitektur – separat zu autorisieren

**Bevorzugter technischer Pfad für einen künftigen RC21-Kandidaten:** GitHub-Quelllinks dürfen nur dann auf den gleich-originigen Dokument-/Source-Viewer umgeschrieben werden, wenn ihr Ziel in einer **unabhängig freigegebenen** und versionierten öffentlichen Zielpfadmenge enthalten ist. Andernfalls muss der ursprüngliche GitHub-Link als externer Link erhalten bleiben. Damit müssen nicht pauschal `science/` oder `tools/` zur Pages-Auslieferung freigeschaltet werden. Eine rein nachträgliche, asynchrone `HEAD`-Probe ist wegen der Klick-/Timing-Rennen nicht automatisch gleichwertig mit einer atomaren Routingentscheidung.

**Alternative (Owner-Entscheidung erforderlich):** Einzelne Dokumente können nach Datenschutz- und Veröffentlichungsreview auf eine neue exakte Allowlist kommen. Der bisherige RC19-Deny-Envelope schließt `science/` und `tools/` absichtlich aus; die Policy selbst müsste dafür in einem getrennten sicherheitsgeprüften Schritt geändert werden. Ein pauschales Verzeichnis-Glob ist keine tragfähige Freigabe.

Notwendige Akzeptanzbedingungen:

1. Statische und dynamisch erzeugte Links mit Browser-Netzwerkprotokoll auf echter Pages-Pfadstruktur; mindestens Initialaufruf ohne bestehenden SW, Wiederaufruf mit SW und Reset-/Offlinezustand.
2. Desktop und Android inkl. Navigation, Download, Drucken/Export, DE/EN-Routen, JSON-Viewer und aufklappbaren Quelllinks. Emulation muss von einem echten Galaxy S24 Ultra getrennt protokolliert werden.
3. Semantische Review-Entscheidung für jede veröffentlichte Dateiklasse, insbesondere sämtliche 269 Registry-Dateien.
4. Positiver und negativer Test des **tatsächlichen GitHub-Pages-Artefakts** nach getrennter Installationsfreigabe; keinen Canary mit echten Geheimnissen verwenden.
5. Erforderliche GitHub-Checks real erzwungen, vor jedem Merge; keine Routine-Ausnahme aus QA-Grün ableiten.

## 5. Freigabestatus

```text
RC20_STATIC_ROUTER_COMPATIBILITY = HOLD_4_LINKS_3_UNIQUE_TARGETS
RC20_DYNAMIC_ROADMAP_CANDIDATES = 14_UNRESOLVED_RUNTIME
RC20_PRIVACY_PATTERN_SCAN = PASS_446_OF_446
RC20_HTTP_TRANSPORT_SHA = PASS_446_OF_446
RC20_MOBILE_UA_HTTP = PASS_73_OF_73_NOT_ANDROID_EMULATION
RC20_BROWSER_RUNTIME_PARITY = NOT_PERFORMED
RC20_SEMANTIC_PRIVACY_REVIEW = NOT_PERFORMED
RC20_REAL_PAGES_ARTIFACT = NOT_TESTED
RC20_RELEASE_GATE = HOLD
RC19_INSTALLATION = NOT_AUTHORIZED
RC17_ROUTINE_AUTO_MERGE = BLOCKED
PR263 = DRAFT_UNMERGED
PR264 = DRAFT_UNMERGED
PR265 = DRAFT_UNMERGED
MAIN = 51bcc8fccb092c104ac0fca5fc98a5b996dcb914
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```

**Urteil:** Eine konkrete fehlende Runtime-Quellenreferenz ist nachgewiesen; die sichere Release-Bedingung ist nicht erfüllt. Zugleich zeigt der vollständige Musterscan kein automatisiert erkennbares Datenschutzmuster. Weder HTTP-Parität noch grüne Privacy-Regex-Tests ratifizieren den Inhalt, die Website oder die Physik.
