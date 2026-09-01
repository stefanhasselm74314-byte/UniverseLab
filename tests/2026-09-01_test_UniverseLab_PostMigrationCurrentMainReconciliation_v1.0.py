#!/usr/bin/env python3
"""Adversarial regression tests for post-migration current-main reconciliation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "tools/2026-09-01_validate_UniverseLab_PostMigrationCurrentMainReconciliation_v1.1.py"
_spec = importlib.util.spec_from_file_location("ul_post_migration_reconciliation_v11", VALIDATOR)
assert _spec and _spec.loader
module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(module)
validate = module.base.validate

STATE = Path("registry/2026-09-01_UniverseLab_CurrentMainCanonicalState_v1.1.json")
SITE = Path("registry/2026-09-01_UniverseLab_SiteState_v1.2.json")
CHECKPOINT = Path("registry/2026-09-01_UniverseLab_SessionCheckpoint_v1.32.json")
ALIAS = Path("registry/session-checkpoint-latest.json")
CLOSURE = Path("registry/2026-09-01_UniverseLab_CanonicalCosmologyPublicMigrationClosure_v1.0.json")
MANIFEST = Path("project-manifest.json")


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expect_failure(root: Path, needle: str) -> None:
    try:
        validate(root)
    except AssertionError as exc:
        assert needle in str(exc), (needle, str(exc))
    else:
        raise AssertionError(f"expected fail-closed rejection containing {needle!r}")


def copy_fixture(dst: Path) -> None:
    shutil.copytree(ROOT / "registry", dst / "registry")
    shutil.copytree(ROOT / "schemas", dst / "schemas")
    shutil.copy2(ROOT / "project-manifest.json", dst / "project-manifest.json")
    shutil.copy2(ROOT / "research-status.html", dst / "research-status.html")
    if (ROOT / "convention-registry.json").is_file():
        shutil.copy2(ROOT / "convention-registry.json", dst / "convention-registry.json")
    site = load(ROOT / SITE)
    for row in site["pages"]:
        source = ROOT / row["path"]
        target = dst / row["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)


def main() -> None:
    validate(ROOT)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / STATE)
        data["physical_governance"]["K1-D"] = "RELEASED"
        write_json(root / STATE, data)
        expect_failure(root, "K1-D")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        with (root / ALIAS).open("a", encoding="utf-8") as handle:
            handle.write("\n")
        expect_failure(root, "byte-identical")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / CLOSURE)
        data["scope"]["migration_status"] = "PENDING"
        write_json(root / CLOSURE, data)
        expect_failure(root, "COMPLETE_FOR_DECLARED_PUBLIC_SET")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / STATE)
        data["program"]["gate_status"] = "CLOSED"
        write_json(root / STATE, data)
        expect_failure(root, "OPEN")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / MANIFEST)
        data["basis_main_commit"] = "46579b58b8ca2ae3fb4ba7726446c5871d84da79"
        write_json(root / MANIFEST, data)
        expect_failure(root, "basis_main_commit")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / SITE)
        row = next(item for item in data["pages"] if item["path"] == "observatory.html")
        row["status"] = "ACTIVE_DIAGNOSTIC_PENDING_NUMERICAL_RECONCILIATION"
        write_json(root / SITE, data)
        expect_failure(root, "observatory.html")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        copy_fixture(root)
        data = load(root / CHECKPOINT)
        data["gate_state"]["physical_evidence_effect"] = "PROMOTED"
        write_json(root / CHECKPOINT, data)
        write_json(root / ALIAS, data)
        expect_failure(root, "physical evidence effect")

    print("UniverseLab post-migration reconciliation adversarial tests: PASS")


if __name__ == "__main__":
    main()
