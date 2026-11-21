# Sternfenster 0.4.1 — Bildrate auf dem eigenen Handy prüfen

## Neu in 0.4.1

**Bildrate prüfen** öffnet einen lokalen Bericht und startet auf Wunsch eine
20-Sekunden-Messung im freien Live-Fenster oder in der Live-Sternkarte. Nach zwei
Sekunden Aufwärmen werden tatsächliche Zeichenaufrufe und deren Zeitabstände
gezählt. Das freie Fenster bleibt nach Messende geöffnet; die Messergebnisse
werden gespeichert und lassen sich mit **Ergebnis kopieren** übernehmen.

1. 0.4.1 als Aktualisierung über die vorhandene Version ab 0.2.0 installieren.
2. **Bildrate prüfen → Im freien Fenster messen (20 s)** wählen.
3. Das Fenster sichtbar halten und das Handy wie gewohnt bewegen. Eine andere
   App kann währenddessen geöffnet werden. Der Fortschritt steht in der Karte.
4. Nach dem Messende zu **Bildrate prüfen** zurückkehren. Das freie Fenster kann
   bei Bedarf verschoben oder über × geschlossen werden, um den Bericht zu lesen.
5. **Ergebnis kopieren** übernimmt den vollständigen Text in die Zwischenablage.

Der Bericht enthält Mittelwert der Render-FPS, Anzahl der Draw-Aufrufe,
Bildabstände (p95 und Maximum), Anzahl der Abstände über 20 ms, Dauer des
Zeichenaufrufs, beobachtete Display-Hz, Kartengröße und Gerätemodell. Es werden
keine Standortdaten in den Bericht geschrieben und nichts automatisch übertragen.
Ein Abbruch, etwa durch Schließen oder Unsichtbarwerden der gemessenen Ansicht,
ersetzt kein vorheriges Ergebnis. Eine neue Messung beendet eine bereits laufende.
Die Messung eines vorhandenen freien Fensters verändert dessen Blickrichtung,
Zoom, Fenstergröße, Rundblick oder Zeitmodus nicht.

**Render-FPS sind Zeichenaufrufe pro tatsächlicher verstrichener Messzeit.**
Für N Draw-Aufrufe liegen N−1 aufeinanderfolgende Bildabstände vor. Der zusätzliche
Intervallwert im JSON verwendet deren echte erste-bis-letzte Zeitspanne. p95 ist
der nächste Rang ceil(0,95 × Stichprobenzahl). Die 20-ms-Grenze ist ein fester
Diagnosewert; sie bezeichnet weder verlorene Bilder noch eine an die aktuelle
Displayrate angepasste Jank-Quote. Nicht verfügbare Werte bleiben ausdrücklich
fehlend. Quantile werden bei Überschreiten der Puffergrenze nicht aus einem
abgeschnittenen Präfix behauptet.

Die Messdauer des Zeichenaufrufs ist verstrichene Zeit innerhalb von `onDraw`,
keine reine CPU-Rechenzeit. Sie kann Unterbrechungen des Threads enthalten, erfasst
aber nicht die nachfolgende GPU-/Compositor-Arbeit. Die eigene Messung zählt keine
tatsächlich am Bildschirm präsentierten Frames. **Auch ein Durchschnitt ab 60 FPS
belegt keine durchgehende Mindestbildrate.** Der API-35-Emulator ersetzt weiterhin
keinen Lauf auf Stefans Samsung.

Der Renderpfad verwendet seine Projektion jetzt dauerhaft wieder und berechnet
von der Blickrichtung unabhängige Viewport-Grenzen nur bei Größen-/Sichtfeldwechsel.
Unveränderte Beschriftungen der Steuerknöpfe werden nicht jede Sekunde neu gesetzt.
Sternkatalog, Projektionsformeln, Detailgrad, Sensorfolge und Bildtakt bleiben
unverändert. Das beseitigt vermeidbare Arbeit; eine konkrete Geschwindigkeitssteigerung
auf dem Telefon wird ohne dortige Messung nicht behauptet.

