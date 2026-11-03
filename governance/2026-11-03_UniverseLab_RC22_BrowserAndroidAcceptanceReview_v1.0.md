# UniverseLab — RC-VALIDATION-22: Browser, Service Worker und Android-Abnahme

**Datum:** 2026-11-03  
**Status:** `CHROMIUM_CI_PENDING / CANDIDATE_OVERLAY_NOT_INSTALLED / REAL_ANDROID_OPEN / RELEASE_HOLD`  
**Abhängigkeit:** RC19-Draft-PR #265 → RC20-Draft-PR #266 → RC21-Draft-PR #267 → RC22 eigener gestapelter Draft.  
**Nichtkanonischer Basis-Head RC21:** `3c4fedf5cb84fa8fc76da6f0b86c1fff8e80792f`.  
**Kritische Schranke:** GitHub-Pages-Publikation, PR-Merge und aktive Router-Installation bleiben nicht autorisiert.

## 1. Fragestellung und Testtrennung

RC20 fand eine reale statische Link-Routing-Inkompatibilität in einem geplanten RC19-Public-Only-Artefakt. RC21 erzeugte eine 77-Pfade-Allowlist-gebundene Router-Variante und validierte sie in einer Node-VM (1.095 Assertions, 9 Python-Tests, kein Browser). RC22 prüft nun den **tatsächlichen Browser-JavaScript-/DOM-/Netzwerkpfad** sowie die mobile Chromium-Darstellung und die Service-Worker-Injektion, ohne ein Website-Artefakt auszuliefern.

Getrennte Evidenzbereiche:

| Ebene | RC22-Methode | Status-/Aussagegrenze |
|---|---|---|
| Originales RC19-Staging | 446 exakte SHA-256-Verifikationen und HTTP-Server mit Positiv-Allowlist | Public-Byteidentität, nicht Freigabe |
| Originaler RC20-Fehler | Echte Chromium-Navigation mit unverändertem Router und erwarteter 404 in der Quellenansicht | Baseline-Negativkontrolle |
| Hypothetische RC21-Installation | In-memory HTTP-Response-Overlay **nur** beim bisherigen Router-Assetpfad | Realer Browser-Engine-Test, keine Repo-/Pages-Mutation |
| Desktop | Echte Headless-Chromium-Engine mit DOM-/Viewer-HTTP-Tests | Desktop-Simulation im CI-Runner |
| Mobile | Dieselbe Chromium-Engine mit 412 × 915 CSS-Pixeln, DPR 3, Touch und S24-Ultra-User-Agent | **Emulation, kein echtes Samsung-Gerät** |
| Service Worker | Registrierung des bestehenden SitePrintExport-SW auf loopback-origin; zweite Navigation mit kontrolliertem Client | SW-Injektion geprüft; HTTPS-Autoregistrierung auf Pages nicht geprüft |
| Android 17 / Opera / Samsung Internet | Separates Betreiberprotokoll erforderlich | `NOT_TESTED`, siehe RC22-Android-Gate |
| Echtes Pages-Artefakt | Keine produktive Installation / kein Browserrelease | `NOT_TESTED` |

## 2. Nichtoperative Prüfarchitektur

1. Das RC19-Werkzeug erstellt auf dem CI-Runner ein temporäres Verzeichnis mit ausschließlich 446 in der unveränderten Manifestliste freigegebenen Dateien. Der Node-Testserver bedient nur diese exakten Pfade unter `/UniverseLab/` und antwortet andernfalls mit `404`.
2. **Baseline-Port:** Die unveränderten 446 Dateien werden von einem lokalen, echten Chromium-Browser aufgerufen; der bestehende Router kann seine RC20-Fehlumleitung demonstrieren.
3. **Overlay-Port:** Der identische Stagingbaum bleibt auf dem Dateisystem und im Manifest unverändert. Nur im HTTP-Response auf den exakten URL-Pfad `assets/2026-08-27_UniverseLab_DocumentLinkRouter_v1.0.js` werden **im RAM** die RC21-Kandidatenbytes geliefert. Kein Artefakt wird dadurch publiziert; die Overlay-Bytes sind **nicht** als RC19-Release-Payload SHA-verifiziert.
4. Der Browser öffnet echte Solver-Hub-/Source-Seiten, fügt ein manifestiertes Dokument-Canary ein, prüft die ausgeschlossenen Quell-URLs, navigiert tatsächlich in beide Viewer und prüft den HTTP-Abruf ihrer Source-Dateien.
5. Mobile Chromium emuliert die S24-Geometrie. Der bestehende Service Worker wird **manuell in der lokalen Testseite** registriert, damit die HTML-Navigations-Injektion und die 14 tatsächlich per Registry-Fetch erzeugten Roadmap-Links beobachtet werden können.
6. Danach wird Offline ausdrücklich als **erwartetes Scheitern** einer uncached Navigation beurteilt, Online-Recovery geprüft und die Testregistrierung wieder abgemeldet. Ein Offline-PASS wird nicht behauptet.

