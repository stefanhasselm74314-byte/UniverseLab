#!/usr/bin/env python3
"""RC08 fail-closed draft semantic reconciliation checks with negative controls."""
from __future__ import annotations
import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = "drafts/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4_DRAFT.json"
CHECKPOINT = "drafts/2026-11-03_UniverseLab_SessionCheckpoint_v1.35_DRAFT.json"
MANIFEST = "drafts/2026-11-03_UniverseLab_ProjectManifest_v2.35_DRAFT.json"
CROSSWALK = "drafts/2026-11-03_UniverseLab_RC08_SemanticFieldCrosswalk_v1.0_DRAFT.json"
BASE = "51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
TREE = "65f423f04bbb2f1462f120a6b31073644cdc28cc"
SOURCE = {
    "G11": ("registry/2026-09-04_UniverseLab_BandVC_G11_StateFreshnessClosure_v1.0.json", "cb98d726da5def5c9a470e9faf80c5811ee52998"),
    "G01": ("registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInterface_v1.0.json", "81582ce7c395b1199e066e89ff44a053eed649ec"),
    "WP1D2": ("registry/2026-09-14_UniverseLab_ULSH05_WP1D2_KinematicInvariantProjectorSolvabilityPreflight_v0.1.json", "fc378618467646262a55ea36b2b686f4fc91252a"),
    "PKNR": ("registry/2026-09-14_UniverseLab_ProvenanceConsistencyDetectabilityContract_v1.1.json", "1686a504ce451bc4f0a67fb311fd0ee5bdf99c94"),
    "HDA": ("registry/2026-08-31_UniverseLab_ULSH_HDA_Delegation_v1.0.json", "0a13444e9aa1dce4e91ea2815cadb99ed42c2030"),
    "ULSING": ("registry/2026-09-28_UL-SING_QuantumClosure_MethodGates_v1.0.json", "2b3fd87e22fe5d7296f914fa3cb2704cee55eb16"),
}

def read(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))

def verify_sources():
    result = {}
    for key, (path, sha) in SOURCE.items():
        actual = subprocess.check_output(["git", "hash-object", str(ROOT / path)], text=True).strip()
        assert actual == sha, (path, "blob SHA mismatch", actual, sha)
        result[key] = read(path)
    return result

