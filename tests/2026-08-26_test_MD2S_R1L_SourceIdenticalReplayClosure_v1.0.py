#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry/2026-08-26_MD2S_R1L_SourceIdenticalReplayClosure_v1.0.json'
REP=ROOT/'recovery/2026-08-26_MD2S_R1L_SourceIdenticalReplayClosure_v1.0.md'
LOCKED={
 'official_MD2S_solver':'NOT_AUTHORIZED',
 'PHYSICAL_BACKGROUND':'NOT_ESTABLISHED',
 'K1-D':'NOT_RELEASED',
 'K1-E':'NOT_ADMISSIBLE',
 'physical_evidence_effect':'NONE',
 'physical_gate_effect':'NONE'
}

def main():
    data=json.loads(REG.read_text(encoding='utf-8'))
    assert data['schema']=='universelab.md2s.r1l.source-identical-replay-closure.v1'
    assert data['status']=='TARGETS_NARROWED_REPLAY_STILL_BLOCKED'
    cur=data['current_recovery_state']
    assert cur['B1.4F']=='PRIMARY_ARTIFACT_RECOVERED_MANIFEST_VALID'
    assert cur['B1.4G']=='PRIMARY_ARTIFACT_RECOVERED_MANIFEST_VALID'
    assert 'NUMERIC_REPRODUCTION_PASS' in cur['B1.4K']
    assert 'NUMERIC_REPRODUCTION_PASS' in cur['B1.4L']
    assert cur['source_identical_two_junction_replay']=='BLOCKED'
    p=data['newly_resolved_exact_prerequisite_package_names']
    assert p['B1.4E']['package']=='HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip'
    assert p['B1.4H']['package']=='HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1_PACKAGE.zip'
    assert p['B1.4E']['binary_currently_recovered'] is False
    assert p['B1.4H']['binary_currently_recovered'] is False
    req=set(data['remaining_source_identical_requirements'])
    for marker in ['A_prime_bulk','A_prime_cap','Lprime_over_L_bulk','Lprime_over_L_cap']:
        assert marker in req
    assert data['promotion_firewall']['chat_reference_is_not_binary_recovery'] is True
    assert data['promotion_firewall']['later_rebuild_or_C1_data_may_fill_historical_missing_fields'] is False
    assert data['promotion_firewall']['interpolation_may_be_labeled_historical_original'] is False
    assert data['governance']==LOCKED
    report=REP.read_text(encoding='utf-8')
    assert 'HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip' in report
    assert 'HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1_PACKAGE.zip' in report
    assert 'TARGETS_NARROWED_REPLAY_STILL_BLOCKED' in report
    print('PASS_MD2S_R1L_SOURCE_IDENTICAL_REPLAY_CLOSURE')

if __name__=='__main__':
    main()
