# Hassi OrbitalClock v0.4 – Android-App und Widgets

## Änderungen gegenüber v0.3

- Korrektur des beim Nova-Launcher-Resize beobachteten **verzerrten Seitenverhältnisses**. Die frei skalierbare Widget-Fläche enthält jetzt einen eigenen `widget_art`-Rahmen, dessen Breite/Höhe aus den vom Launcher gelieferten Widget-Optionen berechnet werden. Das Bild und beide TextClock-Overlays bleiben gemeinsam in diesem Rahmen.
- Android 12+ nutzt `RemoteViews.setViewLayoutWidth/Height` bei Start und Größenänderung. Das Artwork wird **nicht verzerrt**, sondern bei unpassendem Format mit ungenutzten Rändern zentriert dargestellt (Letterboxing). Für ältere Android-Versionen bleiben sichere feste Grundabmessungen erhalten.
- Dynamische Größe der Stunden-/Minutenschrift relativ zur tatsächlichen Motivbreite.
- `previewLayout` für unterstützte Launcher; andere Launcher verwenden weiterhin die statische Vorschaugrafik. Deren Beispielzeit ist keine Live-Uhrzeit.
- Vollbildansicht auf dem S24 Ultra behält das bisherige Layout und den zuschaltbaren Lichtreflex bei.

## Installation

Das APK wird als **Debug-Build** kompiliert. GitHub Actions erzeugt standardmäßig eine pro Build-Umgebung unterschiedliche Debug-Signatur. Wenn Android „App nicht installiert“ meldet, v0.3 zuerst deinstallieren und v0.4 neu installieren. Dabei werden vorhandene Widgets entfernt und müssen neu platziert werden.

## Empfohlene Widget-Proportionen

- Raumstation: langes Hochkantformat (709:1210, ca. 0,586:1).
- Zifferblatt: quadratisches Format (1:1).

Eine Launcher-Kachel darf breiter oder flacher sein: die Uhr sollte dann **nicht gestaucht**, sondern zentriert mit freien Randflächen angezeigt werden. Die tatsächliche Größenmeldung des Nova Launchers muss am Gerät getestet werden.

## Build und Evidenzstatus

Java 17, Android SDK 35, Gradle 8.10.2, AGP 8.7.3. Build via `.github/workflows/hassi-orbitalclock-apk.yml` in einem isolierten Entwicklungsbranch. Eine erfolgreiche Kompilierung ist **kein Gerätetest**. Der Bildkörper rotiert nicht; nur der Lichtreflex in der App. Keine Internetberechtigung und keine personenbezogene Datenübertragung.