Die deterministischen Prüfungen umfassen 57 Messarithmetikfälle, 132.192 bitgenaue
Projektionsvergleiche mit der eingefrorenen 0.4.0-Formel sowie die bestehenden
96.346 Orientierungs- und 7.484 Projektionsprüfungen. Alle 35 Android-Testschritte bestanden: sieben neue Prüfungen für Messung/Bericht/Abbruch,
elf Overlay-, zehn Sensor- und sieben Live-/PiP-Prüfungen. Die neue Messfunktion
zeichnete im Test 141 Draw-Aufrufe in 20,664 Sekunden auf (6,823 Render-FPS);
der Test umfasst Navigation, Sensoränderung und UI-Automation im Software-Emulator.
Er bestätigt die Messarithmetik und den gespeicherten Bericht, keine 60 FPS.
Die separaten Live-/PiP-Abschnitte erreichten gewichtet 19,864 beziehungsweise
21,721 Render-FPS; auch sie bestätigen das Leistungsziel nicht.

Eine unterbrochene Messung blieb auch nach dem ursprünglichen Endtermin abgebrochen
und erhielt das vorherige Ergebnis. Das freie Fenster lief nach Messende weiter.
APK, Signatur, unveränderte Appquellen, CI-Läufe und Grenzen stehen in
`VALIDATION_v0.4.1.json`; unveränderte Rohberichte liegen unter `validation/v0.4.1/`.

## Neu in 0.4.0

**Freies Live-Fenster starten** öffnet eine eigenständige, verschiebbare und
vergrößerbare Sternkarte über anderen Apps. Die Titelleiste dient zum Verschieben,
der Griff unten rechts zum Vergrößern oder Verkleinern. **×** und die Aktion
**Fenster schließen** in der laufenden Benachrichtigung schließen es ausdrücklich.
Das Fenster bleibt bei Home, Appwechsel, Zurück in der Hauptansicht und beim
Entfernen der Hauptansicht aus der Taskliste unabhängig von deren Activity bestehen.

Einmalig muss Android **Über anderen Apps anzeigen** für Sternfenster erlauben.
Die App führt zu dieser Systemeinstellung und prüft die Freigabe bei der Rückkehr.
Die Benachrichtigungsfreigabe ist optional; ihre Ablehnung verhindert den Dienst
nicht. Das Fenster startet ausschließlich nach einer Aktion in einer sichtbaren
Activity. Kein Autostart beim Gerätestart, kein Alarm zum Wiederöffnen und keine
Accessibility-Berechtigung.

Technisch läuft eine begrenzte `TYPE_APPLICATION_OVERLAY`-Fläche in einem eigenen
ForegroundService vom Typ `specialUse`, mit eigenem Renderer und Sensorlistener.
`stopWithTask=false` erhält den Dienst beim Entfernen der Activity. `START_STICKY`
erlaubt Android eine Wiederherstellung nach gewöhnlichem Prozessverlust, sofern
das Fenster vom Nutzer aktiv gelassen wurde; es ist keine Wiederstartgarantie.
Vor einem ausdrücklichen Schließen wird diese Absicht gelöscht. Bei ausgeschaltetem
oder gesperrtem Bildschirm pausieren Sensoren und Vsync-Callbacks ohne Wake-Lock.
Position und Größe werden gespeichert und nach Größen- oder Rotationsänderungen
auf die nutzbare Bildschirmfläche begrenzt. Berührungen außerhalb des Fensters
gehen an die darunterliegende App.

**Samsung-Taskfenster bleiben verfügbar:** Die Live-Sternkarte unterstützt weiterhin
geteilten Bildschirm, Pop-up-Ansicht und Android-Bild-im-Bild. Bei weniger als
550 dp nutzbarer Höhe, weniger als 330 dp Breite oder Querformat blendet sie die
großen Bedienreihen aus. Richtung, Zoom, Handy folgen, Rundblick, Zeit und Fenster
bleiben im **⋮**-Menü erreichbar; Uhrzeit/Winkel sowie ein Karten-HUD bleiben sichtbar.
Fenstergrößenwechsel setzen weder Blickrichtung noch Zeitmodus zurück.

