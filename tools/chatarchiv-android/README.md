# UniverseLab ChatArchiv — Android

Eigenständige Android-App für lokal wiederhergestellte ChatGPT-Gespräche.

## Funktionen (Version 0.4.1 · Forschungsnavigator-QA-Vorschau)

- **UniverseLab**, **Weitere Chats**, **Alle** als getrennte Ansichten.
- **Forschungsnavigator (neu, rein lokal):** Durchsucht gespeicherte sichtbare Gesprächsbeiträge nach ausdrücklich benannten offenen Punkten, Blockern, Widersprüchen und nächsten Schritten, zeigt Fundstelle und heuristische Prüffrage/Prüfweg und springt zum Originalbeitrag. Projektchats oder auf Wunsch alle Chats; Abbruch jederzeit. Keine automatischen Änderungen oder Cloud-Anfragen.
- **QA-Verbesserung 0.4.1:** Nicht jeder Worttreffer ist ein Blocker. Explizite Negationen und reine Aufgaben-/Feldvorlagen werden nun konservativ ausgefiltert; echte Statussperren wie `NOT RELEASED` bleiben erhalten. Hinweise sind nach Art filterbar und über 100 Fundstellen hinaus in Schritten zu je 100 nachladbar. Der Bildschirm bleibt rein lesend.
- Mehrfachimport per Android-Dateiauswahl von `conversations-000.json`, `conversations-001.json` usw. aus einem ChatGPT-Datenexport.
- **ZIP-Import ohne Vollentpackung:** Mehrere ältere ChatGPT-Export-ZIPs über den Android-Dateipicker auswählen. Die App liest nur `conversations.json`/`conversations-000.json` usw. direkt aus dem ZIP-Stream und integriert sie über dieselbe Dublettenprüfung. Medienanhänge werden nicht extrahiert.
- **Optionale Vollspeicher-Suche:** Nach ausdrücklich erteilter Android-Sonderberechtigung „Zugriff auf alle Dateien“ kann die App den gemeinsam genutzten internen Speicher samt Unterordnern rekursiv durchsuchen. Gefunden werden ausschließlich `conversations*.json` und `.zip`-Archive, die solche Dateien enthalten. Eine Ergebnisvorschau verlangt eine weitere Bestätigung vor dem Import; Abbruch ist möglich. Bei großen ZIPs wird nur deren Inhaltsverzeichnis geprüft; der Import liest Gesprächs-JSONs per gezieltem ZIP-Zugriff und überspringt die übrigen Dateien. Suchen und Importieren laufen ohne Cloud-Upload.
- **Versionsschutz bei älteren Exporten:** Bei identischen Chat-IDs wird der Inhalt verglichen. Abweichende ältere oder gleich alte, nicht umfangreichere Varianten landen im privaten Versionsordner; sie überschreiben keine aktuellere Chatfassung. Bei neuerer Fassung wird die alte lokal gesichert. Für den privaten Versionsbestand gilt zum Speicherschutz ein Limit von 1 GiB; bei Erreichen meldet die App einen Fehler und lässt die bisherige Chatfassung unverändert. Die aktuelle App zeigt weiterhin nur die Hauptfassung an; eine Oberfläche zur Ansicht der archivierten Varianten ist noch nicht enthalten.
- Wiederholter Import ist die **Update-Funktion**: IDs werden abgeglichen, vorhandene Gespräche aktualisiert, neue ergänzt. Manuell verschobene Chats behalten ihre Zuordnung.
- Identische Gesprächsinhalte derselben Chat-ID werden über einen lokalen SHA-256-Hash erkannt und **nicht erneut gespeichert**. Die Importanzeige meldet neu/geändert/bereits identisch getrennt. Unterschiedliche Chat-IDs werden nicht wegen ähnlicher Titel automatisch zusammengelegt.
- Volltextsuche über die sichtbaren Nachrichten und Titelsuche, Suche innerhalb eines Gesprächs, Kopieren einzelner Beiträge.
- **Einzelne Gespräche exportieren:** Über „Exportieren“ im Chat kann wahlweise eine vollständige JSON mit dem gespeicherten Mapping und allen vorhandenen Antwortzweigen, eine lesbare Markdown-, TXT- oder HTML-Datei erstellt werden. Die Text-/Markdown-/HTML-Varianten enthalten den aktiven sichtbaren Pfad; die HTML-Variante verwendet eine offlinefähige, rein lokale Formeldarstellung. Über Androids „Dokument erstellen“-Auswahl bestimmt der Nutzer selbst das Ziel.
- **Gesamtes aktives Archiv als ZIP sichern:** Auf dem Startbildschirm kann ein ZIP mit allen derzeitigen Chat-Hauptfassungen erzeugt werden. Es enthält eine reimportierbare `conversations-000.json` als JSON-Array und ein `chatarchiv_manifest.json` mit den Kategoriezuordnungen. Beim späteren Import werden die Kategoriezuordnungen auf neu hinzugekommene Chat-IDs angewendet. Medienanhänge und der separate Altversionsspeicher sind aus Speichergründen **nicht** Teil dieses ZIPs.
- **Drei Formeldarstellungen:** Originaltext unverändert, selektive Unicode-Umsetzung gebräuchlicher LaTeX-Befehle oder Monospace-Quelltextansicht. Der Unicode-Modus ist bewusst ein linearer, nicht vollständiger TeX-Renderer; die gespeicherten Chatdaten und Exporte bleiben unverändert (außer der expliziten lesbaren HTML-Variante).
- **Markiermodus über mehrere Beiträge:** Während die normale Chatliste eine Auswahl innerhalb einzelner Beiträge unterstützt, stellt der zusätzliche Markiermodus den sichtbaren Gesprächspfad in einem durchgehenden auswählbaren Text dar. Zum Schutz vor übergroßen Android-Textansichten sind 2 Millionen Zeichen anzeigbar; für größere Gespräche den Export verwenden.
- Der tatsächliche aktive Nachrichtenpfad aus `mapping`/`current_node` wird verfolgt; alternative Versionen und versteckte interne Inhalte werden nicht als normale Chat-Beiträge ausgegeben.
- **GitHub nur lesen:** Öffentliches UniverseLab-Repository auf `main` per anonymen GET-Abfragen durchsuchen und Quelltext kleiner Dateien ansehen. Daneben eingeschränkter GitHub-Pages-Lesemodus ohne JavaScript, Anmeldung, Cookies und fremde Domains.

