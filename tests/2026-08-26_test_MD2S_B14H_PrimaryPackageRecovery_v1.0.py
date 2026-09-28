#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry/2026-08-26_MD2S_R1L_ForensicEvidenceRegister_v1.5.json'
REP=ROOT/'recovery/2026-08-26_MD2S_B14H_PrimaryPackageRecovery_v1.0.md'
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
    assert data['version']=='1.5.0'
    assert 'FGHKL' in data['status']
    h=data['B1.4H']
    assert h['historical_expected_package_name']=='HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1_PACKAGE.zip'
    assert h['recovered_uploaded_filename']=='HZT_MD2S_B1_4H_RADION_STABILIZED_DESIGN_v0_1.zip'
    assert h['outer_filename_variation_from_historical_link'] is True
    assert h['outer_zip_byte_identity_to_historical_wrapper_independently_established'] is False
    assert h['recovered_zip_size_bytes']==55066
    assert h['recovered_zip_sha256']=='a73210f41362a00b69e169e424da9b8cdba790f0573a1d651cdfeb5d01837f7d'
    assert h['zip_crc_status']=='PASS'
    assert h['payload_file_count']==14
    assert h['internal_manifest_entries']==14
    assert h['internal_manifest_hashes_valid']==14
    assert h['internal_manifest_hashes_invalid']==0
    checks=h['selected_independent_checks']
    assert checks['benchmark_spectrum_cross_file_match_max_abs']==0.0
    assert abs(checks['regulator_spread_recomputed']-checks['regulator_spread_reported'])<1e-18
    assert abs(checks['margin_above_critical_fraction_recomputed']-checks['margin_above_critical_fraction_reported'])<1e-15
    for a,b in zip(checks['canonical_total_Hessian_eigenvalues_recomputed'],checks['canonical_total_Hessian_eigenvalues_reported']):
        assert abs(a-b)<1e-14
    assert checks['zero_threshold_row_present_at_critical_kappa'] is True
    assert h['reproduction_limit']['determinant_shooting_or_generation_solver_code_present'] is False
    assert h['reproduction_limit']['archived_spectrum_recomputed_from_field_equations'] is False
    assert data['current_recovery_state']['B1.4E']=='HISTORICAL_PACKAGE_NAME_RECOVERED_BINARY_NOT_YET_RECOVERED'
    assert data['current_recovery_state']['source_identical_two_junction_replay']=='BLOCKED'
    assert data['promotion_firewall']['B1.4H_recovery_closes_H_package_gap'] is True
    assert data['promotion_firewall']['B1.4H_recovery_closes_source_identical_two_junction_replay'] is False
    assert data['governance']==LOCKED
    text=REP.read_text(encoding='utf-8')
    assert '14/14' in text
    assert 'not' in text.lower() and 'solver' in text.lower()
    assert 'HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip' in text
    print('PASS_MD2S_B14H_PRIMARY_PACKAGE_RECOVERY')

if __name__=='__main__':
    main()
