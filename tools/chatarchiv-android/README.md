# UniverseLab ChatArchiv — Android

Eigenständige Android-App für lokal wiederhergestellte ChatGPT-Gespräche.

## Funktionen (Version 0.2.3)

- **UniverseLab**, **Weitere Chats**, **Alle** als getrennte Ansichten.
- Mehrfachimport per Android-Dateiauswahl von `conversations-000.json`, `conversations-001.json` usw. aus einem ChatGPT-Datenexport.
- **Eigene JSON-Dateiliste:** Über „Nur JSON-Dateien im Ordner anzeigen“ wird ein freigegebener Unterordner ausgelesen und eine Mehrfachauswahl angezeigt, die ausschließlich tatsächliche `.json`-Dateinamen enthält. Andere Dateitypen erscheinen in dieser App-Liste nie. Android kann die Freigabe des Download-Hauptordners sperren; dann die gewünschten Exporte in einen Unterordner wie `Download/ChatGPT_Altexporte` kopieren und diesen wählen. Originaldateien werden nicht verändert.
- **Gefilterte System-Dateiauswahl:** Einzelne Chat-Dateien über den MIME-Filter `application/json` wählen; Bilder, Videos und andere Dateitypen werden nicht angefordert. Für Export-ZIPs gibt es einen separaten ZIP-Dialog. Vor dem Import prüft die App zusätzlich die Endung `.json` bzw. `.zip`. Android-Dokumentanbieter bestimmen letztlich, welche Dateien der Systemdialog anzeigt; falsch klassifizierte JSON-Dateien können ggf. fehlen.
- **ZIP-Import ohne Vollentpackung:** Mehrere ältere ChatGPT-Export-ZIPs über den Android-Dateipicker auswählen. Die App liest nur `conversations.json`/`conversations-000.json` usw. direkt aus dem ZIP-Stream und integriert sie über dieselbe Dublettenprüfung. Medienanhänge werden nicht extrahiert.
- Wiederholter Import gleicht Chat-IDs ab: neue Gespräche werden ergänzt; identische Inhalte übersprungen. Eine geänderte Fassung ersetzt den Bestand nur bei **eindeutig neuerem numerischem `update_time`**; dabei wird die alte Fassung zuerst privat gesichert. Ältere Fassungen oder Konflikte mit fehlenden/gleichen Zeitstempeln ersetzen den aktuellen Stand **nicht**. Die Importanzeige zählt sie getrennt. Manuell verschobene Chats behalten ihre Zuordnung.
- Identische Gesprächsinhalte derselben Chat-ID werden über einen lokalen SHA-256-Hash erkannt und **nicht erneut gespeichert**. Die Importanzeige meldet neu/geändert/bereits identisch getrennt. Unterschiedliche Chat-IDs werden nicht wegen ähnlicher Titel automatisch zusammengelegt.
- Volltextsuche über die sichtbaren Nachrichten und Titelsuche, Suche innerhalb eines Gesprächs, Kopieren einzelner Beiträge.
- Der tatsächliche aktive Nachrichtenpfad aus `mapping`/`current_node` wird verfolgt; alternative Versionen und versteckte interne Inhalte werden nicht als normale Chat-Beiträge ausgegeben.
- **GitHub nur lesen:** Öffentliches UniverseLab-Repository auf `main` per anonymen GET-Abfragen durchsuchen und Quelltext kleiner Dateien ansehen. Daneben eingeschränkter GitHub-Pages-Lesemodus ohne JavaScript, Anmeldung, Cookies und fremde Domains.

## Datenschutz und Grenzen

