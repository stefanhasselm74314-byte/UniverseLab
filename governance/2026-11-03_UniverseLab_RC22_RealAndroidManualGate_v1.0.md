# UniverseLab — RC22: Reales Samsung-/Opera-Abnahmeprotokoll (noch NICHT ausgeführt)

**Status:** `BLOCKED_NO_AUTHORIZED_RC21_PREVIEW_URL`; die Schritte sind **keine Aufforderung**, auf der unveränderten Produktionswebsite die noch nicht installierte RC21-Version zu „bestätigen“.  
**Betreiber:** Stefan, Ein-Personen-Freigabe nach automatischer QA.  
**Gerät:** Samsung Galaxy S24 Ultra (SM-S928B), Android 17; Opera Android bevorzugt, Samsung Internet als zweite Engine/Browseroberfläche.  
**Zweck:** Visuelle, bedienbezogene und netzwerknahe Annahmebedingungen nach gesonderter Autorisierung einer nachweisbaren Preview-/Deploy-URL.

## 0. Sperre vor Beginn

- [ ] Die exakte, ausdrücklich autorisierte RC21-Preview-URL liegt vor und ist nach SHA-256-Veröffentlichungsprüfung einem Build zugeordnet.
- [ ] Der tatsächliche veröffentlichte Router entspricht der reviewten Version. Keine Testlinks auf Dateipfade außerhalb der öffentlich freigegebenen Allowlist.
- [ ] Prüflauf ist **nicht** eine automatische Freigabe. Kein PR-Merge, keine Pages-Produktion und keine Änderung an Required Checks aus einem grünen Ergebnis ableiten.

Solange einer dieser Punkte fehlt, gilt `MANUAL_GATE = BLOCKED_NOT_PERFORMED`.

## 1. Aufzuzeichnende Metadaten

| Feld | Ausfüllwert |
|---|---|
| Datum/Uhrzeit Europe/Berlin | offen |
| Preview-URL und gebundener Commit/Manifest-SHA | offen |
| OS-Build unter Android 17 | offen |
| Opera-Version / Samsung-Internet-Version | offen |
| Datenverbindung / WLAN / mobile Daten | offen |
| Erstbesuch / bestehendes Profil / SW-Reset | offen |
| Browser-Navigation, Screenshot- und PDF-IDs | offen |
| Testerentscheidung / Abweichungen | offen |

## 2. Positiv- und Negativkontrollen nach Bereitstellung einer freigegebenen Preview

- [ ] DE `solver-hub.html`: ausgeschlossene Links „Python-Kern“ und „ULSH-01 Roadmap“ behalten exakt die GitHub-Ziel-URL; beim Tippen öffnen sie GitHub, nicht den lokalen Viewer.
- [ ] DE `source.html`: ausgeschlossener „Privacy-Validator im Repository“ bleibt externer GitHub-Link.
- [ ] EN `solver-hub-en.html`: ausgeschlossener „Python core“ bleibt externer GitHub-Link (mit und ohne kontrollierenden Service Worker).
- [ ] `2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html`: alle 14 nachgeladene Roadmap-Links öffnen GitHub; Filterwechsel und Neurendering ändern die Zielwahl nicht.
- [ ] Mindestens ein vom RC19-Manifest freigegebenes Markdown-Dokument öffnet den korrekten lokalen Dokument-Viewer und zeigt vollständigen Inhalt ohne 404/Loader-Spirale.
- [ ] Mindestens eine freigegebene JS/CSS-Quelldatei öffnet den SourceTextViewer, mit gültigem Rohdateilink.
- [ ] Die expliziten Optionen „Quelldatei öffnen“, „Quelldatei herunterladen“, Druck/PDF und Rücknavigation funktionieren im Betriebssystembrowser.
- [ ] Hoch-/Querformat, Browser-Zoom und Displaygrößenmodus verursachen kein abgeschnittenes Menü, unbedienbare Schaltflächen oder horizontalen Überlauf.
- [ ] Erster Aufruf ohne alten Service Worker, Wiederaufruf mit registriertem Worker und Zustand nach Browser-Cache-/SW-Reset ergeben dieselben erlaubten/verbotenen Zielpfade.
- [ ] Offlineverhalten wird **nur dokumentiert**. Fehlende Offline-PWA-Funktion darf weder als Erfolg noch automatisch als RC21-Fehler fehlinterpretiert werden, solange kein Offlinevertrag beschlossen ist.
- [ ] Es sind keine personenbezogenen Bibliothek-, Chat- oder Zugangsdaten in Screenshots, PDFs oder Browser-Logs enthalten.

## 3. Befundprotokoll

Für jede fehlgeschlagene Kontrolle: exakter Link (ohne private Tokens), Ist-/Soll-URL, Uhrzeit, Browser, SW-Zustand, Screenshot-ID, HTTP-Status falls ermittelt, reproduzierbare Schrittreihenfolge. Unklare oder nicht reproduzierbare Fälle erhalten `OPEN`; sie dürfen nicht als `PASS` behandelt werden.

```text
RC22_REAL_ANDROID_EXECUTION = NOT_PERFORMED
RC22_REAL_OPERA_BROWSER = NOT_PERFORMED
RC22_MANUAL_EVIDENCE = NONE
RC22_AUTHORIZED_PREVIEW = BLOCKED
RC22_OWNER_RATIFICATION = NOT_GRANTED
RC22_RELEASE_GATE = HOLD
```
