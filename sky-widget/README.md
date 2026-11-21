# Sternfenster 0.3.1 — Sternkarte folgt der Handyhaltung

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
CPU-Zeit des Zeichenaufrufs, nicht die GPU-/Compositor-Latenz.

## Benutzung

1. Die signierte APK als **Aktualisierung über 0.2.0, 0.2.1 oder 0.3.0** installieren.
   Paketname und Release-Schlüssel bleiben gleich; keine Deinstallation oder
   Datenlöschung erforderlich. VersionCode ist jetzt 5.
2. **Live-Sternkarte öffnen** startet die große Ansicht.
3. **Schwebendes Live-Fenster starten** oder **Live-Fenster** in der Sternkarte
   wechselt in Androids Bild-im-Bild-Modus. Danach Home drücken, um das Fenster
   über dem Startbildschirm zu sehen.
4. Das schwebende Fenster lässt sich über Android verschieben, vergrößern,
   zur Vollansicht zurückholen und schließen. Es ist kein fest in ein
   Launcher-Raster eingebettetes AppWidget.

Bild-im-Bild nutzt eine sichtbare Activity und benötigt keine Overlay-Berechtigung.
Der Zeichenzyklus beginnt in `onStart` und endet in `onStop`; er läuft während des
bei PiP eintretenden `onPause` weiter. Unsichtbar im Hintergrund läuft kein
Zeichendienst. Ein neues Standortergebnis aus den Einstellungen wird auch während
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

Nur optionale Standortberechtigungen. Keine Internet-, Hintergrundstandort-,
Overlay-, Speicher- oder Benachrichtigungsberechtigung.

## Build und Signierung

Android SDK Platform 36, Build Tools 36.0.0, JDK 17; Gradle optional mit
Gradle 8.11.1 / Android Gradle Plugin 8.10.1. minSdk 26, targetSdk 36.

```bash
python3 tools/build_local.py --sdk /pfad/zum/android-sdk \
  --signing-info /privat/signing.json \
  --output /ausgabe/Sternfenster_Android_v0.3.1.apk
```

Ohne Signierungsdaten erzeugt das Skript ausschließlich eine `UNSIGNED`-Prüfdatei.
CI baut mit einem kurzlebigen eigenen Testschlüssel; der private Release-Schlüssel
wird nicht an das öffentliche Repository oder CI übertragen.

Release-Zertifikat SHA-256 seit 0.2.0:
88ea977a6afba06d2211611bde63fc496ee6c2f3d2e5c8027f1c2a444ffd8180

Version 0.1.0 hatte einen anderen temporären Schlüssel. Nur beim Wechsel von dieser
alten Version ist eine Deinstallation erforderlich; 0.2.0 und spätere Releases
lassen sich direkt aktualisieren.

## Prüfung

Die Sensorversion wird durch `tests/DeviceOrientationCheck.java` (bekannte Posen,
Displayrotation, Roll, Deklination, Polübergänge und Quaternionen) sowie
`tools/runtime_orientation.py` geprüft. Der Integrationstest injiziert konsistente
Gravitations- und Magnetfeldwerte in echte Emulator-Sensoren und prüft die von der
App sichtbaren Winkel, Moduswechsel, Hintergrund-Stopp und PiP. Es gibt keinen
Testeingang für simulierte Posen in der ausgelieferten App. Ergebnisse der aktuellen
Version stehen nach Abschluss in `VALIDATION_v0.3.1.json`. Physische Kompassgenauigkeit
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

Code-Lizenz: MIT. Keine Code- oder Grafikbestandteile der Fremd-App übernommen.
