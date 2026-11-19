#!/usr/bin/env python3
"""Reconstruct a local Gradle project from governance-compliant source names.

UniverseLab's FileNamingContract requires dated, versioned basenames for *all*
committed files. The Android tooling itself requires special fixed filenames.
Therefore the Git repository stores only dated source names; this script
materializes the fixed names into an ephemeral CI directory. No files under
``build_watch/`` need to be committed.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys


SOURCES = {
    "2026-11-19_UL_Watch_Settings_v0.2.txt": "settings.gradle",
    "2026-11-19_UL_Watch_RootGradle_v0.2.txt": "build.gradle",
    "2026-11-19_UL_Watch_GradleProperties_v0.2.txt": "gradle.properties",
    "2026-11-19_UL_Watch_FaceGradle_v0.2.txt": "watchface/build.gradle",
    "2026-11-19_UL_Watch_FaceManifest_v0.2.xml":
        "watchface/src/main/AndroidManifest.xml",
    "2026-11-19_UL_Watch_FaceInfo_v0.2.xml":
        "watchface/src/main/res/xml/watch_face_info.xml",
    "2026-11-19_UL_Watch_FaceStrings_v0.2.xml":
        "watchface/src/main/res/values/strings.xml",
    "2026-11-19_UL_Watch_FaceDefinition_v0.2.xml":
        "watchface/src/main/res/raw/watchface.xml",
    "2026-11-19_UL_Watch_CompassGradle_v0.2.txt": "compass/build.gradle",
    "2026-11-19_UL_Watch_CompassManifest_v0.2.xml":
        "compass/src/main/AndroidManifest.xml",
    "2026-11-19_UL_Watch_CompassActivity_v0.2.java":
        "compass/src/main/java/de/universelab/compass/CompassActivity.java",
    "2026-11-19_UL_Watch_CompassStrings_v0.2.xml":
        "compass/src/main/res/values/strings.xml",
    "2026-11-19_UL_Watch_CompassStyles_v0.2.xml":
        "compass/src/main/res/values/styles.xml",
    "2026-11-19_UL_Watch_AssetGenerator_v0.2.py": "scripts/make_assets.py",
    "2026-11-19_UL_Watch_Tests_v0.2.py": "tests/test_package.py",
    "2026-11-19_UL_Watch_README_v0.2.md": "README_DE.md",
}


def materialize(source_dir: Path, destination: Path) -> None:
    """Copy versioned textual source and generate reproducible image assets."""
    if destination.exists() and any(destination.iterdir()):
        raise RuntimeError(f"Output already exists and is not empty: {destination}")
    for filename, relative in SOURCES.items():
        source = source_dir / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    subprocess.run(
        [sys.executable, str(destination / "scripts/make_assets.py")],
        check=True,
    )
    print(f"Materialized {len(SOURCES)} files in {destination}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "build_watch",
        help="Destination for temporary Android project (must be empty)",
    )
    args = parser.parse_args()
    materialize(Path(__file__).resolve().parent, args.output.resolve())


if __name__ == "__main__":
    main()
