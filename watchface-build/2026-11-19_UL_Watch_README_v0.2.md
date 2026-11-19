# UniverseLab Watch – 6D Gyroscope & Kompass

**Version:** 0.1.0 (technischer Prototyp, 18.11.2026)  
**Zielgeräte:** Galaxy Watch Ultra / Wear OS 4–6 (theoretische WFF-v1-Kompatibilität, noch nicht auf einem Gerät nachgewiesen)  
**Autorenschaft:** eigenständiges UniverseLab-Design, keine kopierten kommerziellen Uhrwerke oder Markenlayouts

## Was bereits vorliegt

| Teil | Implementierung | Nachweis |
|---|---|---|
| Zeit | `DigitalClock` / 24 h, automatisch aus Wear OS | XML-Strukturprüfung |
| Batterie | `[BATTERY_PERCENT]` | XML-Strukturprüfung |
| Schritte | `[STEP_COUNT]` | XML-Strukturprüfung |
| Puls | `[HEART_RATE_Z]` | XML-Strukturprüfung; Wert hängt von Gerät/Messzustand ab |
| Datum | `[DAY]`, `[MONTH]` | XML-Strukturprüfung |
| Drei rotierende Ringachsen | 30-frame animiertes WebP; 3 s/Schleife | 30 Frames und Bildunterschiede geprüft |
| Energiesparansicht | Animation durch WFF-`Variant` ausgeblendet; Standbild bleibt | XML-Strukturprüfung |
| 360°-Gradskala | mathematisch erzeugt, mit N/O/S/W-Markierungen | Koordinatentests bestanden |
| Echte magnetische Richtung | separate `compass`-Android-App mit `TYPE_ROTATION_VECTOR`; Beschleuniger + Magnetfeld als Fallback | Quellcode geschrieben; **noch kein Gerätetest** |
| Anklickbares Kompassfeld | WFF-`Launch` öffnet separate App | XML-Strukturprüfung; **noch kein Gerätetest** |

### Wesentliche Grenze

Seit Januar 2026 verlangt Wear OS für installierbare Watchfaces das **Watch Face Format (WFF)**. Es ist deklarativ und darf keinen eigenen Java-/Kotlin-Code enthalten. Seine veröffentlichten Datenquellen enthalten Beschleunigungsdaten, aber keine frei nutzbare Magnetkompass-Peilung. Deshalb ist die Gradskala im eigentlichen Zifferblatt **statisch**; der echte Kompass wird beim Antippen in einer **zweiten, separat installierten APK** geöffnet. Die 3D-Mechanik im Zifferblatt ist eine bildbasierte 2D-Projektion, keine kontinuierlich gerenderte 3D-Engine.

## Dateien

- `watchface/`: resource-only-WFF-v1-Zifferblatt mit echten Uhrendaten und animiertem WebP.
- `compass/`: Android-App mit Sensorverarbeitung und magnetischer Kursanzeige.
- `assets/watchface-preview.png`: Designvorschau mit **Beispielwerten**.
- `UniverseLab_Watch_Demo_Offline.html`: eigenständige Smartphone-Vorschau, im Browser ohne Internet nutzbar.
- `scripts/make_assets.py`: zeichnet die Kompass-Geometrie und 30 Gyroskop-Bilder deterministisch.
- `scripts/build_demo.py`: bettet Bilder für Offline-HTML ein.
- `tests/test_package.py`: grundlegende Geometrie- und Strukturtests.

## Sofort auf dem Samsung S24 Ultra ausprobieren

1. Die Datei `UniverseLab_Watch_Demo_Offline.html` herunterladen.
2. In einem Browser öffnen (auf Android ggf. über **Eigene Dateien → Downloads → Öffnen mit Browser**).
3. **Mechanik: an/aus**, **Kompass öffnen**, **AOD testen** und den Schieberegler ausprobieren.

Die HTML-Vorschau ist **keine installierte Watchface-APK**. Nur Zeit und Datum sind sicher Live-Werte. Batterie wird angezeigt, sofern der Browser den Akku-Zugriff erlaubt. Puls und Schrittzahl sind ausdrücklich nicht simulierte Live-Messwerte; der Kompass im HTML ist eine Richtungssimulation.

## Android-APK-Build (erfordert SDK, noch nicht ausgeführt)

