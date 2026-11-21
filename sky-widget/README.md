# Sternfenster 0.2.1 — eigene Android-Sternkarte

## Korrektur des Startabsturzes in 0.2.1

Version 0.2.0 griff in `Ui.install` auf den InsetsController des Fensters zu,
bevor `setContentView` die interne DecorView erzeugte. Bei einem Kaltstart
konnte dies MainActivity und SkyActivity mit einer NullPointerException beenden.
Das Startbildschirm-Widget war davon nicht betroffen.

0.2.1 installiert zuerst die Ansicht. Der Zugriff auf den InsetsController
erfolgt anschließend über die angehängte View mit Nullprüfung.
Die Abstände zu Systemleisten und Bildschirmaussparungen bleiben erhalten.

**Update von 0.2.0:** Die APK direkt als Aktualisierung installieren.
Paketname und Release-Signatur sind identisch, der VersionCode steigt von 2 auf 3.
Eine Deinstallation oder das Löschen der App-Daten ist nicht erforderlich.
Widget und gespeicherte Einstellungen bleiben dadurch erhalten.

## Änderungen

- Antippen des Widgets öffnet die eigene Live-Sternkarte.
- Universe Star Finder ist eine ausdrücklich gewählte Zusatzaktion in den Einstellungen.
- Die Vollansicht berechnet den Himmel jede Sekunde, solange sie sichtbar ist. Beim Verlassen stoppt der Zeitgeber.
- Wischen ändert die Blickrichtung. Zwei Finger sowie +/− ändern den Zoom. N/O/S/W und Zurücksetzen sind direkt bedienbar.
- Winkel und Zoom bleiben bei Rotation erhalten.
- Native Widget-Kopfzeilen und drei beschriftete Bedienflächen: Neu, Öffnen, Richtung.
- Karte und Schrift werden nicht mehr unabhängig in Breite und Höhe gestreckt.
- Fensterabstände berücksichtigen Systemleisten und Bildschirmaussparungen.
- Standortanforderungen laufen nach Knopfdruck bei geöffneter App maximal 20 Sekunden.

## Installation und einmaliger Wechsel von 0.1.0

Version 0.1.0 wurde mit einem temporären Android-Debugzertifikat ausgeliefert.
Dessen privater Schlüssel liegt für diesen Build nicht vor.
Version 0.2.0 verwendet einen privat gesicherten, dauerhaften Release-Schlüssel.

Daher können 0.2.0 und 0.2.1 eine Installation von 0.1.0 nicht direkt überschreiben.
Nur für diesen alten Versionswechsel gelten folgende Schritte:

1. Die neue APK herunterladen.
2. Die alte App **Sternfenster** deinstallieren. Dadurch verschwinden ihr Widget und ihre lokalen Einstellungen.
3. Die neue APK installieren und Sternfenster öffnen.
4. Standort erneut ermitteln und das Widget neu hinzufügen.
5. Empfohlene Widget-Größe: 4 × 3 Felder.

Universe Star Finder gehört nicht zu diesem Versionswechsel.
Unsere eigene Sternkarte funktioniert ohne diese andere App.

Zertifikat SHA-256 für 0.2.0 und künftige kompatible Builds:
88ea977a6afba06d2211611bde63fc496ee6c2f3d2e5c8027f1c2a444ffd8180

Den privaten Schlüssel niemals in dieses öffentliche Repository aufnehmen.
Das private Wiederherstellungspaket heißt Sternfenster_Signierung_PRIVAT_ab_v0.2.zip.
Es enthält den KeyStore und seine Zugangsdaten. Für weitere Releases denselben Schlüssel verwenden.

## Wissenschaftliche Bedeutung

Die Darstellung verwendet die eingebetteten 9.096 Datensätze des zuvor ausgelieferten
Yale-Bright-Star-Katalogs. Der Renderer wählt Sterne mit Magnitude ≤ 6,3.
SHA-256 der unveränderten Katalogdatei:
8b36f9e06f7ab275506213cb6ed61ea75570dbfb19725c31ca189fee9196133b

