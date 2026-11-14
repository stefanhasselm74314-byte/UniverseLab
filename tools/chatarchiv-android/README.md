# UniverseLab ChatArchiv — Android

## Sammelupdate v0.5.19 · Archivwerkzeuge (Draft, Samsung-Gerätetest offen)

Diese Version bündelt **drei** zusammengehörige Funktionen – ohne separate Zwischenversionen:

### A. Archiv-Gesundheitsbericht (nur lesen)
- Neuer Hauptmenü-Eintrag **„Archivwerkzeuge · Prüfen, Auswählen, Sichern“** → „Archiv-Gesundheitsprüfung“.
- Untersucht aktive und im Papierkorb liegende Chats auf fehlende Hauptfassungen, abweichende SHA-256-Prüfsummen, unlesbare JSON-Daten, unpassende Chat-IDs, fehlende Suchindizes und 0 sichtbare Beiträge. Zeigt Anzahl gesicherter Altversionen und höchstens 16 Beispiele mit Kurz-ID.
- Begrenzung: Chatdateien über 16 MiB werden nicht vollständig geladen; sie erscheinen als **ungeprüft**, nicht fälschlich als leer oder beschädigt. Prüflauf abbrechbar. **Kein automatisches Löschen**.

### B. Mehrfachauswahl und geschützte Sammelaktionen
- Mehrfachauswahl bezieht sich **ausschließlich auf die gerade angezeigten Suchtreffer**. Android-Auswahlliste mit Mehrfachauswahl und „Alle auswählen / Auswahl aufheben“, inklusive kurzem Chat-ID-Hinweis für identische Titel.
- Nach erneuter expliziter Bestätigung können ausgewählte aktive Chats gesammelt **UniverseLab**, **Weitere Chats** oder dem **Papierkorb** zugeordnet werden.
- Die Änderung wird nur nach Prüfung sämtlicher Chat-IDs in **einem gemeinsamen Index-Schreibvorgang** gespeichert; bei Schreibfehlern wird der vorherige In-Memory-Zustand zurückgesetzt. Im Stapelmodus gibt es keine endgültige Löschung und keine Änderung an Original-Exportdateien.

### C. Umfangreicheres ZIP-Backup mit nachprüfbaren Prüfsummen
- Gesonderte Funktion **„Vollbackup inklusive Papierkorb und Altversionen“**. Sicherung umfasst private Hauptfassungen (aktiv und Papierkorb), vorhandene Altversionsdateien, Suchindizes und den originalen Gesprächsindex (Kategorien, Papierkorb-Metadaten).
- ZIP-Einträge werden speicherschonend übertragen und in `manifest.json` mit SHA-256 und Dateigröße referenziert; die unabhängige Funktion **„Vollbackup mit SHA-256 prüfen“** vergleicht sämtliche Dateien ohne Extraktion.
- Nur die beim ChatArchiv tatsächlich lokal gespeicherten Daten sind enthalten. Medienanhänge, die bislang ausschließlich in externen ChatGPT-Exporten liegen, bleiben außerhalb dieser Sicherung. Fehlende Suchindizes werden im Manifest vermerkt.
- Das neue Gesamtformat ist **noch nicht für eine automatische Wiederherstellung freigegeben**. Das gewohnte ZIP für aktive Hauptfassungen bleibt zusätzlich unverändert verfügbar. Bei unvollständigem Export nicht von einer erfolgreichen Sicherung ausgehen.
- ZIP-Ausgabe nur nach Auswahl eines konkreten Ziels über Android-SAF; ein Cloud-Anbieter als Ziel könnte die Datei hochladen. Keine Daten an GitHub.

### Version und Testregeln
- `versionName 0.5.19`, `versionCode 35`; isolierter Debug-QA-Paketname `de.universelab.chatarchiv.researchqa19`.
- Bestehende Installationen, insbesondere v0.5.12 produktiv und v0.5.16 mit Papierkorb, bleiben unangetastet. Keine neue Android-Berechtigung, kein ChatGPT-Weblogin und keine Änderung an Quell-Exportdateien.
- Build und JVM-Testfälle für das Backup samt Prüfsummen-/Abbruchschutz sowie vorhandene Such-/Archivtests sind Voraussetzungen für die Geräteabnahme.
- `main` bleibt unverändert. **[OFFEN]** GitHub-CI, signierte QA-APK und Gerätetest; keine automatische Freigabe.



## Version 0.5.18 · ODER-Suche nach Anzahl verschiedener Trefferwörter sortieren

