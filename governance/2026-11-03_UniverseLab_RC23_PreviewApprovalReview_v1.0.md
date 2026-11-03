# UniverseLab — RC-VALIDATION-23: kontrollierbare lokale Android-Preview, ohne Distribution

**Datum:** 2026-11-03  
**Status:** `LOCAL_ZIP_QA_PASS / GITHUB_CI_PENDING / NOT_DISTRIBUTED / RELEASE_HOLD`.  
**Abhängigkeit:** RC19-Draft #265 → RC20-Draft #266 → RC21-Draft #267 → RC22-Draft #268 → RC23 eigener gestapelter Draft.  
**RC22-Basis:** Commit `84563af5fb2840f607d70c05bbd07874a0193c2c`, tatsächliche Chromium-CI erfolgreich, echter Android-/Opera-Test offen.  
**Kanonische Basis:** `main` `51bcc8fccb092c104ac0fca5fc98a5b996dcb914` (vor RC23 geprüft).  
**Generator:** `tools/2026-11-03_UniverseLab_RC23_LocalPreviewBuilder_v1.0.py`.  
**Tests:** `tests/2026-11-03_test_UniverseLab_RC23_LocalPreviewBuilder_v1.0.py`.  
**Wichtig:** Kein lokales Preview-ZIP wird im Repository oder als Actions-Artefakt abgelegt. Der CI-Runner verwirft seinen temporären Prüfaufbau nach dem Lauf.

## 1. Sicherheitsarchitektur des lokalen Entwurfs

**[LOKAL NUMERISCH BESTÄTIGT]** Die RC23-Software erstellt ein deterministisches, nicht komprimiertes ZIP (`ZIP_STORED`) mit genau **448 Einträgen**:

- `UniverseLab/` enthält **exakt 446 im RC19-Manifest aufgeführte Pfade**; 445 Dateien haben ihren ursprünglichen RC19-SHA-256.
- An **genau einem** bestehenden Pfad ersetzt der Generator die bisherigen Routerbytes durch den nachrechenbaren RC21-Kandidaten: `assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js`. Damit ist das ZIP ausdrücklich **kein** offizielles RC19-Public-Only-Release-Artefakt.
- Außerhalb von `UniverseLab/` liegen nur `RC23_PREVIEW_META.json` mit 446 bytebezogenen SHA-256-Einträgen und `RC23_LOCAL_PREVIEW_README.txt` mit Status-Firewall und Anleitung. Diese Dateien sind nicht Teil einer Pages-Bereitstellung.

Die 446 Originaldateien müssen vor der Ersetzung erneut den Manifest-Hashes entsprechen. Der RC21-Code muss mit seinem Template deterministisch regenerierbar sein und die bereits dokumentierte Provenienz-SHA erfüllen. Symlinks, zusätzliche Pfade, fehlende Viewer, unbekannte Quelldateien, abweichende Archiveinträge, Traversal-Pfade und veränderte Provenienz führen zu `HOLD`.

Verifizierte lokale Paketidentität, **keine Distribution**:

```text
RC23_TEMPORARY_ZIP_ENTRIES = 448
RC23_WEB_PATHS = 446
RC23_UNMODIFIED_RC19_WEB_PATHS = 445
RC23_EXACT_ROUTER_OVERLAYS = 1
RC23_UNAPPROVED_NEW_WEB_PATHS = 0
RC23_ARCHIVE_BYTES = 5121637
RC23_ARCHIVE_SHA256 = 6de483211a4f42eb42584d9c9d1acc65d48e76a8a87afdf70dd73b0566d5dea7
RC23_PUBLICATION_OR_UPLOAD = NONE
RC23_RELEASE_GATE = HOLD
```

Der vollständige ZIP-Hash ist ein **Identitätsanker**, keine inhaltliche Veröffentlichungsgenehmigung. Die Archivbytes haben keinen empirisch-physikalischen Aussageeffekt.

## 2. Tests und Ergebnisgrenzen

**[LOKAL NUMERISCH BESTÄTIGT]** Zwölf Python-Tests wurden bestanden:

1. Exakter Umfang 446+2, Prüfsummen aller 445 unveränderten Dateien und Kandidatenrouter.
2. Zweifacher reproduzierbarer ZIP-Build mit identischem Gesamt-SHA.
3. Schutz vor existierendem Output und versehentlichem Ausgabepfad im Repository.
4. Manipulierte Routerdatei, abweichende RC21-Provenienz und manipuliertes RC19-Manifest → `HOLD`.
5. Unerlaubter Zusatzpfad, Archiv-Traversal, Inhaltsänderung und Symlink-/Ausführbarkeits-Metadaten → `HOLD`.
6. Entpacktes ZIP wird **ausschließlich auf `127.0.0.1`** durch einen Python-Testserver ausgeliefert: 446 Public-Dateien per HTTP 200 und Hashvergleich; drei negative ausgeschlossene Ziele per HTTP 404.

