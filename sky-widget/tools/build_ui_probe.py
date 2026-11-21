#!/usr/bin/env python3
"""Build a separate unsigned, test-only no-idle accessibility probe APK.

The probe instruments itself and has no Activity or declared permissions.
Only CI signs/installs it with an ephemeral key. It is not part of Sternfenster.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


def run(command):
    result = subprocess.run([str(value) for value in command], text=True, capture_output=True)
    if result.returncode:
        print(result.stdout, file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise SystemExit(result.returncode)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="Exact output name; APK remains UNSIGNED")
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    build_tools = sdk / "build-tools/36.0.0"
    android = sdk / "platforms/android-36/android.jar"
    source = Path(__file__).resolve().parent / "ui_probe/SnapshotInstrumentation.java"
    if not source.is_file():
        parser.error(f"Missing probe source: {source}")
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sternfenster-ui-probe-") as temporary:
        build = Path(temporary)
        for name in ("classes", "dex"):
            (build / name).mkdir()
        manifest = build / "AndroidManifest.xml"
        manifest.write_text('''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="de.universelab.sternfenster.probe">
    <application android:label="Sternfenster CI UI probe" android:debuggable="true"
        android:testOnly="true" android:allowBackup="false"/>
    <instrumentation android:name=".SnapshotInstrumentation"
        android:targetPackage="de.universelab.sternfenster.probe"
        android:functionalTest="true" android:handleProfiling="false"/>
</manifest>
''', encoding="utf-8")
        run([build_tools / "aapt2", "link", "-o", build / "resources.apk", "-I", android,
             "--manifest", manifest, "--min-sdk-version", "26", "--target-sdk-version", "36",
             "--version-code", "1", "--version-name", "1.0-ci-only"])
        javac = shutil.which("javac")
        compiler = [javac] if javac else [shutil.which("java"), "-m", "jdk.compiler/com.sun.tools.javac.Main"]
        run(compiler + ["-source", "17", "-target", "17", "-encoding", "UTF-8", "-classpath", android,
                        "-d", build / "classes", source])
        with zipfile.ZipFile(build / "classes.jar", "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted((build / "classes").rglob("*.class")):
                archive.write(path, path.relative_to(build / "classes"))
        run([build_tools / "d8", "--release", "--min-api", "26", "--lib", android,
             "--output", build / "dex", build / "classes.jar"])
        shutil.copyfile(build / "resources.apk", build / "unsigned.apk")
        with zipfile.ZipFile(build / "unsigned.apk", "a", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted((build / "dex").glob("*.dex")):
                archive.write(path, path.name)
        run([build_tools / "zipalign", "-f", "-p", "4", build / "unsigned.apk", output])
    print(json.dumps({"output": str(output), "unsigned": True, "test_only": True,
                      "bytes": output.stat().st_size, "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    main()
