#!/usr/bin/env python3
"""SIM-70 adversarial pre-execution QA for CP01R4.

No physical BVP solve is permitted by this test.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


MMS = load_module(
    "sim70_cp01r4_mms",
    ROOT / "ulsh/ULSH-01/C-PHYS/2026-09-28_ULSH01_SIM70_CP01R4_ManufacturedSolutionQA_v0.1.py",
)
ENV = load_module(
    "sim70_cp01r4_env",
    ROOT / "tools/2026-09-28_ULSH01_SIM70_CP01R4_EnvironmentHash_v0.1.py",
)
PREFLIGHT = load_module(
    "sim70_cp01r4_initial",
    ROOT / "tools/2026-09-28_ULSH01_SIM70_CP01R4_InitialStatePreflight_v0.1.py",
)
BACKEND = load_module(
    "sim70_cp01r4_primary",
    ROOT / "tools/2026-08-04_hzt_m0_s6_c_phys_m1_background_3c_primary_kernel_v0.2.py",
)


def test_manufactured_solution_reference():
    result = MMS.run_mms()
    assert result["status"] == "PASS_QA_ONLY", result
    assert result["manufactured_solution_result"] is True
    assert result["newton_call_count_delta"] == 0
    assert result["physical_interpretation"] == "NONE"
    assert result["canonical_effect"] == "NONE"

    low = result["low_order_case"]
    high = result["high_order_resolution_case"]
    assert [x["node_count"] for x in low] == [24, 32, 48, 64, 96]
    assert [x["node_count"] for x in high] == [24, 32, 48, 64, 96]


def test_environment_hash_is_deterministic_and_mutation_sensitive():
    first = ENV.build_packet(ROOT, strict=True)
    second = ENV.build_packet(ROOT, strict=True)
    assert first["environment_hash_sha256"] == second["environment_hash_sha256"]
    assert len(first["environment_hash_sha256"]) == 64
    assert first["attestation"] == second["attestation"]

    mutated = copy.deepcopy(first["attestation"])
    original_count = mutated["hardware"]["logical_cpu_count"]
    mutated["hardware"]["logical_cpu_count"] = (
        1 if original_count is None else int(original_count) + 1
    )
    assert ENV.canonical_sha256(mutated) != first["environment_hash_sha256"]

    att = first["attestation"]
    assert att["dependencies"]["numpy"]["version"] == "2.1.3"
    assert att["dependencies"]["scipy"]["version"] == "1.14.1"
    assert att["dependencies"]["sympy"]["version"] == "1.13.3"
    assert att["dependencies"]["mpmath"]["version"] == "1.3.0"
    assert att["hardware"]["cpu_model"] not in {"", "UNKNOWN"}
    assert not str(att["hardware"]["cpu_model"]).isdigit()
    assert att["thread_environment"] == {
        "MKL_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
    }
    assert att["isolation_attestation_flags"]["network_isolated"] is True
    assert att["isolation_attestation_flags"]["gpu_disabled"] is True
    assert att["physical_interpretation"] == "NONE"
    assert att["canonical_effect"] == "NONE"


def test_initial_state_preflight_rejects_corruption_without_solver():
    before = int(getattr(BACKEND, "NEWTON_CALL_COUNT"))
    valid = BACKEND.seven_seeds(24)[0]

    ok = PREFLIGHT.validate_initial_state(BACKEND, valid, 24)
    assert ok["pass"] is True, ok

    malformed = PREFLIGHT.validate_initial_state(BACKEND, valid[:-1], 24)
    assert malformed["pass"] is False
    assert "STATE_SHAPE_INVALID" in malformed["reasons"]

    nonfinite_state = valid.copy()
    nonfinite_state[0] = np.nan
    nonfinite = PREFLIGHT.validate_initial_state(BACKEND, nonfinite_state, 24)
    assert nonfinite["pass"] is False
    assert "NONFINITE_INITIAL_STATE" in nonfinite["reasons"]

    complex_state = valid.astype(complex)
    complex_state[0] += 1j
    complex_result = PREFLIGHT.validate_initial_state(BACKEND, complex_state, 24)
    assert complex_result["pass"] is False
    assert "COMPLEX_INITIAL_STATE_FORBIDDEN" in complex_result["reasons"]

    bad_rho = valid.copy()
    _, params = BACKEND.unpack_state(bad_rho, 24)
    params[5] = 0.0
    rho_result = PREFLIGHT.validate_initial_state(BACKEND, bad_rho, 24)
    assert rho_result["pass"] is False
    assert "RHO_N_BELOW_MARGIN" in rho_result["reasons"]

    bad_ell = valid.copy()
    regions, _ = BACKEND.unpack_state(bad_ell, 24)
    regions[0][1][:] = -2.0
    ell_result = PREFLIGHT.validate_initial_state(BACKEND, bad_ell, 24)
    assert ell_result["pass"] is False
    assert "ELL_N_BELOW_MARGIN" in ell_result["reasons"]

    for result in (malformed, nonfinite, complex_result, rho_result, ell_result):
        assert result["residual_evaluated"] is False
        assert result["jacobian_evaluated"] is False
        assert result["solver_executed"] is False

    after = int(getattr(BACKEND, "NEWTON_CALL_COUNT"))
    assert after == before == 0


if __name__ == "__main__":
    test_manufactured_solution_reference()
    test_environment_hash_is_deterministic_and_mutation_sensitive()
    test_initial_state_preflight_rejects_corruption_without_solver()
    print("SIM-70 CP01R4 pre-execution numerical QA: PASS (MMS + ENV HASH + INITIAL FIREWALL; NO SOLVER)")
