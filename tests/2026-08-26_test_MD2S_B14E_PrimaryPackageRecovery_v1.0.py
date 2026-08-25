#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/'registry/2026-08-26_MD2S_R1L_ForensicEvidenceRegister_v1.6.json'
REP=ROOT/'recovery/2026-08-26_MD2S_B14E_PrimaryPackageRecovery_v1.0.md'
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
    assert data['version']=='1.6.0'
    assert 'EFGHKL' in data['status']
    e=data['B1.4E']
    assert e['historical_expected_package_name']=='HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1_PACKAGE.zip'
    assert e['recovered_uploaded_filename']=='HZT_MD2S_B1_4E_SMOOTH_TARGET_REPAIR_v0_1.zip'
    assert e['outer_filename_variation_from_historical_link'] is True
    assert e['outer_zip_byte_identity_to_historical_wrapper_independently_established'] is False
    assert e['recovered_zip_size_bytes']==2770104
    assert e['recovered_zip_sha256']=='31b80fe24dcb45822b2edb8f24bf83ead40bc05d41b5080f9da8fcd528965c1b'
    assert e['zip_crc_status']=='PASS'
    assert e['internal_manifest_entries']==11
    assert e['internal_manifest_hashes_valid']==11
    assert e['internal_manifest_hashes_invalid']==0
    c=e['selected_independent_checks']
    assert abs(c['patch_delta_q2_recomputed']-c['patch_delta_q2_reported'])<1e-15
    assert abs(c['target_curvature_from_minus_6_c3_recomputed']-c['target_curvature_reported'])<1e-15
    assert abs(c['cap_global_minimum_recomputed']-c['cap_global_minimum_reported'])<1e-15
    assert abs(c['minimum_P_over_r2_recomputed']-c['minimum_P_over_r2_reported'])<1e-15
    assert abs(c['minimum_Q_over_r2_recomputed']-c['minimum_Q_over_r2_reported'])<1e-15
    assert abs(c['scalar_residual_max_r_ge_1e_minus_3_recomputed']-c['scalar_residual_max_reported'])<1e-18
    assert abs(c['scalar_residual_rms_r_ge_1e_minus_3_recomputed']-c['scalar_residual_rms_reported'])<1e-18
    assert c['partial_spectra_cross_file_max_abs_difference']<1e-12
    assert e['reproduction_limit']['generation_solver_code_present'] is False
    assert e['reproduction_limit']['archived_profiles_recomputed_from_field_equations'] is False
    assert data['promotion_firewall']['B1.4E_recovery_closes_E_package_gap'] is True
    assert data['promotion_firewall']['B1.4E_and_B1.4H_package_gaps_both_closed'] is True
    assert data['current_recovery_state']['source_identical_two_junction_replay']=='BLOCKED'
    assert data['governance']==LOCKED
    text=REP.read_text(encoding='utf-8')
    assert '11/11' in text
    assert 'A_prime_bulk' in text and 'Lprime_over_L_cap' in text
    assert 'full solver re-execution' in text
    print('PASS_MD2S_B14E_PRIMARY_PACKAGE_RECOVERY')

if __name__=='__main__':
    main()
