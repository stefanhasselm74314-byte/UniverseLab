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
AUDIT = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D12_CP01R3ManufacturedControlAudit_v1.0.json"
D11 = ROOT / "registry/2026-08-13_ULSH-01_MD2S-BVP_WP3_D11_CP01R3ProtocolDesign_v1.0.json"
EXPECTED_SEED_SPEC_SHA256 = "05315df34903188284b4ea58bffc6b440a06bda9486362a6760c7cc0cfcb1474"
EXPECTED_IMPLEMENTATION_BLOB_SHA1 = "d6313721a459254b13bdc9e06b4b83fc5a0fcca9"


def git_blob_sha1(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


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
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    module = load_tool()

    assert design["next_allowed_action"] == "ULSH-01_WP3_D12_CP01R3_BJP01_ETRN02_IMPLEMENTATION_AND_MANUFACTURED_CONTROLS_ONLY"
    assert seed_spec["run_id_reserved"] == "HZT-M0-S6-C-PHYS-M1-BG3B-CP01R3"
    assert seed_spec["seed_set_id"] == "M1-BG3B-CP01R3-BJP01-SEEDS-01"
    assert seed_spec["physical_execution_authorized"] is False
    assert hashlib.sha256(SEED_SPEC.read_bytes()).hexdigest() == EXPECTED_SEED_SPEC_SHA256
    assert git_blob_sha1(TOOL) == EXPECTED_IMPLEMENTATION_BLOB_SHA1

    assert audit["status"] == "PASS_D12_BJP01_ETRN02_MANUFACTURED_CONTROLS_NO_PHYSICAL_EXECUTION"
    assert audit["tested_head_commit"] == "132e140490682daa0274849773156c9f135e03c4"
    assert audit["workflow_run"] == {"id": 31691213900, "job_id": 94418730440, "conclusion": "success"}
    source = audit["source_binding"]
    assert source["implementation_git_blob_sha1"] == EXPECTED_IMPLEMENTATION_BLOB_SHA1
    assert source["seed_spec_sha256"] == EXPECTED_SEED_SPEC_SHA256
    assert source["numpy_version"] == "2.1.3"
    assert source["run_id_reserved"] == seed_spec["run_id_reserved"]
    assert source["seed_set_id_reserved"] == seed_spec["seed_set_id"]

    result = module.audit()
    assert result["status"] == audit["status"]
    assert result["run_id_reserved"] == seed_spec["run_id_reserved"]
    assert result["seed_set_id_reserved"] == seed_spec["seed_set_id"]
    assert set(result["controls"]) == {"D11-C1", "D11-C2", "D11-C3", "D11-C4", "D11-C5", "D11-C6"}
    assert all(row["status"] == "PASS" for row in result["controls"].values())

    frozen_controls = audit["controls"]
    assert result["controls"]["D11-C1"]["max_abs_projected_junction_residual"] == frozen_controls["D11-C1"]["max_abs_projected_junction_residual"] == 0.0
    assert result["controls"]["D11-C2"]["endpoint_invariant_max_abs"] == frozen_controls["D11-C2"]["endpoint_invariant_max_abs"] == 0.0
    assert result["controls"]["D11-C3"]["relative_spread"] == frozen_controls["D11-C3"]["relative_spread"]
    assert result["controls"]["D11-C3"]["relative_spread"] <= frozen_controls["D11-C3"]["registered_tolerance"] == 0.006
    assert result["controls"]["D11-C4"]["relative_original_state_metric_difference"] == frozen_controls["D11-C4"]["relative_original_state_metric_difference"]
    assert result["controls"]["D11-C4"]["relative_original_state_metric_difference"] < frozen_controls["D11-C4"]["registered_limit"] == 1e-7
    assert result["controls"]["D11-C5"]["iterations"] == frozen_controls["D11-C5"]["iterations"] == 3
    assert result["controls"]["D11-C5"]["root_error_inf"] == frozen_controls["D11-C5"]["root_error_inf"]
    assert result["controls"]["D11-C5"]["root_error_inf"] < frozen_controls["D11-C5"]["registered_limit"] == 1e-7
    assert result["controls"]["D11-C6"]["fail_closed_checks_passed"] == frozen_controls["D11-C6"]["fail_closed_checks_passed"] == 3

    firewall = audit["execution_firewall"]
    assert result["physical_backend_imported"] is firewall["physical_backend_imported"] is False
    assert result["physical_residual_evaluations"] == firewall["physical_residual_evaluations"] == 0
    assert result["physical_jacobian_evaluations"] == firewall["physical_jacobian_evaluations"] == 0
    assert result["physical_solver_calls"] == firewall["physical_solver_calls"] == 0
    assert result["grant_issued"] is firewall["grant_issued"] is False
    assert result["physical_evidence_effect"] == firewall["physical_evidence_effect"] == "NONE"
    assert firewall["physical_cli_exit_code"] == 73

    governance = audit["governance_state"]
    assert governance["WP3"].startswith("OPEN_D12_MANUFACTURED_CONTROLS_PASS")
    assert governance["WP4"].startswith("BLOCKED")
    assert governance["ULSH-02"].startswith("BLOCKED")
    assert governance["K1-D"] == "NOT_RELEASED"
    assert governance["K1-E"] == "NOT_ADMISSIBLE"
    assert governance["physical_evidence_effect"] == "NONE"
    assert audit["next_allowed_action"] == "ULSH-01_WP3_D13_CP01R3_INDEPENDENT_IMPLEMENTATION_REVIEW_NO_PHYSICAL_EXECUTION"

    denied = subprocess.run([sys.executable, str(TOOL), "--physical-run"], capture_output=True, text=True, check=False)
    assert denied.returncode == 73
    assert "not implemented or authorized" in denied.stdout

    print("PASS_WP3_D12_CP01R3_MANUFACTURED_CONTROLS_AUDIT_BOUND_NO_PHYSICAL_EXECUTION")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
