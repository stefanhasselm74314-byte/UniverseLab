#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
MANIFEST = ROOT / "solver-hub-manifest.json"
HUB = ROOT / "solver-hub.html"
BASELINE = ROOT / "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html"
WORKBENCH = ROOT / "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    hub = HUB.read_text(encoding="utf-8")
    baseline = BASELINE.read_text(encoding="utf-8")
    workbench = WORKBENCH.read_text(encoding="utf-8")

    solvers = registry.get("solvers", [])
    if len(solvers) != 14:
        fail(f"expected 14 solver roadmaps, got {len(solvers)}")

    expected_ids = [f"ULSH-{i:02d}" for i in range(1, 15)]
    ids = [solver.get("id") for solver in solvers]
    if ids != expected_ids:
        fail(f"solver ID/order drift: {ids}")

    if registry.get("status") != "PLANNING_BASELINE_NO_EXECUTION_EFFECT":
        fail("v1.0 registry status changed")
    governance = registry.get("governance", {})
    if governance.get("K1-D") != "NOT_RELEASED":
        fail("K1-D drift")
    if governance.get("K1-E") != "NOT_ADMISSIBLE":
        fail("K1-E drift")
    if governance.get("physical_evidence_effect") != "NONE":
        fail("physical evidence drift")

    for solver in solvers:
        if solver.get("readiness", {}).get("physical_release") != "BLOCKED":
            fail(f"physical release changed for {solver.get('id')}")
        if not solver.get("primary_blockers"):
            fail(f"no primary blocker for {solver.get('id')}")
        if not solver.get("release_gate"):
            fail(f"no release gate for {solver.get('id')}")

    program = manifest.get("development_program", {})
    if program.get("baseline_version") != "1.0.0":
        fail("manifest baseline version drift")
    if program.get("workbench_version") != "1.1.0":
        fail("manifest workbench version drift")
    if program.get("registry") != "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json":
        fail("workbench no longer uses frozen v1.0 registry")
    if program.get("dashboard") != "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html":
        fail("manifest workbench dashboard drift")
    if program.get("workbench_effect") != "presentation_and_dependency_work_queue_only":
        fail("workbench effect is no longer presentation-only")

    required_workbench_tokens = [
        "Solver Workbench v1.1",
        "Arbeitsreihenfolge ≠ Ausführungsfreigabe",
        "Nächster Planungsbaustein",
        "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json",
        "physical_release=BLOCKED",
        "K1-D",
        "K1-E",
        "Evidenzeffekt bleibt NONE",
    ]
    for token in required_workbench_tokens:
        if token not in workbench:
            fail(f"missing workbench firewall/UI token: {token}")

    for solver_id in expected_ids:
        if solver_id not in workbench:
            fail(f"workbench dependency phases do not mention {solver_id}")

    if "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html" not in hub:
        fail("Solver Hub does not link workbench v1.1")
    if "2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.html" not in hub:
        fail("Solver Hub lost frozen baseline link")
    if "14 Solver · ein Entwicklungsplan" not in baseline:
        fail("frozen v1.0 baseline page unexpectedly changed or missing")

    forbidden = [
        r"fetch\([^)]*(?:run|execute|grant)",
        r"subprocess",
        r"newton",
        r"shooting",
        r"CP01R1",
    ]
    lowered = workbench.lower()
    for pattern in forbidden:
        if re.search(pattern.lower(), lowered):
            fail(f"execution-capable token/pattern found in workbench: {pattern}")

    print("PASS: ULSH Solver Workbench v1.1 presentation-only contract")


if __name__ == "__main__":
    main()
