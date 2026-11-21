#!/usr/bin/env python3
"""Exercise real Android rendering and PiP; report performance separately.

Exit 0 confirms the functional checks below, not a universal 60-FPS guarantee.
Performance is measured from actual onDraw counters emitted by SternfensterPerf,
with independent Android gfxinfo evidence. Display Hz is never reported as FPS.
The nominal-60 observation permits 59 FPS for measurement-window/clock rounding;
it does not establish a strict minimum of 60 presented frames/second on a phone.

Use a disposable emulator: installation clears this test app's data once.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import statistics
import sys
import time
import traceback

from runtime_smoke import MAIN, PACKAGE, SKY, RuntimeSmoke, TestFailure


PERF = re.compile(
    r"mode=(fullscreen|pip)\s+frames=(\d+)\s+fps=([\d.]+)\s+"
    r"draw_p95_ms=([\d.]+)\s+hz=([\d.]+)(?:\s+pan=(true|false))?")


def parse_samples(log, mode):
    samples = []
    for line in log.splitlines():
        match = PERF.search(line)
        if match and match.group(1) == mode:
            values = {
                "mode": mode, "frames": int(match.group(2)),
                "fps": float(match.group(3)), "draw_p95_ms": float(match.group(4)),
                "display_hz": float(match.group(5)), "log_line": line,
            }
            if match.group(6) is not None:
                values["pan_active"] = match.group(6) == "true"
            samples.append(values)
    return samples


def summarize_samples(samples):
    frames = sum(item["frames"] for item in samples)
    estimated_seconds = sum(item["frames"] / item["fps"] for item in samples if item["fps"] > 0)
    min_fps = min(item["fps"] for item in samples)
    max_p95 = max(item["draw_p95_ms"] for item in samples)
    min_hz = min(item["display_hz"] for item in samples)
    nominal = min_fps >= 59.0 and max_p95 <= 1000 / 60 and min_hz >= 59.0
    return {
        "sample_count": len(samples), "drawn_frames_in_reported_windows": frames,
        "render_fps_min": min_fps, "render_fps_median": statistics.median(x["fps"] for x in samples),
        "render_fps_weighted_mean": round(frames / estimated_seconds, 3) if estimated_seconds else 0,
        "render_fps_max": max(x["fps"] for x in samples),
        "maximum_reported_draw_p95_ms": max_p95,
        "display_hz_min": min_hz, "display_hz_max": max(x["display_hz"] for x in samples),
        "nominal_60_render_target_observed": nominal,
        "performance_status": "NOMINAL_60_RENDER_TARGET_OBSERVED" if nominal else "NOMINAL_60_RENDER_TARGET_NOT_CONFIRMED",
        "nominal_observation_rule": "Every captured window >=59 render FPS; draw p95 <=16.667ms; display >=59Hz.",
        "strict_minimum_60_presented_fps": "NOT_PROVEN_BY_RENDER_COUNTERS",
        "measurement_limits": "onDraw counts and CPU draw duration are not compositor-presented frame counts; an emulator is not the user's phone.",
        "samples": samples,
    }


class Live60Smoke(RuntimeSmoke):
    def __init__(self, args):
        super().__init__(args)
        self.report.update(test="Sternfenster live renderer and PiP", performance={},
                           user_device_test="NOT_PERFORMED", minimum_60_fps_guarantee="NOT_ESTABLISHED")

    def sky_record(self):
        dump = self.adb("shell", "dumpsys", "activity", "activities")
        pattern = (r"(?m)^\s*\* Hist\s+#\d+: ActivityRecord\{[^\n]*"
                   + re.escape(PACKAGE) + r"/(?:\.SkyActivity|" + re.escape(PACKAGE) + r"\.SkyActivity)\b[^\n]*")
        match = re.search(pattern, dump)
        if not match:
            return ""
        tail = dump[match.end():]
        end = re.search(r"(?m)^\s*\* (?:Hist\s+#|Task\{)", tail)
        return match.group() + (tail[:end.start()] if end else tail)

    def in_pip(self):
        record = self.sky_record()
        return ("mLastReportedPictureInPictureMode=true" in record
                and ("mWindowingMode=pinned" in record or "mWindowingMode=2" in record))

    def perf_log(self):
        return self.adb("logcat", "-d", "-v", "epoch", "-s",
                        "SternfensterPerf:I", "SternfensterTestWindow:I", "*:S")

    def mark_window(self, name):
        marker = "begin-" + name + "-" + str(time.monotonic_ns())
        self.adb("shell", "log", "-t", "SternfensterTestWindow", marker)
        return marker

    def since_marker(self, marker):
        raw = self.perf_log()
        if marker not in raw:
            raise TestFailure("Performance window marker is missing from logcat")
        return raw.rsplit(marker, 1)[1]

    def wait_seconds_with_crash_checks(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.assert_no_app_crash()
            time.sleep(min(0.5, max(0, deadline - time.monotonic())))

    def measure(self, name, mode, seconds):
        self.wait_seconds_with_crash_checks(2)
        self.adb("shell", "dumpsys", "gfxinfo", PACKAGE, "reset")
        marker = self.mark_window(name)
        self.wait_seconds_with_crash_checks(seconds)
        raw = self.since_marker(marker)
        (self.out / f"{name}-perf-logcat.txt").write_text(raw, encoding="utf-8")
        gfx = self.adb("shell", "dumpsys", "gfxinfo", PACKAGE, "framestats")
        (self.out / f"{name}-gfxinfo.txt").write_text(gfx, encoding="utf-8")
        samples = parse_samples(raw, mode)
        if len(samples) < math.floor(seconds * 0.6):
            raise TestFailure(f"Too few continuing {mode} frame reports: {len(samples)} in {seconds}s")
        if any(x["frames"] <= 0 or x["fps"] <= 1.1 for x in samples):
            raise TestFailure(f"{mode} did not sustain continuous drawing above the old 1Hz timer")
        if any(not math.isfinite(x[key]) for x in samples for key in ("fps", "draw_p95_ms", "display_hz")):
            raise TestFailure("Non-finite performance measurement")
        if any(x.get("pan_active") is False for x in samples):
            raise TestFailure("Performance window did not keep the moving panorama workload active")
        summary = summarize_samples(samples)
        summary["requested_observation_seconds"] = seconds
        summary["pan_telemetry_available"] = all("pan_active" in x for x in samples)
        count = re.search(r"Total frames rendered:\s*(\d+)", gfx)
        summary["android_gfxinfo_total_frames"] = int(count.group(1)) if count else None
        self.report["performance"][name] = summary
        self.save_report()
        print("PERFORMANCE " + name + " " + json.dumps({key: value for key, value in summary.items()
              if key != "samples"}, ensure_ascii=False), flush=True)
        return summary

    def swipe_sky(self):
        def find():
            for node in self.dump_ui().iter("node"):
                if node.get("package") == PACKAGE and node.get("content-desc", "").startswith("Sternkarte nach "):
                    return (node,)
            return None
        node = self.poll("accessible sky canvas", find, timeout=55)[0]
        values = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
        if not values:
            raise TestFailure("Sky canvas has no usable bounds")
        left, top, right, bottom = map(int, values.groups())
        if right <= left or bottom <= top:
            raise TestFailure("Sky canvas is not visible")
        self.adb("shell", "input", "swipe", str((left * 3 + right) // 4), str((top + bottom) // 2),
                 str((left + right * 3) // 4), str((top + bottom) // 2), "350")

    def run(self):
        with self.step("device-and-install"):
            self.adb("wait-for-device", timeout=30)
            self.poll("boot completed", lambda: self.adb("shell", "getprop", "sys.boot_completed").strip() == "1")
            self.report["environment"] = {
                "sdk": int(self.adb("shell", "getprop", "ro.build.version.sdk").strip()),
                "release": self.adb("shell", "getprop", "ro.build.version.release").strip(),
                "model": self.adb("shell", "getprop", "ro.product.model").strip(),
                "renderer": "Android emulator with SwiftShader; not a Samsung device benchmark",
            }
            self.report["apk_sha256"] = hashlib.sha256(self.args.candidate.read_bytes()).hexdigest()
            self.adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
            self.adb("shell", "wm", "dismiss-keyguard")
            self.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
            self.adb("shell", "settings", "put", "system", "user_rotation", "0")
            self.adb("install", "-r", str(self.args.candidate.resolve()), timeout=90)
            self.adb("shell", "pm", "clear", PACKAGE)
            self.adb("logcat", "-b", "all", "-c")
            self.check_crashes = True

        with self.step("cold-start-and-live-controls"):
            self.launch()
            self.wait_activity(MAIN)
            self.open_sky()
            self.tap(description="Nach Osten blicken")
            self.expect_direction("Ost", 90)
            self.tap(description="Hineinzoomen")
            self.tap(description="Herauszoomen")
            self.swipe_sky()
            self.tap(description="Blick nach Süden zurücksetzen")
            self.expect_direction("Süd", 180)
            self.tap(description="Automatischen Rundblick umschalten")
            self.capture("fullscreen-moving-before")

        with self.step("fullscreen-continuous-rendering") as result:
            result["performance_key"] = "fullscreen"
            self.measure("fullscreen", "fullscreen", 10)
            self.capture("fullscreen-moving-after")

        with self.step("background-stop-and-resume"):
            pid = self.adb("shell", "pidof", PACKAGE).strip()
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("SkyActivity stopped outside PiP", lambda: "state=STOPPED" in self.sky_record())
            self.wait_seconds_with_crash_checks(2)
            marker = self.mark_window("stopped")
            self.wait_seconds_with_crash_checks(3)
            after = self.since_marker(marker)
            (self.out / "stopped-perf-logcat.txt").write_text(after, encoding="utf-8")
            if PERF.search(after):
                raise TestFailure("Invisible stopped Activity kept reporting drawn frames")
            self.launch()
            self.poll("app returned to foreground", lambda: self.resumed_component() in
                      (MAIN, SKY, MAIN.replace('/.', '/' + PACKAGE + '.'), SKY.replace('/.', '/' + PACKAGE + '.')))
            if self.resumed_component() in (MAIN, MAIN.replace('/.', '/' + PACKAGE + '.')):
                self.open_sky()
            else:
                self.wait_activity(SKY)
            if self.adb("shell", "pidof", PACKAGE).strip() != pid:
                raise TestFailure("Home/resume unexpectedly restarted the process")
            self.tap(description="Blick nach Süden zurücksetzen")
            self.tap(description="Automatischen Rundblick umschalten")
            self.capture("fullscreen-resumed")

        with self.step("picture-in-picture-on-home") as result:
            pid = self.adb("shell", "pidof", PACKAGE).strip()
            self.tap(description="Schwebendes Live-Fenster öffnen")
            self.poll("SkyActivity in pinned windowing mode 2", self.in_pip, timeout=45)
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("PiP still visible on Home", self.in_pip, timeout=30)
            if self.adb("shell", "pidof", PACKAGE).strip() != pid:
                raise TestFailure("Entering PiP unexpectedly changed the app process")
            result["windowing_mode"] = 2
            result["mode_name"] = "pinned"
            result["pid"] = pid
            self.dump_ui()
            self.capture("pip-moving-before")
            self.measure("pip", "pip", 8)
            self.capture("pip-moving-after")
            self.poll("PiP remains pinned after measurement", self.in_pip)

        with self.step("dismiss-pip-and-process-restart"):
            old_pid = self.adb("shell", "pidof", PACKAGE).strip()
            self.adb("shell", "am", "force-stop", PACKAGE)
            self.poll("PiP process stopped", lambda: not self.adb("shell", "pidof", PACKAGE, check=False).strip())
            self.poll("PiP task dismissed", lambda: not self.in_pip())
            self.launch()
            self.wait_activity(MAIN)
            self.open_sky()
            if self.adb("shell", "pidof", PACKAGE).strip() == old_pid:
                raise TestFailure("Process restart did not create a new process")
            self.capture("reopened-after-pip-dismissal")

        with self.step("no-app-crash-or-anr"):
            self.assert_no_app_crash()
            raw = self.adb("logcat", "-b", "all", "-d", "-v", "threadtime")
            (self.out / "candidate-logcat.txt").write_text(raw, encoding="utf-8")
            if f"ANR in {PACKAGE}" in raw:
                raise TestFailure("Sternfenster ANR recorded")
        self.report["status"] = "functional_checks_passed"
        self.report["performance_status"] = (
            "NOMINAL_60_RENDER_TARGET_OBSERVED_IN_BOTH_MEASURED_WINDOWS"
            if all(item["nominal_60_render_target_observed"] for item in self.report["performance"].values())
            else "NOMINAL_60_RENDER_TARGET_NOT_CONFIRMED_IN_ALL_WINDOWS")
        self.save_report()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--adb", default="adb")
    parser.add_argument("--serial")
    args = parser.parse_args()
    if not args.candidate.is_file():
        parser.error(f"APK does not exist: {args.candidate}")
    test = Live60Smoke(args)
    try:
        test.run()
    except Exception as exc:
        test.report.update(status="functional_checks_failed", error=str(exc))
        (test.out / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        test.diagnostics()
        test.save_report()
    print("FUNCTIONAL CHECKS PASSED; PERFORMANCE: " + test.report["performance_status"], flush=True)
    print("A strict minimum of 60 presented FPS on the user's phone is NOT established by this emulator test.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
