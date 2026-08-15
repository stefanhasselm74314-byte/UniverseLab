#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-08-15_HZT-M0_S6_C-PHYS_H4R4_ExactCompatibility_LocalIBVP_ManufacturedSolutionPreflight_v0.1.json"


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def require(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    d = json.loads(REG.read_text(encoding="utf-8"))
    require(d["schema"] == "universelab.hzt-m0-s6-c-phys.h4r4-exact-compatibility-local-ibvp-manufactured-solution-preflight.v1", "schema")
    require(d["version"] == "0.1.0", "version")
    require(d["baseline_main_sha"] == "23520f29e30542f0c280290ab036853c2e1cf4d1", "baseline")
    require(d["solver_execution"] is False, "physical solver execution must remain false")
    require(d["manufactured_solution_execution"] is False, "MMS execution must remain false")
    require(d["physical_backend_imported"] is False, "no backend")
    require(d["physical_evidence_effect"] == "NONE", "evidence firewall")
    require(d["canonical_signature"]["physical_times"] == 1, "one-time signature")
    require(d["external_material_firewall"]["gemini_equations_used_as_premises"] is False, "Gemini firewall")

    disp = d["h4r4_disposition"]
    require(disp["local_quasilinear_IBVP_theorem"] == "NOT_RATIFIED", "theorem must not be promoted")
    require(disp["physical_parent_solve_authorized"] is False, "no parent solve")
    require(disp["K1-D"] == "NOT_RELEASED", "K1-D")
    require(disp["K1-E"] == "NOT_ADMISSIBLE", "K1-E")
    require(disp["WP4"] == "BLOCKED", "WP4")
    require(disp["physical_evidence_effect"] == "NONE", "evidence")

    ch = d["compatibility_hierarchy"]
    require("j=1,...,m-1" in ch["recursive_rule"], "compatibility recursion range")
    require("BLOCKED_PENDING_COEFFICIENT_EXPORT" in ch["result"], "jet blocker")

    th = d["theorem_hypothesis_matrix"]
    require(th["symmetric_hyperbolic_principal_form"].startswith("PASS_H4R3"), "H4R3 principal pass binding")
    require(th["compatibility_conditions_through_required_order"] == "NOT_CHECKABLE_YET", "compatibility must remain unratified")
    require(th["local_existence_uniqueness"] == "NOT_RATIFIED", "existence status")

    mms = d["manufactured_solution_preflight"]
    require(mms["execution_authorized"] is False, "MMS execution firewall")
    require("exact_bulk_operator" in mms["bulk_forcing"], "MMS bulk operator")
    require("exact_interface_residual" in mms["boundary_forcing"], "MMS boundary operator")
    forbidden = " ".join(d["forbidden_inferences"])
    for token in ["NO_MMS_PASS_AS_PHYSICAL_PARENT_SOLUTION", "NO_K1D_OR_K1E_PROMOTION", "NO_WP4_OR_PHYSICAL_EVIDENCE_PROMOTION"]:
        require(token in forbidden, token)

    for src in d["source_bindings"]:
        p = ROOT / src["path"]
        require(p.exists(), f"missing source: {src['path']}")
        got = git_blob_sha1(p.read_bytes())
        require(got == src["git_blob_sha1"], f"source hash mismatch {src['path']}: {got}")

    print("H4R4 validation PASS: theorem promotion blocked correctly; exact compatibility structure and MMS preflight frozen; no execution.")


if __name__ == "__main__":
    main()
