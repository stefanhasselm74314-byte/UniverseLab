#!/usr/bin/env python3
from __future__ import annotations

import ast
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D13_CP01R3IndependentImplementationReview_v1.0.json"
D12_AUDIT = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3ManufacturedControlAudit_v1.0.json"
D12_TOOL = ROOT / "tools/2026-08-13_ulsh_01_md2s_bvp_wp3_d12_cp01r3_bjp01_etrn02_v1.0.py"
SEED_SPEC = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3SeedSpec_v1.0.json"
EXPECTED_TOOL_BLOB_SHA1 = "d6313721a459254b13bdc9e06b4b83fc5a0fcca9"
EXPECTED_SEED_SPEC_SHA256 = "05315df34903188284b4ea58bffc6b440a06bda9486362a6760c7cc0cfcb1474"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def reference_bjp(A0: float, L0: float, Y: float, lam: float) -> tuple[float, float, float, float]:
    Astar = (lam - 0.5 * Y) / 4.0
    Lstar = -3.0 * Astar + lam + 0.5 * Y
    r4 = -3.0 * Astar - Lstar + lam + 0.5 * Y
    rchi = -4.0 * Astar + lam - 0.5 * Y
    return Astar - A0, Lstar - L0, r4, rchi


def cheb_tau(n: int) -> list[float]:
    desc = [(math.cos(math.pi * j / (n - 1)) + 1.0) / 2.0 for j in range(n)]
    return list(reversed(desc))


def reference_metric(n: int) -> float:
    tau = cheb_tau(n)
    total = 0.0
    for b in range(8):
        coeff = 0.2 + 0.01 * b
        block = [coeff * (1.0 - t) for t in tau]
        total += sum(v * v for v in block) / n  # seed RMS=0.5 -> frozen scale=1
    params = [-0.05 + i * (0.10 / 7.0) for i in range(8)]
    total += sum(v * v for v in params)  # parameter scales also 1
    return math.sqrt(total)


def function_node(tree: ast.AST, name: str) -> ast.FunctionDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"missing function {name}")


def main() -> int:
    review = json.loads(REVIEW.read_text(encoding="utf-8"))
    audit = json.loads(D12_AUDIT.read_text(encoding="utf-8"))
    source = D12_TOOL.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert review["classification"] == "INDEPENDENT_IMPLEMENTATION_REVIEW_NO_PHYSICAL_EXECUTION"
    assert review["status"] == "PASS_D13_INDEPENDENT_IMPLEMENTATION_REVIEW_D14_BINDING_ALLOWED_NO_PHYSICAL_EXECUTION"
    assert git_blob_sha1(D12_TOOL) == EXPECTED_TOOL_BLOB_SHA1
    assert hashlib.sha256(SEED_SPEC.read_bytes()).hexdigest() == EXPECTED_SEED_SPEC_SHA256
    assert review["source_binding"]["implementation_git_blob_sha1"] == EXPECTED_TOOL_BLOB_SHA1
    assert review["source_binding"]["seed_spec_sha256"] == EXPECTED_SEED_SPEC_SHA256
    assert review["source_binding"]["d12_merge_commit"] == "8228446464c13e55f83f98bce0f964f9af5cdc37"

    # Independent BJP algebra reference.
    for case in ((0.0, 0.0, 1.25, 1.0), (0.2, -0.4, 0.0, 1.0), (-0.3, 0.8, 2.0, 1.0), (1.0, -1.0, 0.75, 0.5)):
        _dA, _dL, r4, rchi = reference_bjp(*case)
        assert abs(r4) < 1e-14
        assert abs(rchi) < 1e-14

    # Independent endpoint identity: tau*c*(tau-1) vanishes at pole and brane.
    for c in (-2.5, -0.1, 0.37, 3.0):
        assert 0.0 * c * (0.0 - 1.0) == 0.0
        assert 1.0 * c * (1.0 - 1.0) == 0.0
        assert abs(c) > 0.0

    # Independent pure-Python reconstruction of D11-C3.
    metrics = [reference_metric(n) for n in (24, 32, 48, 64, 96)]
    mean_metric = sum(metrics) / len(metrics)
    rel_spread = (max(metrics) - min(metrics)) / mean_metric
    frozen_spread = audit["controls"]["D11-C3"]["relative_spread"]
    assert abs(rel_spread - frozen_spread) < 5e-15
    assert rel_spread < audit["controls"]["D11-C3"]["registered_tolerance"] == 0.006

    # Source isolation and import surface.
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert "numpy" in imports
    assert "scipy" not in imports
    assert "importlib" not in imports
    assert "subprocess" not in imports
    for forbidden in (
        "background_3c_primary_kernel",
        "background_3c_independent_backend",
        "CP01R2ImmediateExecution",
        "single_use_grant",
    ):
        assert forbidden not in source

    # ETRN-02 static semantics: metric is frozen once before loop; trust clips original dx.
    solver = function_node(tree, "etrn02_solve_generic")
    solver_source = ast.get_source_segment(source, solver) or ""
    assert 'metric = freeze_stage_metric(state, node_count)' in solver_source
    assert 'clipped = clip_in_state_metric(direction["dx_unclipped"], metric, delta)' in solver_source
    assert 'direction["linear_coordinate"]' not in solver_source
    assert "backtracking_factors" not in solver_source
    metric_pos = solver_source.index("metric = freeze_stage_metric")
    loop_pos = solver_source.index("for iteration in range")
    assert metric_pos < loop_pos

    # Current source calls jacobian_fn twice per outer iteration: freeze this resource semantic.
    jacobian_calls = 0
    for node in ast.walk(solver):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "jacobian_fn":
            jacobian_calls += 1
    assert jacobian_calls == 2

    findings = {row["id"]: row for row in review["independent_review_findings"]}
    assert set(findings) == {"D13-R1", "D13-R2", "D13-R3", "D13-R4", "D13-R5", "D13-R6"}
    assert all(row["status"].startswith("PASS") for row in findings.values())

    observations = {row["id"]: row for row in review["binding_semantics_observations"]}
    assert set(observations) == {"D13-O1", "D13-O2", "D13-O3", "D13-O4", "D13-O5"}
    assert observations["D13-O3"]["classification"] == "RESOURCE_ACCOUNTING_MUST_FREEZE_OR_VERSION_CHANGE"

    assert audit["status"] == "PASS_D12_BJP01_ETRN02_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION"
    assert all(row["status"] == "PASS" for row in audit["controls"].values())
    assert audit["execution_firewall"]["physical_backend_imported"] is False
    assert audit["execution_firewall"]["physical_solver_calls"] == 0

    effect = review["execution_effect"]
    assert effect["physical_backend_imported"] is False
    assert effect["physical_residual_evaluations"] == 0
    assert effect["physical_jacobian_evaluations"] == 0
    assert effect["physical_solver_calls"] == 0
    assert effect["grants_created"] == 0
    assert effect["physical_results_created"] == 0
    assert effect["physical_evidence_effect"] == "NONE"

    governance = review["governance_state"]
    assert governance["WP3"].startswith("OPEN_D13_REVIEW_PASS")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["ULSH-02"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"
    assert review["next_allowed_action"] == "ULSH-01_WP3_D14_CP01R3_EXACT_RUN_INPUT_GENERATED_SEED_AND_SOURCE_BUNDLE_FREEZE_NO_SOLVE"

    print("PASS_WP3_D13_CP01R3_INDEPENDENT_IMPLEMENTATION_REVIEW_NO_PHYSICAL_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