Ein Overlay liegt über anderen Apps; es wird nicht in deren Inhalt eingebettet.
Das Einrasten in Samsungs Taskaufteilung erfolgt weiterhin über die normale
Live-Sternkarte und Samsungs Fenstersteuerung. **Android kann Apps zwangsweise
beenden oder bei Ressourcenmangel schließen.** Sicherheitsrelevante Ansichten
können fremde Overlays ausblenden. Diese Systementscheidungen werden respektiert;
„kann sich niemals schließen“ wird nicht zugesichert.

## Neu in 0.3.1: Handy folgen

Die Blickrichtung folgt jetzt der Achse der rückseitigen Kamera (Gerät −Z).
Drehen, Neigen und seitliches Kippen werden in Vollansicht und sichtbarem PiP
übernommen. Die Kamera wird dafür nicht geöffnet und es gibt keine neue
Berechtigung. Der Modus ist beim ersten Start eingeschaltet, auch beim Öffnen
über das Vorschau-Widget; danach bleibt die gewählte Einstellung gespeichert.

- **Handy folgen** schaltet Sensorsteuerung an oder aus.
- **N/O/S/W, Wischen, Rundblick an und Zurücksetzen** schalten auf manuelle Ansicht.
- **Zoomtasten und Zwei-Finger-Zoom** lassen die Sensorsteuerung eingeschaltet.
- Die Rückseite des Handys zum Himmel richten. Unter dem Horizont erscheinen
  aufgrund der Horizontausblendung keine dort verdeckten Sterne.
- „Warte auf Sensoren“ kennzeichnet fehlende oder seit mehr als zwei Sekunden
  nicht mehr eintreffende Daten. „Kompass ungenau“ folgt Androids Sensorstatus.

Androids Rotation-Vector-Sensor wird bevorzugt, alternativ der geomagnetische
Rotation-Vector oder Beschleunigungs- plus Magnetfeldsensor. Die Abtastrate wird
mit 100 Hz angefordert; die erreichte Rate bestimmt Android. Quaternionen werden
mit einer Zeitkonstante von 25 ms geglättet. Das Rendering folgt weiterhin dem
Displaytakt. Die direkte Kamerabasis erhält die Rollbewegung auch beim Durchgang
durch Zenit/Nadir. Displayrotation und magnetische Deklination werden berücksichtigt.
Die Nordkorrektur nutzt Androids GeomagneticField-Modell mit dem angezeigten Standort,
Meereshöhe als Näherung und echter Uhrzeit, unabhängig vom gewählten Zeitraffer.
Sie ist eine Modellschätzung; Magnetstörungen und Kompasskalibrierung begrenzen die
Richtungsgenauigkeit. Kein Präzisionsinstrument zur Teleskopsteuerung.

Listener werden bei sichtbarer Activity in onStart aktiviert und in onStop entfernt.
Der pausierte, weiterhin sichtbare PiP-Modus behält die Sensoren. Bei fehlender
Hardware bleibt die manuelle Karte verfügbar.

## Kontinuierliche Darstellung seit 0.3.0

Die bisherige Vollansicht zeichnete nur einmal pro Sekunde. Version 0.3.0
zeichnet fortlaufend mit Androids Choreographer im Displaytakt. Die App fordert
mindestens 60 Hz beziehungsweise den höchsten angebotenen Bildmodus bei gleicher
Auflösung an. Der dauerhafte Renderer berechnet die Sternpositionen für jeden
Framezeitpunkt, verwendet vorberechnete Katalogdaten und bündelt schwächere Sterne
in wenigen Zeichenaufrufen.

**60 FPS sind das Leistungsziel, keine zugesicherte Untergrenze auf jedem Gerät.**
Die Anzeige **Render-FPS** zählt ausgeführte `SkyView.onDraw`-Aufrufe je verstrichener
Zeit. Daneben werden die Display-Hz angezeigt. Ein Display mit 60 Hz beweist keine
60 gerenderten oder tatsächlich präsentierten Bilder pro Sekunde. Android,
Energiesparmodus, andere sichtbare Fenster und thermische Grenzen können die
verfügbare Bildrate beeinflussen. `draw_p95_ms` im Diagnoseprotokoll misst nur die
verstrichene Zeit des Zeichenaufrufs, nicht reine CPU-Rechenzeit und nicht die nachfolgende GPU-/Compositor-Latenz.