- `chats Ui New` sucht weiterhin alle Chats mit mindestens einem der drei **verschiedenen** Wörter. Ausgabe-Reihenfolge: **3 von 3**, dann **2 von 3**, zuletzt **1 von 3** passenden Wörtern.
- Gesuchte Ausdrücke werden je Chat und Suchterm höchstens einmal gewertet, auch wenn das Wort mehrfach vorkommt oder zugleich im Titel und im sichtbaren Nachrichtentext steht. Wiederholte identische Eingabewörter beeinflussen die Gewichtung nicht.
- Treffer in Titel und Nachrichten werden kombiniert. Die Suche liest den privaten `.search`-Index dazu einmal stromweise pro Chat; ein früher Titeltreffer beendet die Suche **nicht** mehr vorzeitig.
- Die bestehende Anführungszeichen-Logik bleibt: `"New Chat"` zählt als **ein** vollständiger Suchausdruck. `titel:"New Chat"` bleibt ausschließlich auf den Titel beschränkt.
- Chats mit gleich vielen Trefferausdrücken behalten ihre bisherige Reihenfolge (wie zuvor neueste zuerst). Ohne Suchtext bleibt die bisherige Sortierung vollständig unverändert.
- Neue JVM-Tests für 3–2–1-Reihenfolge, stabile Gleichstände, Titel-und-Inhalt-Kombination, wiederholte Wörter, Begrenzung auf passende Kategorien und Leersuche.
- `versionCode 34`, `versionName 0.5.18`, isolierter QA-Debug-App-Name `UniverseLab Forschung QA v0.5.18` und Paketkennung `de.universelab.chatarchiv.researchqa18`. Keine Überschreibung vorhandener QA-Archive, keine Änderung an gespeicherten Chats oder Papierkorb.
- **OFFEN:** CI-/Android-Build, Berechtigungsprüfung und Gerätestest auf Galaxy S24 Ultra. Kein neues signaturkompatibles produktives APK ohne bisherigen privaten Release-Schlüssel.



## Version 0.5.17 · flexible ODER-Suche und exakte Wortfolgen (Android-Gerätetest offen)

- **Unverbundene Wörter sind Alternativen (ODER):** `New Chats` liefert alle Chats, in deren Titel oder indexierten sichtbaren Nachrichten `New` **oder** `Chats` als eigenständiges Wort vorkommt; ein Chat mit ausschließlich einem dieser Wörter zählt.
- **Anführungszeichen verbinden Wörter zu einer exakten Wortfolge:** `"New Chats"` sucht die unmittelbar zusammenhängende, vollständige Wortfolge; ein Chat mit nur `New` oder nur `Chats` ist dann **kein** Treffer.
- **Optionaler Titelfilter:** `titel:"New Chats"` sucht nur diese Wortfolge im Titel. Ohne `titel:` werden Titel und sichtbare Nachrichten durchsucht.
- Alle Varianten ignorieren Groß-/Kleinschreibung, befolgen Unicode-Wortgrenzen, behandeln Leerraum zwischen *nicht* zitierten Suchwörtern als ODER und verändern weder Quelltexte noch gespeicherte Chats.
- Streaming-Volltextsuche bleibt speicherschonend, inklusive Abgleich von Treffern über Lese-Blockgrenzen hinweg; Parser berücksichtigt maximal 64 Suchausdrücke zu je 256 Zeichen.
- Künstliche JVM-Tests belegen ODER, zusammenhängende Wortfolgen, Titelfilter, Wortgrenzen, Kategorien und Blockgrenzen. Fehlender Treffer im Suchindex bedeutet keine automatische Löschung.
- Neue isolierte QA-Paketkennung `de.universelab.chatarchiv.researchqa17`, um bestehende Installationen mit 641 bzw. später 640 Gesprächen nicht zu überschreiben; produktive Android-Signierung bleibt gesondert geschützt. Versioncode 33 / Versionname 0.5.17.
- Keine neuen Berechtigungen, kein ChatGPT-Kontozugriff, keine Änderung am Papierkorb oder importierten Chatdaten. `main` unverändert; CI, Signatur- und Samsung-Test erforderlich.



## Version 0.5.16 · Schaltflächen im Chat-Aktionsdialog sichtbar (Samsung Android 17)

- **Reproduzierter Fehler v0.5.15:** Lange auf „New chat“ drücken öffnete einen Dialog mit Titel und Nachrichtentext, aber ohne die versprochenen Aktionen. Ursache: `AlertDialog.Builder.setMessage()` und `setItems()` wurden gemeinsam benutzt; bei Android 17 wurde die Optionsliste unterdrückt.
- **Gezielte Korrektur:** Die Kurzfassung des Gesprächstitels sowie die ersten acht Zeichen der Chat-ID stehen nun **im Dialogtitel**; der Dialog verwendet ausschließlich `setItems()` mit „Bereich ändern“ und „Chat löschen“ plus „Abbrechen“. Die eigene nachfolgende Sicherheitsabfrage „Wollen Sie wirklich diesen Chat löschen?“ bleibt unverändert.
- **Keine Löschung bei langem Drücken:** Ohne Auswahl von „Chat löschen“ und zusätzliche explizite Bestätigung wird kein Datensatz verschoben. Der bestehende Papierkorb mit Wiederherstellung und zweiter Sicherheitsabfrage zur endgültigen Löschung bleibt erhalten.
- **QA-Datenschutz:** Eigene Debug-Paketkennung `de.universelab.chatarchiv.researchqa16`. Die vorhandenen v0.5.12-, v0.5.14- und v0.5.15-Installationen werden nicht überschrieben. Neue QA-App enthält von sich aus **keine 641 Chats**; ausschließlich expliziter lokaler Testimport. Öffentliche CI baut keine signaturkompatible produktive APK.
- `versionCode 32` / `versionName 0.5.16`, keine neuen Android-Berechtigungen, kein ChatGPT-Weblogin, keine Daten auf GitHub. [OFFEN] Erneuter Android-17-Gerätetest.



## Version 0.5.15 · bestätigte Chat-Löschung mit Papierkorb und Wiederherstellung (Gerätetest offen)

