# UniverseLab ChatArchiv — Android

Eigenständige Android-App für lokal wiederhergestellte ChatGPT-Gespräche.

## Funktionen (Version 0.1)

- **UniverseLab**, **Weitere Chats**, **Alle** als getrennte Ansichten.
- Mehrfachimport per Android-Dateiauswahl von `conversations-000.json`, `conversations-001.json` usw. aus einem ChatGPT-Datenexport.
- Wiederholter Import ist die **Update-Funktion**: IDs werden abgeglichen, vorhandene Gespräche aktualisiert, neue ergänzt. Manuell verschobene Chats behalten ihre Zuordnung.
- Volltextsuche über die sichtbaren Nachrichten und Titelsuche, Suche innerhalb eines Gesprächs, Kopieren einzelner Beiträge.
- Der tatsächliche aktive Nachrichtenpfad aus `mapping`/`current_node` wird verfolgt; alternative Versionen und versteckte interne Inhalte werden nicht als normale Chat-Beiträge ausgegeben.
- **GitHub nur lesen:** Öffentliches UniverseLab-Repository auf `main` per anonymen GET-Abfragen durchsuchen und Quelltext kleiner Dateien ansehen. Daneben eingeschränkter GitHub-Pages-Lesemodus ohne JavaScript, Anmeldung, Cookies und fremde Domains.

## Datenschutz und Grenzen

- Gespräche, Suchindex und Titel liegen **ausschließlich im privaten App-Speicher auf dem Android-Gerät**; keine Uploads, Analytics oder Werbung. Android-Backup ist deaktiviert.
- Die App benötigt Internetzugriff **nur für den freiwillig geöffneten GitHub-Bereich**; dieser sendet keine Chattexte, Chat-IDs oder Suchanfragen. Der anonyme GitHub-Aufruf übermittelt technisch bedingt Netzwerkmetadaten wie die IP-Adresse.
- Die App fordert keine Berechtigung für den vollständigen Downloadordner an: die Dateien werden explizit über den Android-Systempicker gewählt.
- **Kein automatischer ChatGPT-Kontosync:** Dafür gibt es hier weder ChatGPT-Login noch eine autorisierte Schnittstelle. Updates erfolgen durch Auswahl eines neuen Exports.
- Die `.json`-Dateien enthalten Text und Nachrichtenstruktur. Bilder/Dateianhänge benötigen die separaten Exportdateien, die bei einem unvollständigen ZIP möglicherweise nicht gerettet wurden.
- Formeln/Markdown werden in Version 0.1 **als Originaltext** angezeigt; kein vollständiger TeX-Renderer.
- Die automatische Kategorie basiert auf Stichworten im Gesprächstittel. Per langem Tippen lässt sich die Zuordnung korrigieren.
- `chat.html` und die 40-GB-ZIP müssen **nicht** in die App importiert werden; die sechs `conversations-*.json` genügen.

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
2. **Import / Update** wählen und im Dateiauswahldialog die sechs `conversations-000.json` bis `conversations-005.json` markieren, die sich im zuvor angelegten Ordner `Download/ChatGPT_Rettung_2026-11-08` befinden.
3. Import abwarten und über **UniverseLab**, **Weitere Chats** oder **Alle** navigieren.
4. Später weitere ChatGPT-Exportdateien über **Import / Update** hinzufügen.
