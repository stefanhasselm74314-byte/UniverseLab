# UniverseLab ClockDeck Android v0.1

Eine native Android-App für das Samsung S24 Ultra: drei Homescreen-Uhr-Widgets und ein Live-Hintergrund mit drei umschaltbaren Stilen. Es handelt sich **nicht** um eine Wear-OS-APK.

## Funktionen
- Titanium Skeleton: sichtbare Zahnkränze, Brücken, Dreiachsen-Gyroskop.
- Compass Instrument: Kompass-Skala, echte magnetische Kursanzeige in der separaten Kompassansicht.
- Holo-6D: drehende Ringe und perspektivisch bewegliche Tiefenebenen.
- Echte Zeit in Widgets per Android TextClock (systemgeführt) und im Wallpaper per `Calendar`.
- Batteriestatus im Widget bei periodischem Refresh; im Wallpaper bei laufender Anzeige.
- Native Android-WallpaperService mit Hintergrund-Stopp bei Unsichtbarkeit.
- Sensorparallaxe im Wallpaper nur während Sichtbarkeit.
- Alles lokal, keine Netzwerkberechtigung, kein Analytics, keine Kontozugriffe.

## Installation
1. `UniverseLab_ClockDeck_v0.1_debug.apk` auf das **Smartphone** kopieren und öffnen.
2. Android fragt bei unbekannten APKs nach der Erlaubnis für die Installationsquelle.
3. App **UniverseLab ClockDeck** starten, einen Stil auswählen.
4. „Live-Hintergrund auswählen“ öffnet die Android-Vorschau. Erst dann bestätigen.
5. Widget: Lange auf freie Homescreen-Fläche drücken → Widgets → UniverseLab ClockDeck → Titan, Kompass oder Holo → hinzufügen.
6. Kompass-App in ClockDeck per „Kompass testen“ öffnen; Telefon waagerecht bewegen und ggf. kalibrieren.

## Realitätsgrenzen
- Die mechanischen Zahnräder sind **Grafik**; sie übertragen keine reale mechanische Energie.
- Der `Live Wallpaper`-Kompass basiert auf Magnetfeld und Beschleunigungssensor und zeigt **magnetischen Norden**, mit möglichen Störungen. Nicht für sicherheitskritische Navigation.
- Das Widget enthält **keine permanente Sensorerfassung** und kann seine Kompassrose nicht in Echtzeit drehen; Antippen öffnet eine echte Kompassanzeige.
- Die Widgets haben eine System-`TextClock`, sodass die Uhrzeit weiterläuft, obwohl Widget-Updates unter Android maximal alle 30 Minuten periodisch zugelassen werden.
- Das Wallpaper ist ein reaktives 2,5D-Rendering, **kein optisches Hologramm**.
- Nochmal: Ein erfolgreicher CI-Build ersetzt den Laufzeittest auf dem S24 Ultra nicht.

## Quellcode / Build
Android Gradle Plugin 8.10.1, Gradle 8.11.1, Java 17, compileSdk 36, minSdk 26, targetSdk 35.

Mit Android Studio öffnen oder im CI:

```bash
gradle :app:assembleDebug --no-daemon
```

## Datenschutz
Die App verwendet keine gefährlichen Berechtigungen, keine Netzwerkzugriffe, speichert nur Stil, Energieoption und Geschwindigkeit lokal.