- Langes Drücken auf einen Chat öffnet statt direkter Kategorieänderung das Menü **Bereich ändern** / **Chat löschen**. Vor jeder Löschung erscheint eine eindeutige Sicherheitsabfrage **„Wollen Sie wirklich diesen Chat löschen?“**, mit **Abbrechen** als sichere Alternative.
- Das erste bestätigte Löschen legt den Chat im **lokalen Papierkorb** ab. Chat und seine zugehörigen privaten Daten bleiben wiederherstellbar; die normale Liste, Suche, Forschungsnavigator und Archiv-ZIP-Sicherung enthalten nur aktive Chats. Die Kategorie UniverseLab/Weitere Chats wird beim Wiederherstellen beibehalten.
- Der sichtbare **Papierkorb (N)** zeigt entfernte Gespräche einschließlich kurzer ID zur Unterscheidung vieler „New chat“. Einzelne Chats können daraus **wiederhergestellt** oder nach einer **zweiten ausdrücklichen Sicherheitsabfrage endgültig gelöscht** werden. Endgültiges Löschen entfernt nur die app-internen JSON-/Suchdateien und gespeicherte Altversionen; nie die ursprünglichen ChatGPT-Exportdateien unter Downloads.
- Crash-Sicherheit beim endgültigen Löschen: Bevor Dateien entfernt werden, wird der Zustand `loeschung-ausstehend` atomar im bestehenden Index gesichert. Bei Unterbrechung bleibt der Eintrag im Papierkorb und die Dateilöschung lässt sich erneut ausführen; die Wiederherstellung teilweise gelöschter Daten wird unterbunden. Indexänderungen werden bei Schreibfehlern im Speicher zurückgerollt.
- **Explizit aus Papierkorb ausgeschlossene Chats werden bei späterem Massenimport nicht unbemerkt zurückgeholt.** Der Import meldet deren Anzahl gesondert als „Im Papierkorb belassen“. Nach endgültiger Löschung können bereits vorhandene externe Exporte diesen Chat bei bewusstem Re-Import erneut anlegen.
- **0 sichtbare Beiträge ≠ nachweislich leere Originaldaten** (versteckte Zweige, Metadaten und Medien können existieren); es erfolgt keine automatische Löschung nach dem Titel „New chat“. Alle Löschvorgänge müssen bewusst vom Nutzer ausgelöst werden.
- Zusätzlich eindeutige QA-Paketkennung `de.universelab.chatarchiv.researchqa15` und App-Anzeigename `UniverseLab Forschung QA v0.5.15`. Damit kann die Testversion unabhängig von einer bereits gefüllten QA-v0.5.14 und der produktiven App installiert werden. Für künftige Updates des neuen QA-Pakets ist weiterhin ein konstanter QA-Signierschlüssel notwendig.
- `versionCode 31`, `versionName 0.5.15`. Keine neue Android-Berechtigung, keine ChatGPT-Webanmeldung, keine privaten Daten auf GitHub. Nur isolierter Draft-PR, CI- und Samsung-Test vor Freigabe.



## Version 0.5.14 · geschützte Ansicht bereits gesicherter Chatfassungen (Gerätetest offen)

- Das Gespräch zeigt eine zusätzliche Schaltfläche **„Gesicherte Altversionen ansehen“** mit Anzahl. Ein Dialog listet ausschließlich Dateimetadaten der gespeicherten Fassungen dieses Chat-IDs, nicht die privaten JSON-Inhalte im Repository.
- Nach expliziter Auswahl wird eine historische Fassung **nur lesend** geöffnet. Anzeige prüft SHA-256 des Archivtextes und Chat-ID; ungültige Referenzen oder Fassungen über 32 MiB werden abgewiesen. Erstell-/Änderungsdaten des Chats werden nicht aus dem Dateidatum erfunden: „Lokal gesichert“ bezieht sich auf den Änderungszeitpunkt der privaten Archivdatei.
- In der Altversionsansicht sind das Exportieren und Markieren der **aktuellen** Fassung sowie der auf aktuelle Beiträge gerichtete „Lesen“-Sprung deaktiviert. Die aktuelle Hauptfassung bleibt unberührt; keinerlei automatische Wiederherstellung, Überschreiben oder Löschen.
- Für Chats ohne gesicherte Altversion erscheint ein eindeutiger Hinweis. Keine Migration, keine neuen Berechtigungen, keine Anbindung an ChatGPT-Webkonten oder neue Datenexporte.
- Nur QA-/Buildnachweis, keine produktive Aktualisierung ohne bisheriges privates Release-Zertifikat. Android-17-Gerätetest ausstehend.



## Version 0.5.13 · begrenzter SHA-256-Abgleich lokaler Exportkopien (Gerätetest offen)

- Prüft nach dem freigegebenen SAF-Ordnerscan ausschließlich **Kandidaten mit gleichem Dateinamen und bekannter gleicher Dateigröße** durch tatsächliches Lesen der JSON-Dateien (SHA-256, 32-KiB-Blöcke, ohne ZIP-Entpacken).
- Die Prüfung ist begrenzt auf höchstens 8 Kandidatengruppen, 32 MiB pro Datei und 128 MiB insgesamt. Größere, unlesbare oder nicht berücksichtigte Gruppen bleiben ausdrücklich **ungeprüft** und dürfen nicht als identisch gelten.
- Die Vorschau unterscheidet **inhaltlich identische**, **unterschiedliche** und **ungeprüfte** Gruppen. Keine Hashes oder Gesprächsinhalte verlassen das Gerät.
- Keine automatische Auslassung oder Veränderung von Quelldateien; Import, Chat-ID-Prüfung, Versionsschutz und bestehende Chat-Archive bleiben unverändert. Es handelt sich ausdrücklich **nicht** um eine Anbindung an das angemeldete ChatGPT-Konto.
- Keine neuen Android-Berechtigungen. Private Chats/Schlüssel werden nicht nach GitHub übertragen. CI- und Samsung-Geräteprüfung erforderlich.


