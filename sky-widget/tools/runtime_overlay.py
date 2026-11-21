#!/usr/bin/env python3
"""Exercise the real movable Android overlay and its foreground-service lifetime.

Use only a disposable emulator: setup clears the candidate's data, grants its
overlay app-op and notification permission, and overrides physical sensor inputs.
The release application is started through its visible MainActivity button. The
separate CI accessibility probe observes all interactive windows without waiting
for render idleness; it adds no test interface to Sternfenster.

Task removal uses Android's observed task ID and `am stack remove`, which calls
ActivityTaskManager.removeTask. It is intentionally different from force-stop.
A successful functional run does not establish 60 presented FPS, physical compass
accuracy, Samsung window-manager behavior, or immunity to Android process death.
"""

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time
import traceback
import xml.etree.ElementTree as ET

from runtime_live60 import summarize_samples
from runtime_orientation import OrientationSmoke
from runtime_smoke import MAIN, PACKAGE, SKY, TestFailure


SERVICE = "FloatingSkyService"
OPEN = "Freies Live-Fenster starten"
DRAG = "Live-Fenster verschieben"
CLOSE = "Live-Fenster schließen"
RESIZE = "Live-Fenstergröße ändern"
WINDOW_TITLE = "Sternfenster Live-Fenster"
BOUNDS = re.compile(r"\[(-?\d+),(-?\d+)\]\[(-?\d+),(-?\d+)\]")
OVERLAY_PERF = re.compile(
    r"mode=overlay\s+frames=(\d+)\s+fps=([\d.]+)\s+"
    r"draw_p95_ms=([\d.]+)\s+hz=([\d.]+)")


def bounds_of(node):
    match = BOUNDS.fullmatch(node.get("bounds", ""))
    if not match:
        raise TestFailure(f"No observed screen bounds: {node.attrib}")
    result = tuple(map(int, match.groups()))
    if result[2] <= result[0] or result[3] <= result[1]:
        raise TestFailure(f"Empty observed bounds: {node.attrib}")
    return result


def parse_overlay_samples(raw):
    samples = []
    for line in raw.splitlines():
        match = OVERLAY_PERF.search(line)
        if not match or "SternfensterPerf:" not in line:
            continue
        frames, fps, p95, hz = match.groups()
        samples.append({"mode": "overlay", "frames": int(frames), "fps": float(fps),
                        "draw_p95_ms": float(p95), "display_hz": float(hz), "log_line": line})
    return samples


