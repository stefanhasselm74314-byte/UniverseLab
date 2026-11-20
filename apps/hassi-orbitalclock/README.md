# Hassi OrbitalClock v0.3 – native Android-App + zwei Widgets

**Status:** vollständiges Quellprojekt. Die APK erfordert einen Gradle-/GitHub-Actions-Build; keine APK wird behauptet, solange die Kompilierung nicht durchgelaufen ist.

## Änderungen gegenüber v0.1

- Kein eingebettetes HTML / JavaScript mehr in der Android-App: Datum, Stunde und Minute werden durch native Android-`TextClock`-Elemente angezeigt.
- Die beiden Startbildschirm-Widgets erhalten die gleiche native Uhranzeige.
- Die Vollbild-App bietet Raumstation / Zifferblatt und eine optional rotierende Lichtreflexion. Das Foto selbst und die Widget-Motive bleiben statisch.
- Alle grafischen Ressourcen sind lokal; keine Internetberechtigung, keine Telemetrie.

## Auf Android (Galaxy S24 Ultra) installieren

1. APK (nach erfolgreichem Build) auf das Smartphone laden.
2. Die APK in **Eigene Dateien / Downloads** antippen; die Installation dieser Quelle ggf. für diesen Vorgang freigeben.
3. Startbildschirm lange berühren → **Widgets** → **Hassi OrbitalClock** → **Raumstation** oder **Zifferblatt** hinzufügen.
4. Die Uhr zeigt Stunde/Minute in 24-Stunden-Schreibweise. Antippen öffnet die native Vollbildansicht.

## Bauen

- Android Studio, JDK 17, Android SDK 35, Android Gradle Plugin 8.7.3.
- `gradle assembleDebug` im Projektordner (oder Android Studio: Build → Build APK).
- Die Debug-APK liegt unter `app/build/outputs/apk/debug/app-debug.apk`.
- In einem Repository kann `.github/workflows/build-android-apk.yml` den Build über GitHub Actions ausführen; der Build setzt eine erlaubte CI-Umgebung voraus.

## Grenzen

- `TextClock` wird von Android `RemoteViews` offiziell unterstützt. Die Minutenaktualisierung hängt im Widget zusätzlich von einem korrekt arbeitenden Launcher ab. App und Widgets sind bis zu einem erfolgreichen Gerätetest nicht als validiert anzusehen.
- Bei sehr kleiner Widget-Größe können die Felder beschnitten werden; für das volle Motiv empfehlen sich 4×6 (hochkant) bzw. 4×4 (quadratisch) Zellen.
- Die Bildquelle ist der vom Nutzer bereitgestellte Screenshot; die Grafik kann fremde Markierungen enthalten und wird hier nur für private Verwendung vorbereitet.

## v0.3 Anzeige/Bedienung
- WindowInsets für Statusleiste und Navigationsleiste auf Android 15–17.
- Dynamische Bildhöhe; Bedienfelder folgen dem Bild ohne große Leerflächen.
- Widget hinzufügen: nutzt Androids Launcher-Pinning für die gewählte Variante.
- Debug-APK kann neuen Signierschlüssel verwenden: im Fall INSTALL_FAILED_UPDATE_INCOMPATIBLE erst alte Version deinstallieren, dann v0.3 installieren.