**Keine echte Android-Ausführung.** HTTP-Test und Testbrowser-Engine aus RC22 begründen eine reproduzierbare Testbasis, aber keine Messung in Stefans Opera/Android-17-Umgebung. Das RC23-ZIP wird nicht automatisch verteilt und startet keinen Server von selbst.

## 3. Technische Freigabesicherung von GitHub – separat geprüft

**[BESTÄTIGTE REGELSET-TEILANSICHT]** Das aktuell aktive Ruleset `UniverseLab-main-Basisschutz` (ID `24417933`) enthält für `refs/heads/main` die beiden Regeln `deletion` und `non_fast_forward`. Ein `required_status_checks`- oder `pull_request`-Ruleintrag ist in **diesem Ruleset** nicht vorhanden.

**[OFFEN / ZUGRIFFSBESCHRÄNKUNG]** Die API `branches/main/protection/required_status_checks` antwortet mit HTTP `403` für die GitHub-Anbindung. Weitere wirksame Schutzregeln können deshalb nicht ausgeschlossen werden. Eine automatisch technisch erzwungene CI-/Owner-Freigabe darf aus der verfügbaren Ansicht **nicht behauptet** werden. Es werden weder Regeln verändert noch Schutzmaßnahmen umgangen.

## 4. Zwei ausdrücklich unterschiedliche Owner-Entscheidungen

### A. Nur lokales, an Stefan ausgeliefertes Android-Testpaket

**Noch nicht freigegeben.** Für die spätere Bereitstellung eines ZIP an Stefan sind eine explizite Beschränkung auf `LOCAL_ONLY_LOOPBACK`, ein erneuter vollständiger Dateisatz-/Privacy-Review, der genaue ZIP-SHA und der beabsichtigte Empfänger erforderlich. Erst danach darf ein separates Deliverable erzeugt und über einen autorisierten Weg herunterladbar gemacht werden. Die Anleitung steht bereits in `governance/2026-11-03_UniverseLab_RC23_AndroidLocalPreviewInstructions_v1.0.md`.

Der lokale Browserzugriff über `http://127.0.0.1:8765/UniverseLab/` wäre danach ausschließlich geräteintern; GitHub-Originalquellen können als externe Links die Website `github.com` öffnen. Die Website- und SW-Autoregistrierung ist keine HTTPS-Pages-Emulation.

### B. Öffentlich erreichbare Pages-Preview oder Produktivverteilung

**Nicht autorisiert, nicht Teil von RC23.** Ein öffentlich erreichbarer Preview-Branch/-Repo/-Pages-Deploy ist eine eigenständige externe Veröffentlichung und erfordert vorherige, konkret auf Ziel, Datenumfang, Datenschutz, Rollback und menschlichen Freigabeprozess bezogene Autorisierung. Ein bloßes „CI grün“ oder ein ZIP-Hash reicht nicht aus.

## 5. Freigabestatus

```text
RC23_PREVIEW_PACKAGING_CODE = LOCAL_TEST_PASS
RC23_PREVIEW_ZIP_GENERATED_IN_TEST_TEMP = TRUE
RC23_PREVIEW_ZIP_IN_GITHUB_REPOSITORY = FALSE
RC23_PREVIEW_ZIP_UPLOADED_AS_ARTIFACT = FALSE
RC23_PREVIEW_ZIP_AVAILABLE_FOR_DOWNLOAD = FALSE
RC23_LIVE_PREVIEW_URL = NONE
RC23_REAL_ANDROID_OPERA = NOT_TESTED
RC23_SEMANTIC_PUBLIC_CONTENT_APPROVAL = NOT_PERFORMED
RC23_REQUIRED_STATUS_CHECK_ENFORCEMENT = NOT_PROVEN
RC23_OWNER_DISTRIBUTION_APPROVAL = NOT_GRANTED
RC23_GITHUB_CI = PENDING
RC23_PAGES_DEPLOYMENT_CHANGED = FALSE
RC23_RELEASE_GATE = HOLD
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```

**Urteil:** Die lokale Testpreview ist technisch reproduzierbar vorbereitet. Keiner der nachgelagerten Verteilungs-, Browserprodukt- oder Forschungsgates wird dadurch geöffnet.