Eigenständige Android-App für lokal wiederhergestellte ChatGPT-Gespräche.

## Version 0.5.12 · kleine Schaltflächen nebeneinander, fester Dialogfuß (Gerätetest offen)

- **Gezielter Layoutwechsel:** Eigener, begrenzter Suchdialog mit festem Titel, separat scrollbar gehaltenem Suchbericht und *fester horizontaler Aktionszeile*. Die beiden Aktionen stehen in gleich breiten Feldern nebeneinander; nur der Bericht darüber scrollt.
- **Kleinere, vollständige Beschriftung:** „Nicht importieren“ und „Alle importieren“ ohne automatische Großschreibung in 12 sp; bei schmaleren Darstellungen kann die Schrift bis 10 sp verkleinert werden. Jede Schaltfläche bleibt mindestens 52 dp hoch und auch bei langem Bericht zugänglich.
- **Nur Darstellung:** `versionCode 28`, `versionName 0.5.12`; keine Änderung von Paketkennung, Importablauf, Chatdateien, Scanner, SAF-Freigaben oder Berechtigungen. Ausschließlich isolierter Entwurf `app/chatarchiv-scan-actions-row-v0512`, `main` bleibt unverändert.
- **[OFFEN]** Sichtprüfung auf Samsung Galaxy S24 Ultra/Android 17 einschließlich Play-Protect-Verhalten. Eine erneute Sicherheitsblockade nicht umgehen.

## Version 0.5.11 · begrenzter nativer Suchdialog (am Gerät als unzureichend bestätigt)

- **Behobener Layoutfehler im Code:** Der Ergebnisdialog der rekursiven SAF-Suche wird auf maximal 76 % der Bildschirmhöhe (höchstens 680 dp) begrenzt und mittig angezeigt. Die ausführlichen Suchstatistiken, möglichen Dateikopien und Pfade bleiben innerhalb des Android-Dialogtexts scrollbar; der untere Schaltflächenbereich erhält Platz.
- **Gerätebefund:** Trotz Höhenbegrenzung und kürzerer Bestätigung blieb „Nicht importieren“ auf dem Galaxy S24 Ultra/Android 17 unten teilweise verdeckt. Der systemeigene Dialog stellte die beiden Aktionen weiterhin untereinander dar. v0.5.12 ersetzt diesen Teil des Dialoglayouts.
- **Keine Änderung von Speicherung oder Sicherheit:** `versionCode 27`, `versionName 0.5.11`; Paketkennung, SAF-Freigaben, Import-/Duplikatlogik, Berechtigungen und private Signatur bleiben unverändert. Die Korrektur liegt isoliert auf `app/chatarchiv-scan-dialog-layout-v0511`, nicht auf `main`.

## Version 0.5.10 · gespeicherte SAF-Ordner sichtbar und einzeln verwaltbar (Suchtest am Gerät bestätigt)

- **Ordnertransparenz:** Unter „Gewählten Ordner inkl. Unterordner nach Chat-JSON durchsuchen“ → „Gespeicherte Ordner einzeln verwalten“ zeigt die App bei Androids lokalen Dokumentanbietern einen lesbaren Pfad wie „Interner Speicher/Download/ChatGPT_Rettung_2026-11-08“. Bei externen Anbietern wird nur ein vom Anbieter verfügbarer Ordnername gezeigt, nicht aus einer opaken Dokument-ID ein Pfad erfunden. Alles bleibt lokal.
- **Einzelverwaltung:** Jede Freigabe lässt sich getrennt erneut durchsuchen oder nach ausdrücklicher Bestätigung aufheben. Die übernommene ältere Rettungsordner-Freigabe wird beim Entfernen desselben Ordners ebenfalls aus den Einstellungen gelöscht; importierte Chats und Quelldateien bleiben erhalten. Andere Freigaben bleiben unangetastet.
- **Quellenbericht:** Die Suchvorschau zählt durchsuchte Ordner, Dateien, Chat-JSON und unlesbare Ordner pro freigegebenem Stammordner. Dies erleichtert die Kontrolle bei mehreren Freigaben.
- **Kopienkennzeichnung ohne Evidenzsprung:** Mehrfachreferenzen auf dieselbe Dokument-ID desselben Anbieters werden nur einmal zum Import vorgemerkt. Gleicher Dateiname plus gleiche bekannte Bytezahl wird als **mögliche** Kopie angezeigt; unterschiedliche Dateien werden ohne Inhaltsvergleich nicht automatisch übersprungen. Die bewährte Chat-ID-/SHA-256-Duplikatprüfung bleibt für den eigentlichen Import zuständig.
- **Gerätebefund auf Galaxy S24 Ultra/Android 17:** Ein gespeicherter Ordner wurde mit lokalem Pfad angezeigt. Rekursive Suche fand 2 Ordner, 15 Dateien, 7 Chat-JSON sowie eine *mögliche* Kopie, ohne Lesefehler; 641 Chats blieben erhalten. **Bekannter UI-Fehler:** Bei langem Suchbericht wurde die untere Schaltfläche „Nicht importieren“ abgeschnitten; hierfür ist v0.5.11 vorgesehen.
- **Keine neuen Berechtigungen:** `versionCode 26`, `versionName 0.5.10`; Produktiv-Paketkennung und privater Release-Signierschlüssel bleiben unverändert. `main` und der v0.5.9-PR bleiben unverändert. Das Play-Protect-Verhalten dieser neuen APK ist nicht gesondert dokumentiert.

