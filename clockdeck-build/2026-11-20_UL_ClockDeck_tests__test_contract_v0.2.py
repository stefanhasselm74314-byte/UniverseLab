import pathlib, unittest, xml.etree.ElementTree as ET
ROOT=pathlib.Path(__file__).resolve().parents[1]
A='{http://schemas.android.com/apk/res/android}'
class Contract(unittest.TestCase):
    def test_xml_parse(self):
        for f in (ROOT/'app/src/main').rglob('*.xml'): ET.parse(f)
    def test_no_widget_stretching(self):
        d=ET.parse(ROOT/'app/src/main/res/layout/widget_clock.xml').getroot()
        img=next(e for e in d.iter() if e.attrib.get(A+'id')=='@+id/widget_background')
        self.assertEqual(img.attrib[A+'scaleType'],'fitCenter')
        self.assertEqual(img.attrib[A+'layout_width'],'0dp')
        self.assertTrue('layout_weight' in ''.join(img.attrib.keys()))
    def test_safe_compass_insets_and_no_weighted_spacer(self):
        s=(ROOT/'app/src/main/java/de/universelab/clockdeck/CompassActivity.java').read_text()
        self.assertIn('WindowInsets.Type.systemBars()',s)
        self.assertIn('scroll.setPadding',s)
        self.assertNotIn('LinearLayout.LayoutParams(-1,0,1f)',s)
    def test_new_version_and_widget_bitmap(self):
        v=(ROOT/'app/build.gradle').read_text()
        self.assertIn('versionCode 2',v)
        src=(ROOT/'app/src/main/java/de/universelab/clockdeck/WidgetBase.java').read_text()
        self.assertIn('final int side = 340;',src)
        self.assertNotIn('drawWidget(canvas,width,height',src)
if __name__ == '__main__': unittest.main()
