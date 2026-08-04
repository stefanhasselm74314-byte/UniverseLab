#!/usr/bin/env python3
"""Regression tests for G0 v1.14 denied-authorization state."""
from __future__ import annotations
import copy, importlib.util, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'tools/2026-08-04_validate_g0_three_track_sync_v1.14.py'
SPEC=importlib.util.spec_from_file_location('g0_v1_14',TOOL)
if SPEC is None or SPEC.loader is None: raise RuntimeError('unable to import G0 v1.14 validator')
MOD=importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name]=MOD; SPEC.loader.exec_module(MOD)

def expect_failure(function,phrase):
    try: function()
    except MOD.ContractError as exc:
        assert phrase in str(exc),(phrase,str(exc)); return
    raise AssertionError(f'expected ContractError containing: {phrase}')

def test_repository_state_passes():
    result=MOD.validate(); assert result['status']=='PASS'; assert result['review_outcome']=='DENIED_MISSING_EXECUTION_PACKAGE'
    assert result['decision']=='UL-DEC-0029'; assert result['execution_authorized'] is False
    assert result['solver_executed'] is False; assert result['result_artifact_created'] is False; assert result['physical_evidence_effect']=='NONE'

def test_manifest_rejects_authorization_opening():
    manifest=MOD.load_json('project-manifest.json'); changed=copy.deepcopy(manifest)
    changed['gates']['BACKGROUND_3C_EXECUTION']='AUTHORIZED'; expect_failure(lambda: MOD.validate_manifest(changed),'BACKGROUND_3C_EXECUTION')

def test_manifest_rejects_runner_overclaim():
    manifest=MOD.load_json('project-manifest.json'); changed=copy.deepcopy(manifest)
    changed['c_phys_background_3c']['execution_runner']='PASS'; expect_failure(lambda: MOD.validate_manifest(changed),'execution_runner')

def test_checkpoint_rejects_background_overclaim():
    checkpoint=MOD.load_json(MOD.CHECKPOINT); changed=copy.deepcopy(checkpoint)
    changed['gate_state']['PHYSICAL_BACKGROUND']='ESTABLISHED'; expect_failure(lambda: MOD.validate_checkpoint(changed),'PHYSICAL_BACKGROUND')

def test_manifest_rejects_next_block_drift():
    manifest=MOD.load_json('project-manifest.json'); changed=copy.deepcopy(manifest)
    changed['c_phys_background_3c']['next_block']='EXECUTE_NOW'; expect_failure(lambda: MOD.validate_manifest(changed),'next block')

def main():
    test_repository_state_passes(); test_manifest_rejects_authorization_opening(); test_manifest_rejects_runner_overclaim(); test_checkpoint_rejects_background_overclaim(); test_manifest_rejects_next_block_drift()
    print('PASS: G0 v1.14 canonical regression tests'); return 0
if __name__=='__main__': raise SystemExit(main())