Quelle des Katalogexports: https://github.com/isene/starmap, data/stars.csv.
Die in 0.1.0 eingebetteten Daten werden wiederverwendet; zur Laufzeit gibt es keinen Download.

Es sind berechnete Katalogpositionen, keine Kameraaufnahme. Auch bei Tageslicht
werden die geometrisch oberhalb des Horizonts stehenden Sterne gezeigt.
Wetter, Tageshelligkeit, Berge, Gebäude und Lichtverschmutzung werden nicht modelliert.
J2000-Koordinaten werden ohne Präzession, Nutation, Eigenbewegung und Refraktion
in das lokale Horizontsystem umgerechnet. Eine orientierende Sternkarte,
keine präzise Teleskopsteuerung. Sonne, Mond und Planeten sind nicht enthalten.

Nur optionale Standortberechtigungen. Keine Internet-, Hintergrundstandort-,
Overlay-, Speicher- oder Benachrichtigungsberechtigung.

## Widget und Vollansicht

- **Startbildschirm:** Android-AppWidget, Systemintervall 30 Minuten und manuelles Aktualisieren.
  Energiesparen kann Systemaktualisierungen verzögern.
- **Vollansicht:** Neuberechnung jede Sekunde, während die Activity sichtbar ist.
  Beim App-Wechsel läuft kein Hintergrunddienst weiter.
- **Externe App:** Der optionale Star-Finder-Start repariert dessen GPU-Engine nicht.
  Der Fehler engine_view_recreated gehört nicht zu unserer Zeichenengine.

## Build

Android Studio/Gradle: JDK 17, Gradle 8.11.1, Android Gradle Plugin 8.10.1,
SDK Platform 36. minSdk 26, targetSdk 36, VersionCode 3.

Alternativ ohne Gradle-Abhängigkeiten:

python3 tools/build_local.py --sdk /pfad/zum/android-sdk --signing-info /privat/signing.json --output /ausgabe/Sternfenster_Android_v0.2.1.apk

Benötigt: SDK Platform 36, Build Tools 36.0.0 und ein JDK mit Java-Compiler.
signing.json enthält keystore, alias und password; der Keystorepfad kann relativ
zu signing.json sein. Ohne --signing-info entsteht nur eine mit UNSIGNED
bezeichnete Prüfdatei, keine installierbare Release.
Der Build-Workflow erzeugt eine unsignierte Prüf-APK. Der Laufzeittest signiert
seine APKs ausschließlich mit einem vorübergehenden CI-Testschlüssel.
Der private Release-Schlüssel wird nicht an GitHub übertragen.

## Validierung

- Android-Ressourcen/Java-Build, DEX, ZIP-Struktur und APK-Signatur geprüft.
- 7.484 reine Java-Projektions- und Größenprüfungen bestanden: Achsen, Grenzen,
  Antipoden, endliche Ergebnisse und isotrope Skalierung.
- Statische Zweitprüfung von Activity-Lebenszyklus, Standortberechtigungen,
  Widget-PendingIntents und Systemleistenabständen.
- Die Widget-Anzeige von **0.2.0** ist durch Nutzerscreenshots bestätigt.
  Diese Screenshots zeigen zugleich den Absturz beim Öffnen der App.
- Der neue Laufzeittest prüft zuerst den Startfehler der unveränderten 0.2.0,
  danach Kaltstart, eigene Vollansicht, Bedienung, Wiederaufnahme, Rotation
  und Prozessneustart mit 0.2.1. Das konkrete Ergebnis wird im CI-Protokoll
  und nach erfolgreichem Lauf im Validierungsbericht festgehalten.
- Ein Test von **0.2.1 auf Stefans Samsung-Gerät** steht noch aus.

Code-Lizenz: MIT. Keine Code- oder Grafikbestandteile der Fremd-App übernommen.