## Sicherheitsstand (Version 0.5.9 · SAF-Ordnersuche, auf Galaxy S24 Ultra getestet)
 
- **Keine Vollspeicherberechtigung:** Die produktive App fordert weder `MANAGE_EXTERNAL_STORAGE` noch `READ_EXTERNAL_STORAGE` an. Das APK-Manifest wird im CI-Build auf sensible Berechtigungen geprüft.
- **Automatische, begrenzte Ordnersuche:** Nutzer wählen einen oder mehrere Ordner über Androids Dokumentauswahl. Der Suchlauf durchläuft alle zugänglichen Unterordner nach `conversations*.json` und listet Treffer mit Bestätigung vor dem lokalen Import auf. Die Freigaben bleiben für spätere Aktualisierungen gespeichert; die bestehende Rettungsordner-Freigabe wird übernommen. Keine eigenständige Suche über den kompletten Handyspeicher mehr.
- **ZIP-Dateien:** Die rekursive Ordnersuche zählt ZIP-Dateien, öffnet und importiert sie jedoch nicht automatisch. Über **„Ältere Export-ZIPs auswählen“** ist ZIP-Import weiterhin möglich. Sehr große Archive können Zeit und Speicher beanspruchen; vorhandene Rettungs-JSONs zuerst nutzen.
- **Grenzen:** Android 11+ lässt keinen Zugriff auf den Speicher- oder Downloads-Hauptordner via `ACTION_OPEN_DOCUMENT_TREE` zu. Ein Unterordner muss pro getrenntem Suchbereich einmalig freigegeben werden. Der Android-Sicherheitsstatus muss nach dem Build auf dem realen Gerät geprüft werden. Eine Play-Protect-Blockierung darf nicht als bloßes Signaturproblem abgetan werden.
- **Update:** `versionCode 25`, `versionName 0.5.9`; Paketname und privater Release-Schlüssel bleiben unverändert, damit bestehende App-Daten bei einem erfolgreichen Update erhalten bleiben.

## Frühere Funktionen (Version 0.5.0 · Chat-Übergabe mit Quellenankern)

- **„Chat-Übergabe · neuen Chat vorbereiten“:** Neuer, ausdrücklich nutzergesteuerter Bildschirm. Er untersucht offline ausschließlich die aktuell als **UniverseLab** eingeordneten importierten Chat-Hauptfassungen (kein Zugriff auf den live geöffneten ChatGPT-Chat, keine Cloud-Abfrage). Die vorhandenen Regeln `ResearchFinder` und `ResearchTimeline` liefern priorisierte historische Prüfkandidaten und später formulierte Statusaussagen.
- **Deterministisches Übergabepaket:** Bis zu 12 priorisierte Prüfkandidaten sowie bis zu 3 ältere Fundstellen mit späterer Abschlussaussage; pro Fundstelle Quellchat, Chat-ID, Beitragsnummer, Rolle, Zitat, Prüffrage, Prüfweg und gegebenenfalls eine später zu prüfende Statusbehauptung. Zwei Auswahl-Durchgänge begrenzen Wiederholungen einzelner Chats/Fachgebiete. Das Paket dokumentiert Screening-Grenzen und ist ausdrücklich **[HEURISTISCH]**; später formulierte Abschlüsse gelten nicht automatisch als freigegeben.
- **Fortsetzungsroutine:** Ein in der App anpassbarer Fokus (standardmäßig HPVS → HZT-M0 → HZT-Full) und ein wissenschaftlich konservativer Arbeitsauftrag für den neuen Chat. Die Vorlage verlangt Originalquellen, aktuellen Kanon, Gegenbeispiele, getrennte Evidenzklassen und explizite Freigaben. Eine neue ChatGPT-Sitzung muss **manuell** erstellt und die Übergabe **manuell** eingefügt werden.
- **Sichtbarkeit/Kontrolle:** Vorschau mit Textauswahl und 0–100-%-Navigationsregler; nur per Schaltfläche **„Für neuen Chat kopieren“** gelangt der Text in die Zwischenablage, nur per Android-Dokumentauswahl **„Als .md speichern“** entsteht eine neue externe Datei. Keine automatische Übertragung, keine Änderung der privaten Chatarchive oder GitHub-Schreibzugriffe.
- **Grenzen:** Nur die letzten 350 sichtbaren Nachrichten je Chat, 120.000 Zeichen je Nachricht und maximal 5 Funde je Chat bilden den vorhandenen heuristischen Screening-Input. Das Übergabepaket ist absichtlich begrenzt und ersetzt weder vollständige Chatarchive noch das kanonische Projektregister; es führt keine eigenen neuen physikalischen Beweise.
- **Updatefähigkeit:** Produktive `applicationId` unverändert, `versionCode 16`, `versionName 0.5.0`; private Release-Signatur außerhalb von GitHub bleibt dieselbe wie in den vorigen stabilen APKs. Bestehende 641 Chats werden bei einem regulären Android-Update nicht neu importiert.

