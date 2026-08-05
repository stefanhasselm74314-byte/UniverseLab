#!/usr/bin/env python3
"""Canonical G0 v1.20 validator after Background-3C9 authorization denial."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
RELEASE="2.20-c-phys-m1-background-3c9-authorization-denied-v0.1"
DECISION="UL-DEC-0035"
CHECKPOINT="UL-CHK-20260805-028"
DENIAL="DENIED_REAL_BACKEND_ADAPTER_TRANSACTION_AND_OPERATIVE_SINGLE_USE_GRANT_RELEASE_ABSENT"
NEXT="C-PHYS-R1.0-BACKGROUND-3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_ONLY"
OLD_NEXT="C-PHYS-R1.0-BACKGROUND-3C9_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_ONLY"
OLD_ACTIVE="ACTIVE_PHYSICAL_ADAPTER_AUTHORIZATION_REVIEW_REMAINING"
SNAPSHOT=ROOT/"registry/2026-08-05_UniverseLab_SessionCheckpoint_v1.28.json"
LATEST=ROOT/"registry/session-checkpoint-latest.json"
MANIFEST=ROOT/"project-manifest.json"
DECISIONS=ROOT/"registry/decision-log.jsonl"
REVIEW=ROOT/"registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C9PhysicalAdapterAuthorizationReview_v0.1.json"
REVIEW_VALIDATOR=ROOT/"tools/2026-08-05_validate_hzt_m0_s6_c_phys_m1_background_3c9_v0.1.py"
GRANTS=[ROOT/"registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json",ROOT/"registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"]
ARTIFACT=ROOT/"artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"

def load(path): return json.loads(path.read_text(encoding="utf-8"))
def find_exact(value:Any,target:str,path:str="$"):
    if isinstance(value,dict): return sum((find_exact(item,target,f"{path}.{key}") for key,item in value.items()),[])
    if isinstance(value,list): return sum((find_exact(item,target,f"{path}[{index}]") for index,item in enumerate(value)),[])
    return [path] if value==target else []
def load_review_validator():
    spec=importlib.util.spec_from_file_location("bg3c9_g0",REVIEW_VALIDATOR)
    if spec is None or spec.loader is None: raise RuntimeError("review validator import failed")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module

def validate():
    manifest,latest,snapshot,review=load(MANIFEST),load(LATEST),load(SNAPSHOT),load(REVIEW)
    decisions=[json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert manifest["release"]==RELEASE and manifest["release_date"]=="2026-08-05"
    assert LATEST.read_bytes()==SNAPSHOT.read_bytes() and latest==snapshot
    assert latest["checkpoint_id"]==CHECKPOINT and latest["basis_commit"]=="19b134797a3a4cdf9852ec77084009c317c1642e"
    assert latest["current_workstreams"][0]["next_block"]==NEXT
    selected=[item for item in decisions if item.get("decision_id")==DECISION]
    assert len(selected)==1 and selected[0]["physical_evidence_effect"]=="NONE"
    gates=manifest["gates"]
    expected={
      "R1.0":"ACTIVE_REAL_BACKEND_ADAPTER_CONTROL_RELEASE_IMPLEMENTATION_REMAINING",
      "BACKGROUND_SOLVER_IMPLEMENTATION":"PHYSICAL_ADAPTER_AUDITED_MANUFACTURED_CONTROLS_ONLY_REAL_BACKEND_CONTROL_RELEASE_REMAINING",
      "BACKGROUND_3C8_PHYSICAL_EXECUTION_ADAPTER":"PASS_AUDITED_MANUFACTURED_CONTROLS_ONLY",
      "BACKGROUND_3C9_AUTHORIZATION_REVIEW":DENIAL,
      "BACKGROUND_3C10_REAL_BACKEND_ADAPTER_CONTROL_RELEASE":"NOT_STARTED",
      "BACKGROUND_3C_EXECUTION":"NOT_AUTHORIZED","BACKGROUND_SOLVER_EXECUTION":"NOT_AUTHORIZED",
      "PHYSICAL_BACKGROUND":"NOT_ESTABLISHED","R1.1":"BLOCKED","R1.2":"BLOCKED",
      "official_MD2S_solver":"NOT_AUTHORIZED","FULL_LINEARIZED_BOUNDARY_TRACE_RANK":"NOT_PROVEN",
      "FREDHOLM_PROPERTY":"NOT_PROVEN","CONTINUUM_BVP_JACOBIAN":"NOT_PROVEN",
      "K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE","physical_evidence_effect":"NONE"}
    for key,value in expected.items(): assert gates.get(key)==value,(key,gates.get(key),value)
    assert manifest["next_block"]==NEXT and manifest["parent_action_v0_1"]["next_block"]==NEXT
    assert manifest["c_phys_operator_entry"]["next_block"]==NEXT and manifest["c_phys_operator_entry"]["solver_authorized"] is False
    assert manifest["c_phys_m1"]["next_block"]==NEXT
    assert find_exact(manifest,OLD_NEXT)==[] and find_exact(manifest,OLD_ACTIVE)==[]
    assert find_exact(latest,OLD_NEXT)==[] and find_exact(latest,OLD_ACTIVE)==[]
    assert review["status"]==DENIAL and review["authorization_decision"]["authorized"] is False
    review_result=load_review_validator().validate()
    assert review_result["status"]=="PASS" and review_result["review_status"]==DENIAL
    assert review_result["physical_backend_imported"] is False and review_result["physical_solver_calls"]==0
    blockers={item["blocker_id"] for item in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C9-001" not in blockers and "UL-BLK-C-PHYS-BACKGROUND-3C10-001" in blockers
    verified={item["result_id"]:item for item in latest["verified_results"]}
    assert verified["UL-RES-C-PHYS-M1-BG3C9-001"]["status"]==DENIAL
    assert all(not path.exists() for path in GRANTS) and not ARTIFACT.exists()
    return {"status":"PASS","release":RELEASE,"decision":DECISION,"checkpoint":CHECKPOINT,"review_status":DENIAL,"execution_authorized":False,"physical_backend_imported":False,"physical_solver_calls":0,"cp01r1_attempts":0,"physical_evidence_effect":"NONE","next_block":NEXT}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--json",action="store_true"); args=parser.parse_args(); result=validate(); print(json.dumps(result,indent=2,sort_keys=True) if args.json else "PASS: G0 v1.20")
if __name__=="__main__": main()
