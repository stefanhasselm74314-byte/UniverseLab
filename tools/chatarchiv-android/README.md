# UniverseLab ChatArchiv — Android

Eigenständige Android-App für lokal wiederhergestellte ChatGPT-Gespräche.

## Funktionen (Version 0.2.4)

- **UniverseLab**, **Weitere Chats**, **Alle** als getrennte Ansichten.
- Mehrfachimport per Android-Dateiauswahl von `conversations-000.json`, `conversations-001.json` usw. aus einem ChatGPT-Datenexport.
- **ZIP-Import ohne Vollentpackung:** Mehrere ältere ChatGPT-Export-ZIPs über den Android-Dateipicker auswählen. Die App liest nur `conversations.json`/`conversations-000.json` usw. direkt aus dem ZIP-Stream und integriert sie über dieselbe Dublettenprüfung. Medienanhänge werden nicht extrahiert.
- **Optionale Vollspeicher-Suche:** Nach ausdrücklich erteilter Android-Sonderberechtigung „Zugriff auf alle Dateien“ kann die App den gemeinsam genutzten internen Speicher samt Unterordnern rekursiv durchsuchen. Gefunden werden ausschließlich `conversations*.json` und `.zip`-Archive, die solche Dateien enthalten. Eine Ergebnisvorschau verlangt eine weitere Bestätigung vor dem Import; Abbruch ist möglich. Bei großen ZIPs wird nur deren Inhaltsverzeichnis geprüft; der Import liest Gesprächs-JSONs per gezieltem ZIP-Zugriff und überspringt die übrigen Dateien. Suchen und Importieren laufen ohne Cloud-Upload.
- **Versionsschutz bei älteren Exporten:** Bei identischen Chat-IDs wird der Inhalt verglichen. Abweichende ältere oder gleich alte, nicht umfangreichere Varianten landen im privaten Versionsordner; sie überschreiben keine aktuellere Chatfassung. Bei neuerer Fassung wird die alte lokal gesichert. Für den privaten Versionsbestand gilt zum Speicherschutz ein Limit von 1 GiB; bei Erreichen meldet die App einen Fehler und lässt die bisherige Chatfassung unverändert. Die aktuelle App zeigt weiterhin nur die Hauptfassung an; eine Oberfläche zur Ansicht der archivierten Varianten ist noch nicht enthalten.
- Wiederholter Import ist die **Update-Funktion**: IDs werden abgeglichen, vorhandene Gespräche aktualisiert, neue ergänzt. Manuell verschobene Chats behalten ihre Zuordnung.
- Identische Gesprächsinhalte derselben Chat-ID werden über einen lokalen SHA-256-Hash erkannt und **nicht erneut gespeichert**. Die Importanzeige meldet neu/geändert/bereits identisch getrennt. Unterschiedliche Chat-IDs werden nicht wegen ähnlicher Titel automatisch zusammengelegt.
- Volltextsuche über die sichtbaren Nachrichten und Titelsuche, Suche innerhalb eines Gesprächs, Kopieren einzelner Beiträge.
- Der tatsächliche aktive Nachrichtenpfad aus `mapping`/`current_node` wird verfolgt; alternative Versionen und versteckte interne Inhalte werden nicht als normale Chat-Beiträge ausgegeben.
- **GitHub nur lesen:** Öffentliches UniverseLab-Repository auf `main` per anonymen GET-Abfragen durchsuchen und Quelltext kleiner Dateien ansehen. Daneben eingeschränkter GitHub-Pages-Lesemodus ohne JavaScript, Anmeldung, Cookies und fremde Domains.

## Datenschutz und Grenzen

