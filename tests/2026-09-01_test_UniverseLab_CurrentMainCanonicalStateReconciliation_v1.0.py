#!/usr/bin/env python3
"""Adversarial regression tests for pointer-aware current-main reconciliation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py"
SPEC = importlib.util.spec_from_file_location("ul_state_reconcile", VALIDATOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def expect_failure(root: Path, needle: str) -> None:
    try:
        MODULE.validate(root)
    except (AssertionError, KeyError, ValueError) as exc:
        message = str(exc)
        # A bare Python assert has an empty message.  The fail-closed property is
        # the mandatory condition; when the validator supplies a diagnostic, it
        # must still identify the expected mutated field.
        if message:
            assert needle in message, (needle, message)
        return
    raise AssertionError(f"expected fail-closed rejection containing {needle!r}")


def copy_file(dst: Path, rel: Path) -> None:
    target = dst / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / rel, target)


def copy_minimal_root(dst: Path) -> MODULE.ActivePaths:
    paths = MODULE.resolve_paths(ROOT)
    required = {
        MODULE.CHECKPOINT_ALIAS,
        paths.checkpoint,
        paths.current_state,
        paths.site_state,
        MODULE.MANIFEST,
        MODULE.RESEARCH_STATUS_DE,
        MODULE.RESEARCH_STATUS_EN,
        MODULE.GLOBAL_SHELL,
        MODULE.PLATFORM_WORKFLOW,
        MODULE.G0_WORKFLOW,
    }
    for rel in required:
        copy_file(dst, rel)
    return paths


def write_identical_checkpoint_pair(root: Path, paths: MODULE.ActivePaths, value: dict) -> None:
    payload = json.dumps(value, indent=2, ensure_ascii=False) + "\n"
    (root / paths.checkpoint).write_text(payload, encoding="utf-8")
    (root / MODULE.CHECKPOINT_ALIAS).write_text(payload, encoding="utf-8")


def main() -> None:
    MODULE.validate(ROOT, strict_source_existence=True)

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        paths = copy_minimal_root(tmp)
        state_path = tmp / paths.current_state
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["physical_governance"]["K1-D"] = "RELEASED"
        state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmp, "K1-D")

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        copy_minimal_root(tmp)
        alias_path = tmp / MODULE.CHECKPOINT_ALIAS
        alias_path.write_text(alias_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        expect_failure(tmp, "byte-identical")

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        copy_minimal_root(tmp)
        manifest_path = tmp / MODULE.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["release_date"] = "2026-08-05"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmp, "release_date")

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        paths = copy_minimal_root(tmp)
        checkpoint = json.loads((tmp / paths.checkpoint).read_text(encoding="utf-8"))
        checkpoint.pop("current_goal")
        write_identical_checkpoint_pair(tmp, paths, checkpoint)
        expect_failure(tmp, "current_goal")

    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        paths = copy_minimal_root(tmp)
        manifest_path = tmp / MODULE.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["canonical_state"] = "registry/nonexistent-current-state.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        expect_failure(tmp, "canonical_state")

    print("UniverseLab pointer-aware current-main reconciliation regression tests: PASS")


if __name__ == "__main__":
    main()