Die APKs können aus den beiden **getrennten Anwendungsmodulen** in Android Studio gebaut werden. Das Projekt enthält bewusst keine vorgetäuschte APK und keinen nicht vorhandenen Gradle-Wrapper.

1. Android Studio und ein aktuelles Android SDK (API 36) auf einem Rechner installieren.
2. Dieses Projekt als Gradle-Projekt öffnen. Falls Android Studio einen Gradle-Wrapper verlangt, einen lokalen Gradle-8.11.x-Wrapper für das Projekt erstellen.
3. Die Module `:watchface` und `:compass` mit dem Android-Gradle-Plugin 8.10.1 (Gradle 8.11.1, JDK 17) synchronisieren.
4. **Build → Build APK(s)** für jedes der beiden Module ausführen.
5. Beide Debug-APKs zuerst im Wear-OS-Emulator prüfen (WFF-Validierung, Animation, Ambient/AOD, Launch).
6. Anschließend die APKs auf der Galaxy Watch Ultra installieren, nicht auf dem S24 Ultra.

Nach einem erfolgreichen Debug-Build befinden sich die Dateien typischerweise unter:

```
watchface/build/outputs/apk/debug/watchface-debug.apk
compass/build/outputs/apk/debug/compass-debug.apk
```

### Installation vom S24 Ultra aus (ADB über WLAN)

Wenn auf der Watch **Entwickleroptionen → WLAN-Debugging** aktiviert ist und das S24 Ultra im gleichen WLAN ist:

```sh
# IP, Pairing-Port, Verbindungs-Port und Code stehen auf der Watch.
adb pair UHR_IP:PAIRING_PORT
adb connect UHR_IP:DEBUG_PORT
adb install -r compass-debug.apk
adb install -r watchface-debug.apk
```

Die Dateien müssen dazu vorher in Termux zugänglich sein. Die Verbindung und die Paketinstallation sind noch nicht auf Stefans Uhr getestet. Danach durch langes Drücken auf das Zifferblatt das neue UniverseLab-Face auswählen. **Kein privater Chat-/UniverseLab-Datenbestand wird benötigt oder hochgeladen.**

## Tests und noch offene Aufgaben

Mit `python3 -m unittest discover -s tests -v` wurden geprüft:

- mathematisch korrekte Positionen N=0°, O=90°, S=180°, W=270°;
- Bildabmessungen 450 × 450, 30 Frames und sichtbare Frame-Änderung;
- WFF-Struktur, Datenfelder und App-Verknüpfung;
- `hasCode=false` im Face-Manifest.

**Nicht erfolgt:** Android-Gradle-Build, WFF-Schema-Validator, Wear-OS-Emulator, tatsächliche APK-Installation, Sensor-Kalibrierung, Dauerlauf-/Akkutest, Display- und Touch-Test auf der Galaxy Watch Ultra. Diese Prüfungen sind Voraussetzung für den Status „installierbar / funktionsbestätigt“.

## Technische Quellen (Primärdokumentation)

- [Google: Watch Face Format](https://developer.android.com/training/wearables/wff)
- [Google: WFF-Konfiguration](https://developer.android.com/training/wearables/wff/setup)
- [Google: Zeitdarstellung](https://developer.android.com/training/wearables/wff/time)
- [Google: Animationen](https://developer.android.com/training/wearables/wff/transform/images)
- [Google: WFF-Datenquellen](https://developer.android.com/reference/wear-os/wff/common/attributes/source-type)
- [Google: Positionierungssensoren](https://developer.android.com/develop/sensors-and-location/sensors/sensors_position)
- [Samsung: Watch Face Studio](https://developer.samsung.com/watch-face-studio/overview.html)

## Sicherheits- und Datenhinweis

- Kein Netzwerkzugriff im Zifferblatt oder der Kompass-App implementiert.
- Keine Standortberechtigung; angezeigt wird die **magnetische**, nicht geografisch korrigierte Nordrichtung.
- Bei unzuverlässigen/mangelnden Sensorwerten wird dies sichtbar gemeldet; es werden keine Peilungen erfunden.
- Nicht für sicherheitskritische Navigation.
- Das Projekt ist vom UniverseLab-Hauptrepository unabhängig; an `main` wurden keine Änderungen vorgenommen.