## Benutzung

1. Die signierte APK als **Aktualisierung über 0.2.0 bis 0.4.0** installieren.
   Paketname und Release-Schlüssel bleiben gleich; keine Deinstallation oder
   Datenlöschung erforderlich. VersionCode ist jetzt 7.
2. **Live-Sternkarte öffnen** startet die große Ansicht.
3. **Freies Live-Fenster starten** öffnet das unabhängige Fenster. Die einmalige
   Freigabe erteilen, zu Sternfenster zurückkehren und anschließend eine andere App
   öffnen. Titelleiste ziehen; Größe am Griff unten rechts ändern.
4. Für ein geteiltes Taskfenster **Live-Sternkarte öffnen** und Samsungs
   Fenstersteuerung benutzen. Die kompakte Ansicht bietet die Bedienung unter **⋮**.
5. **Bild-im-Bild starten**, **Live-Fenster** in der großen Sternkarte oder
   **⋮ → Bild-im-Bild öffnen** verwenden den bisherigen Android-PiP-Modus.

Bild-im-Bild nutzt eine sichtbare Activity und benötigt keine Overlay-Berechtigung.
Der Zeichenzyklus beginnt in `onStart` und endet in `onStop`; er läuft während des
bei PiP eintretenden `onPause` weiter. Ohne das separat gestartete freie Fenster
läuft kein Zeichendienst. Ein neues Standortergebnis aus den Einstellungen wird auch während
PiP übernommen. Androids Unterstützung und Freigabe für Bild-im-Bild sind erforderlich.

| Bedienung | Wirkung |
| --- | --- |
| Wischen / zwei Finger / + und − | Blickrichtung und Sichtfeld ändern |
| N / O / S / W | Feste Himmelsrichtung bei 42° Blickhöhe; Rundblick aus |
| Handy folgen | Richtung, Neigung und Rollbewegung des Handys übernehmen |
| Rundblick | Kamera schwenkt gleichmäßig mit 5° pro Sekunde |
| Zeit | Echtzeit 1× → Zeitraffer 60× → Zeitraffer 600× → Echtzeit 1× |
| Zurücksetzen | Süd 180°, Höhe 42°, Sichtfeld 100°, Rundblick aus, echte Uhrzeit |
| Live-Fenster | Schwebende Bild-im-Bild-Ansicht mit Uhrzeit, Zeitmodus und Render-FPS |
| Freies Live-Fenster starten | Unabhängiges Fenster über anderen Apps |
| ⋮ | Alle Bedienaktionen auch in kleinen Taskfenstern |

**Bildrate und Zeitmaßstab sind getrennt.** In Echtzeit ist die natürliche
Himmelsbewegung langsam. Rundblick bewegt die virtuelle Blickrichtung;
Zeitraffer beschleunigt die berechnete astronomische Zeit und wird ausdrücklich
als solcher angezeigt. Es gibt keine zufälligen Ersatzsterne oder erfundene
Himmelsbewegung. Sonne, Mond und Planeten sind weiterhin nicht enthalten.

## Vorhandenes Vorschau-Widget

Das normale Startbildschirm-Widget bleibt ein statisches Vorschaubild mit einem
Systemintervall von 30 Minuten sowie manueller Aktualisierung über **Neu**.
Energiesparen kann Systemaktualisierungen verzögern. **Richtung** wählt den
Himmelsausschnitt, **Öffnen** startet die eigene Vollansicht. Für fortlaufende
Animation ist das schwebende Live-Fenster zu verwenden.

Ein `RemoteViews`-AppWidget kann keine eigene Canvas- oder SurfaceView enthalten.
Das 30-Minuten-Limit betrifft `updatePeriodMillis`, nicht jeden möglichen
manuellen Update-Aufruf. Häufige Bitmap-Updates sind hier kein Ersatz für eine
Vsync-Zeichenfläche.

