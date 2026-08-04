#!/usr/bin/env python3
"""Canonical G0 validator v1.14 for denied Background-3C3 authorization."""
from __future__ import annotations
import argparse, importlib.util, json, re, subprocess, sys
from pathlib import Path, PurePosixPath
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
CHECKPOINT='registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.22.json'
REVIEW_VALIDATOR=ROOT/'tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c3_v0.1.py'
REVIEW='registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C3ExecutionAuthorizationReview_v0.1.json'
NEXT='C-PHYS-R1.0-BACKGROUND-3C4_EXECUTION_RUNNER_IMPLEMENTATION_ONLY'
FUTURE_GRANT=ROOT/'registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json'
OUTPUT_ROOT=ROOT/'artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1'

class ContractError(ValueError): pass

def require(condition: bool,message: str)->None:
    if not condition: raise ContractError(message)

def load_json(relative: str)->dict[str,Any]:
    path=ROOT/relative
    require(path.is_file(),f'missing JSON: {relative}')
    try: value=json.loads(path.read_text(encoding='utf-8'))
    except json.JSONDecodeError as exc: raise ContractError(f'invalid JSON in {relative}: {exc}') from exc
    require(isinstance(value,dict),f'JSON root must be object: {relative}')
    return value

def load_review_validator():
    spec=importlib.util.spec_from_file_location('background3c3_for_g0_v114',REVIEW_VALIDATOR)
    if spec is None or spec.loader is None: raise ContractError('unable to import Background-3C3 validator')
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module); return module

def validate_manifest(m: dict[str,Any])->dict[str,str]:
    require(m['release']=='2.14-c-phys-m1-background-3c3-authorization-denied-v0.1','release drift')
    require(m['architecture']['research_tracks'][1]['status']=='ACTIVE_EXECUTION_RUNNER_IMPLEMENTATION_REMAINING','physical track status drift')
    expected={
        'R1.0':'ACTIVE_EXECUTION_RUNNER_IMPLEMENTATION_REMAINING','R1.1':'BLOCKED','R1.2':'BLOCKED',
        'BACKGROUND_RUN_INPUT':'FROZEN_CP01R1','BACKGROUND_3C_PRIMARY_IMPLEMENTATION':'PASS_AUDITED_NO_EXECUTION',
        'BACKGROUND_3C_INDEPENDENT_BACKEND':'PASS_CONTROL_AUDIT_NO_ROOT_SOLVE','BACKGROUND_3C_DUAL_BACKEND_PACKAGE':'PASS_AUDITED_NO_EXECUTION',
        'BACKGROUND_3C_AUTHORIZATION_REVIEW':'DENIED_MISSING_EXECUTION_PACKAGE','BACKGROUND_3C_EXECUTION':'NOT_AUTHORIZED',
        'BACKGROUND_SOLVER_IMPLEMENTATION':'DUAL_BACKEND_AUDIT_COMPONENTS_PRESENT_EXECUTION_RUNNER_MISSING','BACKGROUND_SOLVER_EXECUTION':'NOT_AUTHORIZED',
        'official_MD2S_solver':'NOT_AUTHORIZED','FULL_LINEARIZED_BOUNDARY_TRACE_RANK':'NOT_PROVEN','FREDHOLM_PROPERTY':'NOT_PROVEN',
        'CONTINUUM_BVP_JACOBIAN':'NOT_PROVEN','PHYSICAL_BACKGROUND':'NOT_ESTABLISHED','K1-D':'NOT_RELEASED','K1-E':'NOT_ADMISSIBLE',
        'physical_evidence_effect':'NONE'}
    for key,value in expected.items(): require(m['gates'].get(key)==value,f'manifest gate drift: {key}')
    bg=m['c_phys_background_3c']
    require(bg['status']=='AUTHORIZATION_REVIEW_DENIED_MISSING_EXECUTION_PACKAGE','Background-3C status drift')
    require(bg['authorization_review']=='DENIED_MISSING_EXECUTION_PACKAGE','authorization review drift')
    for key in ('execution_runner','independent_target_root_solver','immutable_result_writer','resource_enforcement','environment_attestation','classification_engine','interruption_protocol'):
        require(bg[key] in ('NOT_PRESENT','NOT_IMPLEMENTED'),f'missing-runner blocker drift: {key}')
    require(bg['authorization']=='NOT_GRANTED' and bg['future_grant_present'] is False,'authorization drift')
    require(bg['solver_executed'] is False and bg['result_artifact_created'] is False,'execution/result overclaim')
    require(bg['next_block']==NEXT,'next block drift')
    require(m['central_registries']['session_checkpoint_snapshot']==CHECKPOINT,'checkpoint pointer drift')
    require(m['workstream_priority'][0]==f'MD2S-R1-C-PHYS:{NEXT}','workstream priority drift')
    return expected

