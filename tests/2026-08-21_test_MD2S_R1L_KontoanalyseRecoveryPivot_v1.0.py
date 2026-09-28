#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / 'registry/2026-08-21_MD2S_R1L_KontoanalyseRecoveryPivot_v1.0.json'
REP = ROOT / 'recovery/2026-08-21_MD2S_R1L_KontoanalyseRecoveryPivot_v1.0.md'
LOCKED = {
    'official_MD2S_solver':'NOT_AUTHORIZED',
    'PHYSICAL_BACKGROUND':'NOT_ESTABLISHED',
    'K1-D':'NOT_RELEASED',
    'K1-E':'NOT_ADMISSIBLE',
    'physical_evidence_effect':'NONE',
    'physical_gate_effect':'NONE',
}
UUID_RE = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')

def walk_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield str(key)
            yield from walk_keys(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_keys(value)

def main():
    reg_text=REG.read_text(encoding='utf-8')
    data=json.loads(reg_text)
    assert data['schema']=='universelab.md2s.r1l.kontoanalyse-recovery-pivot.v1'
    assert data['version']=='1.0.0'
    assert data['status']=='HIGH_PRIORITY_RECOVERY_PIVOT_IDENTIFIED'
    h=data['source_evidence']['historical_snapshot']
    l=data['source_evidence']['later_export_snapshot']
    assert h['title']==l['title']=='Kontoanalyse ChatGPT'
    assert (h['snapshot_user_messages'],h['snapshot_assistant_messages'],h['snapshot_mapping_nodes'])==(3,9,31)
    assert (l['user_messages'],l['assistant_messages'],l['mapping_nodes'])==(15,29,109)
    assert l['last_modified_date']=='2026-08-18'
    assert l['private_conversation_identifier_committed'] is False
    p=data['source_evidence']['recovery_package_integrity_record']
    assert p['size_bytes']==14884 and p['zip_entries']==12
    assert p['integrity_test']=='PASS'
    assert p['sha256']=='dbee345414409f29f6fee5cc161807fd3f8a2d4b337460d3cf9bb8a307c3dff9'
    assert p['package_bytes_recovered_in_current_file_search'] is False
    assert data['evidence_hygiene']['chat_transcript_alone_may_establish_verified_solver_output'] is False
    assert data['evidence_hygiene']['recovery_package_checksum_alone_proves_package_contents'] is False
    assert data['governance']==LOCKED

    text=REP.read_text(encoding='utf-8')
    assert 'No private conversation identifier is stored' in text
    assert 'verified historical transcript report' in text

    # Privacy guard: no direct conversation-ID field and no UUID-shaped identifier
    # may be embedded in these public provenance artifacts. Descriptive boolean
    # fields such as private_conversation_identifier_committed are allowed.
    normalized_keys={k.lower().replace('-', '_') for k in walk_keys(data)}
    assert 'conversation_id' not in normalized_keys
    assert UUID_RE.search(reg_text) is None
    assert UUID_RE.search(text) is None

    print('PASS_MD2S_R1L_KONTOANALYSE_RECOVERY_PIVOT')

if __name__=='__main__':
    main()