- Gespräche, Suchindex und Titel liegen **ausschließlich im privaten App-Speicher auf dem Android-Gerät**; keine Uploads, Analytics oder Werbung. Android-Backup ist deaktiviert.
- Die App benötigt Internetzugriff **nur für den freiwillig geöffneten GitHub-Bereich**; dieser sendet keine Chattexte, Chat-IDs oder Suchanfragen. Der anonyme GitHub-Aufruf übermittelt technisch bedingt Netzwerkmetadaten wie die IP-Adresse.
- Der bestehende Ordner-/Datei-/ZIP-Import über den Android-Systempicker bleibt ohne Vollspeicherberechtigung nutzbar. Die **neue** Sonderberechtigung `MANAGE_EXTERNAL_STORAGE` wird nur bei Auswahl der Vollspeicher-Suche von Android angefordert. Sie erlaubt technisch auch weitere Zugriffe auf den gemeinsamen Speicher; die implementierte Scan-/Import-Funktion nutzt sie ausschließlich lesend. Android sperrt weiterhin geschützte App-Datenbereiche. Diese Sideload-App ist nicht für die Play-Store-Veröffentlichung vorgesehen.
- **Kein automatischer ChatGPT-Kontosync:** Dafür gibt es hier weder ChatGPT-Login noch eine autorisierte Schnittstelle. Updates erfolgen durch Auswahl eines neuen Exports.
- Die `.json`-Dateien enthalten Text und Nachrichtenstruktur. Bilder/Dateianhänge benötigen die separaten Exportdateien, die bei einem unvollständigen ZIP möglicherweise nicht gerettet wurden.
- Formeln/Markdown werden in Version 0.1 **als Originaltext** angezeigt; kein vollständiger TeX-Renderer.
- Die automatische Kategorie basiert auf Stichworten im Gesprächstittel. Per langem Tippen lässt sich die Zuordnung korrigieren.
- `chat.html` und eine 40-GB-ZIP müssen **nicht** importiert werden, wenn die darin enthaltenen Chat-JSON-Dateien bereits vorhanden sind. Die neue Vollspeicher-Suche kann auch große vollständige ZIPs erkennen und daraus nur Chat-JSONs lesen; beschädigte oder mehrteilige Archive sind davon ausgenommen.
- Alternativ kann die App ZIP-Archive direkt lesen. Bei abgeschnittenen ZIPs können früh liegende intakte Gesprächs-JSONs gerettet werden, eine vollständige Wiederherstellung ist nicht garantiert. Sobald nach den Gesprächs-JSONs große `file-*.dat`-Anhänge beginnen, beendet der Import die ZIP-Durchsuchung, damit keine Dutzenden GB an Medien verarbeitet werden. Gesprächs-JSONs sind pro ZIP auf insgesamt 800 MiB und 100 Einträge begrenzt.

## Repository-Isolation

Der gesamte Android-Code liegt in `tools/chatarchiv-android/`. Der Build-Workflow `.github/workflows/chatarchiv-android-apk.yml` reagiert ausschließlich auf den isolierten Branch `app/chatarchiv-android-readonly-v1`. Keine privaten Exportdaten oder realen Gespräche werden eingecheckt oder in GitHub Actions verarbeitet. Der Build erstellt ein installierbares, automatisch mit dem Android-Debug-Schlüssel signiertes APK-**Testpaket**. Es ist keine Play-Store-Veröffentlichung.

## Build

Android SDK 35, JDK 17, Gradle 8.9, Android Gradle Plugin 8.7.3:

```bash
cd tools/chatarchiv-android
gradle :app:testDebugUnitTest :app:assembleDebug
```

Ausgabe: `app/build/outputs/apk/debug/app-debug.apk`. GitHub Actions stellt diese Datei als `UniverseLab-ChatArchiv-Android-APK` bereit.

## Import auf dem Telefon

1. APK installieren (Android fragt ggf. nach Erlaubnis zur Installation aus dieser Quelle).
2. **Chats importieren** → **Rettungsordner auswählen (empfohlen)** wählen und `Download/ChatGPT_Rettung_2026-11-08` freigeben. Die App findet `conversations-000.json` bis `conversations-005.json` automatisch. Alternativ können einzelne JSON-Dateien ausgewählt werden.
3. Import abwarten und über **UniverseLab**, **Weitere Chats** oder **Alle** navigieren.
4. Später weitere ChatGPT-Exportdateien in den freigegebenen Ordner kopieren und **Chats importieren** → **Gespeicherten Ordner aktualisieren** wählen. Die Kategoriezuordnung bleibt erhalten.
5. Für ältere Exporte **Chats importieren** → **Ältere Export-ZIPs auswählen** verwenden und eine oder mehrere `.zip`-Dateien auswählen. Bereits vorhandene Chats werden anhand ihrer IDs/Inhaltshashes nicht doppelt gespeichert.
6. **Optional:** **Chats importieren** → **Gesamten Handyspeicher nach Chat-Exporten durchsuchen** → Android-Berechtigung ausdrücklich erteilen. Nach der Suche zeigt die App die Anzahl gefundener Gesprächs-JSONs/ZIPs und wartet auf die Importbestätigung. Die Berechtigung kann jederzeit in den Android-App-Einstellungen entzogen werden.