class OverlaySmoke(OrientationSmoke):
    def __init__(self, args):
        super().__init__(args)
        self.report.update(test="Sternfenster movable overlay persistence integration",
                           overlay_observations=[], task_removals=[],
                           functional_status="RUNNING",
                           user_device_test="NOT_PERFORMED",
                           minimum_60_fps_guarantee="NOT_ESTABLISHED",
                           process_death_survival="NOT_TESTED",
                           samsung_multiwindow_behavior="NOT_TESTED")
        self.report["sources"] += [
            "https://developer.android.com/reference/android/app/UiAutomation#getWindows()",
            "https://developer.android.com/reference/android/view/WindowManager.LayoutParams#TYPE_APPLICATION_OVERLAY",
            "https://android.googlesource.com/platform/frameworks/base/+/21f8b0e94160bb3615a569cc454c5c7ffc12221d/services/core/java/com/android/server/am/ActivityManagerShellCommand.java",
        ]
        self.report["performance_status"] = "RENDER_COUNTER_OBSERVATIONS_ONLY_NOT_PRESENTED_FPS"
        self.report["observation_limits"] = [
            "On this API35 emulator, UiAutomation sometimes omits the visible nonfocusable overlay, "
            "especially over the launcher. Persistence requires the app-owned visible WindowManager "
            "surface plus sensor/frame telemetry. Start, drag and resize still require accessibility controls.",
        ]
        self.close_geometry = None
        self.app_uid = None

    def dump_ui(self):
        result = self.adb("shell", "am", "instrument", "-w", "-e", "snapshot", "true",
                          "-e", "all_windows", "true",
                          "de.universelab.sternfenster.probe/.SnapshotInstrumentation", timeout=20)
        encoded = re.search(r"(?m)^INSTRUMENTATION_RESULT: snapshot_xml_base64=([A-Za-z0-9+/=]+)\s*$", result)
        if not encoded or not re.search(r"(?m)^INSTRUMENTATION_CODE:\s*-1\s*$", result):
            (self.out / "ui-probe-failure.txt").write_text(result, encoding="utf-8")
            raise TestFailure("No successful all-windows accessibility snapshot; see ui-probe-failure.txt")
        try:
            raw = base64.b64decode(encoded.group(1), validate=True).decode("utf-8")
        except (ValueError, UnicodeError) as exc:
            raise TestFailure(f"Invalid accessibility snapshot encoding: {exc}") from exc
        root = ET.fromstring(raw)
        if root.get("source") != "UiAutomation-no-idle-all-windows":
            raise TestFailure("The installed probe does not support the requested all-windows snapshot")
        self.last_xml = raw
        if self.recover_pixel_launcher_anr(root):
            return self.dump_ui()
        return root

    @staticmethod
    def sensor_samples(raw):
        # A compact-Activity check runs before the overlay checks. Scope the
        # observations explicitly so an Activity cannot satisfy an overlay check.
        return [sample for sample in OrientationSmoke.sensor_samples(raw)
                if re.search(r"\bmode=overlay\b", sample["log_line"])]

    def compact_sky_observation(self):
        root = self.dump_ui()
        for window in root.findall("window"):
            for node in window.iter("node"):
                if node.get("package") != PACKAGE or not node.get("content-desc", "").startswith("Sternkarte nach "):
                    continue
                sky_bounds, window_bounds = bounds_of(node), bounds_of(window)
                sky_height = sky_bounds[3] - sky_bounds[1]
                window_height = window_bounds[3] - window_bounds[1]
                fraction = sky_height / window_height
                if fraction < 0.60:
                    return None
                menu = self.node(window, description="Fenster und Bedienung")
                if menu is None or menu.get("enabled") != "true" or menu.get("clickable") != "true":
                    return None
                # The menu is closed at this point. Old full-size direction
                # buttons must not occupy the reduced-height star-map area.
                if self.node(window, description="Nach Osten blicken") is not None:
                    return None
                return {"sky_bounds": sky_bounds, "window_bounds": window_bounds,
                        "sky_fraction_of_window_height": round(fraction, 4),
                        "minimum_required_fraction": 0.60,
                        "menu_bounds": bounds_of(menu),
                        "compact_controls_observed": True}
        return None

    def tap_popup_menu_item(self, description, label):
        # Android PopupMenu handles item touches through its adapter. Its enabled
        # row and ListView can both expose clickable=false (observed on API35).
        # Keep the common button tap strict and target only this observed popup.
        def find():
            root = self.dump_ui()
            matches = []
            for window in root.findall("window"):
                if window.get("title") != "Popup Window" or window.get("focused") != "true" or window.get("active") != "true":
                    continue
                for listing in window.iter("node"):
                    if listing.get("class") != "android.widget.ListView" or listing.get("package") != PACKAGE or listing.get("enabled") != "true":
                        continue
                    for row in listing.iter("node"):
                        if row.get("package") != PACKAGE or row.get("content-desc") != description or row.get("enabled") != "true":
                            continue
                        titles = [node for node in row.iter("node")
                                  if node.get("resource-id") == "android:id/title"
                                  and node.get("package") == PACKAGE and node.get("text") == label
                                  and node.get("enabled") == "true"]
                        if len(titles) != 1:
                            continue
                        left, top, right, bottom = bounds_of(row)
                        wl, wt, wr, wb = bounds_of(window)
                        if not (wl <= left < right <= wr and wt <= top < bottom <= wb):
                            continue
                        matches.append(row)
            if len(matches) > 1:
                raise TestFailure("Popup menu item is not unique")
            return (matches[0],) if matches else None
        row = self.poll(f"enabled popup menu row {label!r}", find)[0]
        left, top, right, bottom = bounds_of(row)
        self.adb("shell", "input", "tap", str((left + right) // 2), str((top + bottom) // 2))
        self.report["compact_activity"]["popup_item_tap"] = {
            "label": label, "description": description, "bounds": [left, top, right, bottom],
            "method": "physical tap on enabled row in focused Popup Window/ListView; state checked afterwards",
        }

    def check_compact_activity(self):
        self.launch()
        self.wait_activity(MAIN)
        self.open_sky()
        self.tap(description="Nach Norden blicken")
        initial = self.dump_ui()
        original_width = int(initial.get("screen-width"))
        original_height = int(initial.get("screen-height"))
        raw_size = self.adb("shell", "wm", "size")
        (self.out / "original-display-size.txt").write_text(raw_size)
        override = re.search(r"Override size:\s*(\d+x\d+)", raw_size)
        restore_value = override.group(1) if override else "reset"
        compact_height = round(original_width * 1.2)
        if compact_height > original_height * 0.75:
            raise TestFailure("Configured emulator lacks sufficient portrait height for the compact-size check")
        self.report["compact_activity"] = {
            "method": "Android shell wm size; compact display configuration, not Samsung split-screen",
            "original_size": [original_width, original_height],
            "requested_size": [original_width, compact_height],
            "restore_argument": restore_value,
        }
        try:
            self.adb("shell", "wm", "size", f"{original_width}x{compact_height}")
            self.poll("requested compact display height", lambda: self.dump_ui().get("screen-height") == str(compact_height))
            self.wait_activity(SKY)
            observation = self.poll("star map occupies at least 60% of compact window height with reachable menu",
                                    self.compact_sky_observation)
            self.report["compact_activity"].update(observation)
            self.tap(description="Fenster und Bedienung")
            self.wait_node(description="Nach Osten blicken")
            self.capture("compact-activity-menu")
            self.tap_popup_menu_item("Nach Osten blicken", "O · Osten")
            self.expect_direction("Ost", 90)
            self.capture("compact-activity-east")
        finally:
            self.adb("shell", "wm", "size", restore_value)
            self.poll("original display size restored", lambda: self.dump_ui().get("screen-height") == str(original_height))
        self.wait_activity(SKY)
        self.expect_direction("Ost", 90)
        self.wait_node(description="Nach Osten blicken")
        self.report["compact_activity"]["direction_preserved_after_restore"] = "Ost 90°, Blickhöhe 42°"
        self.capture("normal-size-direction-preserved")
        self.ensure_follow()
        self.tap(description="Zurück")
        self.wait_activity(MAIN)
        self.save_report()

    def service_record(self):
        raw = self.adb("shell", "dumpsys", "activity", "services", PACKAGE)
        pattern = (r"(?m)^\s*\* ServiceRecord\{[^\n]*" + re.escape(PACKAGE)
                   + r"/(?:\." + SERVICE + "|" + re.escape(PACKAGE) + r"\." + SERVICE + r")\b[^\n]*")
        match = re.search(pattern, raw)
        if not match:
            return ""
        tail = raw[match.end():]
        end = re.search(r"(?m)^\s*\* ServiceRecord\{", tail)
        return match.group() + (tail[:end.start()] if end else tail)

    def foreground_service_running(self):
        record = self.service_record()
        return record if re.search(r"\bisForeground=true\b", record) else None

    def overlay_window(self, root):
        found = [window for window in root.findall("window")
                 if self.node(window, description=DRAG) is not None]
        if len(found) > 1:
            raise TestFailure(f"Duplicate live overlays: {len(found)} accessibility windows")
        return found[0] if found else None

    def window_manager_record(self, *, allow_absent=False):
        raw = self.adb("shell", "dumpsys", "window", "windows")
        pattern = r"(?m)^\s*Window #\d+ Window\{[^\n]*" + re.escape(WINDOW_TITLE) + r"[^\n]*"
        matches = list(re.finditer(pattern, raw))
        if not matches and allow_absent:
            return ""
        if len(matches) != 1:
            raise TestFailure(f"Expected one named WindowManager overlay, found {len(matches)}")
        match = matches[0]
        tail = raw[match.end():]
        end = re.search(r"(?m)^\s*Window #\d+ Window\{", tail)
        return match.group() + (tail[:end.start()] if end else tail)

    def observe_overlay(self, label=None, *, require_controls=True):
        root = self.dump_ui()
        window = self.overlay_window(root)
        if window is None and require_controls:
            return None
        width, height = int(root.get("screen-width", "0")), int(root.get("screen-height", "0"))
        if width <= 0 or height <= 0:
            raise TestFailure("Probe did not report usable display dimensions")
        wm = self.window_manager_record()
        if not re.search(r"\bty=(?:APPLICATION_OVERLAY|2038)\b|\btype=2038\b", wm):
            raise TestFailure("Named window is not TYPE_APPLICATION_OVERLAY")
        if not re.search(r"\bpackage=" + re.escape(PACKAGE) + r"\b", wm):
            raise TestFailure("Named overlay window is not owned by Sternfenster")
        if self.app_uid is None or not re.search(r"\bmOwnerUid=" + str(self.app_uid) + r"\b", wm):
            raise TestFailure("Overlay WindowManager owner UID does not match the installed package")
        for evidence in (r"\bmHasSurface=true\b", r"\bSurface:\s*shown=true\b", r"\bmDrawState=HAS_DRAWN\b",
                         r"\bisOnScreen=true\b", r"\bisVisible=true\b", r"\bmObscured=false\b"):
            if not re.search(evidence, wm):
                raise TestFailure(f"Overlay lacks required visible, drawn surface evidence: {evidence}")
        frame = re.search(r"(?:\bmFrame=|\bframe=)(\[-?\d+,-?\d+\]\[-?\d+,-?\d+\])", wm)
        if not frame:
            raise TestFailure("No independently observed WindowManager frame for the overlay")
        wm_bounds = tuple(map(int, BOUNDS.fullmatch(frame.group(1)).groups()))
        if not (0 <= wm_bounds[0] < wm_bounds[2] <= width and 0 <= wm_bounds[1] < wm_bounds[3] <= height):
            raise TestFailure(f"WindowManager placed the overlay outside the display: {wm_bounds}")
        bounds = wm_bounds
        if require_controls:
            bounds = bounds_of(window)
            if not (0 <= bounds[0] < bounds[2] <= width and 0 <= bounds[1] < bounds[3] <= height):
                raise TestFailure(f"Overlay accessibility window is outside the display: {bounds}")
            for description in (DRAG, CLOSE, RESIZE):
                control = self.node(window, description=description)
                if control is None or control.get("enabled") != "true":
                    raise TestFailure(f"Overlay control missing or disabled: {description}")
                control_bounds = bounds_of(control)
                if not (bounds[0] <= control_bounds[0] < control_bounds[2] <= bounds[2]
                        and bounds[1] <= control_bounds[1] < control_bounds[3] <= bounds[3]):
                    raise TestFailure(f"Overlay control lies outside its window: {description}")
                if description == CLOSE:
                    if control.get("clickable") != "true":
                        raise TestFailure("Observed overlay close button is not clickable")
                    self.close_geometry = {"window_bounds": bounds, "control_bounds": control_bounds,
                                           "phase": self.phase, "label": label,
                                           "enabled": True, "clickable": True}
        observed = {"phase": self.phase, "label": label, "bounds": bounds,
                    "wm_bounds": wm_bounds, "display_size": [width, height],
                    "window_title": window.get("title") if window is not None else None,
                    "window_id": window.get("id") if window is not None else None,
                    "accessibility_overlay_present": window is not None,
                    "accessibility_controls_required": require_controls,
                    "window_type_confirmed": "TYPE_APPLICATION_OVERLAY",
                    "owner_uid": self.app_uid, "surface_shown": True, "has_drawn": True,
                    "is_visible": True, "is_on_screen": True, "obscured": False,
                    "visibility_source": "WindowManager app-owned surface and screen bounds"}
        if label:
            self.report["overlay_observations"].append(observed)
            (self.out / f"{label}-window-manager.txt").write_text(wm)
            (self.out / f"{label}-service.txt").write_text(self.service_record())
            self.save_report()
        return observed

    def wait_overlay(self, label, *, require_controls=True):
        def observed():
            if not self.foreground_service_running():
                return None
            return self.observe_overlay(label, require_controls=require_controls)
        # A fresh accessibility connection can report the focused Activity
        # before its nonfocusable overlay. Keep the successful UI/WM observation
        # from this bounded poll; a redundant one-shot read can be partial again.
        return self.poll("visible, bounded application overlay with foreground service", observed)

    def drag_control(self, description, dx, dy):
        node = self.wait_node(description=description)
        left, top, right, bottom = bounds_of(node)
        root = ET.fromstring(self.last_xml)
        width, height = int(root.get("screen-width")), int(root.get("screen-height"))
        x, y = (left + right) // 2, (top + bottom) // 2
        end_x = min(width - 2, max(2, x + round(dx)))
        end_y = min(height - 2, max(2, y + round(dy)))
        self.adb("shell", "input", "swipe", str(x), str(y), str(end_x), str(end_y), "550")
        return {"description": description, "from": [x, y], "to": [end_x, end_y]}

    def measure_overlay(self, name, seconds=6):
        self.wait_seconds_with_crash_checks(2)
        self.adb("shell", "dumpsys", "gfxinfo", PACKAGE, "reset")
        marker = self.mark_window(name)
        self.wait_seconds_with_crash_checks(seconds)
        raw = self.since_marker(marker)
        (self.out / f"{name}-perf-logcat.txt").write_text(raw)
        gfx = self.adb("shell", "dumpsys", "gfxinfo", PACKAGE, "framestats")
        (self.out / f"{name}-gfxinfo.txt").write_text(gfx)
        samples = parse_overlay_samples(raw)
        if len(samples) < math.floor(seconds * 0.6):
            raise TestFailure(f"Overlay stopped reporting frames: {len(samples)} reports in {seconds}s")
        if any(sample["frames"] <= 0 or sample["fps"] <= 1.1 for sample in samples):
            raise TestFailure("Overlay did not continue rendering above the historical 1Hz timer")
        if any(not math.isfinite(sample[key]) for sample in samples
               for key in ("fps", "draw_p95_ms", "display_hz")):
            raise TestFailure("Overlay emitted non-finite performance measurements")
        # Retain the existing measurement rule exactly. Functional persistence
        # never changes the thresholds or turns a slow emulator result into 60 FPS.
        summary = summarize_samples(samples)
        summary["requested_observation_seconds"] = seconds
        summary["workload"] = "visible overlay with live clock and enabled physical-sensor following"
        count = re.search(r"Total frames rendered:\s*(\d+)", gfx)
        summary["android_gfxinfo_total_frames"] = int(count.group(1)) if count else None
        self.report["performance"][name] = summary
        self.save_report()
        print("PERFORMANCE " + name + " " + json.dumps({k: v for k, v in summary.items() if k != "samples"}), flush=True)
        return summary

    def wait_overlay_pose(self, marker, azimuth, altitude):
        self.wait_overlay(self.phase + "-pose", require_controls=False)
        # The compact Activity check has ended. Sensor samples are additionally
        # scoped to mode=overlay so Activity telemetry cannot satisfy this check.
        result = self.wait_pose(marker, azimuth, altitude, ui=False)
        result["ui"]["source"] = "visible overlay sensor telemetry"
        self.save_report()
        return result

    def main_task_id(self):
        raw = self.adb("shell", "dumpsys", "activity", "activities")
        match = re.search(r"ActivityRecord\{[^\n]*" + re.escape(PACKAGE)
                          + r"/(?:\.MainActivity|" + re.escape(PACKAGE)
                          + r"\.MainActivity)\s+t(\d+)\b", raw)
        if not match:
            raise TestFailure("No observable MainActivity task to remove")
        return int(match.group(1))

    def task_absent(self, task_id):
        for kind in ("activities", "recents"):
            raw = self.adb("shell", "dumpsys", "activity", kind)
            (self.out / f"task-removal-{kind}.txt").write_text(raw)
            if re.search(r"Task\{[^\n]*#" + str(task_id) + r"\b", raw):
                return False
            if re.search(r"ActivityRecord\{[^\n]*\bt" + str(task_id) + r"\b", raw):
                return False
        return True

    def overlay_absent(self):
        return not self.service_record() and not self.window_manager_record(allow_absent=True)

    def tap_overlay_close(self, label):
        current = self.observe_overlay(label + "-before-close", require_controls=False)
        frame = current["wm_bounds"]
        root = ET.fromstring(self.last_xml)
        window = self.overlay_window(root)
        control = self.node(window, description=CLOSE) if window is not None else None
        if control is not None and control.get("enabled") == "true" and control.get("clickable") == "true":
            bounds = bounds_of(control)
            x, y = (bounds[0] + bounds[2]) // 2, (bounds[1] + bounds[3]) // 2
            source = "current enabled accessibility close button and visible WindowManager frame"
            reference = None
        else:
            reference = self.close_geometry
            if not reference or not reference["enabled"] or not reference["clickable"]:
                raise TestFailure("No previously observed enabled close-button geometry for a physical tap")
            old = reference["window_bounds"]
            if (frame[2] - frame[0], frame[3] - frame[1]) != (old[2] - old[0], old[3] - old[1]):
                raise TestFailure("Overlay size changed; previously observed close-button geometry cannot be reused")
            cb = reference["control_bounds"]
            x = frame[0] + (cb[0] + cb[2]) // 2 - old[0]
            y = frame[1] + (cb[1] + cb[3]) // 2 - old[1]
            source = "previously observed enabled close button, unchanged size, translated to current visible WindowManager frame"
        if not (frame[0] <= x < frame[2] and frame[1] <= y < frame[3]):
            raise TestFailure("Observed close-button tap would fall outside the current overlay frame")
        self.report.setdefault("close_actions", []).append({
            "phase": self.phase, "label": label, "source": source, "point": [x, y],
            "current_wm_bounds": frame, "previous_accessibility_geometry": reference,
        })
        self.save_report()
        self.adb("shell", "input", "tap", str(x), str(y))

    def close_overlay(self, label):
        sensor_marker = self.mark_sensor_window(label + "-close")
        perf_marker = self.mark_window(label + "-close")
        self.tap_overlay_close(label)
        self.poll("explicit close removed overlay window and service", self.overlay_absent)
        self.poll("overlay sensor listener released",
                  lambda: "listening_stopped" in self.sensor_since(sensor_marker))
        self.poll("overlay render callbacks stopped",
                  lambda: "rendering_stopped" in self.since_marker(perf_marker))
        # A bounded observation after cleanup catches an unintended sticky
        # restart, fresh sensor status or continued scheduled render callbacks.
        self.wait_seconds_with_crash_checks(1)
        quiet_sensor = self.mark_sensor_window(label + "-closed-observation")
        quiet_perf = self.mark_window(label + "-closed-observation")
        deadline = time.monotonic() + 6
        while time.monotonic() < deadline:
            self.assert_no_app_crash()
            if self.service_record():
                raise TestFailure("Foreground service restarted after explicit close")
            self.wait_seconds_with_crash_checks(0.5)
        self.poll("overlay remains absent after explicit close", self.overlay_absent, timeout=10)
        sensor = self.sensor_since(quiet_sensor)
        perf = self.since_marker(quiet_perf)
        (self.out / f"{label}-closed-sensor-logcat.txt").write_text(sensor)
        (self.out / f"{label}-closed-perf-logcat.txt").write_text(perf)
        (self.out / f"{label}-closed-sensorservice.txt").write_text(self.adb("shell", "dumpsys", "sensorservice"))
        if "listening_started" in sensor or self.sensor_samples(sensor):
            raise TestFailure("Sensor listener/status loop resumed after explicit close")
        if parse_overlay_samples(perf):
            raise TestFailure("Overlay kept drawing after explicit close")
        self.capture(label + "-closed")

    def run(self):
        with self.step("emulator-install-and-system-permission-setup"):
            self.adb("wait-for-device", timeout=30)
            self.poll("boot completed", lambda: self.adb("shell", "getprop", "sys.boot_completed").strip() == "1")
            sdk = int(self.adb("shell", "getprop", "ro.build.version.sdk").strip())
            self.report["environment"] = {
                "sdk": sdk, "release": self.adb("shell", "getprop", "ro.build.version.release").strip(),
                "model": self.adb("shell", "getprop", "ro.product.model").strip(),
                "renderer": "Android emulator with SwiftShader; not a physical-device benchmark",
                "permission_setup": "SYSTEM_ALERT_WINDOW appops allow; POST_NOTIFICATIONS runtime grant",
                "sensor_input": "Android emulator physical acceleration/magnetic-field/gyroscope overrides",
                "display_condition": "interactive display; emulator power stay-on enabled for the observation",
            }
            if sdk < 33:
                raise TestFailure("This workflow requires API33+ to test notification permission and current foreground-service behavior")
            status = self.adb("emu", "sensor", "status")
            (self.out / "emulator-sensor-status.txt").write_text(status)
            for name in ("acceleration", "magnetic-field", "gyroscope"):
                if not re.search(re.escape(name) + r":\s*enabled", status):
                    raise TestFailure(f"Required emulator sensor unavailable: {name}")
            self.report["apk_sha256"] = hashlib.sha256(self.args.candidate.read_bytes()).hexdigest()
            self.adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
            self.adb("shell", "wm", "dismiss-keyguard")
            self.adb("shell", "svc", "power", "stayon", "true")
            self.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
            self.adb("shell", "settings", "put", "system", "user_rotation", "0")
            self.adb("install", "-r", str(self.args.candidate.resolve()), timeout=90)
            self.adb("shell", "pm", "clear", PACKAGE)
            package_uid = self.adb("shell", "dumpsys", "package", PACKAGE)
            match = re.search(r"(?m)^\s*(?:appId|userId)=(\d+)\s*$", package_uid)
            current_user = self.adb("shell", "am", "get-current-user").strip()
            if not match or current_user != "0":
                raise TestFailure("Cannot observe Sternfenster app ID on the disposable emulator's primary user")
            self.app_uid = int(match.group(1))
            self.report["environment"]["app_uid"] = self.app_uid
            self.adb("shell", "appops", "set", PACKAGE, "SYSTEM_ALERT_WINDOW", "allow")
            self.adb("shell", "pm", "grant", PACKAGE, "android.permission.POST_NOTIFICATIONS")
            permission = self.adb("shell", "appops", "get", PACKAGE, "SYSTEM_ALERT_WINDOW")
            (self.out / "overlay-appop.txt").write_text(permission)
            if not re.search(r"SYSTEM_ALERT_WINDOW:\s*allow\b", permission):
                raise TestFailure("Overlay app-op grant was not observed")
            self.adb("logcat", "-b", "all", "-c")
            self.check_crashes = True
            self.set_pose(0, 25, "compact-activity-initial-north")

        with self.step("compact-activity-map-space-menu-and-direction-preservation"):
            self.check_compact_activity()

        with self.step("visible-main-button-starts-foreground-overlay"):
            self.wait_activity(MAIN)
            marker = self.set_pose(0, 25, "overlay-initial-north")
            self.tap(text=OPEN)
            self.wait_overlay("overlay-started")
            self.wait_overlay_pose(marker, 0, 25)
            self.measure_overlay("initial-overlay")
            self.capture("overlay-started")
            (self.out / "sensorservice-overlay-active.txt").write_text(self.adb("shell", "dumpsys", "sensorservice"))

        with self.step("header-drag-and-real-resize-handle") as result:
            before = self.wait_overlay("before-drag")
            screen_width, screen_height = before["display_size"]
            result["drag"] = self.drag_control(DRAG, screen_width * 0.1, screen_height * 0.17)
            def moved():
                observation = self.observe_overlay()
                if observation and max(abs(observation["bounds"][i] - before["bounds"][i]) for i in (0, 1)) >= 20:
                    return observation
                return None
            moved_bounds = self.poll("header drag changes the overlay position", moved)
            left, top, right, bottom = moved_bounds["bounds"]
            result["resize"] = self.drag_control(RESIZE, -(right - left) * 0.19, -(bottom - top) * 0.19)
            def resized():
                observation = self.observe_overlay()
                if not observation:
                    return None
                b = observation["bounds"]
                return observation if abs((b[2] - b[0]) - (right - left)) >= 15 and abs((b[3] - b[1]) - (bottom - top)) >= 15 else None
            self.poll("resize handle changes both observed window dimensions", resized)
            self.wait_overlay("overlay-dragged-and-resized")
            self.capture("overlay-dragged-and-resized")

        with self.step("drag-constrains-window-to-display") as result:
            observation = self.wait_overlay("before-boundary-drag")
            width, height = observation["display_size"]
            result["drag"] = self.drag_control(DRAG, width, height)
            bounded = self.wait_overlay("overlay-at-display-boundary")
            # The pointer reaches the bottom-right edge, while the whole window
            # and its close/resize controls remain reachable on the display.
            if bounded["bounds"] == observation["bounds"]:
                raise TestFailure("Boundary drag did not move the overlay at all")
            self.capture("overlay-at-display-boundary")
            self.persisted_bounds = bounded["bounds"]

        with self.step("home-keeps-overlay-sensors-and-renderer-alive"):
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("launcher resumed", lambda: (component := self.resumed_component()) and not component.startswith(PACKAGE + "/"))
            marker = self.set_pose(90, 55, "overlay-home-east")
            self.wait_overlay_pose(marker, 90, 55)
            self.measure_overlay("home-overlay")
            self.capture("overlay-over-home")

        with self.step("switching-to-settings-keeps-overlay-live"):
            self.adb("shell", "am", "start", "-W", "-a", "android.settings.SETTINGS")
            self.poll("Settings resumed behind the overlay", lambda: self.resumed_component().startswith("com.android.settings/"))
            marker = self.set_pose(270, 35, "overlay-settings-west")
            self.wait_overlay_pose(marker, 270, 35)
            self.measure_overlay("settings-overlay")
            self.capture("overlay-over-settings")

        with self.step("removing-main-task-keeps-foreground-overlay-live") as result:
            task_id = self.main_task_id()
            before_pid = self.adb("shell", "pidof", PACKAGE).strip()
            if not before_pid:
                raise TestFailure("No app process before task removal")
            removal = self.adb("shell", "am", "stack", "remove", str(task_id))
            (self.out / "remove-main-task-command.txt").write_text(removal)
            if "Error:" in removal or "Exception" in removal:
                raise TestFailure(f"Android rejected task removal: {removal}")
            self.poll("observed main task absent from activities and recents", lambda: self.task_absent(task_id))
            marker = self.set_pose(45, 15, "overlay-main-task-removed")
            self.wait_overlay_pose(marker, 45, 15)
            self.measure_overlay("task-removed-overlay")
            after_pid = self.adb("shell", "pidof", PACKAGE).strip()
            if after_pid != before_pid:
                raise TestFailure("Main-task removal unexpectedly replaced the running foreground-service process")
            observation = self.wait_overlay("overlay-after-main-task-removal", require_controls=False)
            self.persisted_bounds = observation["bounds"]
            result.update(task_id=task_id, before_pid=before_pid, after_pid=after_pid,
                          method="adb shell am stack remove observedTaskId; ActivityTaskManager.removeTask; not force-stop")
            self.report["task_removals"].append({key: result[key] for key in ("task_id", "before_pid", "after_pid", "method")})
            self.capture("overlay-after-main-task-removal")

        with self.step("explicit-close-releases-service-sensors-and-frames"):
            self.close_overlay("first-explicit-close")

        with self.step("reopen-preserves-position-and-size-without-auto-reopening") as result:
            self.launch()
            self.wait_activity(MAIN)
            self.wait_node(text=OPEN)
            if not self.overlay_absent():
                raise TestFailure("Launching MainActivity reopened an explicitly closed overlay")
            self.tap(text=OPEN)
            observation = self.wait_overlay("overlay-reopened")
            result.update(before=self.persisted_bounds, after=observation["bounds"])
            if any(abs(a - b) > 8 for a, b in zip(self.persisted_bounds, observation["bounds"])):
                raise TestFailure(f"Overlay position/size not restored: {self.persisted_bounds} -> {observation['bounds']}")
            marker = self.set_pose(180, 40, "overlay-reopened-south")
            self.wait_overlay_pose(marker, 180, 40)
            self.capture("overlay-reopened-same-position-size")
            self.close_overlay("final-explicit-close")

        with self.step("no-sternfenster-crash-or-anr"):
            self.assert_no_app_crash()
            raw = self.adb("logcat", "-b", "all", "-d", "-v", "threadtime")
            (self.out / "candidate-logcat.txt").write_text(raw)
            (self.out / "sensor-telemetry.txt").write_text(self.sensor_log())
            if f"ANR in {PACKAGE}" in raw:
                raise TestFailure("Sternfenster ANR recorded")
        self.report.update(status="overlay_integration_passed", functional_status="PASSED")
        self.save_report()

    def diagnostics(self):
        super().diagnostics()
        for name, command in (
            ("final-window-manager.txt", ("shell", "dumpsys", "window", "windows")),
            ("final-services.txt", ("shell", "dumpsys", "activity", "services", PACKAGE)),
            ("final-sensorservice.txt", ("shell", "dumpsys", "sensorservice")),
        ):
            try:
                (self.out / name).write_text(self.adb(*command, timeout=20))
            except TestFailure as exc:
                print(f"Diagnostic unavailable: {name}: {exc}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--serial")
    args = parser.parse_args()
    if not args.candidate.is_file():
        parser.error(f"APK not found: {args.candidate}")
    test = OverlaySmoke(args)
    try:
        test.run()
    except Exception as exc:
        test.report.update(status="overlay_integration_failed", functional_status="FAILED", error=str(exc))
        (test.out / "failure.txt").write_text(traceback.format_exc())
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        test.diagnostics()
        test.save_report()
    print("OVERLAY INTEGRATION PASSED; inspect separate performance observations. "
          "60 presented FPS, Samsung window management and process-death survival are not established.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
