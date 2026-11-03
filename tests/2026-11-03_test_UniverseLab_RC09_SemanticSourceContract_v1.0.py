#!/usr/bin/env python3
"""RC09: 39-source pinned provenance, declared-scope verification and negative tests.

This is NOT independent mathematical or empirical validation of the HZT model.
"""
from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "drafts/2026-11-03_UniverseLab_RC09_SemanticSourceContract_v1.0_DRAFT.json"
INVENTORY = ROOT / "drafts/2026-11-03_UniverseLab_RC07_ChangedFileInventory_v1.0_DRAFT.json"
PINNED = "51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
TREE = "65f423f04bbb2f1462f120a6b31073644cdc28cc"
BASELINE = "3022dc8aac27ed2054fdb7643708fe57440b9256"

def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

def field(obj, path):
    for token in path.split("."):
        if not isinstance(obj, dict) or token not in obj:
            raise AssertionError(f"missing field {path}, token={token}")
        obj = obj[token]
    return obj

def verify(matrix, inventory, sources):
    assert matrix["schema"] == "universelab.rc09.source-level-semantic-contract.v1"
    assert matrix["status"] == "DRAFT_SOURCE_SEMANTIC_CLASSIFICATION_NOT_INDEPENDENT_SCIENTIFIC_AUDIT"
    assert matrix["pinned_merged_main_commit"] == PINNED
    assert matrix["pinned_tree"] == TREE
    assert matrix["priority_source_count"] == 39
    assert matrix["physical_gate_effect"] == matrix["physical_evidence_effect"] == "NONE"
    assert matrix["additional_audit_obligation"]["manual_claim_review_required"] == 251
    assert matrix["additional_audit_obligation"]["original_claim_candidates"] == 993
    assert matrix["additional_audit_obligation"]["remaining_scientific_missing_links"] == 10
    assert "INDEPENDENT_MATH_PROOFS_NOT_PERFORMED" in matrix["release_blockers"]
    assert "SITE_STATE_SUCCESSOR_REQUIRED" in matrix["release_blockers"]
    rows=matrix["source_rows"]
    expected={e["path"] for e in inventory["entries"] if e["priority"]=="P1"}
    assert len(expected)==39
    actual=[r["source"] for r in rows]
    assert len(actual)==len(set(actual))==39
    assert set(actual)==expected
    assert {r["id"] for r in rows}=={f"RC09-{i:02d}" for i in range(1,40)}
    nassert=0
    for row in rows:
        path=row["source"]
        assert path.startswith(("registry/","governance/")) and ".." not in path
        assert row["format"] == ("json" if path.endswith(".json") else "md")
        assert row["source_present_at_merged_base"] is True
        assert row["physical_inference_authorized"] is False
        assert row["independent_mathematical_rederivation"] == "NOT_PERFORMED"
        assert row["target"]=="DRAFT_RECONCILIATION_ONLY"
        assert row["scope_result"] and row["semantic_class"] and row["assertions"]
        assert sources[path]["sha"]==row["blob_sha"]
        for test in row["assertions"]:
            nassert+=1
            if test["kind"]=="git_blob_sha":
                assert test["value"]==sources[path]["sha"]
            elif test["kind"]=="source_field":
                assert row["format"]=="json"
                assert field(sources[path]["body"],test["path"])==test["value"], (path,test["path"])
            elif test["kind"]=="text_contains":
                assert row["format"]=="md"
                assert test["value"] in sources[path]["body"], (path,test["value"])
            else:
                raise AssertionError(f"unsupported assertion type {test['kind']}")
        if row["semantic_class"]=="ANALYTIC_NONOPERATIVE_6D_PERTURBATION":
            o=sources[path]["body"]
            assert o.get("solver_authorized") is False
            assert o.get("physical_gate_effect")==o.get("physical_evidence_effect")=="NONE"
            assert isinstance(o.get("forbidden_inferences"),list) and bool(o["forbidden_inferences"])
        if row["semantic_class"]=="HISTORICAL_ACTIVE_POINTER_SNAPSHOT":
            o=sources[path]["body"]
            assert o.get("basis_main_commit",o.get("basis_commit"))==BASELINE
    assert nassert>=170
    return nassert

def main():
    m=load("drafts/2026-11-03_UniverseLab_RC09_SemanticSourceContract_v1.0_DRAFT.json")
    inv=load("drafts/2026-11-03_UniverseLab_RC07_ChangedFileInventory_v1.0_DRAFT.json")
    sources={}
    for row in m["source_rows"]:
        path=row["source"]
        p=ROOT / path
        assert p.is_file(),path
        sha=subprocess.check_output(["git","hash-object",str(p)],text=True).strip()
        text=p.read_text(encoding="utf-8")
        sources[path]={"sha":sha,"body":json.loads(text) if path.endswith(".json") else text}
    count=verify(m,inv,sources)
    def reject(name, mutation):
        bad=copy.deepcopy(m)
        mutation(bad)
        try:
            verify(bad,inv,sources)
        except AssertionError:
            print("PASS NEGATIVE:",name)
        else:
            raise AssertionError("Invalid contract accepted: "+name)
    reject("wrong_tree",lambda x:x.__setitem__("pinned_tree","0"*40))
    reject("lost_source",lambda x:x["source_rows"].pop())
    reject("altered_blob",lambda x:x["source_rows"][0].__setitem__("blob_sha","0"*40))
    reject("claim_queue_suppression",lambda x:x["additional_audit_obligation"].__setitem__("manual_claim_review_required",0))
    reject("fabricated_physical_evidence",lambda x:x["source_rows"][0].__setitem__("physical_inference_authorized",True))
    reject("wrong_source_field",lambda x:x["source_rows"][5]["assertions"][-1].__setitem__("value","RELEASED"))
    reject("duplicate_source",lambda x:x["source_rows"][1].__setitem__("source",x["source_rows"][0]["source"]))
    reject("missing_site_state",lambda x:x["release_blockers"].remove("SITE_STATE_SUCCESSOR_REQUIRED"))
    print(f"RC09 PASS: {len(m['source_rows'])} files, {count} source assertions, 8 negative controls")
    print("NOT PROVEN: field-theory equations, global solvability, 4D observables, empirical HZT support")
    print("CANONICAL_PROMOTION = BLOCKED")

if __name__=="__main__":
    main()
