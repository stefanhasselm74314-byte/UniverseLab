#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-08-07_ULSH_SolverDevelopmentProgram_v1.0.json"
MANIFEST = ROOT / "solver-hub-manifest.json"
DASHBOARD = ROOT / "solver-development.html"
HUB = ROOT / "solver-hub.html"
README = ROOT / "README_SOLVER_HUB.md"

EXPECTED_IDS = [f"ULSH-{i:02d}" for i in range(1, 15)]
REQUIRED_SECTIONS = [
    "## Ziel",
    "## Aktueller Stand",
    "## Upstream",
    "## Fehlende Theorie-/Vertragsarbeit",
    "## Implementierungspakete",
    "## Kontrollen",
    "## Pflicht-Outputs",
    "## Freigabegate",
    "## Downstream",
]
ALLOWED_READINESS = {"DEFINED", "PARTIAL", "MISSING", "BLOCKED", "NOT_APPLICABLE"}
DIMENSIONS = {
    "derivation",
    "equation_set",
    "boundary_or_initial_data",
    "numerical_method",
    "control_validation",
    "physical_release",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def main() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if registry.get("status") != "PLANNING_BASELINE_NO_EXECUTION_EFFECT":
        fail("roadmap registry must have no execution effect")
    gov = registry.get("governance", {})
    if gov.get("K1-D") != "NOT_RELEASED" or gov.get("K1-E") != "NOT_ADMISSIBLE":
        fail("K1 governance drift")
    if gov.get("physical_evidence_effect") != "NONE":
        fail("roadmap registry must not create physical evidence")
    if "progress_percent" in REGISTRY.read_text(encoding="utf-8"):
        fail("pseudo-precise progress percentages are forbidden")

    solvers = registry.get("solvers", [])
    ids = [s.get("id") for s in solvers]
    if ids != EXPECTED_IDS:
        fail(f"expected ordered canonical IDs {EXPECTED_IDS}, got {ids}")
    if len({s.get("module_id") for s in solvers}) != 14:
        fail("module IDs must be unique")

    by_id = {s["id"]: s for s in solvers}
    for solver in solvers:
        readiness = solver.get("readiness", {})
        if set(readiness) != DIMENSIONS:
            fail(f"readiness dimensions drift for {solver['id']}")
        if not set(readiness.values()) <= ALLOWED_READINESS:
            fail(f"invalid readiness value for {solver['id']}")
        if readiness["physical_release"] != "BLOCKED":
            fail(f"physical release must remain BLOCKED for {solver['id']}")
        if not solver.get("primary_blockers"):
            fail(f"missing primary blockers for {solver['id']}")
        if not solver.get("release_gate"):
            fail(f"missing release gate for {solver['id']}")
        for dep in solver.get("upstream", []) + solver.get("downstream", []):
            if dep not in by_id:
                fail(f"unknown dependency {dep} in {solver['id']}")
        path = ROOT / solver["roadmap_path"]
        if not path.is_file():
            fail(f"missing roadmap file {path}")
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if section not in text:
                fail(f"{solver['id']} roadmap missing section: {section}")

    # Upstream/downstream edges must be reciprocal.
    for solver in solvers:
        sid = solver["id"]
        for upstream in solver.get("upstream", []):
            if sid not in by_id[upstream].get("downstream", []):
                fail(f"non-reciprocal edge {upstream} -> {sid}")
        for downstream in solver.get("downstream", []):
            if sid not in by_id[downstream].get("upstream", []):
                fail(f"non-reciprocal edge {sid} -> {downstream}")

    # Dependency graph must remain acyclic.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            fail(f"dependency cycle detected at {node}")
        if node in visited:
            return
        visiting.add(node)
        for nxt in by_id[node].get("downstream", []):
            visit(nxt)
        visiting.remove(node)
        visited.add(node)

    for sid in EXPECTED_IDS:
        visit(sid)

    dev = manifest.get("development_program", {})
    if dev.get("roadmap_count") != 14:
        fail("hub manifest roadmap count drift")
    if dev.get("registry") != REGISTRY.relative_to(ROOT).as_posix():
        fail("hub manifest registry path drift")
    if dev.get("dashboard") != "solver-development.html":
        fail("hub manifest dashboard drift")
    if manifest.get("governance", {}).get("physical_evidence_effect") != "NONE":
        fail("hub manifest evidence drift")

    dashboard = DASHBOARD.read_text(encoding="utf-8")
    hub = HUB.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    if REGISTRY.name not in dashboard:
        fail("dashboard is not bound to the registry")
    if "solver-development.html" not in hub:
        fail("Solver Hub does not link the development dashboard")
    if "14 Solver" not in hub or "14 Solver" not in dashboard:
        fail("14-solver program not visibly declared")
    if "Planungsstatus != Solverfreigabe" not in readme:
        fail("README planning firewall missing")

    print("PASS: ULSH Solver Development Program v1.0")
    print("solvers=14 roadmaps=14 graph=acyclic physical_release=BLOCKED K1-D=NOT_RELEASED K1-E=NOT_ADMISSIBLE")


if __name__ == "__main__":
    main()
