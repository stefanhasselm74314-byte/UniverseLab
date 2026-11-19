"""Holo-6D structural, geometry and image tests; not a device test."""

from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops


ROOT = Path(__file__).resolve().parents[1]
DRAWABLE = ROOT / "holoface/src/main/res/drawable"
XML = ROOT / "holoface/src/main/res/raw/watchface.xml"


class HoloFaceTests(unittest.TestCase):
    def test_three_independent_gyro_layers(self):
        document = ET.parse(XML)
        gyros = document.findall(".//Gyro")
        self.assertEqual(len(gyros), 3)
        for gyro in gyros:
            self.assertIn("[ACCELEROMETER_ANGLE_Y]", gyro.attrib["x"])
            self.assertIn("[ACCELEROMETER_ANGLE_X]", gyro.attrib["y"])
            self.assertIn("clamp", gyro.attrib["x"])
        self.assertEqual(len({g.attrib["x"] for g in gyros}), 3)

    def test_depth_plate_transparency_and_variation(self):
        images = []
        for name in ("holo_void", "holo_back", "holo_front"):
            with Image.open(DRAWABLE / f"{name}.png") as im:
                self.assertEqual(im.size, (450, 450))
                rgba = im.convert("RGBA")
                alpha = rgba.getchannel("A")
                self.assertEqual(alpha.getextrema()[0], 0)
                self.assertGreater(alpha.getextrema()[1], 50)
                images.append(rgba)
        self.assertIsNotNone(ImageChops.difference(images[1], images[2]).getbbox())

    def test_preview_and_ambient_mode(self):
        with Image.open(DRAWABLE / "preview.png") as preview:
            self.assertEqual(preview.size, (450, 450))
        root = ET.parse(XML).getroot()
        animated = root.find(".//PartAnimatedImage")
        self.assertIsNotNone(animated)
        self.assertIsNotNone(animated.find('Variant[@mode="AMBIENT"]'))
        images = root.findall(".//PartImage")
        for resource in ("holo_void", "holo_back", "holo_front"):
            matches = [part for part in images if
                       (part.find("Image") is not None and
                        part.find("Image").attrib.get("resource") == resource)]
            self.assertEqual(len(matches), 1)
            self.assertIsNotNone(matches[0].find('Variant[@mode="AMBIENT"]'))

    def test_unique_watchface_application(self):
        manifest = (ROOT / "holoface/src/main/AndroidManifest.xml").read_text()
        gradle = (ROOT / "holoface/build.gradle").read_text()
        self.assertIn('android:hasCode="false"', manifest)
        self.assertIn("de.universelab.holo6d", gradle)
        self.assertIn("':holoface'", (ROOT / "settings.gradle").read_text())


if __name__ == "__main__":
    unittest.main()
