#!/usr/bin/env python3
"""Fail-closed audit and execution gate for Background-3C primary implementation.

`audit` performs deterministic algebra and contract QA only. `run` is denied
before any Newton iteration while the append-only v0.2 grant artifact is absent.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import inspect
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
KERNEL_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.1.py"
METHOD_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3APreregistrationContract_v0.1.json"
TOPOLOGY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"
ASSEMBLY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json"
RUN_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BRunInputFreezeContract_v0.2.json"
SEED_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3BSeedSpecification_v0.1.json"
AUTH_DENIED_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.1.json"
FUTURE_GRANT_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
RESULT_SCHEMA_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResultSchema_v0.1.json"
RESOURCE_POLICY_PATH = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CResourcePolicy_v0.1.json"
EXIT_NOT_AUTHORIZED = 73
EXPECTED_RUN_HASH = "0ecf1a2ecffb7b3b768a86ba889135982edcc118910085461760e66bc9b90302"
EXPECTED_KERNEL_BLOB = "d451be299d0ca93a7dc4587782675b7adab5cfd7"


class GateError(RuntimeError):
    pass


class AuthorizationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def load_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing required artifact: {path.relative_to(ROOT)}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise GateError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root must be object: {path.relative_to(ROOT)}")
    return value


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_kernel():
    spec = importlib.util.spec_from_file_location("background3c_primary_kernel_v01", KERNEL_PATH)
    if spec is None or spec.loader is None:
        raise GateError("unable to import primary kernel")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def verify_contract_chain() -> dict[str, Any]:
    method = load_json(METHOD_PATH)
    topology = load_json(TOPOLOGY_PATH)
    assembly = load_json(ASSEMBLY_PATH)
    run = load_json(RUN_PATH)
    seeds = load_json(SEED_PATH)
    authorization = load_json(AUTH_DENIED_PATH)
    result_schema = load_json(RESULT_SCHEMA_PATH)
    resources = load_json(RESOURCE_POLICY_PATH)

    payload = run["frozen_run_payload"]
    require(payload["run_id"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1", "run id drift")
    require(run["frozen_run_payload_sha256"] == EXPECTED_RUN_HASH, "recorded run hash drift")
    require(canonical_sha256(payload) == EXPECTED_RUN_HASH, "recomputed run hash drift")
    require(payload["topological_sector_ordered"] == {"N_F": 1, "N_sigma": 1, "m_sigma": 1}, "topological sector drift")
    require(topology["canonical_effective_topological_input"]["ordered_vector"] == ["N_F", "N_sigma", "m_sigma"], "topology contract drift")
    require(assembly["canonical_assembly"]["regional_node_counts"] == [24, 32, 48, 64, 96], "assembly node schedule drift")
    require(assembly["canonical_assembly"]["degree_rule"] == "degree=node_count-1", "degree rule drift")
    require(assembly["counting_audit"]["total_unknowns"] == assembly["counting_audit"]["total_residuals"] == "8*N+8", "square count drift")
    require(method["primary_discretization"]["regional_node_counts"] == [24, 32, 48, 64, 96], "method node schedule drift")
    require(method["nonlinear_method"]["method"] == "DAMPED_NEWTON_TRUST_REGION", "nonlinear method drift")
    require(method["nonlinear_method"]["linear_solver"] == "rank-revealing QR primary with SVD diagnostic", "linear solver drift")
    require(method["normalization_and_norms"]["bulk_component_scaling"] == "unit dimensionless scaling; every component also reported separately", "bulk scaling drift")
    require(method["normalization_and_norms"]["boundary_component_scaling"] == "unit dimensionless scaling; every component also reported separately", "boundary scaling drift")
    require(seeds["seed_set_id"] == payload["seed_set_id"], "seed set identity drift")
    require(seeds["seed_count"] == 7, "seed count drift")
    require(authorization["status"] == "NOT_GRANTED" and authorization["authorized"] is False, "authorization denial drift")
    require(authorization["required_future_grant_artifact"] == str(FUTURE_GRANT_PATH.relative_to(ROOT)), "future grant path drift")
    require(not FUTURE_GRANT_PATH.exists(), "unexpected execution grant artifact present")
    require(result_schema["status"] == "FROZEN_NOT_INSTANTIATED", "result schema status drift")
    require(result_schema["current_state"]["result_artifact_created"] is False, "result artifact overclaim")
    require(resources["status"] == "FROZEN_EXECUTION_NOT_AUTHORIZED", "resource policy status drift")
    require(resources["execution_environment"]["network_access"] is False, "network access opened")
    require(resources["execution_environment"]["randomness"] is False, "randomness opened")
    return {
        "method": method,
        "assembly": assembly,
        "run": run,
        "payload": payload,
        "authorization": authorization,
        "result_schema": result_schema,
        "resources": resources,
    }


def verify_kernel_defaults(kernel: Any, method: dict[str, Any]) -> dict[str, Any]:
    signature = inspect.signature(kernel.damped_newton)
    defaults = {name: parameter.default for name, parameter in signature.parameters.items()}
    expected = {
        "maximum_iterations": method["nonlinear_method"]["maximum_newton_iterations_per_mesh"],
        "maximum_backtracking_steps": method["nonlinear_method"]["maximum_backtracking_steps"],
        "armijo_parameter": method["nonlinear_method"]["armijo_parameter"],
        "minimum_step_fraction": method["nonlinear_method"]["minimum_step_fraction"],
        "trust_radius_initial": method["nonlinear_method"]["trust_region_initial_radius"],
        "trust_radius_minimum": method["nonlinear_method"]["trust_region_minimum_radius"],
        "stagnation_window_iterations": method["nonlinear_method"]["stagnation_window_iterations"],
        "stagnation_relative_improvement_floor": method["nonlinear_method"]["stagnation_relative_improvement_floor"],
    }
    for key, value in expected.items():
        require(defaults[key] == value, f"kernel nonlinear default drift: {key}")
    require(kernel.FIELD_ORDER == ("u_A", "u_ell", "u_varphi", "u_g"), "field order drift")
    require(kernel.PARAMETER_ORDER == (
        "varphi_N_0", "q_N", "A_S_0", "varphi_S_0", "q_S", "rho_N", "rho_S", "k4"
    ), "parameter order drift")
    require(kernel.BOUNDARY_ORDER == (
        "R_A", "R_ell", "R_varphi", "R_patch", "R_4D", "R_chi", "R_scalar", "R_gauge"
    ), "boundary order drift")
    return expected


def audit() -> dict[str, Any]:
    chain = verify_contract_chain()
    kernel = load_kernel()
    require(kernel.NEWTON_CALL_COUNT == 0, "Newton executed during import")
    defaults = verify_kernel_defaults(kernel, chain["method"])

    node_count = 24
    grid = kernel.chebyshev_lobatto(node_count)
    derivative_errors: dict[str, float] = {}
    for power in range(8):
        values = grid.tau**power
        exact = np.zeros_like(values) if power == 0 else power * grid.tau ** (power - 1)
        derivative_errors[str(power)] = float(np.max(np.abs(grid.D @ values - exact)))
    require(max(derivative_errors.values()) <= 5.0e-12, "Chebyshev differentiation audit failed")
    require(grid.degree == node_count - 1, "node-count to degree drift")
    require(kernel.state_size(node_count) == 8 * node_count + 8, "state size drift")

    model = kernel.model_from_payload(chain["payload"], control_a_F=True)
    sector = kernel.sector_from_payload(chain["payload"])
    seed = kernel.control_seed_state(node_count)
    residual, metadata = kernel.residual(seed, node_count, model, sector)
    require(residual.size == kernel.state_size(node_count), "residual size not square")
    bulk = residual[:-8]
    y0 = (8.0 - 2.0 * math.sqrt(10.0)) / 3.0
    expected_boundary = np.asarray([
        0.0, 0.0, 0.0, 0.0,
        1.0 + 9.0 * y0 / 8.0,
        1.0 - 9.0 * y0 / 8.0,
        0.0,
        -3.0 * y0 / 2.0,
    ])
    require(float(np.max(np.abs(bulk))) <= 1.0e-9, "control seed bulk assembly audit failed")
    require(float(np.max(np.abs(metadata["boundary"] - expected_boundary))) <= 5.0e-11, "control seed boundary assembly audit failed")
    constraint_inf = float(max(
        np.max(np.abs(metadata["north"].constraint)),
        np.max(np.abs(metadata["south"].constraint)),
    ))
    require(constraint_inf <= 1.0e-10, "control seed constraint audit failed")
    require(len(kernel.seven_seeds(node_count)) == 7, "seven-seed construction drift")

    test_matrix = np.asarray([[2.0, 1.0], [1.0, 3.0]])
    test_rhs = np.asarray([1.0, 2.0])
    rrqr_solution, rrqr_diagnostics = kernel.rrqr_step(test_matrix, test_rhs)
    require(np.max(np.abs(rrqr_solution - np.linalg.solve(test_matrix, test_rhs))) <= 1.0e-14, "RRQR solve audit failed")
    require(rrqr_diagnostics["rrqr_rank"] == 2, "RRQR rank audit failed")
    require(kernel.NEWTON_CALL_COUNT == 0, "Newton executed during audit")

    output_root = ROOT / "artifacts/hzt-m0/md2s/background3c" / chain["payload"]["run_id"]
    require(not output_root.exists(), "result output path exists before authorization")
    return {
        "status": "PASS_PRIMARY_IMPLEMENTATION_AUDIT_NO_SOLVER_EXECUTION",
        "run_id": chain["payload"]["run_id"],
        "run_payload_sha256": EXPECTED_RUN_HASH,
        "kernel_git_blob_sha": EXPECTED_KERNEL_BLOB,
        "node_count": node_count,
        "polynomial_degree": grid.degree,
        "state_and_residual_size": residual.size,
        "derivative_error_max": max(derivative_errors.values()),
        "control_bulk_raw_inf": float(np.max(np.abs(bulk))),
        "control_boundary_raw": dict(zip(kernel.BOUNDARY_ORDER, map(float, metadata["boundary"]))),
        "control_constraint_raw_inf": constraint_inf,
        "rrqr_rank_test": rrqr_diagnostics["rrqr_rank"],
        "newton_call_count": kernel.NEWTON_CALL_COUNT,
        "kernel_defaults": defaults,
        "authorization_status": chain["authorization"]["status"],
        "independent_backend": "NOT_PRESENT_BLOCKING",
        "result_artifact_created": False,
        "physical_evidence_effect": "NONE",
    }


def require_execution_authorization() -> dict[str, Any]:
    denial = load_json(AUTH_DENIED_PATH)
    if denial.get("authorized") is not False or denial.get("status") != "NOT_GRANTED":
        raise AuthorizationError("immutable v0.1 denial artifact drift")
    if not FUTURE_GRANT_PATH.is_file():
        raise AuthorizationError("BACKGROUND-3C execution authorization v0.2 is absent")
    grant = load_json(FUTURE_GRANT_PATH)
    if grant.get("authorized") is not True or grant.get("status") != "GRANTED_QUARANTINED_DIAGNOSTIC":
        raise AuthorizationError("future execution grant is not valid")
    raise AuthorizationError("BACKGROUND-3C1 primary implementation is not an execution package; independent backend and a new runner version are required")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("audit", "run"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "run":
            require_execution_authorization()
            raise GateError("unreachable execution path")
        payload = audit()
    except AuthorizationError as exc:
        payload = {"status": "NOT_AUTHORIZED", "error": str(exc), "solver_executed": False, "result_artifact_created": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"NOT AUTHORIZED: {exc}")
        return EXIT_NOT_AUTHORIZED
    except (GateError, ValueError, KeyError, FloatingPointError) as exc:
        payload = {"status": "FAIL", "error": str(exc), "solver_executed": False}
        print(json.dumps(payload, indent=2, sort_keys=True) if args.json else f"FAIL: {exc}")
        return 1
    print(json.dumps(payload, indent=2, sort_keys=True) if args.json else payload["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