## Forschungsnavigator: Aussagekraft und Grenzen

Der Navigator ist zunächst ein **regelbasierter Such- und Priorisierungsassistent**, kein eigenständig mathematisch argumentierendes KI-System. Er erkennt ausdrücklich markierte Textstellen mit Stichwörtern wie `[OFFEN]`, `BLOCKER`, `WIDERSPRUCH`, `PENDING`, `TODO` oder `Nächster Schritt` und legt eine nach Priorität geordnete Prüfliste an.

- Lokal und lesend: Datenquelle sind allein die bereits importierten Chats auf dem Android-Gerät. Weder Chattext noch daraus erzeugte Fundstellen werden an GitHub oder einen KI-Dienst gesendet.
- Quellengebunden: Pro Fundstelle werden Chat-Titel, Rolle, Nummer des sichtbaren Beitrags und ein Textausschnitt angezeigt. Antippen springt zum passenden Beitrag des Originalchats.
- Bewusst begrenzt: Für einen schnellen Screening-Durchlauf betrachtet die App die letzten 350 sichtbaren Beiträge pro Chat, höchstens 120.000 Zeichen pro Beitrag, maximal fünf Funde pro Chat. Zunächst erscheinen bis zu 100 Funde; weitere können in 100er-Schritten nachgeladen werden.
- Kein Statusabgleich: Wiederholte oder inzwischen erledigte Aufgaben können weiterhin auftauchen. Ein Worttreffer ist **kein Beweis**, dass die Frage sachlich ungelöst oder aktuell ist. Die Priorität ist eine Heuristik, kein wissenschaftlicher Schweregrad.
- Der angezeigte Prüfweg ist ein **Vorschlag**: Definitionsprüfung, Rechnungs-/Dimensionskontrolle, Konvergenz- oder Datenabgleich je nach erkanntem Thema. Es werden keine physikalischen Behauptungen automatisch verifiziert, keine neuen Sätze bewiesen und keine Ergebnisse kanonisiert.
- Für eine spätere, wirklich eigenständigere Fragenfindung sind nachvollziehbare Hypothesenbildung, Statusabgleich gegen aktuelle Quellen, Widerspruchspaare, reproduzierbare Prüftests und explizite Nutzerfreigabe als eigene Ausbauetappen erforderlich.

### Sicheres Testen auf dem Smartphone

Die in GitHub Actions erzeugte **Debug-APK** hat in diesem Forschungszweig die gesonderte Android-Paketkennung `de.universelab.chatarchiv.researchqa` und den Icon-Titel `UniverseLab Forschung QA (Test)`. Sie wird parallel zur bestehenden `de.universelab.chatarchiv` installiert; die bisherigen privaten Daten bleiben unabhängig und unverändert.

Ein Austausch von Chatdaten zwischen den getrennten App-Speichern erfolgt **nicht automatisch**. Wer die Vorschau testen möchte, kann in der bisherigen App zunächst **Alle Gespräche als ZIP sichern** wählen und diese Sicherung bewusst in die Vorschau importieren. Der ZIP-Export enthält aktive Chat-Hauptfassungen und Kategorien, **nicht** Altversionsverläufe oder externe Medienanhänge. Das ist ein Testpaket; nicht die bestehende App deinstallieren, um eine Signaturkollision zu umgehen.

## Datenschutz und Grenzen

