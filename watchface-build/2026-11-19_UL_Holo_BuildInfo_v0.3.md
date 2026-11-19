# UniverseLab Holo-6D Edition – experimentelles Watchface

**Datum:** 19.11.2026  
**Version:** v0.3.0, eigenständige Alternative zum Gyroscope-Face v0.2  
**Status:** Softwareentwurf. Installation, Laufzeit und Stromverbrauch auf
Galaxy Watch Ultra bisher **nicht** geprüft.

## Funktion

Auf einem realen flachen Super-AMOLED-Display wird eine **2.5D-Tiefenillusion**
dargestellt. Das ist ausdrücklich kein optisches Hologramm und keine Projektion
über das Uhrglas hinaus.

Die Wear-OS-Watch-Face-Format-1-Konfiguration benutzt drei unabhängig
bewegliche Ebenen und das offizielle `<Gyro>`-Element:

| Ebene | Ressource | Horizontales Bewegungsgesetz |
|---|---|---|
| Hintergrundring | `holo_back.png` | Δx = −0,12·clamp(θᵧ, −40°, 40°) px |
| Mechanisches Gyroskop | animiertes WebP | Δx = 0,08·clamp(θᵧ, −40°, 40°) px |
| Vordergrundlicht | `holo_front.png` | Δx = 0,20·clamp(θᵧ, −40°, 40°) px |

Die vertikale Verschiebung verwendet entsprechend θₓ. θₓ/θᵧ sind die von WFF
bereitgestellten Beschleunigungssensor-Neigungswinkel; die Faktoren sind
ästhetisch gewählte Displaypixel pro Grad, **keine physikalisch kalibrierte
Stereodisparität**. Die maximale Verschiebungsdifferenz der hintersten und
vordersten Ebene beträgt 12,8 px bei ±40°. Es entsteht monokulare
Bewegungsparallaxe durch unterschiedliche Bildtransformationen.

Die Gradskala N/O/S/W bleibt statisch. Ein **echter magnetischer Kompass**
wird wie in v0.2 über eine separat installierte Sensor-App geöffnet. Uhrzeit,
Batterie, Schritte, Puls und Datum stammen aus WFF-Datenquellen.

## Energiesparen

- In Always-on/Ambient werden Animation und lichtintensive Zusatzebenen
  ausgeblendet; das Standbild bleibt.
- Maximal 30 animierte WebP-Frames, 100 ms je Frame wie in v0.2.
- Der `<Gyro>`-Effekt kann häufige Sensoraktualisierungen verursachen;
  Stromverbrauch und AOD-Verhalten müssen **am Gerät** gemessen werden.
- Ziel ist nach späterem Gerätetest eine stromsparende Alltagskonfiguration;
  diese Fassung ist zunächst ein Experiment.

## Projektaufbau

Im CI-Build werden drei eigenständige APKs erstellt:

- `watchface-debug.apk`: funktionaler Basisstand v0.2
- `compass-debug.apk`: Sensorkompass v0.2
- `holoface-debug.apk`: Holo-6D v0.3 mit drei Parallaxenebenen

`python watchface-build/2026-11-19_UL_Holo_Materialize_v0.3.py` generiert die
herkömmlichen Android-Dateinamen nur im Build-Verzeichnis. Der Datums- und
Versionsvertrag des UniverseLab-Repositories bleibt für die eingecheckten
Dateien erhalten.

Zusätzlich entsteht die eigenständige, vollständig offline nutzbare
`UniverseLab_Holo_6D_Offline_v0.3.html`. Die Neigung kann am Smartphone mit
Touch/Reglern simuliert werden; der optional aktivierbare Bewegungssensor
benötigt gegebenenfalls Browservertrauen (HTTPS) und Erlaubnis. Das ist eine
**Browserdemonstration**, keine Wear-OS-Ausführung.

**Prüfstufen:** XML-Konsistenz, eigene Unit-Tests, offizieller Google
WFF-v1-Validator, Android-Gradle-Build; danach erst Emulator und Galaxy Watch.

## Primärdokumentation

- [Watch Face Format: Gyro](https://developer.android.com/reference/wear-os/wff/common/transform/gyro)
- [Watch Face Format: Dynamic appearance](https://developer.android.com/training/wearables/wff/transform)
- [Watch Face Format: XML validation](https://developer.android.com/training/wearables/wff/debug)
