#!/usr/bin/env python3
"""Real-device regression for the v0.2.0 WindowInsets cold-start crash.

Requires a freshly booted Android API 30+ emulator, adb, and two APKs signed
with the SAME disposable test key. No release signing material is needed.

Example (the workflow builds/signs both APKs and boots an API 35 emulator):
  python3 tools/runtime_smoke.py --baseline /tmp/baseline-signed.apk \
      --candidate /tmp/candidate-signed.apk --output-dir /tmp/runtime-results

Exit 0 means the exact baseline crash was reproduced AND the fixed build
passed every lifecycle check. A missing baseline crash is a failure, not a
skip. Screenshots, UI XML, logcat and report.json remain available on failure.
Only a disposable emulator should be used: this clears the app's test data.
"""

import argparse
import base64
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback
import xml.etree.ElementTree as ET


PACKAGE = "de.universelab.sternfenster"
MAIN = f"{PACKAGE}/.MainActivity"
SKY = f"{PACKAGE}/.SkyActivity"


class TestFailure(RuntimeError):
    """A failed observable assertion, including adb/device failures."""


class RuntimeSmoke:
    def __init__(self, args):
        self.args = args
        self.out = args.output_dir.resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.report = {"status": "running", "checks": [], "environment": {}}
        self.phase = "setup"
        self.check_crashes = False
        self.last_xml = None

    def adb(self, *arguments, timeout=30, check=True, binary=False):
        command = [self.args.adb]
        if self.args.serial:
            command += ["-s", self.args.serial]
        command += list(arguments)
        with (self.out / "adb-commands.txt").open("a", encoding="utf-8") as log:
            log.write(f"[{self.phase}] {' '.join(command)}\n")
        try:
            result = subprocess.run(command, capture_output=True, timeout=timeout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise TestFailure(f"adb failed: {' '.join(arguments)}: {exc}") from exc
        stdout = result.stdout if binary else result.stdout.decode("utf-8", "replace")
        stderr = result.stderr.decode("utf-8", "replace")
        if check and result.returncode:
            raise TestFailure(f"adb exit {result.returncode}: {' '.join(arguments)}\n"
                              f"{stdout if not binary else '<binary output>'}\n{stderr}")
        return stdout

    def save_report(self):
        (self.out / "report.json").write_text(
            json.dumps(self.report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    @contextlib.contextmanager
    def step(self, name):
        self.phase = name
        started = time.monotonic()
        result = {"name": name, "status": "running"}
        self.report["checks"].append(result)
        print(f"CHECK {name}", flush=True)
        try:
            yield result
        except Exception as exc:
            result.update(status="failed", error=str(exc))
            raise
        else:
            result["status"] = "passed"
            print(f"PASS  {name}", flush=True)
        finally:
            result["seconds"] = round(time.monotonic() - started, 2)
            self.save_report()

    def crash_log(self):
        return self.adb("logcat", "-b", "crash", "-d", "-v", "threadtime")

    def assert_no_app_crash(self):
        if not self.check_crashes:
            return
        crash = self.crash_log()
        if f"Process: {PACKAGE}" in crash or f">>> {PACKAGE} <<<" in crash:
            (self.out / "candidate-crash.txt").write_text(crash, encoding="utf-8")
            raise TestFailure("Candidate crashed. See candidate-crash.txt.")

    def poll(self, description, predicate, timeout=40):
        deadline = time.monotonic() + timeout
        last_error = None
        while time.monotonic() < deadline:
            self.assert_no_app_crash()
            try:
                value = predicate()
                if value:
                    return value
            except (ET.ParseError, TestFailure) as exc:
                last_error = str(exc)
            # Bounded polling backoff, never a replacement for checking state.
            time.sleep(0.35)
        suffix = f" Last observation: {last_error}" if last_error else ""
        raise TestFailure(f"Timed out waiting for {description}.{suffix}")

    def resumed_component(self):
        dump = self.adb("shell", "dumpsys", "activity", "activities")
        for line in dump.splitlines():
            if "mResumedActivity" in line or "topResumedActivity" in line:
                match = re.search(r" ([A-Za-z0-9_.]+/[A-Za-z0-9_.$]+)", line)
                if match:
                    return match.group(1)
        return ""

    def wait_activity(self, component):
        # AOSP dumps normally abbreviate the class name; accept the full name too.
        full = component.replace("/.", f"/{PACKAGE}.")
        return self.poll(f"resumed {component}",
                         lambda: self.resumed_component() in (component, full))

    def dump_ui(self):
        if os.environ.get("STERNFENSTER_UI_PROBE") == "1":
            # The independent CI test APK snapshots actual accessibility nodes
            # without waitForIdle, so continuous rendering does not block input.
            result = self.adb("shell", "am", "instrument", "-w", "-e", "snapshot", "true",
                              "de.universelab.sternfenster.probe/.SnapshotInstrumentation", timeout=20)
            encoded = re.search(r"(?m)^INSTRUMENTATION_RESULT: snapshot_xml_base64=([A-Za-z0-9+/=]+)\s*$", result)
            if not encoded or not re.search(r"(?m)^INSTRUMENTATION_CODE:\s*-1\s*$", result):
                (self.out / "ui-probe-failure.txt").write_text(result, encoding="utf-8")
                raise TestFailure("No successful no-idle UI snapshot; see ui-probe-failure.txt")
            try:
                raw = base64.b64decode(encoded.group(1), validate=True).decode("utf-8")
            except (ValueError, UnicodeError) as exc:
                raise TestFailure(f"Invalid no-idle UI snapshot encoding: {exc}") from exc
        else:
            remote = "/sdcard/sternfenster-runtime.xml"
            self.adb("shell", "rm", "-f", remote)
            # Legacy fallback for runs without the separate CI instrumentation APK.
            self.adb("shell", "uiautomator", "dump", "--compressed", remote, timeout=18)
            raw = self.adb("exec-out", "cat", remote)
        root = ET.fromstring(raw[raw.index("<?xml"):]) if "<?xml" in raw else ET.fromstring(raw)
        self.last_xml = raw
        if self.recover_pixel_launcher_anr(root):
            # Closing an unrelated emulator dialog does not establish app health.
            # Return a fresh hierarchy; all normal app assertions still apply.
            return self.dump_ui()
        return root

    def recover_pixel_launcher_anr(self, root):
        # Observed on the API-35 emulator during launcher startup. Match only
        # this exact system dialog; never dismiss a Sternfenster error dialog.
        def exact(resource, text):
            return [node for node in root.iter("node")
                    if node.get("package") == "android"
                    and node.get("resource-id") == resource
                    and node.get("text") == text]
        title = "Pixel Launcher isn't responding"
        if len(exact("android:id/alertTitle", title)) != 1:
            return False
        close = exact("android:id/aerr_close", "Close app")
        if len(close) != 1 or len(exact("android:id/aerr_wait", "Wait")) != 1:
            return False
        button = close[0]
        if button.get("enabled") != "true" or button.get("clickable") != "true":
            return False
        bounds = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", button.get("bounds", ""))
        if not bounds:
            return False
        left, top, right, bottom = map(int, bounds.groups())
        if right <= left or bottom <= top:
            return False
        events = self.report.setdefault("emulator_recoveries", [])
        if len(events) >= 2:
            raise TestFailure("Pixel Launcher ANR recovery limit reached (2); emulator remains unhealthy")
        self.assert_no_app_crash()
        evidence = f"pixel-launcher-anr-{len(events) + 1}"
        self.capture(evidence)
        event = {"phase": self.phase, "dialog_title": title, "action": "Close app",
                 "button_bounds": button.get("bounds"), "evidence_prefix": evidence}
        events.append(event)
        self.save_report()
        print(f"EMULATOR RECOVERY: {title}; evidence: {evidence}", flush=True)
        self.adb("shell", "input", "tap", str((left + right) // 2), str((top + bottom) // 2))
        return True

    @staticmethod
    def node(root, *, text=None, description=None):
        for node in root.iter("node"):
            if node.get("package") != PACKAGE:
                continue
            if text is not None and node.get("text", "").strip() != text:
                continue
            if description is not None and node.get("content-desc", "") != description:
                continue
            return node
        return None

    def wait_node(self, *, text=None, description=None):
        def find():
            node = self.node(self.dump_ui(), text=text, description=description)
            # ElementTree leaf nodes are falsey, so return a one-element tuple.
            return (node,) if node is not None else None
        return self.poll(f"UI element {text or description!r}", find, timeout=55)[0]

    def tap(self, *, text=None, description=None):
        node = self.wait_node(text=text, description=description)
        if node.get("enabled") != "true" or node.get("clickable") != "true":
            raise TestFailure(f"UI element is not enabled/clickable: {text or description}")
        match = re.fullmatch(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", node.get("bounds", ""))
        if not match:
            raise TestFailure(f"Missing UI bounds: {node.attrib}")
        left, top, right, bottom = map(int, match.groups())
        if right <= left or bottom <= top:
            raise TestFailure(f"UI element is outside the visible screen: {node.attrib}")
        self.adb("shell", "input", "tap", str((left + right) // 2), str((top + bottom) // 2))

    def expect_direction(self, direction, degrees):
        description = (f"Sternkarte nach {direction}, Blickhöhe 42 Grad. "
                       "Mit Richtungstasten und Zoom bedienbar.")
        self.wait_node(description=description)
        return self.poll(
            f"visible direction {direction} {degrees} degrees",
            lambda: any(f"· {direction} {degrees}° · Blickhöhe 42" in node.get("text", "")
                        for node in self.dump_ui().iter("node")), timeout=55)

    def capture(self, name):
        image = self.adb("exec-out", "screencap", "-p", binary=True)
        if not image.startswith(b"\x89PNG\r\n\x1a\n"):
            raise TestFailure("screencap did not produce a PNG")
        (self.out / f"{name}.png").write_bytes(image)
        if self.last_xml:
            (self.out / f"{name}.xml").write_text(self.last_xml, encoding="utf-8")
        (self.out / f"{name}-activities.txt").write_text(
            self.adb("shell", "dumpsys", "activity", "activities"), encoding="utf-8")

    def launch(self):
        # The real launcher flags restore the existing task after Home. SkyActivity
        # remains non-exported and is only entered through the visible UI button.
        result = self.adb("shell", "am", "start", "-W", "-a", "android.intent.action.MAIN",
                          "-c", "android.intent.category.LAUNCHER", "-f", "0x10200000",
                          "-n", MAIN)
        (self.out / f"{self.phase}-start.txt").write_text(result, encoding="utf-8")

    def open_sky(self):
        self.tap(text="Live-Sternkarte öffnen")
        self.wait_activity(SKY)
        self.wait_node(text="Sternfenster · Live")

    def rotate(self, orientation):
        self.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
        self.adb("shell", "settings", "put", "system", "user_rotation", str(orientation))
        self.poll(f"UI rotation {orientation}",
                  lambda: self.dump_ui().get("rotation") == str(orientation), timeout=55)
        self.wait_activity(SKY)

    def run(self):
        with self.step("device-ready") as result:
            self.adb("wait-for-device", timeout=30)
            self.poll("Android boot completed",
                      lambda: self.adb("shell", "getprop", "sys.boot_completed").strip() == "1")
            sdk = int(self.adb("shell", "getprop", "ro.build.version.sdk").strip())
            if sdk < 30:
                raise TestFailure(f"API {sdk} does not execute the affected WindowInsets code")
            self.report["environment"] = {
                "sdk": sdk,
                "release": self.adb("shell", "getprop", "ro.build.version.release").strip(),
                "model": self.adb("shell", "getprop", "ro.product.model").strip(),
            }
            for label, apk in (("baseline", self.args.baseline), ("candidate", self.args.candidate)):
                self.report[f"{label}_sha256"] = hashlib.sha256(apk.read_bytes()).hexdigest()
            self.adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
            self.adb("shell", "wm", "dismiss-keyguard")
            self.adb("shell", "settings", "put", "system", "accelerometer_rotation", "0")
            self.adb("shell", "settings", "put", "system", "user_rotation", "0")

        with self.step("baseline-exact-crash") as result:
            self.adb("install", "-r", str(self.args.baseline.resolve()), timeout=90)
            self.adb("shell", "pm", "clear", PACKAGE)
            self.adb("shell", "am", "force-stop", PACKAGE)
            self.adb("logcat", "-b", "all", "-c")
            self.launch()
            required = [f"Process: {PACKAGE}", "FATAL EXCEPTION", "java.lang.NullPointerException",
                        "PhoneWindow.getInsetsController", "Ui.install"]
            def exact_crash():
                crash = self.crash_log()
                (self.out / "baseline-crash.txt").write_text(crash, encoding="utf-8")
                return crash if all(token in crash for token in required) else None
            evidence = self.poll("exact baseline WindowInsets NullPointerException", exact_crash, timeout=25)
            result["matched_stack_tokens"] = required
            result["expected_failure_reproduced"] = True
            self.capture("baseline-crash")

        with self.step("candidate-cold-start"):
            self.adb("shell", "am", "force-stop", PACKAGE)
            self.adb("install", "-r", str(self.args.candidate.resolve()), timeout=90)
            self.adb("logcat", "-b", "all", "-c")
            self.check_crashes = True
            self.launch()
            self.wait_activity(MAIN)
            self.wait_node(text="Live-Sternkarte öffnen")
            self.capture("candidate-main")

        with self.step("open-live-sky"):
            self.open_sky()
            # New releases initially follow the phone. Exercise the explicit
            # manual reset before asserting the historical fixed south view.
            self.tap(description="Blick nach Süden zurücksetzen")
            self.expect_direction("Süd", 180)
            self.capture("candidate-sky")

        with self.step("visible-controls-and-clock") as result:
            self.tap(description="Nach Osten blicken")
            self.expect_direction("Ost", 90)
            self.tap(description="Hineinzoomen")
            self.tap(description="Herauszoomen")
            self.tap(description="Blick nach Süden zurücksetzen")
            self.expect_direction("Süd", 180)
            self.tap(description="Nach Westen blicken")
            self.expect_direction("West", 270)
            self.tap(description="Nach Norden blicken")
            self.expect_direction("Nord", 0)
            self.tap(description="Nach Osten blicken")
            self.expect_direction("Ost", 90)
            def clock():
                for node in self.dump_ui().iter("node"):
                    value = node.get("text", "")
                    if re.match(r"^\d{2}:\d{2}:\d{2} · Ost 90°", value):
                        return value
                return None
            first = self.poll("live clock", clock, timeout=55)
            def changed_clock():
                current = clock()
                return current if current and current != first else None
            second = self.poll("advancing live clock", changed_clock, timeout=55)
            result.update(clock_before=first, clock_after=second)
            self.capture("candidate-controls")

        with self.step("home-and-resume-same-activity"):
            pid = self.adb("shell", "pidof", PACKAGE).strip()
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("launcher in foreground",
                      lambda: (current := self.resumed_component()) and not current.startswith(PACKAGE + "/"))
            self.launch()
            self.wait_activity(SKY)
            self.expect_direction("Ost", 90)
            if self.adb("shell", "pidof", PACKAGE).strip() != pid:
                raise TestFailure("Home/resume unexpectedly replaced the application process")
            self.capture("candidate-resumed")

        with self.step("rotate-and-restore-state"):
            self.rotate(1)
            self.expect_direction("Ost", 90)
            self.capture("candidate-landscape")
            self.rotate(0)
            self.expect_direction("Ost", 90)
            self.capture("candidate-portrait-restored")

        with self.step("process-cold-restart") as result:
            old_pid = self.adb("shell", "pidof", PACKAGE).strip()
            # Home executes onPause, persisting the selected direction before kill.
            self.adb("shell", "input", "keyevent", "KEYCODE_HOME")
            self.poll("app paused before force-stop",
                      lambda: (current := self.resumed_component()) and not current.startswith(PACKAGE + "/"))
            self.adb("shell", "am", "force-stop", PACKAGE)
            self.poll("old process stopped", lambda: not self.adb("shell", "pidof", PACKAGE, check=False).strip())
            self.launch()
            self.wait_activity(MAIN)
            self.open_sky()
            self.expect_direction("Ost", 90)
            new_pid = self.adb("shell", "pidof", PACKAGE).strip()
            if not new_pid or new_pid == old_pid:
                raise TestFailure("Cold restart did not create a new app process")
            result.update(old_pid=old_pid, new_pid=new_pid)
            self.capture("candidate-restarted")

        with self.step("back-and-reopen"):
            self.tap(description="Zurück")
            self.wait_activity(MAIN)
            self.open_sky()
            self.expect_direction("Ost", 90)
            self.capture("candidate-final")

        with self.step("no-candidate-crash-or-anr"):
            self.assert_no_app_crash()
            logcat = self.adb("logcat", "-b", "all", "-d", "-v", "threadtime")
            (self.out / "candidate-logcat.txt").write_text(logcat, encoding="utf-8")
            if f"ANR in {PACKAGE}" in logcat:
                raise TestFailure("Candidate reported an ANR; see candidate-logcat.txt")
        self.report["status"] = "passed"
        self.save_report()

    def diagnostics(self):
        for filename, arguments in (
            ("final-logcat.txt", ("logcat", "-b", "all", "-d", "-v", "threadtime")),
            ("final-activities.txt", ("shell", "dumpsys", "activity", "activities")),
            ("final-package.txt", ("shell", "dumpsys", "package", PACKAGE)),
        ):
            try:
                (self.out / filename).write_text(self.adb(*arguments, timeout=20), encoding="utf-8")
            except TestFailure as exc:
                print(f"Diagnostic unavailable: {filename}: {exc}", file=sys.stderr)
        try:
            self.capture("final-screen")
        except TestFailure as exc:
            print(f"Screenshot unavailable: {exc}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--baseline", type=Path, required=True, help="signed v0.2.0 APK with the known crash")
    parser.add_argument("--candidate", type=Path, required=True, help="fixed APK, signed with the same test key")
    parser.add_argument("--output-dir", type=Path, required=True, help="diagnostic artifact directory")
    parser.add_argument("--adb", default="adb", help="adb executable")
    parser.add_argument("--serial", help="optional adb device serial")
    args = parser.parse_args()
    for apk in (args.baseline, args.candidate):
        if not apk.is_file():
            parser.error(f"APK does not exist: {apk}")
    smoke = RuntimeSmoke(args)
    try:
        smoke.run()
    except Exception as exc:
        smoke.report.update(status="failed", error=str(exc))
        (smoke.out / "failure.txt").write_text(traceback.format_exc(), encoding="utf-8")
        print(f"FAIL: {exc}", file=sys.stderr, flush=True)
        return 1
    finally:
        smoke.diagnostics()
        smoke.save_report()
    print(f"Runtime regression passed. Evidence: {smoke.out}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
