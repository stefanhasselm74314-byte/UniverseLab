#!/usr/bin/env python3
"""Exercise the real user-started pacing measurement and its saved Android UI.

Use only a disposable API35 emulator: setup clears Sternfenster data and grants
overlay/notification access. The separate accessibility probe observes actual
controls; there are no test entry points in the release app. Functional success
means that real draw callbacks produce a consistent saved report, the overlay
keeps running after completion, and interruption preserves the prior result.
It does not establish 60 presented FPS or the performance of a physical Samsung.
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

from runtime_overlay import OverlaySmoke, parse_overlay_samples
from runtime_smoke import MAIN, PACKAGE, SKY, TestFailure


REPORT = f"{PACKAGE}/.PerformanceActivity"
OPEN_REPORT = "Bildrate prüfen"
MEASURE_OVERLAY = "Im freien Fenster messen (20 s)"
MEASURE_FULLSCREEN = "In Vollansicht messen (20 s)"
RESULT_DESCRIPTION = "Ergebnis der Bildratenmessung"
STATUS_DESCRIPTION = "Status der Bildratenmessung"
NO_RESULT = "Noch keine abgeschlossene Messung."


def validate_completed(data):
    """Reject inconsistent counters without converting average FPS into a gate."""
    integer_fields = (
        "frames", "duration_ns", "interval_count", "interval_min_ns",
        "interval_max_ns",
        "intervals_above_20_ms", "invalid_events", "warmup_ms",
        "requested_duration_ms", "window_modes", "width_min_px",
        "width_max_px", "height_min_px", "height_max_px",
    )
    for key in integer_fields:
        if type(data.get(key)) is not int or data[key] < 0:
            raise TestFailure(f"Measurement lacks a nonnegative integer {key}: {data.get(key)!r}")
    for key in ("render_fps", "interval_fps", "interval_mean_ns", "display_hz_min", "display_hz_max"):
        value = data.get(key)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise TestFailure(f"Measurement lacks a finite positive {key}: {value!r}")
    for key in ("interval_p95_ns", "draw_p95_ns"):
        value = data.get(key)
        if (type(value) not in (int, float) or not math.isfinite(value)
                or value < 0 or value != int(value)):
            raise TestFailure(f"Measurement lacks a finite integral nanosecond percentile {key}: {value!r}")
    if data["requested_duration_ms"] != 20_000 or data["warmup_ms"] != 2_000:
        raise TestFailure("The user-facing two-second warmup / twenty-second measurement was not used")
    if data["duration_ns"] < 20_000_000_000:
        raise TestFailure("The completed collection did not cover twenty monotonic seconds")
    if data["frames"] < 2 or data["render_fps"] <= 1.1:
        raise TestFailure("No continuing draw workload above the historical one-Hz timer was measured")
    if data["interval_count"] != data["frames"] - 1:
        raise TestFailure("N draw timestamps must yield exactly N−1 successive intervals")
    expected_fps = data["frames"] * 1e9 / data["duration_ns"]
    if not math.isclose(data["render_fps"], expected_fps, rel_tol=1e-9, abs_tol=1e-9):
        raise TestFailure("Saved render rate does not equal draw count / measured elapsed time")
    if not math.isclose(data["interval_fps"], 1e9 / data["interval_mean_ns"], rel_tol=1e-9, abs_tol=1e-9):
        raise TestFailure("Saved interval rate does not equal reciprocal mean draw-start spacing")
    minimum, maximum = data["interval_min_ns"], data["interval_max_ns"]
    if not (0 < minimum <= data["interval_p95_ns"] <= maximum):
        raise TestFailure("Draw-interval minimum/95th-percentile/maximum are inconsistent")
    if not minimum <= data["interval_mean_ns"] <= maximum:
        raise TestFailure("Mean draw interval falls outside the observed interval range")
    if data["interval_count"] * data["interval_mean_ns"] > data["duration_ns"] + 1:
        raise TestFailure("Successive draw intervals span more than the measurement duration")
    over = data["intervals_above_20_ms"]
    if not 0 <= over <= data["interval_count"]:
        raise TestFailure("Above-threshold interval count exceeds the observed intervals")
    if maximum <= 20_000_000 and over != 0:
        raise TestFailure("Above-threshold intervals reported despite maximum <=20ms")
    if minimum > 20_000_000 and over != data["interval_count"]:
        raise TestFailure("Not all intervals above20ms counted despite minimum >20ms")
    if not (0 < data["draw_p95_ns"] <= data["duration_ns"]):
        raise TestFailure("Draw-call elapsed duration is not plausible")
    if data["display_hz_min"] > data["display_hz_max"]:
        raise TestFailure("Display refresh range is reversed")
    for axis in ("width", "height"):
        if not 0 < data[axis + "_min_px"] <= data[axis + "_max_px"]:
            raise TestFailure(f"Invalid measured {axis} range")
    if data.get("complete") is not True or data.get("cancelled") is not False:
        raise TestFailure("The completed user measurement is marked partial or cancelled")
    if data.get("samples_overflowed") is not False or data["invalid_events"] != 0:
        raise TestFailure("The runtime measurement contains overflow or invalid timing samples")
    if data["window_modes"] != 4 or data.get("hardware_canvas_seen") is not True:
        raise TestFailure("Measurement did not observe the actual accelerated overlay canvas")
    if data.get("phone_follow_seen") is not True:
        raise TestFailure("Measurement did not include the requested live sensor-follow workload")
    if data.get("minimum_60_presented_fps") != "NOT_ESTABLISHED_BY_THIS_MEASUREMENT":
        raise TestFailure("Report must distinguish draw callbacks from presented-frame guarantees")
    if data.get("measurement") != "onDraw callbacks; not compositor-presented frames":
        raise TestFailure("Measurement semantics are missing or changed")


class PacingSmoke(OverlaySmoke):
    def __init__(self, args):
        super().__init__(args)
        self.report.update(
            test="Sternfenster user-started device pacing report",
            completed_measurements=[],
            performance_status="DRAW_CALLBACK_MEASUREMENT_ONLY_NOT_A_PRESENTED_FPS_TEST",
            user_device_test="NOT_PERFORMED",
            minimum_60_fps_guarantee="NOT_ESTABLISHED",
        )

    def measurement_log(self):
        return self.adb("logcat", "-d", "-v", "epoch", "-s",
                        "SternfensterMeasure:I", "SternfensterPacingTest:I", "*:S")

    def mark_measurement(self, label):
        marker = label + "-" + str(time.monotonic_ns())
        self.adb("shell", "log", "-t", "SternfensterPacingTest", marker)
        return marker

    def measurement_since(self, marker):
        raw = self.measurement_log()
        if marker not in raw:
            raise TestFailure("Measurement log observation marker is missing")
        return raw.rsplit(marker, 1)[1]

    @staticmethod
    def completed_events(raw):
        results = []
        for line in raw.splitlines():
            match = re.search(r"SternfensterMeasure:\s*completed (\{.*\})\s*$", line)
            if match:
                try:
                    value = json.loads(match.group(1))
                except json.JSONDecodeError as exc:
                    raise TestFailure(f"Completed measurement log is not intact JSON: {exc}") from exc
                if not isinstance(value, dict):
                    raise TestFailure("Completed measurement is not a JSON object")
                results.append(value)
        return results

    def report_text(self):
        return self.wait_node(description=RESULT_DESCRIPTION).get("text", "")

    def open_report(self):
        self.launch()
        component = self.poll("a resumed Sternfenster Activity",
                              lambda: c if (c := self.resumed_component()).startswith(PACKAGE + "/") else None)
        if component in (SKY, SKY.replace("/.", f"/{PACKAGE}.")):
            # A launcher return can restore the interrupted native sky task.
            self.adb("shell", "input", "keyevent", "KEYCODE_BACK")
            component = self.poll("report or main after leaving the observed sky Activity",
                                  lambda: c if (c := self.resumed_component()) not in
                                  (SKY, SKY.replace("/.", f"/{PACKAGE}.")) else None)
        if component in (MAIN, MAIN.replace("/.", f"/{PACKAGE}.")):
            self.tap(text=OPEN_REPORT)
        self.wait_activity(REPORT)
        self.wait_node(description=RESULT_DESCRIPTION)

    def setup(self):
        self.adb("wait-for-device", timeout=30)
        self.poll("boot completed", lambda: self.adb("shell", "getprop", "sys.boot_completed").strip() == "1")
        sdk = int(self.adb("shell", "getprop", "ro.build.version.sdk").strip())
        if sdk < 33:
            raise TestFailure("This focused workflow expects API33+ foreground/notification behavior")
        self.report["environment"] = {
            "sdk": sdk,
            "release": self.adb("shell", "getprop", "ro.build.version.release").strip(),
            "model": self.adb("shell", "getprop", "ro.product.model").strip(),
            "renderer": "API35 emulator with SwiftShader; not a physical Samsung benchmark",
            "permission_setup": "SYSTEM_ALERT_WINDOW appops allow; POST_NOTIFICATIONS runtime grant",
            "observation": "Independent accessibility probe, WindowManager surface, logcat and visible saved report",
        }
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
        if not match or self.adb("shell", "am", "get-current-user").strip() != "0":
            raise TestFailure("Cannot observe primary-user app ownership on the disposable emulator")
        self.app_uid = int(match.group(1))
        self.report["environment"]["app_uid"] = self.app_uid
        self.adb("shell", "appops", "set", PACKAGE, "SYSTEM_ALERT_WINDOW", "allow")
        self.adb("shell", "pm", "grant", PACKAGE, "android.permission.POST_NOTIFICATIONS")
        permission = self.adb("shell", "appops", "get", PACKAGE, "SYSTEM_ALERT_WINDOW")
        if not re.search(r"SYSTEM_ALERT_WINDOW:\s*allow\b", permission):
            raise TestFailure("Overlay app-op grant was not observed")
        (self.out / "overlay-appop.txt").write_text(permission)
        sensor_status = self.adb("emu", "sensor", "status")
        (self.out / "emulator-sensor-status.txt").write_text(sensor_status)
        for name in ("acceleration", "magnetic-field", "gyroscope"):
            if not re.search(re.escape(name) + r":\s*enabled", sensor_status):
                raise TestFailure(f"Required emulator sensor is missing: {name}")
        self.adb("logcat", "-b", "all", "-c")
        self.check_crashes = True
        self.set_pose(0, 25, "pacing-initial-north")

    def run(self):
        with self.step("install-and-observed-system-permissions"):
            self.setup()

        with self.step("visible-main-navigation-to-device-report"):
            self.launch()
            self.wait_activity(MAIN)
            self.tap(text=OPEN_REPORT)
            self.wait_activity(REPORT)
            if self.report_text() != NO_RESULT:
                raise TestFailure("A freshly cleared app unexpectedly has a completed device report")
            self.wait_node(text=MEASURE_OVERLAY)
            self.wait_node(text=MEASURE_FULLSCREEN)
            self.capture("measurement-screen-before-first-run")

        with self.step("user-started-overlay-measurement-completes-from-real-draws") as result:
            marker = self.mark_measurement("overlay-measurement")
            self.tap(text=MEASURE_OVERLAY)
            self.wait_overlay("measurement-overlay-started")
            self.poll("measurement began after warmup",
                      lambda: re.search(r"SternfensterMeasure:\s*started mode=.+ duration_ms=20000", self.measurement_since(marker)), timeout=20)
            self.capture("measurement-overlay-collecting")
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("launcher resumed behind measurement overlay",
                      lambda: (c := self.resumed_component()) and not c.startswith(PACKAGE + "/"))
            pose_marker = self.set_pose(90, 55, "pacing-home-east")
            self.wait_overlay_pose(pose_marker, 90, 55)
            completed = self.poll("completed twenty-second measurement JSON",
                                  lambda: self.completed_events(self.measurement_since(marker)), timeout=45)
            if len(completed) != 1:
                raise TestFailure(f"One user request produced {len(completed)} completed measurements")
            measurement = completed[0]
            validate_completed(measurement)
            event_log = self.measurement_since(marker)
            warmup = event_log.find("SternfensterMeasure: warmup mode=")
            started = event_log.find("SternfensterMeasure: started mode=")
            finished = event_log.find("SternfensterMeasure: completed ")
            if not 0 <= warmup < started < finished:
                raise TestFailure("Measurement did not follow warmup → collection → completed order")
            self.report["completed_measurements"] = completed
            result.update(mode=measurement["mode"], frames=measurement["frames"],
                          duration_ns=measurement["duration_ns"], render_fps=measurement["render_fps"],
                          interval_count=measurement["interval_count"], interval_p95_ns=measurement["interval_p95_ns"],
                          minimum_60_presented_fps="NOT_ESTABLISHED_BY_THIS_MEASUREMENT")
            (self.out / "completed-overlay-measurement.json").write_text(json.dumps(measurement, ensure_ascii=False, indent=2) + "\n")
            (self.out / "measurement-logcat.txt").write_text(self.measurement_since(marker))
            (self.out / "measurement-gfxinfo.txt").write_text(self.adb("shell", "dumpsys", "gfxinfo", PACKAGE, "framestats"))

        with self.step("measurement-completion-keeps-live-overlay-running"):
            self.wait_overlay("overlay-after-measurement-completed", require_controls=False)
            marker = self.mark_window("overlay-after-measurement")
            self.wait_seconds_with_crash_checks(3)
            raw = self.since_marker(marker)
            (self.out / "overlay-after-measurement-perf-logcat.txt").write_text(raw)
            if not parse_overlay_samples(raw):
                raise TestFailure("Measurement completion stopped the live renderer")
            self.wait_overlay("overlay-still-running-after-measurement", require_controls=False)
            self.capture("overlay-after-measurement-completed")
            self.close_overlay("measurement-explicit-close")

        with self.step("saved-user-report-matches-completed-measurement"):
            self.open_report()
            saved = self.report_text()
            if f"Zeichenaufrufe: {measurement['frames']}" not in saved:
                raise TestFailure("Saved visible report disagrees with the recorded actual frame count")
            if f"Bildabstände: {measurement['interval_count']}" not in saved:
                raise TestFailure("Saved visible report disagrees with N−1 draw intervals")
            rate = re.search(r"Ø Render-FPS:\s*([\d,]+)", saved)
            if not rate or abs(float(rate.group(1).replace(",", ".")) - measurement["render_fps"]) > .006:
                raise TestFailure("Saved report render rate disagrees with completed measurement JSON")
            if "Tatsächlich am Bildschirm präsentierte Bilder werden hier nicht gezählt." not in saved:
                raise TestFailure("Saved report must explicitly separate drawing from presentation")
            if "Messung abgeschlossen" not in saved:
                raise TestFailure("Completed clean report lacks its completion status")
            self.report["saved_report_text"] = saved
            (self.out / "saved-user-report.txt").write_text(saved)
            self.capture("saved-device-measurement-report")

        with self.step("interrupted-fullscreen-measurement-preserves-prior-result") as result:
            marker = self.mark_measurement("fullscreen-interruption")
            self.tap(text=MEASURE_FULLSCREEN)
            self.wait_activity(SKY)
            self.poll("fullscreen collection starts after warmup",
                      lambda: re.search(r"SternfensterMeasure:\s*started mode=.+ duration_ms=20000", self.measurement_since(marker)), timeout=20)
            started_at = time.monotonic()
            self.capture("fullscreen-measurement-before-interruption")
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("fullscreen interruption cancels collection",
                      lambda: "SternfensterMeasure: cancelled mode=" in self.measurement_since(marker))
            # Observe beyond the scheduled finish deadline: a stale timer must
            # neither complete a hidden measurement nor replace the saved result.
            remaining = started_at + 22 - time.monotonic()
            if remaining > 0:
                self.wait_seconds_with_crash_checks(remaining)
            raw = self.measurement_since(marker)
            (self.out / "interrupted-measurement-logcat.txt").write_text(raw)
            if self.completed_events(raw):
                raise TestFailure("The cancelled hidden measurement completed after its deadline")
            self.open_report()
            self.poll("interruption status visible", lambda: "Messung abgebrochen:" in
                      self.wait_node(description=STATUS_DESCRIPTION).get("text", ""))
            if self.report_text() != saved:
                raise TestFailure("Interrupted measurement replaced or changed the previous completed report")
            result.update(previous_completed_result_preserved=True,
                          observation="Beyond the original twenty-second completion deadline")
            self.capture("interrupted-measurement-keeps-previous-report")

        with self.step("no-sternfenster-crash-or-anr"):
            self.assert_no_app_crash()
            raw = self.adb("logcat", "-b", "all", "-d", "-v", "threadtime")
            (self.out / "candidate-logcat.txt").write_text(raw)
            if f"ANR in {PACKAGE}" in raw:
                raise TestFailure("Sternfenster ANR recorded")
        self.report.update(status="frame_pacing_measurement_integration_passed", functional_status="PASSED")
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
    test = PacingSmoke(args)
    try:
        test.run()
    except Exception as exc:
        test.report.update(status="frame_pacing_measurement_integration_failed", functional_status="FAILED", error=str(exc))
        (test.out / "failure.txt").write_text(traceback.format_exc())
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        test.diagnostics()
        test.save_report()
    print("PACING REPORT INTEGRATION PASSED; actual draw measurements are separate from presented FPS and phone performance.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