## Funktionen (Version 0.4.5 · leichter greifbare Scrollleiste)

- **Unsichtbar vergrößerte Griffzone 0.4.5:** Die native Schnellscroll-Leiste bleibt optisch unverändert (24 dp). Direkt links davon ist eine zusätzliche unsichtbare Touch-Zone aktiviert; zusammen sind die horizontalen Griffbereiche 56 dp breit. Ein kurzes Tippen in der Erweiterung löst weiterhin die normale Chat-/Schaltflächenaktion aus. Erst eine deutliche vertikale Wisch-/Ziehbewegung übernimmt die Schnellnavigation relativ zur aktuellen Listenposition. Der ursprüngliche Scrollgriff bleibt für Standardgesten erhalten. Auch Forschungsnavigator und Hauptarchiv nutzen diese Navigation.
- **Rückwärtskompatible Aktualisierung:** Identische Android-Paketkennung und private Release-Signatur mit erhöhtem Versionscode (15); keine Datenbankmigration und kein erneuter Chatimport nötig.

## Funktionen (Version 0.4.4 · dauerhafte Scrollnavigation)

- **UniverseLab**, **Weitere Chats**, **Alle** als getrennte Ansichten.
- **Forschungsnavigator (neu, rein lokal):** Durchsucht gespeicherte sichtbare Gesprächsbeiträge nach ausdrücklich benannten offenen Punkten, Blockern, Widersprüchen und nächsten Schritten, zeigt Fundstelle und heuristische Prüffrage/Prüfweg und springt zum Originalbeitrag. Projektchats oder auf Wunsch alle Chats; Abbruch jederzeit. Keine automatischen Änderungen oder Cloud-Anfragen.
- **Scrollnavigation 0.4.4:** In den Chat-, Hauptlisten- und Forschungsnavigator-Ansichten erhält die native Schnellscroll-Leiste eine dauerhaft sichtbare 24-dp-Grifffläche und eine abgesetzte Spur. `SCROLLBARS_INSIDE_INSET` hält sie vom Text fern. Im Einzelchat hilft der zusätzliche Dialog **„Zu Beitrag springen“** beim Sprung zu einem der sichtbaren (gegebenenfalls gefilterten) Beiträge. Die Schaltfläche **„Lesen“** öffnet einen einzelnen langen Beitrag in einer eigenen Textansicht mit einem horizontalen 0–100-%-Regler für die pixelbasierte Navigation. Originaltext bleibt auswählbar, der Beitrag wird nicht umgeschrieben, Kopieren nutzt den vollständigen Originalinhalt. Bei über 2 Mio. Zeichen wird nur die Anzeige gekürzt und darauf hingewiesen.
- **Verlaufsabgleich 0.4.3 (heuristisch):** Für Fundstellen mit genau einer erkennbaren Aufgabenkennung (beispielsweise `K1-D` oder `Z8B-01`) sucht die App in den gesichteten Chats nach zeitlich nachfolgenden, ausdrücklich formulierten Statusaussagen. Sie zeigt Originalquelle und spätere Chat-Aussage getrennt an. Kurzes Tippen öffnet den ursprünglichen Beitrag, langes Tippen bei vorhandener Verknüpfung die spätere Aussage. Aussagen ohne eindeutige Kennung, hypothetische Formulierungen, Fragen und nicht chronologisch zuordenbare chatübergreifende Erwähnungen werden **nicht** als Abschluss eingeordnet. Alle Befunde sind [HEURISTISCH], kein Abgleich mit dem Projektkanon oder GitHub. Belege bleiben unverändert und rein lokal.
- **Korrektur 0.4.2:** Die Hauptansichten berücksichtigen die Android-Status-, Navigations- und Kameraausschnittbereiche. Insbesondere bleibt **„Weitere 100 anzeigen“** oberhalb der Navigation bedienbar (Build-Prüfung; endgültige Bestätigung am Gerät steht aus).
- **QA-Verbesserung 0.4.1:** Nicht jeder Worttreffer ist ein Blocker. Explizite Negationen und reine Aufgaben-/Feldvorlagen werden nun konservativ ausgefiltert; echte Statussperren wie `NOT RELEASED` bleiben erhalten. Hinweise sind nach Art filterbar und über 100 Fundstellen hinaus in Schritten zu je 100 nachladbar. Der Bildschirm bleibt rein lesend.
- Mehrfachimport per Android-Dateiauswahl von `conversations-000.json`, `conversations-001.json` usw. aus einem ChatGPT-Datenexport.
- **ZIP-Import ohne Vollentpackung:** Mehrere ältere ChatGPT-Export-ZIPs über den Android-Dateipicker auswählen. Die App liest nur `conversations.json`/`conversations-000.json` usw. direkt aus dem ZIP-Stream und integriert sie über dieselbe Dublettenprüfung. Medienanhänge werden nicht extrahiert.
- **Frühere Option bis 0.5.8:** Die Sonderberechtigung für den gesamten gemeinsamen Speicher ist in 0.5.9 entfernt. Stattdessen wird nach dokumentengestützter Ordnerfreigabe nur dort rekursiv gesucht (siehe aktueller Sicherheitsstand oben).
- **Versionsschutz bei älteren Exporten:** Bei identischen Chat-IDs wird der Inhalt verglichen. Abweichende ältere oder gleich alte, nicht umfangreichere Varianten landen im privaten Versionsordner; sie überschreiben keine aktuellere Chatfassung. Bei neuerer Fassung wird die alte lokal gesichert. Für den privaten Versionsbestand gilt zum Speicherschutz ein Limit von 1 GiB; bei Erreichen meldet die App einen Fehler und lässt die bisherige Chatfassung unverändert. Die aktuelle App zeigt weiterhin nur die Hauptfassung an; eine Oberfläche zur Ansicht der archivierten Varianten ist noch nicht enthalten.
- Wiederholter Import ist die **Datenaktualisierung**: IDs werden abgeglichen, vorhandene Gespräche aktualisiert, neue ergänzt. Manuell verschobene Chats behalten ihre Zuordnung.
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

