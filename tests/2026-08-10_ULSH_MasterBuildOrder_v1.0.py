#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "registry/2026-08-10_ULSH_MasterBuildOrder_v1.0.json"
BASELINE = ROOT / "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
PAGE = ROOT / "2026-08-10_ULSH_MasterBuildOrder_v1.0.html"
DOC = ROOT / "science/solver-hub/2026-08-10_ULSH_MasterBuildOrder_v1.0.md"
FIREWALL = ROOT / "science/solver-hub/2026-08-10_ULSH_MasterBuildOrder_Firewall_v1.0.md"
HUB = ROOT / "solver-hub.html"
README = ROOT / "README_SOLVER_HUB.md"
WORKBENCH = ROOT / "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html"


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    master = json.loads(MASTER.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))

    if master.get("status") != "PLANNING_EXECUTION_ORDER_NO_SOLVER_EXECUTION":
        fail("master build order status drift")
    gov = master.get("governance", {})
    if gov.get("K1-D") != "NOT_RELEASED" or gov.get("K1-E") != "NOT_ADMISSIBLE":
        fail("K1 governance drift")
    if gov.get("physical_evidence_effect") != "NONE":
        fail("physical evidence effect must remain NONE")

    solvers = master.get("solvers", [])
    baseline_solvers = baseline.get("solvers", [])
    if len(solvers) != 14 or len(baseline_solvers) != 14:
        fail("exactly 14 canonical solvers required")
    ids = [s["id"] for s in solvers]
    base_ids = [s["id"] for s in baseline_solvers]
    if ids != base_ids:
        fail("master solver order/identity must match frozen roadmap baseline")
    if len(set(ids)) != 14:
        fail("duplicate solver ID")

    all_wp = []
    for solver in solvers:
        upstream = solver.get("upstream", [])
        if any(x not in ids for x in upstream):
            fail(f"unknown upstream ID in {solver['id']}")
        wp = solver.get("work_packages", [])
        if len(wp) != 4:
            fail(f"{solver['id']} must have exactly four work packages")
        if not all(str(x).startswith(f"WP{i} ") for i, x in enumerate(wp, 1)):
            fail(f"{solver['id']} work-package numbering drift")
        if not solver.get("release_gate"):
            fail(f"{solver['id']} missing release gate")
        all_wp.extend(f"{solver['id']}-{i}" for i in range(1, 5))
    if len(all_wp) != 56 or len(set(all_wp)) != 56:
        fail("exactly 56 unique work-package slots required")

    paths = master.get("critical_paths", [])
    if len(paths) != 4:
        fail("exactly four critical paths required")
    for path in paths:
        seq = path.get("sequence", [])
        if not seq or seq[0] != "ULSH-01":
            fail(f"critical path {path.get('id')} must start with ULSH-01")
        if any(x not in ids for x in seq):
            fail(f"unknown solver in critical path {path.get('id')}")

    lanes = master.get("parallel_preparatory_lanes", [])
    if [x.get("lane") for x in lanes] != ["P1", "P2", "P3"]:
        fail("preparatory lane set/order drift")
    if master.get("next_primary_focus") != "ULSH-01":
        fail("ULSH-01 must remain the primary critical-path focus")

    text = PAGE.read_text(encoding="utf-8")
    for token in [
        "56 Arbeitspakete",
        "ULSH-01",
        "K1-D bleibt NOT RELEASED",
        "registry/2026-08-10_ULSH_MasterBuildOrder_v1.0.json",
    ]:
        if token not in text:
            fail(f"master dashboard missing token: {token}")
    if "fetch(src" not in text or "innerHTML" not in text:
        fail("master dashboard registry rendering contract missing")

    doc = DOC.read_text(encoding="utf-8")
    for sid in ids:
        if sid not in doc:
            fail(f"master document missing {sid}")

    firewall = FIREWALL.read_text(encoding="utf-8")
    for token in ["K1-D = NOT_RELEASED", "K1-E = NOT_ADMISSIBLE", "physical evidence effect = NONE", "CP01R1"]:
        if token not in firewall:
            fail(f"master firewall missing: {token}")

    if not WORKBENCH.exists():
        fail("Solver Workbench v1.1 must coexist with Master Build Order")

    hub = HUB.read_text(encoding="utf-8")
    for token in [
        "2026-08-10_ULSH_SolverDevelopmentProgram_v1.1.html",
        "2026-08-10_ULSH_MasterBuildOrder_v1.0.html",
        "56",
        "WORKBENCH + BUILD ORDER",
    ]:
        if token not in hub:
            fail(f"Solver Hub coexistence binding missing: {token}")

    readme = README.read_text(encoding="utf-8")
    for token in [
        "## Solver Workbench v1.1",
        "## Master Build Order v1.0",
        "2026-08-10_ULSH_MasterBuildOrder_v1.0.html",
        "56 Work Packages",
    ]:
        if token not in readme:
            fail(f"README planning-layer binding missing: {token}")

    print("PASS: ULSH Master Build Order v1.0")
    print("solvers=14 work_packages=56 critical_paths=4 lanes=3 primary=ULSH-01")
    print("workbench_v1.1=preserved baseline_v1.0=frozen")
    print("K1-D=NOT_RELEASED K1-E=NOT_ADMISSIBLE physical_evidence_effect=NONE")


if __name__ == "__main__":
    main()