## Wissenschaftliche Bedeutung

Die eingebettete unveränderte Datei enthält 9.096 Datensätze des zuvor verwendeten
Yale-Bright-Star-Katalogexports. Der Renderer verwendet die ausgewählten Sterne
mit Magnitude ≤ 6,3. Schwächere Sterne werden für die Zeichnung in Helligkeits-/
Farbgruppen zusammengefasst; ihre Positionen werden nicht gerastert.

Katalogdatei SHA-256:
8b36f9e06f7ab275506213cb6ed61ea75570dbfb19725c31ca189fee9196133b

Quelle des übernommenen Katalogexports: https://github.com/isene/starmap,
`data/stars.csv`. Keine Katalogdownloads zur Laufzeit.

Die Karte zeigt berechnete Positionen, keine Kameraaufnahme. Auch tagsüber werden
geometrisch über dem Horizont stehende Sterne gezeigt. Tageslicht, Wetter, Gebäude
und Lichtverschmutzung werden nicht modelliert. J2000-Katalogkoordinaten ohne
Präzession, Nutation, Eigenbewegung und Refraktion: eine orientierende Sternkarte,
keine Teleskopsteuerung.

Optionale Standortberechtigungen; für das freie Fenster Overlayfreigabe und ein
deklarierter ForegroundService mit optionaler Benachrichtigungsfreigabe.
Keine Internet-, Kamera-, Hintergrundstandort-, Speicher- oder
Accessibility-Berechtigung.

## Build und Signierung

Android SDK Platform 36, Build Tools 36.0.0, JDK 17; Gradle optional mit
Gradle 8.11.1 / Android Gradle Plugin 8.10.1. minSdk 26, targetSdk 36.

```bash
python3 tools/build_local.py --sdk /pfad/zum/android-sdk \
  --signing-info /privat/signing.json \
  --output /ausgabe/Sternfenster_Android_v0.4.1.apk
```

Ohne Signierungsdaten erzeugt das Skript ausschließlich eine `UNSIGNED`-Prüfdatei.
CI baut mit einem kurzlebigen eigenen Testschlüssel; der private Release-Schlüssel
wird nicht an das öffentliche Repository oder CI übertragen.

Release-Zertifikat SHA-256 seit 0.2.0:
88ea977a6afba06d2211611bde63fc496ee6c2f3d2e5c8027f1c2a444ffd8180

Version 0.1.0 hatte einen anderen temporären Schlüssel. Nur beim Wechsel von dieser
alten Version ist eine Deinstallation erforderlich; 0.2.0 und spätere Releases
lassen sich direkt aktualisieren.

## Historische Prüfung von 0.4.0

Für 0.4.0 prüft `tools/runtime_overlay.py` das tatsächlich sichtbare Android-Overlay:
Start aus der Oberfläche, WindowManager-Typ und Grenzen, Ziehen, Vergrößern,
Home, Wechsel zu Chrome, Entfernen des beobachteten App-Tasks,
fortgesetzte Sensorsteuerung/Renderzähler sowie ausdrückliches Schließen ohne
selbstständiges Wiederöffnen. Der separate Accessibility-Probe erhält einen
opt-in-Modus für alle interaktiven Fenster; die vorhandenen Tests behalten ihren
bisherigen Standardmodus. Wenn Android das nicht fokussierte Overlay im
Accessibility-Baum auslässt, werden Paketbesitz, UID, Fenstertyp, sichtbare und
gezeichnete WindowManager-Surface sowie Bildschirmgrenzen geprüft. Ein bloß
weiterlaufender Dienst gilt nicht als sichtbares Fenster.

