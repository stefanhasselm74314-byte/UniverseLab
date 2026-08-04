#!/usr/bin/env python3
"""Regression and fail-closed tests for Background-3C2 dual backend."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c2_v0.1.py"
DUAL_GATE_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_dual_backend_gate_v0.1.py"
INDEPENDENT_PATH = ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_independent_backend_v0.1.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


VALIDATOR = load_module("background3c2_validator_test", VALIDATOR_PATH)
INDEPENDENT = load_module("background3c2_independent_test", INDEPENDENT_PATH)


def expect_failure(function, phrase: str) -> None:
    try:
        function()
    except (VALIDATOR.ContractError, RuntimeError, ValueError) as exc:
        assert phrase in str(exc), (phrase, str(exc))
        return
    raise AssertionError(f"expected failure containing: {phrase}")


def test_repository_contract_passes() -> None:
    result = VALIDATOR.validate()
    assert result["status"] == "PASS"
    assert result["audit"]["status"] == "PASS_DUAL_BACKEND_CONTROL_AUDIT_NO_NONLINEAR_EXECUTION"
    assert result["audit"]["primary_newton_call_count"] == 0
    assert result["audit"]["independent_shooting_jacobian_call_count"] == 0
    assert result["audit"]["independent_integration_call_count"] == 6
    assert result["execution_authorized"] is False
    assert result["solver_executed"] is False
    assert result["physical_evidence_effect"] == "NONE"


def test_pole_series_and_rhs_are_finite() -> None:
    payload = {
        "model_parameters_ordered": {
            "Lambda_hat": "1", "mhat_phi_sq": "1", "a_F": "1/4",
            "lambda_hat": "1", "z_sigma_hat": "1", "q_hat": "1"
        }
    }
    model = INDEPENDENT.model_from_payload(payload, control_a_F=True)
    shooting = INDEPENDENT.control_shooting_vector()
    state = INDEPENDENT.pole_initial_state(1.0e-3, 0.0, 0.0, shooting[1], shooting[7], model)
    rhs = INDEPENDENT.rhs_x(1.0e-3, state, shooting[1], shooting[7], model)
    assert np.all(np.isfinite(state))
    assert np.all(np.isfinite(rhs))
    assert abs(INDEPENDENT.radial_constraint(state, shooting[1], shooting[7], model)) < 1.0e-10


def test_rank_and_source_overclaims_are_rejected() -> None:
    contract = VALIDATOR.load_json(VALIDATOR.INDEPENDENT_CONTRACT)
    changed = copy.deepcopy(contract)
    changed["source"]["imports_primary_residual"] = True
    expect_failure(lambda: VALIDATOR.validate_independent_contract(changed), "independence overclaim")

    dual = VALIDATOR.load_json(VALIDATOR.DUAL_CONTRACT)
    changed_dual = copy.deepcopy(dual)
    changed_dual["audit_execution_limits"]["independent_shooting_jacobian_calls"] = 1
    expect_failure(lambda: VALIDATOR.validate_dual_contract(changed_dual), "shooting Jacobian limit")


def test_execution_and_physical_overclaims_are_rejected() -> None:
    dual = VALIDATOR.load_json(VALIDATOR.DUAL_CONTRACT)
    changed = copy.deepcopy(dual)
    changed["execution_authorization"]["authorized"] = True
    expect_failure(lambda: VALIDATOR.validate_dual_contract(changed), "authorization overclaim")

    changed = copy.deepcopy(dual)
    changed["gate_state"]["physical_background"] = "ESTABLISHED"
    expect_failure(lambda: VALIDATOR.validate_dual_contract(changed), "background overclaim")


def test_run_and_direct_invocation_are_denied() -> None:
    for path, extra in ((DUAL_GATE_PATH, ["run", "--json"]), (INDEPENDENT_PATH, [])):
        process = subprocess.run([sys.executable, str(path), *extra], cwd=ROOT, capture_output=True, text=True, check=False)
        assert process.returncode == 73, process.stdout + process.stderr
    assert not VALIDATOR.FUTURE_GRANT.exists()
    assert not VALIDATOR.OUTPUT_ROOT.exists()


def test_centered_fd_jacobian_not_used_by_audit() -> None:
    assert INDEPENDENT.SHOOTING_JACOBIAN_CALL_COUNT == 0


def main() -> int:
    test_repository_contract_passes()
    test_pole_series_and_rhs_are_finite()
    test_rank_and_source_overclaims_are_rejected()
    test_execution_and_physical_overclaims_are_rejected()
    test_run_and_direct_invocation_are_denied()
    test_centered_fd_jacobian_not_used_by_audit()
    print("PASS: Background-3C2 independent dual-backend regression tests")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
