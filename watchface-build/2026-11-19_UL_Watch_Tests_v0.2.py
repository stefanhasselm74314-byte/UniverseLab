"""Checks that can run without Android SDK or an attached watch."""

import importlib.util
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("make_assets", ROOT / "scripts/make_assets.py")
geo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geo)


class ProjectTests(unittest.TestCase):
    def test_cardinal_geometry(self):
        self.assertEqual(tuple(round(x) for x in geo.pt(225,225,200,0)), (225,25))
        self.assertEqual(tuple(round(x) for x in geo.pt(225,225,200,90)), (425,225))
        self.assertEqual(tuple(round(x) for x in geo.pt(225,225,200,180)), (225,425))
        self.assertEqual(tuple(round(x) for x in geo.pt(225,225,200,270)), (25,225))

    def test_images(self):
        res = ROOT / "watchface/src/main/res/drawable"
        with Image.open(res / "watch_bg.png") as bg:
            self.assertEqual(bg.size, (450,450))
        with Image.open(res / "gyro_anim.webp") as anim:
            self.assertEqual(anim.n_frames, 30)
            anim.seek(0)
            first = anim.convert("RGBA").copy()
            anim.seek(10)
            tenth = anim.convert("RGBA").copy()
            self.assertIsNotNone(ImageChops.difference(first,tenth).getbbox())

    def test_wff_sources_and_structure(self):
        root = ET.parse(ROOT / "watchface/src/main/res/raw/watchface.xml").getroot()
        self.assertEqual(root.tag, "WatchFace")
        self.assertEqual(root.attrib["width"], "450")
        self.assertEqual(root.attrib["height"], "450")
        self.assertEqual(len(root.findall(".//DigitalClock")), 1)
        self.assertEqual(len(root.findall(".//PartAnimatedImage")), 1)
        expressions = {node.attrib.get("expression") for node in root.findall(".//Parameter")}
        self.assertEqual(expressions,{"[BATTERY_PERCENT]","[STEP_COUNT]",
                                      "[HEART_RATE_Z]","[DAY]","[MONTH]"})
        launches = root.findall(".//Launch")
        self.assertEqual(len(launches), 1)
        self.assertIn("de.universelab.compass", launches[0].attrib["target"])

    def test_resource_only_wff_manifest(self):
        root=ET.parse(ROOT / "watchface/src/main/AndroidManifest.xml").getroot()
        ns="{http://schemas.android.com/apk/res/android}"
        self.assertEqual(root.find("application").attrib[ns+"hasCode"],"false")
        self.assertEqual(root.find("application/property").attrib[ns+"value"],"1")
        self.assertTrue((ROOT / "compass/src/main/java/de/universelab/compass/CompassActivity.java").exists())


if __name__ == "__main__":
    unittest.main()