**Auslieferungsprüfung bestanden:** elf Overlay-/Fensterprüfungen, zehn
Sensorprüfungen und sieben bestehende Live-/PiP-Prüfungen auf Android 15 / API 35.
Nach Entfernung des tatsächlich beobachteten Haupttasks blieb der Prozess mit
derselben PID aktiv; das sichtbare Fenster zeichnete weiter und reagierte auf
geänderte Sensorsignale. Ausdrückliches Schließen entfernte Fenster, Dienst und
Sensorlistener ohne Wiederauftauchen während der anschließenden Beobachtung.
Erneutes Öffnen stellte Position und Größe exakt wieder her. Die kompakte Ansicht
verwendete im Test mit verkleinerter Bildschirmhöhe 75,54 % der Höhe für die Karte;
Menüaktionen und Blickrichtung blieben erhalten. Kein Sternfenster-Absturz oder
Sternfenster-ANR wurde beobachtet.

Die unveränderte Chrome-Willkommensseite diente als andere App; keine Anmeldung
oder Webnavigation. Ein vorheriger Lauf mit der Android-15-Einstellungshauptseite
zeigte eine beabsichtigte Systemgrenze: Diese blendet fremde Overlays mit
`HIDE_NON_SYSTEM_OVERLAY_WINDOWS` aus, obwohl Fenster und Dienst weiter existieren.
Für solche geschützten Ansichten bleibt die normale Activity mit Android-PiP oder
geteilter Taskansicht verfügbar. Die Schutzfunktion wird nicht umgangen.

Die gemessenen gewichteten Overlay-Raten lagen im SwiftShader-Emulator je Phase
zwischen 19,102 und 28,210 Render-FPS; die Live-/PiP-Prüfung erreichte 20,153 bzw.
15,089 Render-FPS. **Diese Läufe bestätigen keine 60-FPS-Untergrenze.** Eine Messung
von 0.4.0 auf Stefans Telefon und von tatsächlich präsentierten Frames steht aus.
Samsungs Fensterverwaltung, physische Kompassgenauigkeit und Wiederherstellung nach
systembedingtem Prozessverlust wurden nicht im Emulator nachgewiesen. Die
Freigabedialoge wurden statisch geprüft; CI erteilt die Berechtigungen vor dem Test.

Alle Ergebnisse, Grenzen, APK-Prüfsumme und CI-Läufe stehen in
`VALIDATION_v0.4.0.json`. Die unveränderten Rohberichte liegen unter
`validation/v0.4.0/`. Der Appcode der 0.4.0-Auslieferung entspricht Commit
`fdb4f7e7d45fca20a0b8289556699ddb984066f0`; nachfolgende Commits bis zur
0.4.0-Dokumentation betreffen Prüfwerkzeuge und Dokumentation. CI verwendet einen eigenen Testschlüssel und
baut aus denselben Appquellen wie die ausgelieferte signierte APK.

### Historische 0.3.1-Prüfung

Die Sensorversion wird durch `tests/DeviceOrientationCheck.java` (bekannte Posen,
Displayrotation, Roll, Deklination, Polübergänge und Quaternionen) sowie
`tools/runtime_orientation.py` geprüft. Der Integrationstest injiziert konsistente
Gravitations- und Magnetfeldwerte in echte Emulator-Sensoren und prüft die von der
App sichtbaren Winkel, Moduswechsel, Hintergrund-Stopp und PiP. Es gibt keinen
Testeingang für simulierte Posen in der ausgelieferten App. Ergebnisse dieser
Version stehen in `VALIDATION_v0.3.1.json`. Alle zehn Sensorprüfungen, sieben
Live-/PiP-Funktionsprüfungen und zehn historischen Regressionstests bestanden.
96.346 Orientierungs-/Projektionsprüfungen sowie 7.484 bestehende
Projektionsprüfungen bestanden ebenfalls. Nach den Laufzeittests wurde nur noch
die vertikale Ausrichtung der vier Bewegungsschaltflächen korrigiert und die APK
neu gebaut/signaturgeprüft; dieser kleine Layoutnachtrag wurde nicht erneut im
Emulator ausgeführt. Physische Kompassgenauigkeit
und eine garantierte Mindestbildrate auf dem Telefon sind durch den Emulator nicht
bewiesen.

### Historische 0.3.0-Prüfung

Der neue Laufzeittest `tools/runtime_live60.py` prüft Start, Bedienung,
Hintergrund-Stopp, Wiederaufnahme und fortlaufendes PiP auf dem Startbildschirm.
Bei aktivem Rundblick misst er 10 Sekunden Vollansicht und 8 Sekunden PiP.
Appseitige Renderzähler und Android-`gfxinfo` werden separat gesichert.

