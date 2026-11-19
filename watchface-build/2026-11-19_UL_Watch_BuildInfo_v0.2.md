# UniverseLab Watch – reproduzierbarer Wear-OS-APK-Build

**Stand:** 19.11.2026, Build-Vorbereitung v0.2. Die echte Laufzeit auf einer
Galaxy Watch Ultra ist noch nicht geprüft.

Die Quelle bleibt mit dem UniverseLab FileNamingContract kompatibel: alle
versionierten Quelldateien liegen unter `watchface-build/`; `build.gradle`,
`AndroidManifest.xml` usw. entstehen **nur im temporären CI-Arbeitsverzeichnis**.

1. `python watchface-build/2026-11-19_UL_Watch_Materialize_v0.2.py`
2. `python -m unittest discover -s build_watch/tests -v`
3. `gradle -p build_watch :watchface:assembleDebug :compass:assembleDebug`

Voraussetzungen: Python 3.12, Pillow 11.3.0, JDK 17, Android SDK Platform 36,
Android Gradle Plugin 8.10.1 und Gradle 8.11.1. Der GitHub-Actions-Workflow
installiert diese Abhängigkeiten automatisch und stellt zwei **Debug-APKs** als
Workflow-Artefakt bereit, **sofern der Android-Build erfolgreich ist**.

- `watchface-debug.apk`: deklaratives WFF-v1-Zifferblatt mit animiertem Gyroskop
- `compass-debug.apk`: eigenständige App mit Sensorkompass

Das Zifferblatt enthält eine feste 360°-Kompassrose; die dynamische magnetische
Peilung liefert ausschließlich die separate App. Eine korrekt gebaute APK ist
noch kein Nachweis für die Qualität der Sensorwerte, das Verhalten bei Always-On
oder die praktische Installierbarkeit auf Stefans Uhr. Kein Signierschlüssel,
persönliche Daten, Play-Store-Zugang oder externer Netzwerkcode wird eingebunden.