### Signaturkompatible Aktualisierung ab 0.4.2

Die produktive APK hat unverändert die Paketkennung `de.universelab.chatarchiv`,
`versionCode 14` und wird **außerhalb von GitHub Actions** mit dem bereits vorhandenen
**privaten UniverseLab-Signaturschlüssel** signiert. Der Schlüssel darf niemals in das
öffentliche Repository, Buildprotokolle oder GitHub-Artefakte gelangen.
So erkennt Android bei einem bereits mit diesem Schlüssel signierten ChatArchiv die
Installation als **Aktualisieren** und erhält alle dort gespeicherten Chats.
Die zuvor erstellte ZIP-Sicherung bleibt als Rückfalloption erforderlich.

Die QA-Test-App `de.universelab.chatarchiv.researchqa` ist eine **andere Installation**
mit einer anderen Signatur und getrennten 641-Chat-Daten. Eine signierte produktive APK
kann sie **nicht** verlustfrei direkt ersetzen. Falls die ursprüngliche ChatArchiv-App
die 641 Chats noch nicht enthält, kann ihre vorhandene ZIP-Sicherung dort **einmal**
importiert werden. Danach erfolgen Produktiv-Updates ohne erneuten Import.

GitHub Actions baut die Release-APK nur **unsigniert** und lädt sie als
`UniverseLab-ChatArchiv-Unsigned-Release` hoch. Die lokale, private Signatur
und Zertifikatsprüfung müssen **nach** jedem Build erfolgen. Das GitHub-Debug-APK
bleibt ein separates Testpaket, keine signaturkompatible Produktivaktualisierung.

### Sicheres Testen auf dem Smartphone

Die in GitHub Actions erzeugte **Debug-APK** hat in diesem Forschungszweig die gesonderte Android-Paketkennung `de.universelab.chatarchiv.researchqa` und den Icon-Titel `UniverseLab Forschung QA (Test)`. Sie wird parallel zur bestehenden `de.universelab.chatarchiv` installiert; die bisherigen privaten Daten bleiben unabhängig und unverändert.

Ein Austausch von Chatdaten zwischen den getrennten App-Speichern erfolgt **nicht automatisch**. Wer die Vorschau testen möchte, kann in der bisherigen App zunächst **Alle Gespräche als ZIP sichern** wählen und diese Sicherung bewusst in die Vorschau importieren. Der ZIP-Export enthält aktive Chat-Hauptfassungen und Kategorien, **nicht** Altversionsverläufe oder externe Medienanhänge. Das ist ein Testpaket; nicht die bestehende App deinstallieren, um eine Signaturkollision zu umgehen.

## Datenschutz und Grenzen

- Gespräche, Suchindex und Titel liegen **ausschließlich im privaten App-Speicher auf dem Android-Gerät**; keine Uploads, Analytics oder Werbung. Android-Backup ist deaktiviert.
- Die App benötigt Internetzugriff **nur für den freiwillig geöffneten GitHub-Bereich**; dieser sendet keine Chattexte, Chat-IDs oder Suchanfragen. Der anonyme GitHub-Aufruf übermittelt technisch bedingt Netzwerkmetadaten wie die IP-Adresse.
- Der Ordner-/Datei-/ZIP-Import erfolgt über den Android-Systempicker. **0.5.9 fordert keine Vollspeicherberechtigung mehr an.** Nur die ausdrücklich freigegebenen Ordner und Unterordner werden bei der automatischen Suche untersucht. Diese Sideload-App ist nicht für die Play-Store-Veröffentlichung vorgesehen.
- **Kein automatischer ChatGPT-Kontosync:** Dafür gibt es hier weder ChatGPT-Login noch eine autorisierte Schnittstelle. Updates erfolgen durch Auswahl eines neuen Exports.
- Die `.json`-Dateien enthalten Text und Nachrichtenstruktur. Bilder/Dateianhänge benötigen die separaten Exportdateien, die bei einem unvollständigen ZIP möglicherweise nicht gerettet wurden.
- Formeln bleiben im Archiv originalgetreu gespeichert. Der optionale Unicode-Modus ist eine Annäherung für häufige Befehle, keine verlustfreie mathematische Satzengine. Für exakte Provenienz und Kopien weiterhin „Original“ oder vollständigen JSON-Export verwenden.
- Bei allen Exporten können Android-Dokumentanbieter auch Cloud-Dienste anbieten. **Nur der vom Nutzer gewählte Zielanbieter** erhält die Datei; es gibt keinen selbsttätigen Chat-Upload durch die App.
- Die automatische Kategorie basiert auf Stichworten im Gesprächstittel. Per langem Tippen lässt sich die Zuordnung korrigieren.
- `chat.html` und eine 40-GB-ZIP müssen **nicht** importiert werden, wenn die darin enthaltenen Chat-JSON-Dateien bereits vorhanden sind. Die Ordnersuche ab 0.5.9 öffnet keine ZIPs automatisch; ZIP-Import ist ein gesonderter, ausdrücklich ausgelöster Vorgang.
- Alternativ kann die App ZIP-Archive direkt lesen. Bei abgeschnittenen ZIPs können früh liegende intakte Gesprächs-JSONs gerettet werden, eine vollständige Wiederherstellung ist nicht garantiert. Sobald nach den Gesprächs-JSONs große `file-*.dat`-Anhänge beginnen, beendet der Import die ZIP-Durchsuchung, damit keine Dutzenden GB an Medien verarbeitet werden. Gesprächs-JSONs sind pro ZIP auf insgesamt 3 GiB und 100 Einträge begrenzt.

