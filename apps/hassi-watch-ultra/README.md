# Hassi OrbitalWatch Ultra · Wear OS WFF v1
Zwei native, getrennt installierbare Watch Face Format Zifferblaetter fuer Galaxy Watch Ultra.
Aus dem bestehenden OrbitalClock-Motiv. **Weder Galaxy Wearable noch Bluetooth allein installieren diese APKs.**
Installation erfolgt auf der Uhr durch Watch Face Studio / Android Studio oder drahtloses ADB.
Android WFF Version 1, minSdk 33, targetSdk 35, kein App-Code.
Die Original-App unter apps/hassi-orbitalclock bleibt unberuehrt.
Build: python -m pip install Pillow && python apps/hassi-watch-ultra/tools/prepare_assets.py
gradle --no-daemon :watchface-dial:assembleDebug :watchface-station:assembleDebug (im Modul apps/hassi-watch-ultra).
Teststatus: GitHub-Action Build ist noch keine Validierung am physischen Geraet.
