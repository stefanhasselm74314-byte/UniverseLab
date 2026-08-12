#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

REG = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_BridgeContract_v0.1.json')
PARENT = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_ProtocolFreeze_v0.1.json')


def main() -> None:
    d = json.loads(REG.read_text())
    p = json.loads(PARENT.read_text())

    assert d['bridge_id'] == 'AIP-LENS-01-NULL-N2-BRIDGE'
    assert d['parent_protocol'] == 'AIP-LENS-01-NULL-N2-PROTOCOL-FREEZE'
    assert d['baseline_main_sha'] == '6c5baa48447b61117010ba67010756c584201224'
    assert p['execution_state']['next_candidate'] == 'AIP-LENS-01-NULL-N2-BRIDGE'
    assert d['status'] == 'BRIDGE_CONTRACT_DEFINED_EXECUTABLE_VALIDATION_ONLY_PHYSICAL_SIMULATOR_NOT_YET_VALIDATED_NO_REAL_DATA_EXECUTION'

    assert d['observable_semantics']['real_data_target'] == 'KIDS1000_DR4_FIDUCIAL_COSEBIS'
    assert d['observable_semantics']['n1_toy_feature_reuse'] == 'FORBIDDEN'
    assert d['observable_semantics']['published_posterior_as_training_target'] == 'FORBIDDEN'

    stages = [x['stage'] for x in d['forward_chain']]
    assert stages == [
        'COSMOLOGY_TO_MATTER_POWER',
        'MATTER_POWER_TO_TOMOGRAPHIC_SHEAR_POWER',
        'SHEAR_POWER_TO_CORRELATION_FUNCTIONS',
        'CORRELATION_FUNCTIONS_TO_COSEBIS',
    ]
    assert 'P_delta(k,z)' in d['forward_chain'][0]['output']
    assert 'C_ell_ij' == d['forward_chain'][1]['output']
    assert 'E_n_ij' in d['forward_chain'][3]['output']
    assert 'B_n_ij' in d['forward_chain'][3]['output']

    ref = d['authoritative_reference_route']
    assert 'KCAP/CosmoSIS' in ref['implementation_family']
    assert ref['real_data_opened_in_this_bridge'] is False
    assert ref['released_posterior_chains_opened_in_this_bridge'] is False
    assert ref['exact_reference_configuration_values_frozen_here'] is False

    tr = d['simulation_training_contract']
    assert tr['real_measurements_in_training'] is False
    assert tr['real_measurements_in_calibration'] is False
    assert tr['published_best_fit_as_label'] is False
    assert tr['required_independent_partitions'] == ['TRAIN', 'VALIDATION', 'CALIBRATION', 'FINAL_SIM_TEST', 'OOD_STRESS']
    assert tr['split_leakage'] == 'FORBIDDEN'

    gates = d['physical_validation_gates']
    assert gates['B0_contract_completeness'] == 'PASS_BY_THIS_STAGE_IF_CI_GREEN'
    for key in ('B1_reference_config_hash_freeze', 'B2_forward_engine_implementation', 'B3_cross_engine_or_reference_grid_validation', 'B4_cosebis_semantic_equivalence', 'B5_independent_simulation_calibration_coverage', 'B6_domain_shift_and_ood_validation', 'B7_independent_bridge_review'):
        assert gates[key] == 'PENDING'
    assert gates['real_data_execution_authorization'] == 'BLOCKED_UNTIL_B1_THROUGH_B7_PASS'

    ex = d['execution_state']
    assert ex['bridge_contract_defined'] is True
    for key in ('physical_forward_engine_executed', 'physical_simulator_validated', 'real_dataset_downloaded', 'real_dataset_opened', 'new_ml_model_trained', 'real_data_inference_performed', 'execution_authorized'):
        assert ex[key] is False
    assert ex['next_candidate'] == 'AIP-LENS-01-NULL-N2-BRIDGE-IMPLEMENTATION-FREEZE'

    assert d['gate_disposition']['AIP-G2'] == 'NOT_PASSED_BRIDGE_CONTRACT_ONLY_NO_PHYSICAL_SIMULATOR_VALIDATION'
    assert d['gate_disposition']['AIP-G6'] == 'NOT_TESTED_REAL_DATA_EXECUTION_BLOCKED'

    gov = d['governance_firewall']
    assert gov['hzt_comparison'] is False
    assert gov['hzt_parameters_used'] is False
    assert gov['solver_state_modified'] is False
    assert gov['WP4'] == 'BLOCKED'
    assert gov['K1-D'] == 'NOT_RELEASED'
    assert gov['K1-E'] == 'NOT_ADMISSIBLE'
    assert gov['physical_evidence_effect'] == 'NONE'

    print('AIP-LENS-01-NULL-N2 bridge contract: PASS')


if __name__ == '__main__':
    main()
