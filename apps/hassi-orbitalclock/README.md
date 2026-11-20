# Hassi OrbitalClock v0.5 — Android-App und Widgets

## Änderungen
- Android-Widget-Hintergrund wird **transparent** gezeichnet (`@android:color/transparent`).
- Beide Zeitfelder sind native `TextClock`-Komponenten und bleiben automatisch synchron zur Systemzeit.
- Beide Motive besitzen **weiche transparente Bildränder**, nicht nur einen transparenten Widget-Container. Die Raumstation enthält weiterhin den Sternenhimmel innerhalb des Bildmotivs. Es handelt sich nicht um eine freigestellte 3D-Geometrie.
- Proportionale Größenberechnung mit zentriertem `widget_art`; auf Nova Launcher bleibt der Kreis rund.
- Schriftgröße skaliert adaptiv mit der darstellbaren Motivbreite.
- Android-App besitzt Motivauswahl, Lichtreflex und direkten Launcher-Widget-Picker.

## Signatur – wichtig

Dieses GitHub-Projekt ist öffentlich. Ein **privater** dauerhaft verwendeter Signierschlüssel darf weder als Datei noch als Klartext ins Repository eingecheckt werden.

Workflow und `app/build.gradle` unterstützen jetzt optional ein dauerhaftes Release-Signing via GitHub-Actions-Secrets:

1. `ORBITAL_SIGNING_KEYSTORE_B64` – base64-encodierte JKS/P12-Datei.
2. `ORBITAL_SIGNING_PASSWORD` – Keystore-Passwort.
3. `ORBITAL_SIGNING_ALIAS` – Schlüsselalias.
4. `ORBITAL_SIGNING_KEY_PASSWORD` – Schlüsselpasswort.

Bei vollständiger Konfiguration erzeugt GitHub Actions `assembleRelease` mit diesem Schlüssel; sonst wie bisher `assembleDebug`, das je CI-Runner nicht updatekompatibel sein muss. **Für v0.5 sind noch keine geschützten Secrets bestätigt.**

V0.4 wurde mit einem anderen, ephemeren Debugschlüssel signiert. Eine neue Release-Signatur (auch wenn diese jetzt dauerhaft eingerichtet wird) kann v0.4 nicht ohne Deinstallation ersetzen. Bei anschließenden Releases mit *derselben* privaten Signatur sind Updates ohne Deinstallation möglich.

**Keinesfalls einen privaten Signierschlüssel im GitHub-Repository hochladen oder im Chat veröffentlichen.**

## Build

In Android Studio öffnen und Build > Build APK(s) ausführen oder isolierten GitHub-Branch mit `.github/workflows/hassi-orbitalclock-apk.yml` bauen. Basis: Java 17, Android SDK 35, AGP 8.7.3, Gradle 8.10.2.

## Grenzen
- Das eigentliche Motiv rotiert nicht; nur ein Lichtreflex bewegt sich in der App.
- Preview-Bild in einigen Launchern ist statisch und zeigt ggf. eine ältere Beispielzeit.
- Automatisches Widget-Update wird durch Android `TextClock` ausgeführt; System-Energiesparmaßnahmen können das Verhalten beeinflussen.
- Ein erfolgreicher CI-Build ist kein Gerätetest.
