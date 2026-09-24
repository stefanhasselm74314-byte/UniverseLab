#!/usr/bin/env python3
"""Adversarial regression tests for the UniverseLab Pages deployment guard."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "tools/2026-09-24_verify_UniverseLab_PagesDeploySource_v1.0.py"
WORKFLOW = ROOT / ".github/workflows/deploy-pages.yml"
SW = ROOT / "2026-08-19_UniverseLab_SitePrintExportServiceWorker_v1.0.js"

CURRENT = "a" * 40
HISTORICAL = "b" * 40
ADVANCED = "c" * 40


def load_guard():
    spec = importlib.util.spec_from_file_location("ul_pages_guard", GUARD)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def rejects(fn) -> None:
    try:
        fn()
    except Exception:
        return
    raise AssertionError("expected fail-closed rejection")


def main() -> None:
    guard = load_guard()

    # TEST A — current main SHA: deployment allowed.
    guard.verify(CURRENT, CURRENT, 1)

    # TEST B — historical SHA: deployment blocked.
    rejects(lambda: guard.verify(HISTORICAL, CURRENT, 1))

    # TEST C — manual rerun: blocked even if the SHA still equals main.
    rejects(lambda: guard.verify(CURRENT, CURRENT, 2))

    # TEST D — main advances after an earlier successful check: second check blocks.
    guard.verify(CURRENT, CURRENT, 1)
    rejects(lambda: guard.verify(CURRENT, ADVANCED, 1))

    # Fail closed on malformed or unavailable source identities.
    rejects(lambda: guard.verify("", CURRENT, 1))
    rejects(lambda: guard.verify(CURRENT, "", 1))

    workflow = WORKFLOW.read_text(encoding="utf-8")
    guard_cmd = "2026-09-24_verify_UniverseLab_PagesDeploySource_v1.0.py"
    assert workflow.count(guard_cmd) >= 2
    assert workflow.index("Revalidate deployment source before publish") < workflow.index("Deploy to GitHub Pages")
    assert "deploy-meta.json" in workflow
    assert "googlebc3b5b4a4888e35c.html" in workflow
    assert "Post-deploy attestation" in workflow
    assert "UNIVERSELAB_DEPLOY_SHA" in workflow

    sw = SW.read_text(encoding="utf-8")
    assert "googlebc3b5b4a4888e35c.html" in sw
    assert "PASSTHROUGH_PATHS" in sw

    print("UniverseLab Pages deploy integrity adversarial tests: PASS")


if __name__ == "__main__":
    main()
