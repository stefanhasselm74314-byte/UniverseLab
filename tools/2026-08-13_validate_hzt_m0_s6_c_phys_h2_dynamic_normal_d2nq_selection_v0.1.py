#!/usr/bin/env python3
"""Fail-closed validator for C-PHYS H2 dynamic-normal D2N-Q selection test."""

from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-13_HZT-M0_S6_C-PHYS_H2_DynamicNormal_D2NQ_SelectionTest_v0.1.json"

EXPECTED_STATUS = (
    "PASS_EXACT_CODAZZI_DEGENERACY_THEOREM_D2NQ_DYNAMIC_SELECTION_NOT_DERIVED_"
    "CURRENT_PARENT_EMBEDDING_CLOSURE_REQUIRED"
)


def git_blob_sha(path: pathlib.Path) -> str:
    proc = subprocess.run(
        ["git", "hash-object", str(path.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def fail(msg: str) -> None:
    raise AssertionError(msg)


def validate() -> dict:
    data = json.loads(REG.read_text(encoding="utf-8"))

    if data.get("status") != EXPECTED_STATUS:
        fail("unexpected H2 status")
    if data.get("physical_evidence_effect") != "NONE":
        fail("physical evidence firewall changed")
    if data.get("solver_execution") is not False:
        fail("H2 must not execute a solver")

    ext = data["external_material_firewall"]
    if ext.get("gemini_blocks") != "EXTERNAL_UNVERIFIED_GEMINI_DRAFT":
        fail("Gemini quarantine missing")
    if ext.get("gemini_equations_used_as_premises") is not False:
        fail("Gemini premise firewall violated")
    if ext.get("two_time_branch_imported") is not False:
        fail("two-time branch imported into one-time C-PHYS")

    for binding in data["source_bindings"]:
        path = ROOT / binding["path"]
        if not path.is_file():
            fail(f"missing source binding: {binding['path']}")
        actual = git_blob_sha(path)
        if actual != binding["git_blob_sha1"]:
            fail(
                f"source hash mismatch for {binding['path']}: "
                f"expected {binding['git_blob_sha1']} got {actual}"
            )

    geom = data["geometric_setup"]
    if geom.get("ambient_signature") != "(-,+,+,+,+,+)":
        fail("ambient signature drift")
    if geom.get("normal_metric") != "delta_ij_positive_definite":
        fail("normal metric drift")
    if geom["gauss_identity"].get("Q_00") != "3*B_squared":
        fail("Q00 identity drift")

    cod = data["codazzi_projection"]
    required_codazzi = {
        "covariant_flrw_equation": "Dperp_t(beta_i)+H*(alpha_i+beta_i)=S_i/3",
        "beta_contraction": "0.5*D_t(B_squared)+H*(alpha_dot_beta+B_squared)=beta_dot_S/3",
        "alpha_dot_beta_solution": "alpha_dot_beta=-B_squared-D_t(B_squared)/(2*H)+beta_dot_S/(3*H)",
    }
    for key, value in required_codazzi.items():
        if cod.get(key) != value:
            fail(f"Codazzi formula drift: {key}")

    fluid = data["effective_fluid_identity"]
    if fluid.get("exchange_equation") != "D_t(rho_Q)+3*H*(rho_Q+p_Q)=2*M4^2*beta_dot_S":
        fail("exchange identity drift")
    if fluid.get("source_free_w") != "w_Q=-1-(1/3)*d_ln_B_squared/d_ln_a":
        fail("source-free w identity drift")

    deg = data["codazzi_degeneracy_theorem"]
    if deg.get("result") != "D2NQ_LAMBDA_PLUS_DUST_PROFILE_IS_ALLOWED_BUT_NOT_SELECTED":
        fail("degeneracy conclusion drift")

    dyn = data["dynamic_selection_test"]
    if dyn.get("answer") != "NO_AT_CURRENT_CLOSURE":
        fail("dynamic selection must remain fail-closed")
    if dyn.get("disposition") != "BLOCKED_BY_MISSING_TIME_DEPENDENT_BULK_EMBEDDING_CLOSURE_NOT_FALSIFIED":
        fail("dynamic selection disposition drift")

    theorem = data["parent_action_scope_theorem"]
    if theorem.get("independent_embedding_field_present") is not False:
        fail("embedding field silently added")
    if theorem.get("deltaS_delta_Ki_munu_equation_exists") is not False:
        fail("nonexistent K Euler-Lagrange equation claimed")
    if theorem.get("preferred_current_C_PHYS_path") != "PATH_A":
        fail("current C-PHYS completion path changed")

    gates = data["gate_disposition"]
    expected_gates = {
        "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "WP4": "BLOCKED",
        "physical_evidence_effect": "NONE",
    }
    for key, value in expected_gates.items():
        if gates.get(key) != value:
            fail(f"governance firewall drift: {key}")

    if data.get("next_candidate") != "C-PHYS-PARENT-H3-TIME-DEPENDENT-6D-M1-COSMOLOGICAL-ANSATZ-AND-PROJECTED-CLOSURE":
        fail("unexpected next block")

    return {
        "ok": True,
        "status": data["status"],
        "source_bindings": len(data["source_bindings"]),
        "dynamic_selection": dyn["answer"],
        "K1-D": gates["K1-D"],
        "K1-E": gates["K1-E"],
        "WP4": gates["WP4"],
        "physical_evidence_effect": gates["physical_evidence_effect"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = validate()
    except Exception as exc:  # fail closed
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, sort_keys=True))
        else:
            print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, sort_keys=True))
    else:
        print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