## Repository-Isolation

Der gesamte Android-Code liegt in `tools/chatarchiv-android/`. Der Build-Workflow `.github/workflows/chatarchiv-android-apk.yml` reagiert auf die isolierten App-Zweige `app/chatarchiv-android-readonly-v1` und `app/chatarchiv-research-navigator-v0` sowie die isolierten QA-/Update-Zweige `app/chatarchiv-research-qa-v041`, `app/chatarchiv-stable-update-v042`, `app/chatarchiv-timeline-qa-v043` und `app/chatarchiv-scroll-navigation-v044`; `main` bleibt unberührt. Keine privaten Exportdaten oder realen Gespräche werden eingecheckt oder in GitHub Actions verarbeitet. Der Build erstellt ein mit dem Android-Debug-Schlüssel signiertes APK-**Testpaket** und eine **unsignierte Release-APK** zur späteren privaten Signierung. Es ist keine Play-Store-Veröffentlichung.

## Build

Android SDK 35, JDK 17, Gradle 8.9, Android Gradle Plugin 8.7.3:

```bash
cd tools/chatarchiv-android
gradle :app:testDebugUnitTest :app:assembleDebug :app:assembleRelease
```

Ausgabe: `app/build/outputs/apk/debug/app-debug.apk` (QA, signiert mit wechselndem Debug-Schlüssel) und `app/build/outputs/apk/release/app-release-unsigned.apk` (Produktivpaket, **noch nicht installierbar**). GitHub Actions liefert beide getrennt; der private signierte Update-Build erfolgt lokal.

## Import auf dem Telefon

1. APK installieren (Android fragt ggf. nach Erlaubnis zur Installation aus dieser Quelle).
2. **Chats importieren** → **Rettungsordner auswählen (empfohlen)** wählen und `Download/ChatGPT_Rettung_2026-11-08` freigeben. Die App findet `conversations-000.json` bis `conversations-005.json` automatisch. Alternativ können einzelne JSON-Dateien ausgewählt werden.
3. Import abwarten und über **UniverseLab**, **Weitere Chats** oder **Alle** navigieren.
4. Später weitere ChatGPT-Exportdateien in den freigegebenen Ordner kopieren und **Chats importieren** → **Gespeicherten Ordner aktualisieren** wählen. Die Kategoriezuordnung bleibt erhalten.
5. Für ältere Exporte **Chats importieren** → **Ältere Export-ZIPs auswählen** verwenden und eine oder mehrere `.zip`-Dateien auswählen. Bereits vorhandene Chats werden anhand ihrer IDs/Inhaltshashes nicht doppelt gespeichert.
6. **Optional:** **Chats importieren** → **Gewählten Ordner inkl. Unterordner nach Chat-JSON durchsuchen** → gewünschten Unterordner einmalig freigeben. Weitere Ordner können ergänzt und später gemeinsam automatisch erneut durchsucht werden. Gefundene JSON-Dateien erscheinen vor dem Import in einer Vorschau; ZIPs werden nur gezählt und müssen bewusst separat ausgewählt werden.
7. Einen Chat öffnen → **Exportieren** und zwischen vollständigem JSON, Markdown, TXT und HTML auswählen. Die JSON-Datei enthält auch inaktive Zweige der gespeicherten Unterhaltung; die lesbaren Formate enthalten den aktiven sichtbaren Verlauf.
8. Einen Chat öffnen → **Original / Unicode / Monospace** für die Anzeige wählen. Mit **Markieren** eine durchgehende Markieransicht über mehrere Beiträge öffnen.
9. Auf der Hauptseite **Alle Gespräche als ZIP sichern** für ein reimportierbares Backup der aktuellen Hauptfassungen und ihrer Kategoriezuordnungen wählen. Altversionen und externe Medienanhänge sind dabei nicht eingeschlossen.
10. **Forschungsnavigator · offene Fragen** öffnen: Projektchats werden zunächst lokal gesichtet. **Alle Chats prüfen** erweitert den Suchbereich; eine Fundstelle antippen, um den Originalbeitrag zu sehen.