def verify(s, c, m, src, cw):
    all_candidates = (s, c, m)
    for n in all_candidates:
        a = n["reconciliation_addendum"]
        assert a["status"] == "DRAFT_NOT_CANONICAL"
        assert a["nonoperative_only"] is True
        assert a["current_merge_tree_status"] == "VERIFIED_GIT_OBJECT_PINNED_MERGE_COMMIT"
        assert a["reconciliation_basis_commit"] == BASE
        assert a["semantic_rc08"]["crosswalk"] == CROSSWALK
        assert n["physical_gate_effect"] == n["physical_evidence_effect"] == "NONE"
    assert s["basis_main_commit"] == c["basis_commit"] == m["basis_main_commit"] == BASE
    assert s["basis_main_tree"] == c["basis_tree"] == m["basis_main_tree"] == TREE
    assert cw["verified_git_tree"] == TREE
    assert cw["pinned_merged_main_commit"] == BASE
    assert len(cw["field_decisions"]) == 12
    assert set(cw["source_provenance"]) == set(SOURCE)
    for key, (path, sha) in SOURCE.items():
        assert cw["source_provenance"][key]["path"] == path
        assert cw["source_provenance"][key]["blob_sha"] == sha

    sg = s["reconciliation_addendum"]["semantic_rc08"]
    cg = c["reconciliation_addendum"]["semantic_rc08"]
    mg = m["reconciliation_addendum"]["semantic_rc08"]
    assert sg == cg == mg
    g11, g01, wp, pk, hd, sing = (src[key] for key in ("G11", "G01", "WP1D2", "PKNR", "HDA", "ULSING"))
    assert g11["closure_status"] == "IMPLEMENTED_REVIEW_PENDING"  # source-local historical value
    assert g11["governance_provenance_missing_links_after_closure"] == 0
    assert g11["scientific_missing_links_after_closure"] == 10
    assert sg["band_vc_g11"]["september_chain_integration"] == "MERGED_PR210"
    assert sg["band_vc_g11"]["governance_provenance_missing_links_after_closure"] == 0
    assert sg["band_vc_g11"]["current_snapshot_reconciliation"] == "OPEN_DRAFT"
    assert s["active_analysis_block"]["governance_provenance_gap"] == "UL-BVC-G11_SEPTEMBER_CHAIN_MERGED_PR210_CURRENT_RECONCILIATION_OPEN"
    assert c["active_block"]["state_freshness_action"] == "PR210_MERGED_SEPTEMBER_CHAIN_NEW_RC08_CANONICAL_RECONCILIATION_PENDING"
    assert any(row["defect_id"] == "UL-BVC-G11" and row["repair_status"] == "MERGED_PR210_HISTORICAL_SCOPE_ONLY_RC08_NEW_SNAPSHOT_PENDING" for row in c["confirmed_defects"])
    assert m["public_claim_audit"]["band_v_c_governance_provenance_missing_links"] == 1  # historical quantity retained

    assert g01["release_requirements"]["G01"] == "OPEN_BLOCKING"
    assert g01["hzt_outputs"]["mu_k_a"] == g01["hzt_outputs"]["eta_k_a"] == g01["hzt_outputs"]["Sigma_k_a"] == "NOT_RELEASED"
    assert sg["band_vc_g01"]["gate"] == "OPEN_BLOCKING"
    assert s["scientific_open_state"]["bridge_growth_poisson_slip_lensing_map"] == "OPEN_UNRELEASED"

    g = wp["gate_state"]
    assert g["WP1D_physical_DOF_count"] == "NOT_RELEASED"
    assert g["WP1D_constraint_elimination"] == "BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING"
    assert g["WP1D1_closed_range_of_G"] == "NOT_PROVEN"
    assert g["WP1D1_Fredholm_property_of_G"] == "NOT_PROVEN"
    assert sg["ulsh05_wp1d2"]["physical_DOF_count"] == "NOT_RELEASED"
    assert sg["ulsh05_wp1d2"]["closed_range"] == "NOT_PROVEN"
    assert sg["ulsh05_wp1d2"]["Fredholm_property"] == "NOT_PROVEN"

    assert pk["adoption"]["status"] == "USER_RATIFIED_METHOD_RULE"
    assert pk["implementation"]["automatic_evidence_evaluator"] is False
    assert sg["provenance_rule"]["merged_pr"] == 235
    assert sg["provenance_rule"]["automatic_evidence_evaluator"] is False
    assert hd["authority"]["operative_authority"] is False
    assert hd["authority"]["identity_binding_status"] == "PENDING_CANONICAL_ID_BINDING"
    assert sg["hda"]["operative_authority"] is False
    assert sg["hda"]["reserved_matters_require_owner_ratification"] is True

    assert sg["ul_sing"]["method_gates"] == ["QG-PI-01","QG-GAP-01","KK-CTP-01"]
    assert [x["gate_id"] for x in sing["gates"]] == sg["ul_sing"]["method_gates"]
    assert all(x["physical_gate_effect"] == x["physical_evidence_effect"] == "NONE" for x in sing["gates"])
    assert all(x["closure_status"].startswith("NOT_EVALUATED") for x in sing["gates"])
    for name,expected in {"K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE","FM-G0":"OPEN"}.items():
        assert m["gates"][name] == c["gate_state"][name] == expected
    assert s["physical_governance"]["K1-D"] == "NOT_RELEASED"
    assert s["physical_governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert s["physical_governance"]["physical_background"] == "NOT_ESTABLISHED"
    assert s["physical_governance"]["physical_response_rank"] == "NOT_EXECUTED"
    assert c["canonical_snapshot"] == "registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json"
    assert sg["snapshot_timestamp_status"].startswith("HISTORICAL_VALUE_INHERITED")
    assert sg["checkpoint_snapshot_pointer_status"].startswith("HISTORICAL_VALUE_INHERITED")

def negatives(s,c,m,src,cw):
    probes = [
        ("tree_mutation", lambda s,c,m: s.__setitem__("basis_main_tree","000")),
        ("gate_promotion", lambda s,c,m: m["gates"].__setitem__("K1-D","RELEASED")),
        ("false_G11_closure", lambda s,c,m: s["reconciliation_addendum"]["semantic_rc08"]["band_vc_g11"].__setitem__("governance_provenance_missing_links_after_closure",1)),
        ("false_physical_DOF", lambda s,c,m: s["reconciliation_addendum"]["semantic_rc08"]["ulsh05_wp1d2"].__setitem__("physical_DOF_count","RELEASED")),
        ("false_HDA_operativity", lambda s,c,m: s["reconciliation_addendum"]["semantic_rc08"]["hda"].__setitem__("operative_authority",True)),
        ("fake_auto_evidence", lambda s,c,m: s["reconciliation_addendum"]["semantic_rc08"]["provenance_rule"].__setitem__("automatic_evidence_evaluator",True)),
        ("premature_snapshot", lambda s,c,m: c.__setitem__("canonical_snapshot","registry/fake_release.json")),
        ("method_gate_promotion", lambda s,c,m: s["reconciliation_addendum"]["semantic_rc08"]["ul_sing"].__setitem__("method_gates",["QG-PI-01"])),
    ]
    for name,fn in probes:
        ss,cc,mm = copy.deepcopy((s,c,m))
        fn(ss,cc,mm)
        try:
            verify(ss,cc,mm,src,cw)
        except AssertionError:
            print("PASS negative:",name)
        else:
            raise AssertionError("Negative control incorrectly accepted: " + name)

def main():
    s,c,m = [read(p) for p in (STATE,CHECKPOINT,MANIFEST)]
    cw=read(CROSSWALK)
    sources=verify_sources()
    verify(s,c,m,sources,cw)
    negatives(s,c,m,sources,cw)
    print("RC08 PASS: 6 pinned source blobs, 12 field decisions, 8 negative controls")
    print("RELEASE BLOCKED: only scoped semantic review; pointer/timestamp and full canon reconciliation outstanding")

if __name__=="__main__":
    main()