## 3. Fest verdrahtete Akzeptanz- und Negativbedingungen

- Echte Chromium-Engine muss starten, sonst Test-`HOLD` statt „simuliert bestanden“.
- Baseline muss das bisherige ausgeschlossene Roadmap-Ziel in den Viewer umschreiben; dessen Source-Fetch muss `404` ergeben. Bei Nichtreproduktion ist eine Untersuchung erforderlich, kein stilles Positivurteil.
- Overlay muss bei manifestiertem Markdown und JS zu den korrekten lokalen Viewern routen, die Quell-HTTP-Antwort muss `200` sein und der Viewer die tatsächliche Quelldatei anzeigen.
- Die drei statischen RC20-Ausschlussziele bleiben externe GitHub-Links. Eine englische, nicht durch GlobalShell bestückte Seite wird separat geprüft.
- Die 14 `solvers[*].roadmap_path`-Links müssen tatsächlich aus der öffentlichen Registry geladen und nach Service-Worker-Injektion als GitHub-Links erhalten bleiben.
- Das Browser-Canary muss auch unter SW-Kontrolle reagieren. Touch-Navigation, Offline-Erwartung und Recovery müssen konsistent sein.
- Ein JSON-Protokoll und Screenshots werden **nur als kurzlebiges, nichtkanonisches GitHub-Actions-Artefakt** abgelegt, nicht in `main` oder Pages. Screenshots sind technisch erzeugte Spuren, noch keine manuell bewertete visuelle Abnahme.
- Ein grüner Workflow besagt ausschließlich `CHROMIUM_STAGING_QA_PASS_NOT_RELEASE`, **niemals** `PRODUCTION_APPROVED` oder `ANDROID_REAL_DEVICE_PASS`.

## 4. Offene technische und semantische Punkte

1. RC22 kann ohne autorisierte Test-URL weder den RC21-Kandidaten auf **echtem GitHub Pages** noch auf Stefans realem Galaxy S24 Ultra prüfen. Das separate manuelle Akzeptanzprotokoll ist eine **Vorbereitung**, keine durchgeführte Messung.
2. Der echte Produktions-Service-Worker wird auf `https:` automatisch registriert; die lokale CI prüft die SW-Funktion über explizite Registrierung in einem vertrauenswürdigen `127.0.0.1`-Kontext. HTTPS-Autoregistrierung, Cachealter, bestehende Registrierungen und reale Browserprofile bleiben offen.
3. Die Chromium-Mobile-Emulation deckt weder Android-17-OS-Druckdialoge noch Opera-Features, Samsung-Internet-Codec-/UI-Sonderfälle, reale Touch-/Speicherprobleme oder Hardwareverhalten ab.
4. Querüberlauf wird im Browserbericht als Diagnose gemessen. Screenshots müssen vor einer visuellen Abnahme tatsächlich gesichtet werden. Accessibility-/Performance-/Cross-Browser-Regressionstests sind **nicht Bestandteil** dieses engen RC22-Pakets.
5. Eine in-memory ersetzte Antwort beweist keine kanonische Verteilung oder Vollständigkeit des zukünftigen Deployments. Nach jeder autorisierten Source-Änderung müssen manifestierte Dateihashes neu festgelegt, ein eigenständiger Public-Privacy-Review durchgeführt und reale Pages-Daten geprüft werden.

## 5. Freigabestatus

```text
RC22_CHROMIUM_DESKTOP = CI_PENDING
RC22_CHROMIUM_MOBILE_EMULATION = CI_PENDING
RC22_BASELINE_NEGATIVE_404 = CI_PENDING
RC22_SERVICE_WORKER_INJECTION = CI_PENDING
RC22_REAL_ANDROID_S24_ULTRA = NOT_TESTED
RC22_OPERA_ANDROID = NOT_TESTED
RC22_REAL_GITHUB_PAGES_ARTIFACT = NOT_TESTED
RC22_AUTHORIZED_PREVIEW_URL = NOT_AVAILABLE
RC22_ROUTER_INSTALLED = FALSE
RC22_PUBLIC_MANIFEST_CHANGED = FALSE
RC22_DEPLOYMENT_CHANGED = FALSE
RC22_RELEASE_GATE = HOLD
CANONICAL_PROMOTION = BLOCKED
PHYSICAL_GATE_EFFECT = NONE
PHYSICAL_EVIDENCE_EFFECT = NONE
```

**Urteil:** RC22 stellt einen auswertbaren, später in CI real ausführbaren Chromium-Testpfad und eine eigenständige Sperre für echte Android-/Pages-Freigabe bereit. Erst ein **ausgeführter, ausgewerteter** CI-Run kann den Chromium-Teilstatus verändern. Der Verteilungs- und Forschungsgate bleibt unabhängig davon `HOLD`.
