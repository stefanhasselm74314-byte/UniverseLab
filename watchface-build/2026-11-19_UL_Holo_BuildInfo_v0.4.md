# UniverseLab Holo-6D Titan-Spectrum Edition v0.4

**Datum:** 19.11.2026
**Version:** 0.4.0, getrennter Entwicklungsschritt nach Holo-6D v0.3
**Status:** experimenteller Softwarestand; Gerätelaufzeit, AOD-Verhalten und Stromverbrauch ungeprüft.

## Gestaltung und technische Umsetzung

- Hybriddesign aus Titan Skeleton und Spectrum Axis.
- Virtuelle gunmetal-Zahnräder, silberne Brücken und rote Lager auf der hinteren Parallaxenebene.
- Schmaler umlaufender Farbspektrum-Ring auf der vorderen Parallaxenebene.
- Mittlerer Dreiachsenkäfig als 30-Frame-WebP wie im geprüften v0.3-Stand.
- Drei WFF-v1-Gyro-Ebenen: Neigungsfaktoren -0,12, +0,08 und +0,20 px/Grad;
  maximal 12,8 Pixel Differenz bei 40 Grad.
- Uhrzeit, Batterie, Schritte, Puls und Datum nutzen native WFF-Datenquellen.
- Kompassrose im Zifferblatt statisch; echte Magnetpeilung nur in separater Sensor-App.
- 2,5D-Bewegungsparallaxe im AMOLED-Display, kein echtes optisches Hologramm.

Die Zahnräder, Brücken und der Spektralring entstehen reproduzierbar aus
eigenständiger Pillow-Geometrie. Das KI-Designbild ist ein ZIELBILD, keine
Pixel-genaue APK-Vorschau und kein Beleg funktionierender Sensordaten.

## Build und Installation

Materialisierung: watchface-build/2026-11-19_UL_Holo_Materialize_v0.4.py

- watchface-debug.apk: Basis-Watchface v0.2
- compass-debug.apk: Magnetkompass v0.2
- holoface-debug.apk: Titan-Spectrum v0.4
- UniverseLab_Holo_6D_Offline_v0.4.html: Smartphone-Vorschau

Die Holo-APK verwendet dieselbe Paketkennung de.universelab.holo6d
mit erhoehtem versionCode 4 und soll Version 0.3 aktualisieren.

## Pruefgrenzen

CI-Pruefungen: Unittests, Bildgeometrie, WFF-v1-Schema und Gradle-Build.
Ein erfolgreicher Build bestaetigt NICHT die reale Gyroskopreaktion,
die Display-Laufzeit oder die Akkuvertraeglichkeit auf der Uhr.

Die freigegebene v0.3-Entwurfsbasis bleibt in ihrem urspruenglichen Draft-PR
nachvollziehbar und unveraendert; main bleibt unangetastet.
