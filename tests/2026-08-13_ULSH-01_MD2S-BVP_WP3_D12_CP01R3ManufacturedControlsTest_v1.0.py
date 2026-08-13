#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/2026-08-13_ulsh_01_md2s_bvp_wp3_d12_cp01r3_bjp01_etrn02_v1.0.py"
SEED_SPEC = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3SeedSpec_v1.0.json"
D11 = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D11_CP01R3ProtocolDesign_v1.0.json"
EXPECTED_SEED_SPEC_SHA256 = "05315df34903188284b4ea58bffc6b440a06bda9486362a6760c7cc0cfcb1474"


def load_tool():
    spec = importlib.util.spec_from_file_location("ulsh_cp01r3_d12", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    design = json.loads(D11.read_text(encoding="utf-8"))
    seed_spec = json.loads(SEED_SPEC.read_text(encoding="utf-8"))
    module = load_tool()

    assert design["next_allowed_action"] == "ULSH-01_WP3_D12_CP01R3_BJP01_ETRN02_IMPLEMENTATION_AND_MANUFACTURED_CONTROLS_ONLY"
    assert seed_spec["run_id_reserved"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3"
    assert seed_spec["seed_set_id"] == "M1-BG3B-CP01R3-BJP01-SEEDS-01"
    assert seed_spec["physical_execution_authorized"] is False
    assert hashlib.sha256(SEED_SPEC.read_bytes()).hexdigest() == EXPECTED_SEED_SPEC_SHA256

    result = module.audit()
    assert result["status"] == "PASS_D12_BJP01_ETRN02_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION"
    assert result["run_id_reserved"] == seed_spec["run_id_reserved"]
    assert result["seed_set_id_reserved"] == seed_spec["seed_set_id"]
    assert set(result["controls"]) == {"D11-C1", "D11-C2", "D11-C3", "D11-C4", "D11-C5", "D11-C6"}
    assert all(row["status"] == "PASS" for row in result["controls"].values())
    assert result["controls"]["D11-C1"]["max_abs_projected_junction_residual"] < 1e-14
    assert result["controls"]["D11-C2"]["endpoint_invariant_max_abs"] < 1e-15
    assert result["controls"]["D11-C3"]["relative_spread"] <= result["controls"]["D11-C3"]["registered_tolerance"]
    assert result["controls"]["D11-C4"]["relative_original_state_metric_difference"] < 1e-7
    assert result["controls"]["D11-C5"]["root_error_inf"] < 1e-7
    assert result["controls"]["D11-C6"]["fail_closed_checks_passed"] == 3
    assert result["physical_backend_imported"] is False
    assert result["physical_residual_evaluations"] == 0
    assert result["physical_jacobian_evaluations"] == 0
    assert result["physical_solver_calls"] == 0
    assert result["grant_issued"] is False
    assert result["physical_evidence_effect"] == "NONE"

    denied = subprocess.run([sys.executable, str(TOOL), "--physical-run"], capture_output=True, text=True, check=False)
    assert denied.returncode == 73
    assert "not implemented or authorized" in denied.stdout

    print("PASS_WP3_D12_CP01R3_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
