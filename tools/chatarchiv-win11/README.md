# UniverseLab ChatArchiv – Windows 11 (v0.1.0)

Eigenständige Windows-11-Desktopanwendung als **erster funktionsfähiger Port** der Android-App 0.5.9.
Die APK selbst ist Android-spezifisch und kann unter Windows nicht nativ verwendet werden.

## Installation (Windows 11 x64)

1. Das von GitHub Actions gebaute Artefakt `UniverseLab-ChatArchiv-Win11-v0.1.0` herunterladen und entpacken.
2. `UniverseLab.ChatArchiv.Win11.exe` doppelt anklicken. Sie ist eine selbstenthaltende .NET-8-Windows-Anwendung; keine separate .NET-Installation nötig.
3. Über **JSON / ZIP importieren** den offiziellen ChatGPT-Export oder ein von der Android-App erstelltes ZIP auswählen. Für die gezielte lokale Suche kann auch **Ordner durchsuchen** genutzt werden.

## Implementiert

- Eigenes Windows-Fenster (WinForms), lokale Ablage unter `%LOCALAPPDATA%\UniverseLab\ChatArchiv-Win11`.
- Streaming-Import von `conversations*.json` aus JSON oder ZIP; keine Extraktion der Medienanhänge.
- Chat-ID-Dublettenprüfung, neuere Fassungen ersetzen ältere und erhalten alte Fassung separat; Kategoriezuordnung bleibt erhalten.
- Liest den Android-Archiv-Export `chatarchiv_manifest.json` (`category_by_id`) und sichert selbst kompatible ZIPs.
- Trennung UniverseLab / Weitere Chats, Volltextsuche, sichtbarer aktiver Gesprächspfad, Original-JSON-Erhalt und Markdown-/TXT-/HTML-/JSON-Export.
- Konservativer Forschungsnavigator mit maximal 5 Hinweisen je Chat, bis zu 12 markierbaren Hinweisen für eine manuelle Chat-Übergabe. **[HEURISTISCH]** – keine physikalische Statusbestätigung.
- Kein automatischer ChatGPT-Login, kein automatisches Hochladen, keine GitHub-Schreibzugriffe.

## Grenzen und Sicherheit

- **Früher Windows-Port:** Nicht alle Android-Funktionen sind bereits vorhanden (u. a. detaillierte Status-Zeitachsen, Versionsübersicht, optionale GitHub-Leseoberfläche, Formel-Ansichtsmodi, große Scrollgriff-Gesten).
- Die Windows-Anwendung übernimmt keine Chatdaten automatisch aus der Android-App. Die Übertragung erfolgt ausdrücklich über die von Android erzeugte ZIP-Archivdatei oder über die ChatGPT-Exportdateien.
- Der Forschungsnavigator erkennt Textsignale, aber nicht deren heutige Wahrheit. Fundstellen niemals ohne Original- und Kanonprüfung freigeben.
- Medienanhänge werden nicht importiert. HTML-Export ist vollständig offline und lädt keine externen Ressourcen.
- Für ZIP-Import sind maximal 100 passende JSON-Einträge und zusammen höchstens 3 GiB unkomprimierte Gesprächs-JSON vorgesehen. Viele oder große Anhänge werden ignoriert.
- Die Anwendung ist ein quelloffener Entwicklungsbuild ohne kostenpflichtiges Codesignatur-Zertifikat. Windows SmartScreen kann deshalb einen **Unbekannter Herausgeber**-Hinweis zeigen; Datei nur aus dem von uns geprüften GitHub-Build beziehen, nicht Schutzfunktionen pauschal abschalten.
- Win11 x64 wurde automatisiert gebaut/getestet; ein manueller Installationstest auf Stefans PC bleibt erforderlich.

## Reproduzierbarer Build

```powershell
dotnet publish tools/chatarchiv-win11/UniverseLab.ChatArchiv.Win11.csproj -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:PublishTrimmed=false -o out/win11
./out/win11/UniverseLab.ChatArchiv.Win11.exe --self-test
```

Der Windows-Build hat keine Verbindung zum produktiven Android-Signaturschlüssel. Das GitHub-Repository erhält weder private Archivdaten noch private Schlüssel.
