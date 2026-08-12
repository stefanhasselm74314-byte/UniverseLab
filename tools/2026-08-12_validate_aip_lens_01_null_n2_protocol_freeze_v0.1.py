#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

REG = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_ProtocolFreeze_v0.1.json')


def main() -> None:
    d = json.loads(REG.read_text())
    assert d['protocol_id'] == 'AIP-LENS-01-NULL-N2-PROTOCOL-FREEZE'
    assert d['parent_review'] == 'AIP-LENS-01-NULL-N1-RESULT-REVIEW'
    assert d['baseline_main_sha'] == 'fec2a378e3765610af7ad5852b5f834ca196cb39'
    assert d['status'] == 'FROZEN_REAL_DATA_TARGET_IDENTIFIED_EXECUTION_BLOCKED_PENDING_PHYSICAL_SIMULATOR_FEATURE_BRIDGE_AND_SEPARATE_AUTHORIZATION'

    ds = d['dataset']
    assert ds['dataset_id'] == 'KIDS1000_DR4_COSMIC_SHEAR_ASGARI2021'
    assert ds['release'] == 'KiDS-1000 / KiDS-DR4'
    assert ds['official_package_filename'] == 'KiDS1000_cosmic_shear_data_release.tgz'
    assert ds['paper']['arxiv'] == '2007.15633v2'
    assert ds['paper']['journal'] == 'A&A 645, A104 (2021)'
    assert ds['paper']['doi'] == '10.1051/0004-6361/202039070'
    assert ds['survey_area_deg2'] == 1006
    assert ds['usage_terms']['formal_open_license_claimed'] is False
    assert ds['usage_terms']['publication_acknowledgement_required'] is True

    obs = d['frozen_observable_scope']
    assert obs['primary_statistic'] == 'COSEBIs'
    assert obs['targets'] == ['S8', 'Omega_m']
    assert 'posterior chains as training labels' in ' '.join(obs['forbidden_inputs_during_method_construction']).lower()

    baseline = d['reference_non_ml_baseline']
    assert baseline['type'] == 'KIDS1000_FIDUCIAL_COSEBIS_REFERENCE_PIPELINE'
    assert baseline['role'] == 'AUTHORITATIVE_REAL_DATA_REPRODUCTION_BASELINE'
    assert baseline['use_of_published_reference'] == 'POST_EXECUTION_COMPARISON_ONLY'
    assert baseline['baseline_must_be_reproduced_before_ml_real_data_claim'] is True

    blind = d['blinding_and_leakage_control']
    assert blind['strict_discovery_blinding_possible'] is False
    assert len(blind['procedural_controls']) >= 5

    fw = d['n1_to_n2_transfer_firewall']
    assert fw['n1_physical_simulator'] is False
    assert fw['n1_feature_semantics_compatible_with_kids_cosebis'] is False
    assert fw['n1_weights_reusable_on_real_kids_data'] is False
    assert fw['n1_model_direct_application_to_real_data'] == 'FORBIDDEN'
    assert fw['required_bridge'] == 'AIP-LENS-01-NULL-N2-BRIDGE'
    assert len(fw['bridge_requirements']) >= 9

    exec_state = d['execution_state']
    assert exec_state['dataset_downloaded_by_this_protocol'] is False
    assert exec_state['real_data_opened_by_this_protocol'] is False
    assert exec_state['new_model_trained_by_this_protocol'] is False
    assert exec_state['real_data_inference_performed'] is False
    assert exec_state['execution_authorized'] is False
    assert exec_state['next_candidate'] == 'AIP-LENS-01-NULL-N2-BRIDGE'
    assert exec_state['subsequent_required_gate'] == 'AIP-LENS-01-NULL-N2-EXECUTION-AUTHORIZATION'

    gates = d['gate_disposition']
    assert gates['AIP-G2'] == 'PHYSICAL_SIMULATOR_VALIDATION_NOT_YET_PASSED'
    assert gates['AIP-G6'] == 'NOT_TESTED_REAL_DATA_EXECUTION_BLOCKED'
    assert gates['AIP-G7'] == 'NOT_REACHED'

    gov = d['governance_firewall']
    assert gov['hzt_comparison'] is False
    assert gov['hzt_parameters_used'] is False
    assert gov['solver_state_modified'] is False
    assert gov['likelihood_modified'] is False
    assert gov['physical_parameters_modified'] is False
    assert gov['topology_modified'] is False
    assert gov['WP4'] == 'BLOCKED'
    assert gov['K1-D'] == 'NOT_RELEASED'
    assert gov['K1-E'] == 'NOT_ADMISSIBLE'
    assert gov['physical_evidence_effect'] == 'NONE'

    forbidden = set(d['forbidden_inferences'])
    assert 'NO_DIRECT_N1_TOY_MODEL_APPLICATION_TO_KIDS_REAL_DATA' in forbidden
    assert 'NO_REAL_DATA_EXECUTION_WITHOUT_N2_BRIDGE_AND_SEPARATE_AUTHORIZATION' in forbidden
    assert 'NO_N2_CONTROL_RESULT_AS_HZT_SUPPORT_OR_EVIDENCE' in forbidden

    print('AIP-LENS-01-NULL-N2 protocol freeze: PASS')


if __name__ == '__main__':
    main()