def validate_checkpoint(cp: dict[str,Any])->dict[str,str]:
    require(cp['checkpoint_id']=='UL-CHK-20260804-022','checkpoint id drift')
    require(cp['canonical_snapshot']==CHECKPOINT,'checkpoint snapshot drift')
    require(cp['supersedes']=='registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.21.json','checkpoint supersedes drift')
    basis=cp.get('basis_commit'); require(isinstance(basis,str) and re.fullmatch(r'[0-9a-f]{40}',basis),'checkpoint basis format drift')
    if (ROOT/'.git').exists():
        result=subprocess.run(['git','-C',str(ROOT),'cat-file','-e',f'{basis}^{{commit}}'],capture_output=True,text=True,check=False)
        require(result.returncode==0,f'checkpoint basis absent: {basis}')
    expected={
        'BACKGROUND_RUN_INPUT':'FROZEN_CP01R1','BACKGROUND_3C_PRIMARY_IMPLEMENTATION':'PASS_AUDITED_NO_EXECUTION',
        'BACKGROUND_3C_INDEPENDENT_BACKEND':'PASS_CONTROL_AUDIT_NO_ROOT_SOLVE','BACKGROUND_3C_DUAL_BACKEND_PACKAGE':'PASS_AUDITED_NO_EXECUTION',
        'BACKGROUND_3C_AUTHORIZATION_REVIEW':'DENIED_MISSING_EXECUTION_PACKAGE','BACKGROUND_3C_EXECUTION':'NOT_AUTHORIZED',
        'BACKGROUND_SOLVER_IMPLEMENTATION':'DUAL_BACKEND_AUDIT_COMPONENTS_PRESENT_EXECUTION_RUNNER_MISSING','BACKGROUND_SOLVER_EXECUTION':'NOT_AUTHORIZED',
        'FULL_LINEARIZED_BOUNDARY_TRACE_RANK':'NOT_PROVEN','FREDHOLM_PROPERTY':'NOT_PROVEN','CONTINUUM_BVP_JACOBIAN':'NOT_PROVEN',
        'PHYSICAL_BACKGROUND':'NOT_ESTABLISHED','OFFICIAL_MD2S_SOLVER':'NOT_AUTHORIZED','K1-D':'NOT_RELEASED','K1-E':'NOT_ADMISSIBLE','PHYSICAL_EVIDENCE_EFFECT':'NONE'}
    for key,value in expected.items(): require(cp['gate_state'].get(key)==value,f'checkpoint gate drift: {key}')
    require(cp['current_workstreams'][0]['next_block']==NEXT,'checkpoint next block drift')
    return expected

def validate_alias()->dict[str,Any]:
    latest=load_json('registry/session-checkpoint-latest.json'); path=PurePosixPath(latest['canonical_snapshot'])
    require(not path.is_absolute() and '..' not in path.parts,'checkpoint path escape')
    require(latest==load_json(CHECKPOINT),'checkpoint alias mismatch'); return latest

def validate_decision()->str:
    decisions=[json.loads(line) for line in (ROOT/'registry/decision-log.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    ids=[x['decision_id'] for x in decisions]; require(len(ids)==len(set(ids)),'duplicate decision ids')
    nums=[]
    for decision_id in ids:
        match=re.fullmatch(r'UL-DEC-(\d{4})',decision_id); require(match is not None,f'invalid decision id: {decision_id}'); nums.append(int(match.group(1)))
    require(nums==sorted(nums),'decision order drift'); require(ids[-1]=='UL-DEC-0029','Background-3C3 decision must be latest')
    latest=decisions[-1]; require(latest['status']=='ACTIVE','decision status drift')
    require(latest['evidence_effect']=='GOVERNANCE_AND_EXECUTION_SAFETY_REVIEW_ONLY','decision evidence drift')
    require(latest['supersedes'] is None,'decision must remain additive'); return latest['decision_id']
def validate()->dict[str,Any]:
    review=load_review_validator().validate(); require(review['status']=='PASS','authorization review revalidation failed')
    require(review['review_outcome']=='DENIED_MISSING_EXECUTION_PACKAGE','review outcome drift')
    require(review['solver_executed'] is False and review['execution_authorized'] is False,'review execution overclaim')
    recorded=load_json(REVIEW); require(recorded['authorized'] is False,'recorded authorization opened')
    require(not FUTURE_GRANT.exists(),'unexpected grant artifact present'); require(not OUTPUT_ROOT.exists(),'unexpected result directory present')
    manifest=load_json('project-manifest.json'); checkpoint=validate_alias()
    return {'contract':'G0_BACKGROUND_3C3_AUTHORIZATION_DENIED_V1_14','status':'PASS','review_outcome':review['review_outcome'],
            'manifest_gates':validate_manifest(manifest),'checkpoint_gates':validate_checkpoint(checkpoint),'decision':validate_decision(),
            'execution_authorized':False,'solver_executed':False,'result_artifact_created':False,'physical_evidence_effect':'NONE','next_block':NEXT}
def main()->int:
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--json',action='store_true'); args=parser.parse_args()
    try: payload=validate()
    except (ContractError,RuntimeError,ValueError,KeyError,FloatingPointError) as exc:
        payload={'status':'FAIL','error':str(exc),'execution_authorized':False}; print(json.dumps(payload,indent=2,sort_keys=True) if args.json else f'FAIL: {exc}'); return 1
    print(json.dumps(payload,indent=2,sort_keys=True) if args.json else 'PASS: G0 synchronized through denied Background-3C3 review'); return 0
if __name__=='__main__': raise SystemExit(main())
