#!/usr/bin/env python3
"""Rebuild the standard Android project from versioned, contract-compliant source files."""
from pathlib import Path
import shutil, subprocess, sys, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
OUT=HERE.parent/"build_clockdeck"
SOURCE_MAP={
  "README_DE.md": "2026-11-20_UL_ClockDeck_README_DE_v0.1.md",
  "app/build.gradle": "2026-11-20_UL_ClockDeck_app__build_v0.1.gradle",
  "app/src/main/AndroidManifest.xml": "2026-11-20_UL_ClockDeck_app__src__main__AndroidManifest_v0.1.xml",
  "app/src/main/java/de/universelab/clockdeck/Battery.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__Battery_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/ClockRenderer.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__ClockRenderer_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/CompassActivity.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__CompassActivity_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/CompassWidget.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__CompassWidget_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/HoloWallpaperService.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__HoloWallpaperService_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/HoloWidget.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__HoloWidget_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/MainActivity.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__MainActivity_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/TitanWidget.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__TitanWidget_v0.1.java",
  "app/src/main/java/de/universelab/clockdeck/WidgetBase.java": "2026-11-20_UL_ClockDeck_app__src__main__java__de__universelab__clockdeck__WidgetBase_v0.1.java",
  "app/src/main/res/layout/widget_clock.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__layout__widget_clock_v0.1.xml",
  "app/src/main/res/values/strings.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__values__strings_v0.1.xml",
  "app/src/main/res/xml/wallpaper_info.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__xml__wallpaper_info_v0.1.xml",
  "app/src/main/res/xml/widget_compass.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__xml__widget_compass_v0.1.xml",
  "app/src/main/res/xml/widget_holo.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__xml__widget_holo_v0.1.xml",
  "app/src/main/res/xml/widget_titan.xml": "2026-11-20_UL_ClockDeck_app__src__main__res__xml__widget_titan_v0.1.xml",
  "build.gradle": "2026-11-20_UL_ClockDeck_build_v0.1.gradle",
  "gradle.properties": "2026-11-20_UL_ClockDeck_gradle_v0.1.properties",
  "settings.gradle": "2026-11-20_UL_ClockDeck_settings_v0.1.gradle",
  "tools/make_icons.py": "2026-11-20_UL_ClockDeck_tools__make_icons_v0.1.py"
}
if OUT.exists() and any(OUT.iterdir()):
    raise RuntimeError("Build destination exists and is not empty: "+str(OUT))
for dest,filename in SOURCE_MAP.items():
    target=OUT/dest
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(HERE/filename,target)
subprocess.run([sys.executable,str(OUT/"tools/make_icons.py")],check=True)
for xml in OUT.rglob("*.xml"):
    ET.parse(xml)
from PIL import Image
for icon in ["app_icon.png","widget_preview_titan.png","widget_preview_compass.png","widget_preview_holo.png"]:
    with Image.open(OUT/"app/src/main/res/drawable"/icon) as im:
        assert im.width>200 and im.height>200
assert (OUT/"app/src/main/AndroidManifest.xml").read_text().count('android.appwidget.provider')==3
assert 'WallpaperService' in (OUT/"app/src/main/AndroidManifest.xml").read_text()
print("PASS: recreated",len(SOURCE_MAP),"Android files; 3 widget providers, 1 live wallpaper; XML + images valid")
