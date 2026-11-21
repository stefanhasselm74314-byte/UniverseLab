# Sternfenster – Android-Himmelswidget v0.1.0

Eigenständiges Homescreen-Widget für Android 8+; ausgelegt für Samsung Galaxy S24 Ultra.

## Funktionen

- Standort und aktuelle Uhrzeit steuern Sternpositionen (offline).
- Echte Sternpositionen und Helligkeiten, nicht zufällige Dekoration.
- Vier Blickrichtungen N/O/S/W (↻), manuelles Aktualisieren (⟳).
- Tippen auf den Himmel öffnet die vorhandene **Universe Star Finder v4.0.0** App
  (`com.youvendo.international_space_registry`, Activity `com.youvendo.star_finder.MainActivity`);
  wenn nicht installiert, öffnet sich die Widget-App.
- Automatische Aktualisierung durch Android ungefähr alle **30 Minuten**,
  mit möglichen Verzögerungen durch Energiesparrichtlinien.
- Kein Internetzugriff und keine Telemetrie; Standort lokal im App-Speicher.

## Installation (nach Build)

1. Installiere `app-debug.apk` auf dem Android-Gerät (aus Android-Dateien).
2. Öffne **Sternfenster** einmal, tippe **Standort ermitteln** und erteile optional
   die Berechtigung. Ohne Berechtigung verwendet die App einen klar gekennzeichneten
   Standardwert für Dresden.
3. Auf freie Stelle des Startbildschirms lange drücken → **Widgets** →
   **Sternfenster** → hinzufügen; mindestens ca. 4×2 Felder sind empfehlenswert.
4. Auf die Sternkarte tippen = Star Finder öffnen. ↻ und ⟳ steuern das Widget.

## Bauen

Dieses ZIP ist ein Android-Gradle-Projekt. Android Studio: Ordner öffnen,
JDK 17 und Android SDK Platform 35 bereitstellen, **Build APK(s)** ausführen.
Alternativ: `gradle assembleDebug` mit Gradle 8.10.2 (Android Gradle Plugin 8.8.2).

Die enthaltene kleine Sternliste dient nur als **Offline-Fallback** für den Source-Build.
Für vollständige Genauigkeit den öffentlichen Yale Bright Star Catalog hinzufügen:

```sh
curl -fsSL https://raw.githubusercontent.com/isene/starmap/master/data/stars.csv \
  -o app/src/main/assets/stars.csv
```

Das vorbereitete GitHub-Actions-Workflow lädt diesen Katalog vor dem Build automatisch.

## Wissenschaftliche und technische Grenzen

- Himmelspositionen: J2000 → lokale horizontale Koordinaten mit Greenwich Mean
  Sidereal Time (GMST), keine Präzession, Nutation, Eigenbewegung, Parallaxe oder
  Refraktion – für ein dekorativ-informatives Homescreen-Widget geeignet, aber
  **nicht** für präzise Teleskop-Ausrichtung.
- Alle Sterne unter dem mathematischen Horizont sind ausgeblendet; lokale Berge,
  Gebäude, Lichtverschmutzung und Wetter werden nicht modelliert.
- Blickrichtung ist vom Nutzer über ↻ wählbar, **nicht** per Gyroskop/Kompass
  automatisch geführt (Homescreen-Widgets besitzen keinen fortlaufenden Sensordatenstream).
- Widget ≠ Fernanzeige des Star-Finder-Grafikfensters. Die APK enthält keine
  öffentliche Widget-API oder deklarierte Sternkarten-ContentProvider-Schnittstelle.
- Android-AppWidgets haben systembedingte Updates/Bitmap-Größenbegrenzungen;
  daher kein kontinuierlicher 30/60-fps-Stream.
- Der APK-Build wurde in der aktuellen lokalen Umgebung **nicht** verifiziert,
  da dort keine Android-SDK-/Gradle-Buildwerkzeuge installiert sind.

## Herkunft / Lizenz

Yale Bright Star Catalogue, 5th Revised Edition (Hoffleit & Warren 1991),
public domain, bereitgestellt via https://github.com/isene/starmap (`data/stars.csv`).
Code: MIT-Lizenz, von Grund auf neu geschrieben. Es wurden keine Assets/Code aus
Universe Star Finder extrahiert oder übernommen.