- Gespräche, Suchindex und Titel liegen **ausschließlich im privaten App-Speicher auf dem Android-Gerät**; keine Uploads, Analytics oder Werbung. Android-Backup ist deaktiviert.
- Die App benötigt Internetzugriff **nur für den freiwillig geöffneten GitHub-Bereich**; dieser sendet keine Chattexte, Chat-IDs oder Suchanfragen. Der anonyme GitHub-Aufruf übermittelt technisch bedingt Netzwerkmetadaten wie die IP-Adresse.
- Die App fordert keine Berechtigung für den vollständigen Downloadordner an: die Dateien werden explizit über den Android-Systempicker gewählt.
- **Kein automatischer ChatGPT-Kontosync:** Dafür gibt es hier weder ChatGPT-Login noch eine autorisierte Schnittstelle. Updates erfolgen durch Auswahl eines neuen Exports.
- Die `.json`-Dateien enthalten Text und Nachrichtenstruktur. Bilder/Dateianhänge benötigen die separaten Exportdateien, die bei einem unvollständigen ZIP möglicherweise nicht gerettet wurden.
- Formeln/Markdown werden in Version 0.2.1 **als Originaltext** angezeigt; kein vollständiger TeX-Renderer.
- Die automatische Kategorie basiert auf Stichworten im Gesprächstittel. Per langem Tippen lässt sich die Zuordnung korrigieren.
- `chat.html` und die 40-GB-ZIP müssen **nicht** in die App importiert werden; die sechs `conversations-*.json` genügen.
- Alternativ kann die App ZIP-Archive direkt lesen. Bei abgeschnittenen ZIPs können früh liegende intakte Gesprächs-JSONs gerettet werden, eine vollständige Wiederherstellung ist nicht garantiert. Sobald nach den Gesprächs-JSONs große `file-*.dat`-Anhänge beginnen, beendet der Import die ZIP-Durchsuchung, damit keine Dutzenden GB an Medien verarbeitet werden. Gesprächs-JSONs sind pro ZIP auf insgesamt 800 MiB und 100 Einträge begrenzt.

## Repository-Isolation

Der gesamte Android-Code liegt in `tools/chatarchiv-android/`. Der Build-Workflow `.github/workflows/chatarchiv-android-apk.yml` reagiert ausschließlich auf den isolierten Branch `app/chatarchiv-android-readonly-v1`. Keine privaten Exportdaten oder realen Gespräche werden eingecheckt oder in GitHub Actions verarbeitet. Der Build erstellt ein mit einem kurzlebigen Android-Debug-Schlüssel signiertes APK-**Testpaket**. Die auf dem Telefon installierbare Version wird anschließend außerhalb des öffentlichen Repositories mit einem **privat aufbewahrten stabilen Schlüssel** signiert, damit Folgeversionen regulär aktualisiert werden können. Schlüssel und private Dateien werden nicht in GitHub gespeichert. Es ist keine Play-Store-Veröffentlichung.

## Build

Android SDK 35, JDK 17, Gradle 8.9, Android Gradle Plugin 8.7.3:

```bash
cd tools/chatarchiv-android
gradle :app:testDebugUnitTest :app:assembleDebug
```

Ausgabe: `app/build/outputs/apk/debug/app-debug.apk`. GitHub Actions stellt diese Datei als `UniverseLab-ChatArchiv-Android-APK` bereit.

## Import auf dem Telefon

1. APK installieren (Android fragt ggf. nach Erlaubnis zur Installation aus dieser Quelle).
2. **Chats importieren** → **Rettungsordner auswählen (empfohlen)** wählen und `Download/ChatGPT_Rettung_2026-11-08` freigeben. Die App findet `conversations-000.json` bis `conversations-005.json` automatisch. Für eine sichtbare Liste ausschließlich von JSON-Dateien „Nur JSON-Dateien im Ordner anzeigen“ wählen: Ordner freigeben, gewünschte JSON-Dateien anhaken und importieren.
3. Import abwarten und über **UniverseLab**, **Weitere Chats** oder **Alle** navigieren.
4. Später weitere ChatGPT-Exportdateien in den freigegebenen Ordner kopieren und **Chats importieren** → **Gespeicherten Ordner aktualisieren** wählen. Die Kategoriezuordnung bleibt erhalten.
5. Für ältere Exporte **Chats importieren** → **Ältere Export-ZIPs auswählen** verwenden und eine oder mehrere `.zip`-Dateien auswählen. Bereits vorhandene Chats werden anhand ihrer IDs/Inhaltshashes nicht doppelt gespeichert.
6. Für ältere, einzeln aus ChatGPT Space heruntergeladene `conversations-*.json`-Dateien am besten **Nur JSON-Dateien im Ordner anzeigen** benutzen. Die Dateien müssen direkt im gewählten Unterordner liegen. Alternativ steht **Einzelne JSON-Dateien (Android-Dialog)** bereit; dort können Android-Dateianbieter trotz MIME-Filter auch andere Dateien auflisten, die App weist falsch benannte Dateien jedoch ab. **Nicht den gesamten Downloadordner mit mehreren GB fremder Dokumente importieren.**
7. Nach dem Import die Statusangaben **Ältere Versionen geschützt** und **Unklare Änderungen nicht ersetzt** prüfen. In diesen Fällen bleiben die vorher gespeicherten Fassungen unverändert; die Quell-JSON/ZIPs behalten, bis ein Vergleich durchgeführt wurde.