- Gespräche, Suchindex und Titel liegen **ausschließlich im privaten App-Speicher auf dem Android-Gerät**; keine Uploads, Analytics oder Werbung. Android-Backup ist deaktiviert.
- Die App benötigt Internetzugriff **nur für den freiwillig geöffneten GitHub-Bereich**; dieser sendet keine Chattexte, Chat-IDs oder Suchanfragen. Der anonyme GitHub-Aufruf übermittelt technisch bedingt Netzwerkmetadaten wie die IP-Adresse.
- Der bestehende Ordner-/Datei-/ZIP-Import über den Android-Systempicker bleibt ohne Vollspeicherberechtigung nutzbar. Die **neue** Sonderberechtigung `MANAGE_EXTERNAL_STORAGE` wird nur bei Auswahl der Vollspeicher-Suche von Android angefordert. Sie erlaubt technisch auch weitere Zugriffe auf den gemeinsamen Speicher; die implementierte Scan-/Import-Funktion nutzt sie ausschließlich lesend. Android sperrt weiterhin geschützte App-Datenbereiche. Diese Sideload-App ist nicht für die Play-Store-Veröffentlichung vorgesehen.
- **Kein automatischer ChatGPT-Kontosync:** Dafür gibt es hier weder ChatGPT-Login noch eine autorisierte Schnittstelle. Updates erfolgen durch Auswahl eines neuen Exports.
- Die `.json`-Dateien enthalten Text und Nachrichtenstruktur. Bilder/Dateianhänge benötigen die separaten Exportdateien, die bei einem unvollständigen ZIP möglicherweise nicht gerettet wurden.
- Formeln bleiben im Archiv originalgetreu gespeichert. Der optionale Unicode-Modus ist eine Annäherung für häufige Befehle, keine verlustfreie mathematische Satzengine. Für exakte Provenienz und Kopien weiterhin „Original“ oder vollständigen JSON-Export verwenden.
- Bei allen Exporten können Android-Dokumentanbieter auch Cloud-Dienste anbieten. **Nur der vom Nutzer gewählte Zielanbieter** erhält die Datei; es gibt keinen selbsttätigen Chat-Upload durch die App.
- Die automatische Kategorie basiert auf Stichworten im Gesprächstittel. Per langem Tippen lässt sich die Zuordnung korrigieren.
- `chat.html` und eine 40-GB-ZIP müssen **nicht** importiert werden, wenn die darin enthaltenen Chat-JSON-Dateien bereits vorhanden sind. Die neue Vollspeicher-Suche kann auch große vollständige ZIPs erkennen und daraus nur Chat-JSONs lesen; beschädigte oder mehrteilige Archive sind davon ausgenommen.
- Alternativ kann die App ZIP-Archive direkt lesen. Bei abgeschnittenen ZIPs können früh liegende intakte Gesprächs-JSONs gerettet werden, eine vollständige Wiederherstellung ist nicht garantiert. Sobald nach den Gesprächs-JSONs große `file-*.dat`-Anhänge beginnen, beendet der Import die ZIP-Durchsuchung, damit keine Dutzenden GB an Medien verarbeitet werden. Gesprächs-JSONs sind pro ZIP auf insgesamt 3 GiB und 100 Einträge begrenzt.

## Repository-Isolation

Der gesamte Android-Code liegt in `tools/chatarchiv-android/`. Der Build-Workflow `.github/workflows/chatarchiv-android-apk.yml` reagiert auf die isolierten App-Zweige `app/chatarchiv-android-readonly-v1` und `app/chatarchiv-research-navigator-v0` sowie den isolierten QA-Zweig `app/chatarchiv-research-qa-v041`; `main` bleibt unberührt. Keine privaten Exportdaten oder realen Gespräche werden eingecheckt oder in GitHub Actions verarbeitet. Der Build erstellt ein installierbares, automatisch mit dem Android-Debug-Schlüssel signiertes APK-**Testpaket**. Es ist keine Play-Store-Veröffentlichung.

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
7. Einen Chat öffnen → **Exportieren** und zwischen vollständigem JSON, Markdown, TXT und HTML auswählen. Die JSON-Datei enthält auch inaktive Zweige der gespeicherten Unterhaltung; die lesbaren Formate enthalten den aktiven sichtbaren Verlauf.
8. Einen Chat öffnen → **Original / Unicode / Monospace** für die Anzeige wählen. Mit **Markieren** eine durchgehende Markieransicht über mehrere Beiträge öffnen.
9. Auf der Hauptseite **Alle Gespräche als ZIP sichern** für ein reimportierbares Backup der aktuellen Hauptfassungen und ihrer Kategoriezuordnungen wählen. Altversionen und externe Medienanhänge sind dabei nicht eingeschlossen.
10. **Forschungsnavigator · offene Fragen** öffnen: Projektchats werden zunächst lokal gesichtet. **Alle Chats prüfen** erweitert den Suchbereich; eine Fundstelle antippen, um den Originalbeitrag zu sehen.
