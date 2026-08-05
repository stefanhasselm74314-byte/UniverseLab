#!/usr/bin/env python3
"""Canonical G0 v1.18 validator after Background-3C7 authorization denial."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RELEASE="2.18-c-phys-m1-background-3c7-authorization-denied-v0.1"
DECISION="UL-DEC-0033"
CHECKPOINT="UL-CHK-20260805-026"
DENIAL="DENIED_PHYSICAL_BACKEND_ADAPTER_AND_SINGLE_USE_GRANT_RELEASE_ABSENT"
NEXT="C-PHYS-R1.0-BACKGROUND-3C8_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_ONLY"
OLD_NEXT="C-PHYS-R1.0-BACKGROUND-3C7_INTEGRATED_RELEASE_AUTHORIZATION_REVIEW_ONLY"
OLD_STATUS="BACKGROUND_3C6_CONTROL_RELEASE_AUDITED_AUTHORIZATION_REVIEW_REMAINING"
SNAPSHOT=ROOT/"registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.26.json"
LATEST=ROOT/"registry/session-checkpoint-latest.json"
MANIFEST=ROOT/"project-manifest.json"
DECISIONS=ROOT/"registry/decision-log.jsonl"
REVIEW=ROOT/"registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C7IntegratedReleaseAuthorizationReview_v0.1.json"
REVIEW_VALIDATOR=ROOT/"tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c7_v0.1.py"
GRANTS=[ROOT/"registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",ROOT/"registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"]
ARTIFACT=ROOT/"artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def find_exact(v:Any,t:str,p:str="$"):
    if isinstance(v,dict): return sum((find_exact(x,t,f"{p}.{k}") for k,x in v.items()),[])
    if isinstance(v,list): return sum((find_exact(x,t,f"{p}[{i}]") for i,x in enumerate(v)),[])
    return [p] if v==t else []
def load_review_validator():
    s=importlib.util.spec_from_file_location("bg3c7_g0",REVIEW_VALIDATOR)
    if s is None or s.loader is None: raise RuntimeError("validator import failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m); return m

def validate():
    manifest,latest,snapshot,review=load(MANIFEST),load(LATEST),load(SNAPSHOT),load(REVIEW)
    decisions=[json.loads(x) for x in DECISIONS.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert manifest["release"]==RELEASE and manifest["release_date"]=="2026-08-05"
    assert LATEST.read_bytes()==SNAPSHOT.read_bytes() and latest==snapshot
    assert latest["checkpoint_id"]==CHECKPOINT and latest["basis_commit"]=="24d9e3d7a5fdadaeef185cf596bce3f394add60a"
    assert latest["current_workstreams"][0]["next_block"]==NEXT
    selected=[d for d in decisions if d.get("decision_id")==DECISION]
    assert len(selected)==1 and selected[0]["physical_evidence_effect"]=="NONE"
    gates=manifest["gates"]
    expected={"R1.0":"ACTIVE_PHYSICAL_EXECUTION_ADAPTER_IMPLEMENTATION_REMAINING","BACKGROUND_SOLVER_IMPLEMENTATION":"INTEGRATED_CONTROL_RELEASE_AUDITED_PHYSICAL_ADAPTER_MISSING","BACKGROUND_3C6_EXECUTION_RELEASE":"PASS_AUDITED_CONTROL_ONLY","BACKGROUND_3C7_AUTHORIZATION_REVIEW":DENIAL,"BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER":"NOT_STARTED","BACKGROUND_3C_EXECUTION":"NOT_AUTHORIZED","BACKGROUND_SOLVER_EXECUTION":"NOT_AUTHORIZED","PHYSICAL_BACKGROUND":"NOT_ESTABLISHED","R1.1":"BLOCKED","R1.2":"BLOCKED","official_MD2S_solver":"NOT_AUTHORIZED","K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE","physical_evidence_effect":"NONE"}
    for k,v in expected.items(): assert gates.get(k)==v,(k,gates.get(k),v)
    assert manifest["next_block"]==NEXT and manifest["parent_action_v0_1"]["next_block"]==NEXT
    assert manifest["c_phys_operator_entry"]["next_block"]==NEXT and manifest["c_phys_operator_entry"]["solver_authorized"] is False
    assert find_exact(manifest,OLD_NEXT)==[] and find_exact(manifest,OLD_STATUS)==[]
    assert review["status"]==DENIAL and review["authorization_decision"]["authorized"] is False
    assert load_review_validator().validate()["status"]=="PASS"
    blockers={b["blocker_id"] for b in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C7-001" not in blockers and "UL-BLK-C-PHYS-BACKGROUND-3C8-001" in blockers
    verified={r["result_id"]:r for r in latest["verified_results"]}
    assert verified["UL-RES-C-PHYS-M1-BG3C7-001"]["status"]==DENIAL
    assert all(not p.exists() for p in GRANTS) and not ARTIFACT.exists()
    return {"status":"PASS","release":RELEASE,"decision":DECISION,"checkpoint":CHECKPOINT,"review_status":DENIAL,"execution_authorized":False,"physical_solver_calls":0,"cp01r1_attempts":0,"physical_evidence_effect":"NONE","next_block":NEXT}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",action="store_true"); a=p.parse_args(); r=validate(); print(json.dumps(r,indent=2,sort_keys=True) if a.json else "PASS: G0 v1.18")
if __name__=="__main__": main()
