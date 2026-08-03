#!/usr/bin/env python3
"""Validate the MD-2S parameter/flux contract and evaluate diagnostic invariants.

This tool is fail-closed and dependency-free. It validates the directed symbolic
contract and can compute winding and global-flux residuals for explicitly
provided profiles. It does not solve the MD-2S boundary-value problem and has
no evidence effect.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


class ContractError(ValueError):
    """Raised when a contract or diagnostic payload violates the schema."""


REQUIRED_GATE_VALUES = {
    "MF-006": "PARTIAL_STRUCTURAL_FREEZE",
    "R1.1": "BLOCKED",
    "MD2S_SOLVER": "NOT_AUTHORIZED",
    "TWO_JUNCTION_VERDICT": "NOT_EXECUTABLE",
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
}

REQUIRED_DIMENSIONS = {
    "kappa6_squared": "M^-4",
    "Lambda_geom": "M^2",
    "phi": "M^2",
    "U": "M^6",
    "lambda": "M^5",
    "Z_sigma": "M^3",
    "q_sigma": "M^-1",
    "q_ref": "M^-1",
    "A_chi": "M",
    "F_rchi": "M^2",
    "Q": "M^3",
    "Phi_F": "M",
    "X_sigma": "M^2",
    "Y_sigma": "M^5",
}


def _number(name: str, value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{name} must be numeric") from exc
    if not math.isfinite(result):
        raise ContractError(f"{name} must be finite")
    return result


def _integer(name: str, value: Any) -> int:
    if isinstance(value, bool):
        raise ContractError(f"{name} must be an integer")
    try:
        converted = int(value)
    except (TypeError, ValueError) as exc:
        raise ContractError(f"{name} must be an integer") from exc
    if float(converted) != _number(name, value):
        raise ContractError(f"{name} must be an integer")
    return converted


def load_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ContractError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return data


def validate_parameter_contract(contract: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if contract.get("schema") != "universelab.md2s-parameter-angular-flux-contract.v0.1":
        issues.append("unexpected parameter-contract schema")
    if contract.get("status") != "PARTIAL_STRUCTURAL_FREEZE":
        issues.append("parameter contract must remain PARTIAL_STRUCTURAL_FREEZE")
    if contract.get("evidence_effect") != "NONE":
        issues.append("evidence_effect must remain NONE")
    if contract.get("solver_authorized") is not False:
        issues.append("solver_authorized must remain false")

    dimensions = contract.get("dimensions")
    if not isinstance(dimensions, dict):
        issues.append("dimensions must be an object")
    else:
        for symbol, expected in REQUIRED_DIMENSIONS.items():
            if dimensions.get(symbol) != expected:
                issues.append(f"dimension mismatch for {symbol}: expected {expected}")

    winding = contract.get("winding_contract")
    if not isinstance(winding, dict):
        issues.append("winding_contract must be an object")
    else:
        if winding.get("single_valuedness") != "sigma(chi+Delta_chi)-sigma(chi)=2 pi N_sigma":
            issues.append("single-valued winding rule changed")
        if winding.get("gauge_invariant_d_chi") != "2 pi N_sigma/Delta_chi-q_sigma A_chi":
            issues.append("gauge-invariant winding combination changed")

    flux = contract.get("global_flux_contract")
    if not isinstance(flux, dict):
        issues.append("global_flux_contract must be an object")
    else:
        if flux.get("quantization") != "q_ref Phi_F=2 pi N_F":
            issues.append("global flux quantization form changed")
        if flux.get("q_ref_equals_q_sigma") != "OPEN_REQUIRES_MINIMAL_CHARGE_PROOF":
            issues.append("q_ref=q_sigma must remain open")

    gates = contract.get("freeze_effect")
    if not isinstance(gates, dict):
        issues.append("freeze_effect must be an object")
    else:
        for gate, expected in REQUIRED_GATE_VALUES.items():
            if gates.get(gate) != expected:
                issues.append(f"{gate} must remain {expected}")
    return issues


def validate_dependency_graph(graph: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    if graph.get("schema") != "universelab.md2s-symbolic-dependency-graph.v0.1":
        issues.append("unexpected dependency-graph schema")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or not nodes:
        return ["nodes must be a non-empty list"], []
    if not isinstance(edges, list):
        return ["edges must be a list"], []

    node_map: dict[str, dict[str, Any]] = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            issues.append(f"nodes[{index}] must be an object")
            continue
        node_id = node.get("id")
        if not isinstance(node_id, str) or not node_id:
            issues.append(f"nodes[{index}] has invalid id")
            continue
        if node_id in node_map:
            issues.append(f"duplicate node id: {node_id}")
        node_map[node_id] = node

    adjacency: dict[str, list[str]] = {node_id: [] for node_id in node_map}
    indegree: dict[str, int] = {node_id: 0 for node_id in node_map}
    edge_keys: set[tuple[str, str]] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            issues.append(f"edges[{index}] must be an object")
            continue
        source = edge.get("from")
        target = edge.get("to")
        if source not in node_map or target not in node_map:
            issues.append(f"edges[{index}] references an unknown node")
            continue
        key = (str(source), str(target))
        if key in edge_keys:
            issues.append(f"duplicate edge: {source}->{target}")
            continue
        edge_keys.add(key)
        adjacency[str(source)].append(str(target))
        indegree[str(target)] += 1

    queue = sorted(node_id for node_id, degree in indegree.items() if degree == 0)
    topological_order: list[str] = []
    while queue:
        current = queue.pop(0)
        topological_order.append(current)
        for target in sorted(adjacency[current]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()

    if len(topological_order) != len(node_map):
        issues.append("dependency graph contains a directed cycle")
    if graph.get("directed_acyclic") is not True:
        issues.append("directed_acyclic declaration must be true")

    blockers = graph.get("blocking_nodes_for_R1_1")
    if not isinstance(blockers, list) or not blockers:
        issues.append("blocking_nodes_for_R1_1 must be a non-empty list")
        blockers = []
    else:
        for blocker in blockers:
            if blocker not in node_map:
                issues.append(f"unknown R1.1 blocker: {blocker}")
            elif node_map[blocker].get("status") in {
                "DERIVED", "FROZEN", "RELEASED", "STRUCTURALLY_FROZEN"
            }:
                issues.append(f"R1.1 blocker is unexpectedly closed: {blocker}")

    governance = graph.get("governance")
    if not isinstance(governance, dict):
        issues.append("graph governance must be an object")
    else:
        for gate, expected in REQUIRED_GATE_VALUES.items():
            if governance.get(gate) != expected:
                issues.append(f"graph governance {gate} must remain {expected}")

    return issues, topological_order


def winding_quantities(*, delta_chi: float, n_sigma: int, q_sigma: float,
                       a_chi: float, radius_l: float, z_sigma: float) -> dict[str, float]:
    delta_chi = _number("Delta_chi", delta_chi)
    n_sigma = _integer("N_sigma", n_sigma)
    q_sigma = _number("q_sigma", q_sigma)
    a_chi = _number("A_chi", a_chi)
    radius_l = _number("L", radius_l)
    z_sigma = _number("Z_sigma", z_sigma)
    if delta_chi <= 0:
        raise ContractError("Delta_chi must be strictly positive")
    if radius_l <= 0:
        raise ContractError("L must be strictly positive")
    if z_sigma < 0:
        raise ContractError("Z_sigma must be non-negative")

    gradient = 2.0 * math.pi * n_sigma / delta_chi
    d_chi = gradient - q_sigma * a_chi
    x_sigma = d_chi * d_chi / (radius_l * radius_l)
    return {
        "partial_chi_sigma": gradient,
        "d_chi": d_chi,
        "X_sigma": x_sigma,
        "Y_sigma": z_sigma * x_sigma,
    }


def _trapezoid(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ContractError("each flux segment requires equal arrays with at least two samples")
    total = 0.0
    for index in range(len(x) - 1):
        step = x[index + 1] - x[index]
        if step <= 0:
            raise ContractError("segment r samples must be strictly increasing")
        total += 0.5 * step * (y[index] + y[index + 1])
    return total


def flux_quantities(*, delta_chi: float, q_ref: float, n_flux: int,
                    segments: list[dict[str, Any]]) -> dict[str, Any]:
    delta_chi = _number("Delta_chi", delta_chi)
    q_ref = _number("q_ref", q_ref)
    n_flux = _integer("N_flux", n_flux)
    if delta_chi <= 0:
        raise ContractError("Delta_chi must be strictly positive")
    if q_ref == 0:
        raise ContractError("q_ref must be nonzero for a quantization residual")
    if not isinstance(segments, list) or not segments:
        raise ContractError("segments must be a non-empty list")

    regional_integrals: list[float] = []
    for segment_index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ContractError(f"segments[{segment_index}] must be an object")
        r = [_number(f"segments[{segment_index}].r", value) for value in segment.get("r", [])]
        a = [_number(f"segments[{segment_index}].A", value) for value in segment.get("A", [])]
        radius = [_number(f"segments[{segment_index}].L", value) for value in segment.get("L", [])]
        z_f = [_number(f"segments[{segment_index}].Z_F", value) for value in segment.get("Z_F", [])]
        q_value = _number(f"segments[{segment_index}].Q", segment.get("Q"))
        if not (len(r) == len(a) == len(radius) == len(z_f)):
            raise ContractError(f"segments[{segment_index}] arrays must have equal length")
        if any(value <= 0 for value in radius):
            raise ContractError(f"segments[{segment_index}].L must be strictly positive")
        if any(value <= 0 for value in z_f):
            raise ContractError(f"segments[{segment_index}].Z_F must be strictly positive")
        integrand = [
            q_value * radius_value * math.exp(-4.0 * a_value) / z_value
            for a_value, radius_value, z_value in zip(a, radius, z_f)
        ]
        regional_integrals.append(_trapezoid(r, integrand))

    phi_f = delta_chi * sum(regional_integrals)
    residual = q_ref * phi_f - 2.0 * math.pi * n_flux
    return {
        "regional_integrals": regional_integrals,
        "Phi_F": phi_f,
        "R_flux": residual,
        "quantized_target": 2.0 * math.pi * n_flux,
    }


def rescale_angular_payload(payload: dict[str, Any], c: float) -> dict[str, Any]:
    c = _number("c", c)
    if c <= 0:
        raise ContractError("angular rescaling c must be strictly positive")
    result = json.loads(json.dumps(payload))
    result["Delta_chi"] = _number("Delta_chi", result["Delta_chi"]) * c
    result["A_chi"] = _number("A_chi", result["A_chi"]) / c
    result["L"] = _number("L", result["L"]) / c
    for segment in result.get("segments", []):
        segment["L"] = [_number("segment.L", value) / c for value in segment["L"]]
    return result


def evaluate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ContractError("diagnostic input must be an object")
    winding = winding_quantities(
        delta_chi=payload.get("Delta_chi"),
        n_sigma=payload.get("N_sigma"),
        q_sigma=payload.get("q_sigma"),
        a_chi=payload.get("A_chi"),
        radius_l=payload.get("L"),
        z_sigma=payload.get("Z_sigma"),
    )
    flux = flux_quantities(
        delta_chi=payload.get("Delta_chi"),
        q_ref=payload.get("q_ref"),
        n_flux=payload.get("N_flux"),
        segments=payload.get("segments"),
    )
    return {
        "schema": "universelab.md2s-parameter-flux-evaluation.v0.1",
        "status": "DIAGNOSTIC_ONLY",
        "evidence_effect": "NONE",
        "winding": winding,
        "flux": flux,
        "gates": REQUIRED_GATE_VALUES,
    }


def validate_files(contract_path: Path, graph_path: Path) -> dict[str, Any]:
    contract = load_json(contract_path)
    graph = load_json(graph_path)
    issues = validate_parameter_contract(contract)
    graph_issues, order = validate_dependency_graph(graph)
    issues.extend(graph_issues)
    if issues:
        raise ContractError("; ".join(issues))
    return {
        "status": "PASS",
        "evidence_effect": "NONE",
        "parameter_schema": contract["schema"],
        "graph_schema": graph["schema"],
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "topological_order": order,
        "R1_1_blockers": graph["blocking_nodes_for_R1_1"],
        "gates": REQUIRED_GATE_VALUES,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contract",
        type=Path,
        default=root / "registry/2026-08-03_MD2S_ParameterAngularFluxContract_v0.1.json",
    )
    parser.add_argument(
        "--graph",
        type=Path,
        default=root / "registry/2026-08-03_MD2S_SymbolicDependencyGraph_v0.1.json",
    )
    parser.add_argument("--input", type=Path, help="optional diagnostic winding/flux JSON")
    parser.add_argument("--output", type=Path, help="optional output JSON")
    args = parser.parse_args()

    try:
        result = validate_files(args.contract, args.graph)
        if args.input:
            result["diagnostic_evaluation"] = evaluate_payload(load_json(args.input))
    except ContractError as exc:
        parser.error(str(exc))

    rendered = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
