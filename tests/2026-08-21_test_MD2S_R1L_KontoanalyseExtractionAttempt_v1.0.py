#!/usr/bin/env python3
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry/2026-08-21_MD2S_R1L_KontoanalyseExtractionAttempt_v1.0.json'
REP=ROOT/'recovery/2026-08-21_MD2S_R1L_KontoanalyseExtractionAttempt_v1.0.md'
UUID_RE=re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
LOCKED={
 'official_MD2S_solver':'NOT_AUTHORIZED',
 'PHYSICAL_BACKGROUND':'NOT_ESTABLISHED',
 'K1-D':'NOT_RELEASED',
 'K1-E':'NOT_ADMISSIBLE',
 'physical_evidence_effect':'NONE',
 'physical_gate_effect':'NONE'
}

def main():
    raw=REG.read_text(encoding='utf-8')
    data=json.loads(raw)
    assert data['schema']=='universelab.md2s.r1l.kontoanalyse-extraction-attempt.v1'
    assert data['status']=='SCOPED_MESSAGE_LEVEL_EXTRACTION_BLOCKED_SOURCE_BYTES_NOT_SURFACED'
    assert data['chat_target']['title']=='Kontoanalyse ChatGPT'
    assert data['chat_target']['later_export_last_modified_date']=='2026-08-18'
    assert data['chat_target']['private_conversation_identifier_committed'] is False
    fs=data['file_library_date_slice']
    assert fs['date']=='2026-08-18'
    assert fs['navigation_result_count']==1
    assert fs['only_surfaced_file']=='MD2S_Randdaten_Benchmark_RECOVERY_2026-08-18_SHA256.txt'
    assert fs['zip_bytes_surfaced'] is False
    assert fs['raw_message_transcript_surfaced'] is False
    pkg=data['recovery_package_integrity_record']
    assert pkg['size_bytes']==14884
    assert pkg['zip_entries']==12
    assert pkg['integrity_test']=='PASS'
    assert pkg['sha256']=='dbee345414409f29f6fee5cc161807fd3f8a2d4b337460d3cf9bb8a307c3dff9'
    assert pkg['content_independently_verified_from_zip_bytes'] is False
    assert data['classification_effect']['B1.4K']=='E4_UNVERIFIED_HISTORICAL_CHAT_REPORT'
    assert data['classification_effect']['B1.4L']=='E4_UNVERIFIED_HISTORICAL_CHAT_REPORT'
    assert data['classification_effect']['verified_solver_output_established'] is False
    assert data['historical_missing_interface_fields']==['A_prime_bulk','A_prime_cap','Lprime_over_L_bulk','Lprime_over_L_cap']
    assert data['governance']==LOCKED
    report=REP.read_text(encoding='utf-8')
    assert 'SCOPED_MESSAGE_LEVEL_EXTRACTION_BLOCKED_SOURCE_BYTES_NOT_SURFACED' in report
    assert 'VERIFIED_HISTORICAL_TRANSCRIPT_REPORT' in report
    assert 'VERIFIED_SOLVER_OUTPUT' in report
    assert UUID_RE.search(raw) is None
    assert UUID_RE.search(report) is None
    print('PASS_MD2S_R1L_KONTOANALYSE_EXTRACTION_ATTEMPT')

if __name__=='__main__':
    main()