Ein erfolgreicher Funktionslauf belegt keine pauschale 60-FPS-Untergrenze. Der
Bericht weist Messwerte und Leistungsbewertung gesondert aus. Ein Emulator ersetzt
keine Messung auf Stefans Samsung. Die konkrete Auslieferungsprüfung steht in
`VALIDATION_v0.3.0.json`.

Der erste API-35-Lauf bestand alle sieben Funktionsprüfungen, einschließlich
animierter PiP-Ansicht über dem Launcher. Mit SwiftShader bei 1080 × 2400 Pixeln
wurden im bewegten Vollbild gewichtet 15,391 Render-FPS und im PiP 17,149 Render-FPS
gemessen. **Der Lauf bestätigt daher keine 60 FPS.** Die aufgezeichneten
Frame-Metriken zeigen lange Wartezeiten vor dem RenderThread; eine Übertragung
dieser virtuellen Leistung auf das physische Telefon ist nicht gerechtfertigt.
Die Auswertung mit Formeln und Datenqualitätsgrenzen steht in
`PERF_ANALYSIS_v0.3.0.json`; die zugrunde liegenden Frame-Zeitstempel bleiben unter
`validation/v0.3.0/` im Projekt erhalten.

Für die laufend animierte Oberfläche verwendet CI ein separates, kurzlebiges
Test-APK für Accessibility-Snapshots ohne Warten auf UI-Ruhe. Es instrumentiert
ausschließlich sein eigenes Paket und ist weder Teil der Release-APK noch eine
zusätzliche Berechtigung der App. Die eigentlichen UI-, Absturz- und
Leistungsprüfungen bleiben unverändert.

Auch der abschließende Lauf mit diesem Probe bestand alle sieben Live-/PiP-
Funktionsprüfungen und alle zehn historischen Regressionstests. Die wiederholte
Leistungsmessung erreichte gewichtet 14,907 Render-FPS im Vollbild und 15,108 im
PiP. Ein gesonderter Pixel-Launcher-ANR des Emulators wurde erkannt und geschlossen;
im Sternfenster-Prozess trat kein Absturz oder ANR auf. Der Leistungsnachweis von
mindestens 60 FPS auf dem physischen Telefon bleibt offen.

Die historischen Berichte `VALIDATION_v0.2.0.json` und `VALIDATION_v0.2.1.json`
dokumentieren frühere Releases. Der dort behobene Startfehler beim zu frühen
Fensterzugriff bleibt korrigiert. Die Nutzerscreenshots von 0.2.1 bestätigen die
Darstellung beider App-Ansichten und des Vorschau-Widgets auf dem Samsung.

## Android-Primärquellen

- https://developer.android.com/reference/android/hardware/SensorManager
- https://developer.android.com/reference/android/view/Display#getRotation()
- https://developer.android.com/reference/android/hardware/GeomagneticField
- https://developer.android.com/develop/sensors-and-location/sensors/sensors_overview
- https://developer.android.com/reference/android/widget/RemoteViews
- https://developer.android.com/develop/ui/views/appwidgets/advanced
- https://developer.android.com/develop/ui/views/picture-in-picture
- https://developer.android.com/reference/android/view/Choreographer
- https://developer.android.com/reference/android/view/View#setRequestedFrameRate(float)
- https://developer.android.com/media/optimize/performance/frame-rate
- https://developer.android.com/reference/android/view/WindowManager.LayoutParams#TYPE_APPLICATION_OVERLAY
- https://developer.android.com/develop/background-work/services/fgs/service-types
- https://developer.android.com/reference/android/provider/Settings#ACTION_MANAGE_OVERLAY_PERMISSION
- https://developer.android.com/develop/background-work/services/fgs/handle-user-stopping
- https://developer.android.com/about/versions/12/features#hide-application-overlay-windows

Code-Lizenz: MIT. Keine Code- oder Grafikbestandteile der Fremd-App übernommen.
