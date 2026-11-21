package de.universelab.sternfenster.probe;

import android.accessibilityservice.AccessibilityServiceInfo;
import android.app.Activity;
import android.app.Instrumentation;
import android.app.UiAutomation;
import android.graphics.Point;
import android.graphics.Rect;
import android.hardware.display.DisplayManager;
import android.os.Bundle;
import android.os.SystemClock;
import android.util.Base64;
import android.util.Xml;
import android.view.Display;
import android.view.accessibility.AccessibilityNodeInfo;
import java.io.StringWriter;
import java.nio.charset.StandardCharsets;
import org.xmlpull.v1.XmlSerializer;

/** CI-only cross-app accessibility snapshot. Never waits for UI/render idleness. */
public final class SnapshotInstrumentation extends Instrumentation {
    private int nodes;
    private final Rect screen = new Rect();

    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        start();
    }

    @Override public void onStart() {
        Bundle result = new Bundle();
        AccessibilityNodeInfo root = null;
        try {
            UiAutomation automation = getUiAutomation();
            if (automation == null) throw new IllegalStateException("UiAutomation unavailable");
            AccessibilityServiceInfo info = automation.getServiceInfo();
            if (info == null) throw new IllegalStateException("Accessibility service not connected");
            info.flags |= AccessibilityServiceInfo.FLAG_REPORT_VIEW_IDS
                    | AccessibilityServiceInfo.FLAG_INCLUDE_NOT_IMPORTANT_VIEWS;
            automation.setServiceInfo(info);

            // Connection/window availability is different from UI idleness. The
            // animation keeps running while this bounded root-availability poll runs.
            long deadline = SystemClock.uptimeMillis() + 5000;
            do {
                root = automation.getRootInActiveWindow();
                if (root != null && root.isVisibleToUser()) break;
                if (root != null) { root.recycle(); root = null; }
                SystemClock.sleep(50);
            } while (SystemClock.uptimeMillis() < deadline);
            if (root == null) throw new IllegalStateException("No visible active-window accessibility root");

            Display display = getContext().getSystemService(DisplayManager.class).getDisplay(Display.DEFAULT_DISPLAY);
            int rotation = display == null ? 0 : display.getRotation();
            if (display != null) {
                Point size = new Point();
                display.getRealSize(size);
                screen.set(0, 0, size.x, size.y);
            }
            StringWriter output = new StringWriter();
            XmlSerializer xml = Xml.newSerializer();
            xml.setOutput(output);
            xml.startDocument("UTF-8", true);
            xml.startTag(null, "hierarchy");
            xml.attribute(null, "rotation", Integer.toString(rotation));
            xml.attribute(null, "source", "UiAutomation-no-idle-snapshot");
            nodes = 0;
            writeNode(xml, root, 0, 0);
            xml.endTag(null, "hierarchy");
            xml.endDocument();
            byte[] bytes = output.toString().getBytes(StandardCharsets.UTF_8);
            if (bytes.length > 600_000) throw new IllegalStateException("Snapshot exceeds safe instrumentation-result size");
            result.putString("snapshot_status", "ok");
            result.putString("snapshot_xml_base64", Base64.encodeToString(bytes, Base64.NO_WRAP));
            result.putInt("snapshot_nodes", nodes);
            finish(Activity.RESULT_OK, result);
        } catch (Throwable error) {
            result.putString("snapshot_status", "error");
            result.putString("snapshot_error", error.getClass().getName() + ": " + error.getMessage());
            finish(Activity.RESULT_CANCELED, result);
        } finally {
            if (root != null) root.recycle();
        }
    }

    private void writeNode(XmlSerializer xml, AccessibilityNodeInfo node, int index, int depth) throws Exception {
        if (!node.isVisibleToUser()) return;
        if (depth > 64 || ++nodes > 2000) throw new IllegalStateException("Unexpected accessibility-tree size");
        Rect bounds = new Rect();
        node.getBoundsInScreen(bounds);
        if (!screen.isEmpty() && !bounds.intersect(screen)) bounds.setEmpty();
        xml.startTag(null, "node");
        attribute(xml, "index", Integer.toString(index));
        attribute(xml, "text", safe(node.getText()));
        attribute(xml, "resource-id", safe(node.getViewIdResourceName()));
        attribute(xml, "class", safe(node.getClassName()));
        attribute(xml, "package", safe(node.getPackageName()));
        attribute(xml, "content-desc", safe(node.getContentDescription()));
        attribute(xml, "checkable", Boolean.toString(node.isCheckable()));
        attribute(xml, "checked", Boolean.toString(node.isChecked()));
        attribute(xml, "clickable", Boolean.toString(node.isClickable()));
        attribute(xml, "enabled", Boolean.toString(node.isEnabled()));
        attribute(xml, "focusable", Boolean.toString(node.isFocusable()));
        attribute(xml, "focused", Boolean.toString(node.isFocused()));
        attribute(xml, "scrollable", Boolean.toString(node.isScrollable()));
        attribute(xml, "long-clickable", Boolean.toString(node.isLongClickable()));
        attribute(xml, "password", Boolean.toString(node.isPassword()));
        attribute(xml, "selected", Boolean.toString(node.isSelected()));
        attribute(xml, "bounds", "[" + bounds.left + "," + bounds.top + "][" + bounds.right + "," + bounds.bottom + "]");
        for (int i = 0; i < node.getChildCount(); i++) {
            AccessibilityNodeInfo child = node.getChild(i);
            if (child == null) continue;
            try { writeNode(xml, child, i, depth + 1); }
            finally { child.recycle(); }
        }
        xml.endTag(null, "node");
    }

    private static void attribute(XmlSerializer xml, String name, String value) throws Exception {
        xml.attribute(null, name, value);
    }

    private static String safe(CharSequence value) {
        if (value == null) return "";
        String text = value.toString();
        StringBuilder result = new StringBuilder(text.length());
        for (int i = 0; i < text.length();) {
            int point = text.codePointAt(i);
            i += Character.charCount(point);
            if (point == 9 || point == 10 || point == 13 || (point >= 32 && point <= 0xd7ff)
                    || (point >= 0xe000 && point <= 0xfffd) || (point >= 0x10000 && point <= 0x10ffff)) {
                result.appendCodePoint(point);
            }
        }
        return result.toString();
    }
}
