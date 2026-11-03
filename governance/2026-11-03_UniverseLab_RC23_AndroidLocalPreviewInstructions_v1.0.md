# RC23 – Android-17-Lokaltest mit Termux und Opera (erst NACH Freigabe)

**Status:** `ANLEITUNG_VORBEREITET`, `ZIP_NICHT_AUSGELIEFERT`, `BETREIBERFREIGABE_OFFEN`.

Der Link zur eigentlichen ZIP-Datei **existiert absichtlich noch nicht**. RC23 erstellt bei seinen Tests nur flüchtige ZIP-Kandidaten im CI-Runner. Diese Anleitung darf erst benutzt werden, wenn ein konkretes, separat freigegebenes ZIP mit passendem SHA-256 heruntergeladen wurde.

## Vorbedingungen

- Freigabe ausdrücklich **nur** für lokale Distribution an Stefan und ausschließliche Nutzung auf seinem Galaxy S24 Ultra. Keine öffentliche Pages-Preview.
- Herkunft aus RC23-geprüfter Quelle; ZIP-Hash muss exakt der separat mitgelieferten Prüfsumme entsprechen. Für den aktuellen, **noch nicht freigegebenen** Entwurf lautet der lokale QA-Hash `6de483211a4f42eb42584d9c9d1acc65d48e76a8a87afdf70dd73b0566d5dea7`.
- In Termux muss Python und `unzip` vorhanden sein; Speicherzugriff nach Zustimmung über `termux-setup-storage`.
- Kein bestehender Ordner darf durch Entpacken überschrieben werden. Einen neuen, leeren Testordner wählen.

## Vorbereitete Schritte

Nach Freigabe, wenn das ZIP im Download-Ordner liegt:

1. In Termux nötigenfalls installieren:

   ```bash
   pkg install python unzip
   termux-setup-storage
   ```

2. Prüfsumme prüfen (Dateinamen an das tatsächlich gelieferte ZIP anpassen):

   ```bash
   cd ~/storage/downloads
   sha256sum RC23_LocalPreview.zip
   ```

   Ist der Hash nicht identisch mit dem **freigegebenen** SHA, **nicht** entpacken oder ausführen.

3. Einen eindeutig neuen Ordner erstellen und ohne Überschreiben entpacken:

   ```bash
   mkdir RC23_Lokaltest_20261103
   unzip -n RC23_LocalPreview.zip -d RC23_Lokaltest_20261103
   cd RC23_Lokaltest_20261103
   ```

4. Nur im eigenen Smartphone loopback-lokal ausliefern:

   ```bash
   python -m http.server 8765 --bind 127.0.0.1
   ```

5. Auf **demselben Smartphone** in Opera die Adresse öffnen:

   `http://127.0.0.1:8765/UniverseLab/`

6. Danach die tatsächlichen Links/Viewer gemäß `governance/2026-11-03_UniverseLab_RC22_RealAndroidManualGate_v1.0.md` prüfen. Fehler mit exakter Uhrzeit, Ist-/Soll-URL, Browser-Version, gegebenenfalls Screenshots dokumentieren. Private Chat-/Accountdaten nicht mitschneiden.

7. In Termux den Server nach dem Test mit **Strg+C** beenden. Nicht über andere IP-Adressen, Netzwerktunnel, Portfreigaben oder eine öffentliche Domain erreichbar machen.

## Evidenzgrenzen

Die lokale Website ist eine **nichtkanonische Vorschau**. Im ZIP ist genau ein Routerpfad gegenüber RC19 ersetzt; keine Github-Pages-Installation. Die Website verwendet absolute Pfade mit dem Präfix `/UniverseLab/`, daher ist der lokale HTTP-Server nötig. Ein bloßes Öffnen von `index.html` als `file://` liefert **keine belastbare Parität**.

Das Service-Worker-Autoregistrierungsskript aktiviert sich im normalen Site-Bootstrap nur unter HTTPS. Die lokale HTTP-Vorschau prüft daher nicht die produktive automatische SW-Registrierung. Auch SSL, echte GitHub-Pages-Caches, die Wirkung auf andere Endgeräte, den semantischen Datenschutz und physikalische Hypothesen prüft dieses Verfahren nicht.

```text
RC23_READY_FOR_ANDROID_DISTRIBUTION = NO
RC23_REAL_S24_TEST = NOT_PERFORMED
RC23_PUBLICATION = NONE
RC23_RELEASE_GATE = HOLD
```
