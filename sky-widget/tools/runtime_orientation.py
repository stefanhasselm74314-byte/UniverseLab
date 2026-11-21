#!/usr/bin/env python3
"""Test real Android sensor delivery, camera-direction following and lifecycle.

Only a disposable Android emulator is supported: this clears Sternfenster data
and overrides its emulated acceleration/magnetic/gyroscope sensors. No test-only
sensor injection path exists in the release app. UI assertions use the separate
no-idle accessibility probe, while PiP assertions use diagnostic sensor telemetry.

The input vectors represent a rear-camera sightline (device -Z) with a specified
magnetic azimuth and elevation. Absolute heading tolerances allow the application's
geographic declination correction and emulator sensor-fusion convergence. This is
an integration check, not a compass-accuracy or physical-device FPS benchmark.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import time
import traceback

from runtime_live60 import Live60Smoke
from runtime_smoke import MAIN, PACKAGE, SKY, TestFailure


FOLLOW = "Blickrichtung des Handys folgen"
ANGLES = re.compile(r"·\s+\S+\s+(-?[\d.]+)°\s+·\s+Blickhöhe\s+(-?[\d.]+)°")
FIELDS = re.compile(r"\b(following|listening|fresh|az|alt|mode)=([^\s]+)")


def angular_distance(a, b):
    return abs((a - b + 180) % 360 - 180)


def pose_vectors(azimuth, altitude):
    """R^T times world gravity and a 50-north/-20-up microtesla field.

    Device X points screen-right, Y points screen-top and camera looks along -Z.
    Upright camera-right = (cos A, -sin A, 0), camera-up =
    (-sin h sin A, -sin h cos A, cos h), device Z =
    (-cos h sin A, -cos h cos A, -sin h), in East/North/Up coordinates.
    """
    a, h = math.radians(azimuth), math.radians(altitude)
    gravity = (0.0, 9.80665 * math.cos(h), -9.80665 * math.sin(h))
    magnetic = (-50 * math.sin(a),
                -50 * math.sin(h) * math.cos(a) - 20 * math.cos(h),
                -50 * math.cos(h) * math.cos(a) + 20 * math.sin(h))
    return gravity, magnetic


class OrientationSmoke(Live60Smoke):
    def __init__(self, args):
        super().__init__(args)
        self.report.update(test="Sternfenster device orientation integration",
                           sensor_inputs=[], observed_poses=[],
                           physical_compass_accuracy="NOT_MEASURED",
                           performance_status="NOT_A_PERFORMANCE_BENCHMARK")
        self.report["sources"] = [
            "https://developer.android.com/studio/run/emulator-console",
            "https://developer.android.com/reference/android/hardware/SensorManager#getRotationMatrix(float[],%20float[],%20float[],%20float[])",
            "https://android.googlesource.com/platform/external/qemu/+/emu-master-dev/android/android-emu/android/console.cpp",
        ]
        self.previous_pose = None

    def sensor_log(self):
        return self.adb("logcat", "-d", "-v", "epoch", "-s",
                        "SternfensterSensor:I", "SternfensterSensorTestWindow:I", "*:S")

    def mark_sensor_window(self, label):
        marker = label + "-" + str(time.monotonic_ns())
        self.adb("shell", "log", "-t", "SternfensterSensorTestWindow", marker)
        return marker

    def sensor_since(self, marker):
        raw = self.sensor_log()
        if marker not in raw:
            raise TestFailure("Sensor observation marker missing from logcat")
        return raw.rsplit(marker, 1)[1]

    @staticmethod
    def sensor_samples(raw):
        values = []
        for line in raw.splitlines():
            if "SternfensterSensor:" not in line:
                continue
            fields = dict(FIELDS.findall(line))
            if all(key in fields for key in ("following", "listening", "fresh", "az", "alt")):
                fields.update(az=float(fields["az"]), alt=float(fields["alt"]), log_line=line)
                values.append(fields)
        return values

    def set_sensor(self, name, values):
        encoded = ":".join(f"{value:.7f}" for value in values)
        result = self.adb("emu", "sensor", "set", name, encoded)
        if "KO:" in result or not re.search(r"(?m)^OK\s*$", result):
            raise TestFailure(f"Emulator rejected {name} override: {result}")

    def set_pose(self, azimuth, altitude, label):
        marker = self.mark_sensor_window(label)
        acceleration, magnetic = pose_vectors(azimuth, altitude)
        self.set_sensor("gyroscope", (0, 0, 0))
        self.set_sensor("acceleration", acceleration)
        self.set_sensor("magnetic-field", magnetic)
        observed = {}
        for name, expected in (("acceleration", acceleration), ("magnetic-field", magnetic)):
            raw = self.adb("emu", "sensor", "get", name)
            match = re.search(re.escape(name) + r"\s*=\s*([-+\deE.:]+)", raw)
            if not match:
                raise TestFailure(f"Cannot verify injected {name}: {raw}")
            actual = tuple(float(value) for value in match.group(1).split(":"))
            if len(actual) != 3 or any(abs(a - b) > 0.002 for a, b in zip(actual, expected)):
                raise TestFailure(f"{name} readback differs from injected vector")
            observed[name] = actual
        self.report["sensor_inputs"].append({
            "label": label, "magnetic_camera_azimuth": azimuth,
            "camera_altitude": altitude, "readback": observed,
            "method": "adb emulator raw sensor overrides; gyroscope held at zero while stationary",
        })
        self.previous_pose = (azimuth, altitude)
        self.save_report()
        return marker

    def ui_pose(self):
        root = self.dump_ui()
        for node in root.iter("node"):
            if node.get("package") != PACKAGE:
                continue
            value = node.get("text", "")
            match = ANGLES.search(value)
            if match:
                return {"az": float(match.group(1)), "alt": float(match.group(2)), "text": value}
        return None

    def wait_pose(self, marker, azimuth, altitude, *, ui=True):
        def reached():
            samples = self.sensor_samples(self.sensor_since(marker))
            valid = [s for s in samples if s["following"] == "true"
                     and s["listening"] == "true" and s["fresh"] == "true"
                     and angular_distance(s["az"], azimuth) <= 20
                     and abs(s["alt"] - altitude) <= 7]
            # Two independent status windows establish settled sensor delivery.
            if len(valid) < 2 or valid[-1] != samples[-1]:
                return None
            if ui:
                pose = self.ui_pose()
                if not pose or angular_distance(pose["az"], azimuth) > 20 or abs(pose["alt"] - altitude) > 7:
                    return None
            else:
                pose = {"az": valid[-1]["az"], "alt": valid[-1]["alt"], "source": "visible PiP sensor telemetry"}
            return {"ui": pose, "telemetry": valid[-1]}
        result = self.poll(f"sensor-follow pose near az={azimuth}, alt={altitude}", reached, timeout=65)
        self.report["observed_poses"].append({"phase": self.phase, "expected_magnetic_azimuth": azimuth,
                                              "expected_altitude": altitude, "observed": result})
        self.save_report()
        return result

    def ensure_follow(self):
        node = self.wait_node(description=FOLLOW)
        if node.get("text", "").strip() == "Handy folgen: aus":
            self.tap(description=FOLLOW)
        self.wait_node(text="Handy folgen: an")

    def run(self):
        with self.step("device-and-real-sensor-overrides"):
            self.adb("wait-for-device", timeout=30)
            self.poll("boot completed", lambda: self.adb("shell", "getprop", "sys.boot_completed").strip() == "1")
            self.report["environment"] = {
                "sdk": int(self.adb("shell", "getprop", "ro.build.version.sdk").strip()),
                "release": self.adb("shell", "getprop", "ro.build.version.release").strip(),
                "model": self.adb("shell", "getprop", "ro.product.model").strip(),
                "sensor_input": "Android emulator raw acceleration/magnetic-field/gyroscope overrides",
            }
            status = self.adb("emu", "sensor", "status")
            (self.out / "emulator-sensor-status.txt").write_text(status)
            for name in ("acceleration", "magnetic-field", "gyroscope"):
                if not re.search(re.escape(name) + r":\s*enabled", status):
                    raise TestFailure(f"Required emulator sensor {name} is unavailable")
            self.report["apk_sha256"] = hashlib.sha256(self.args.candidate.read_bytes()).hexdigest()
            self.adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
            self.adb("shell", "wm", "dismiss-keyguard")
            self.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
            self.adb("shell", "settings", "put", "system", "user_rotation", "0")
            self.adb("install", "-r", str(self.args.candidate.resolve()), timeout=90)
            self.adb("shell", "pm", "clear", PACKAGE)
            self.adb("logcat", "-b", "all", "-c")
            self.check_crashes = True
            marker = self.set_pose(0, 25, "initial-north")

        with self.step("default-follow-and-north-up-pose"):
            self.launch()
            self.wait_activity(MAIN)
            self.open_sky()
            self.wait_node(text="Handy folgen: an")
            self.wait_pose(marker, 0, 25)
            self.capture("sensor-north-25")
            (self.out / "sensorservice-active.txt").write_text(self.adb("shell", "dumpsys", "sensorservice"))

        with self.step("changing-phone-direction-and-elevation"):
            marker = self.set_pose(90, 55, "turn-east-tilt-up")
            self.wait_pose(marker, 90, 55)
            self.capture("sensor-east-55")

        with self.step("zoom-preserves-follow-mode"):
            marker = self.mark_sensor_window("zoom")
            self.tap(description="Hineinzoomen")
            self.wait_node(text="Handy folgen: an")
            self.wait_pose(marker, 90, 55)
            self.tap(description="Herauszoomen")
            self.wait_node(text="Handy folgen: an")

        with self.step("manual-direction-disables-follow"):
            self.tap(description="Nach Osten blicken")
            self.wait_node(text="Handy folgen: aus")
            self.expect_direction("Ost", 90)
            marker = self.set_pose(270, 35, "manual-view-new-phone-pose")
            def remained_manual():
                samples = self.sensor_samples(self.sensor_since(marker))
                if len(samples) < 3:
                    return False
                return all(s["following"] == "false" and s["listening"] == "false"
                           and angular_distance(s["az"], 90) < 0.1 and abs(s["alt"] - 42) < 0.1
                           for s in samples)
            self.poll("manual view ignores changed sensor pose for three status windows", remained_manual)
            self.expect_direction("Ost", 90)
            self.capture("manual-east-remains-fixed")

        with self.step("reenable-follow-and-display-rotation"):
            marker = self.mark_sensor_window("reenable-follow")
            self.ensure_follow()
            self.wait_pose(marker, 270, 35)
            marker = self.mark_sensor_window("landscape")
            self.rotate(1)
            self.wait_pose(marker, 270, 35)
            self.capture("sensor-landscape")
            self.rotate(0)
            self.wait_node(text="Handy folgen: an")

        with self.step("pan-disables-follow-and-reset-is-manual"):
            self.tap(description="Automatischen Rundblick umschalten")
            self.wait_node(text="Handy folgen: aus")
            self.wait_node(text="Rundblick: an")
            self.tap(description="Blick nach Süden zurücksetzen")
            self.wait_node(text="Handy folgen: aus")
            self.expect_direction("Süd", 180)
            self.ensure_follow()

        with self.step("hidden-stops-sensors-and-resume-restarts"):
            pid = self.adb("shell", "pidof", PACKAGE).strip()
            marker = self.mark_sensor_window("home-stop")
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("SkyActivity stopped outside PiP", lambda: "state=STOPPED" in self.sky_record())
            self.poll("sensor listener released", lambda: "listening_stopped" in self.sensor_since(marker))
            (self.out / "sensorservice-stopped.txt").write_text(self.adb("shell", "dumpsys", "sensorservice"))
            marker = self.set_pose(180, 60, "phone-moved-while-hidden")
            self.launch()
            self.poll("app foreground", lambda: self.resumed_component().startswith(PACKAGE + "/"))
            if self.resumed_component() in (MAIN, MAIN.replace('/.', '/' + PACKAGE + '.')):
                self.open_sky()
            self.wait_activity(SKY)
            self.wait_node(text="Handy folgen: an")
            self.wait_pose(marker, 180, 60)
            if self.adb("shell", "pidof", PACKAGE).strip() != pid:
                raise TestFailure("Home/resume unexpectedly replaced the process")
            self.capture("sensor-follow-resumed")

        with self.step("sensor-follow-continues-in-pip-on-home"):
            self.tap(description="Schwebendes Live-Fenster öffnen")
            self.poll("PiP pinned", self.in_pip, timeout=45)
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            marker = self.set_pose(45, 15, "pip-phone-moved")
            self.wait_pose(marker, 45, 15, ui=False)
            self.poll("PiP remains pinned", self.in_pip)
            self.capture("sensor-follow-pip")

        with self.step("no-app-crash-or-anr"):
            self.assert_no_app_crash()
            raw = self.adb("logcat", "-b", "all", "-d", "-v", "threadtime")
            (self.out / "candidate-logcat.txt").write_text(raw)
            (self.out / "sensor-telemetry.txt").write_text(self.sensor_log())
            if f"ANR in {PACKAGE}" in raw:
                raise TestFailure("Sternfenster ANR recorded")
        self.report["status"] = "sensor_follow_integration_passed"
        self.save_report()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--serial")
    args = parser.parse_args()
    if not args.candidate.is_file():
        parser.error(f"APK not found: {args.candidate}")
    test = OrientationSmoke(args)
    try:
        test.run()
    except Exception as exc:
        test.report.update(status="sensor_follow_integration_failed", error=str(exc))
        (test.out / "failure.txt").write_text(traceback.format_exc())
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        test.diagnostics()
        test.save_report()
    print("SENSOR-FOLLOW INTEGRATION PASSED; physical compass accuracy and device FPS remain unmeasured.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
