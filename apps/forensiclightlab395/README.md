# Forensic Light Lab 395 · Android + Desktop

**Version:** 0.1.0 · **Zielgerät:** Samsung Galaxy S24 Ultra mit Android 17 · **Lichtquelle:** LUXNOVAQ UV-A 395 nm, 9 LEDs.

## Funktionen

- Kameravorschau mit lokal verarbeiteten RGB-Daten, Auswahl aus sechs Bildmodi.
- Bildregler für Helligkeit, Kontrast, Sättigung und Violett-Unterdrückung.
- Unveränderte Originalaufnahmen bei Weißlicht und UV 395 nm.
- Überlagerungsvergleich mit Wischregler (keine automatische Bildregistrierung).
- Getrennter Export von Originalen und bearbeiteten PNGs, unter Android im Ordner `Pictures/ForensicLightLab`.
- Keine Cloud-Verbindung, keine Bildübertragung, keine Analysedaten an Dritte.

## Android Studio

Projektordner öffnen und `:app:assembleDebug` ausführen. Java 17, Android Gradle Plugin 8.7.3, Gradle 8.10.2, Android SDK 35 erforderlich. Die gesamte App nutzt Android-System-APIs, keine weiteren Bibliotheken. APK unter `app/build/outputs/apk/debug/app-debug.apk`.

## Windows / PC

Die Datei `ForensicLightLab_395_Offline.html` im Browser öffnen. Kamera benötigt einen unterstützten sicheren Origin; Dateiöffnung wird nicht von jedem Browser akzeptiert. Alternativ ein lokales HTTP-Serverfenster starten, etwa `python -m http.server 8765`, und `http://localhost:8765/ForensicLightLab_395_Offline.html` aufrufen. Lokale Datei-Bildimporte funktionieren auch ohne Kamera.

## Grenzen und Sicherheit

Die Lampen-Wellenlänge wird hardwareseitig erzeugt, **nicht** von der App. Die violette Unterdrückung erfolgt nur auf RGB-Pixeln; sie ersetzt keinen optischen Langpass-/Sperrfilter. Die Kamera ist kein kalibriertes Spektrometer. Händlerangabe „45 W“ ist nicht als optische Leistung validiert. Nicht direkt in UV-Licht blicken; geeigneten UV-Augenschutz benutzen.

## Datenschutz

WebView lädt ausschließlich seine lokale HTML-Ressource. Netzwerkaufrufe werden explizit abgeblockt. `INTERNET` ist ausschließlich für die sichere WebView-Asset-Origin deklariert. Aufnahme startet nur nach Nutzereingabe; bei Hintergrundwechsel stoppt die Kamera. Die Android-App speichert erst nach explizitem Export.

**Status:** Funktionsfähiger Quellprojekt-Prototyp. Keine forensische Zertifizierung und keine Geräte-Hardwarevalidierung.
