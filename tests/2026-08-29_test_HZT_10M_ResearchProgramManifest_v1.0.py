#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
M = ROOT / 'registry/2026-08-29_UniverseLab_Hyperzeit_10M_ResearchProgramManifest_v1.0.json'
F = ROOT / 'registry/2026-08-29_HZT_M0_ForwardMap_FM0_Inventory_v0.1.json'


def main():
    m = json.loads(M.read_text(encoding='utf-8'))
    f = json.loads(F.read_text(encoding='utf-8'))

    assert m['status'] == 'ACTIVE_RATIFIED_RESEARCH_PROGRAM'
    assert m['program_horizon'] == {'start': '2026-09-01', 'end': '2027-06-30'}
    assert len(m['workstreams']) == 12

    hold = m['cp01r4_hold']
    assert hold['active'] is True and hold['through_program_horizon'] is True
    assert hold['operative_authorization_decision_created'] is False
    assert hold['single_use_grant_created'] is False
    assert hold['backend_imported'] is False and hold['solver_executed'] is False

    g = hold['gate_state']
    assert g['physical_background'] == 'NOT_ESTABLISHED'
    assert g['physical_rank_R'] == 'NOT_EXECUTED'
    assert g['WP3'] == 'NOT_STARTED'
    assert g['WP4'] == 'BLOCKED_NOT_AUTHORIZED'
    assert g['K1-D'] == 'NOT_RELEASED' and g['K1-E'] == 'NOT_ADMISSIBLE'

    assert m['program_metrics']['physical_cp01r4_executions'] == 0
    assert m['program_metrics']['operative_cp01r4_grants'] == 0
    assert m['active_start']['work_package'] == 'FM-0'

    assert f['work_package'] == 'FM-0' and f['gate_status'] == 'OPEN'
    assert f['physical_gate_effect'] == 'NONE' and f['physical_evidence_effect'] == 'NONE'
    assert all(x['parent_provenance'] == 'OPEN_RECOVERY_REQUIRED' for x in f['parameter_set_from_ratified_program'])

    print('PASS: 10M research-program ratification and FM-0 initialization preserve CP01R4 fail-closed state.')


if __name__ == '__main__':
    main()
