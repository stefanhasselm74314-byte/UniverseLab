#!/usr/bin/env python3
from __future__ import annotations
import json
import math
from pathlib import Path

REG = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N1_ResultReview_v0.1.json')


def close(a, b, tol=5e-12):
    return math.isclose(a, b, rel_tol=0.0, abs_tol=tol)


def main():
    d = json.loads(REG.read_text())
    assert d['review_id'] == 'AIP-LENS-01-NULL-N1-RESULT-REVIEW'
    assert d['status'] == 'PASS_N1_RESULT_REVIEW_SYNTHETIC_INFRASTRUCTURE_VALIDATED_N2_PROTOCOL_PREPARATION_ELIGIBLE_NO_REAL_DATA_EXECUTION'
    assert d['canonical_run']['workflow_run_id'] == 31601928296
    assert d['canonical_run']['head_sha'] == 'd7476e0e163d4267f36be0256d110937684f59e1'
    assert d['canonical_run']['run_class'] == 'CANONICAL_MAIN'
    assert d['canonical_run']['conclusion'] == 'success'
    assert d['canonical_run']['artifact_id'] == 9143456964
    assert d['canonical_run']['artifact_zip_sha256'] == 'dce854e11dadda1e0650d59ba3722c83c89cc02f94ae5ddcdf704be15a8109ce'
    integ = d['integrity']
    assert integ['expected_entry_count'] == 4
    assert integ['expected_entries_present'] is True
    assert integ['summary_and_log_byte_identical'] is True
    assert integ['split_manifest_binding_matches_summary'] is True
    assert integ['final_test_rows'] == 256
    assert integ['final_test_unique_ids'] == 256
    assert integ['final_test_id_uniqueness_pass'] is True
    assert integ['reported_failures'] == []
    assert d['independent_final_test_recomputation']['tolerance'] == 5e-12
    for target in ('Omega_m', 'S8'):
        r = d['independent_final_test_recomputation'][target]
        assert r['match_within_tolerance'] is True
        for metric in ('ml_rmse', 'bias', 'coverage68', 'coverage95', 'corr_residual_noise', 'corr_residual_ia'):
            assert close(r[f'{metric}_recomputed'], r[f'{metric}_reported'])
        assert d['reported_threshold_review'][target]['thresholds_pass'] is True
    assert d['reported_threshold_review']['ood']['thresholds_pass'] is True
    assert d['reported_threshold_review']['ood']['independently_recomputed_from_preserved_artifact'] is False
    assert d['review_findings']['physical_simulator_validation'] == 'NOT_TESTED'
    assert d['review_findings']['real_data_validation'] == 'NOT_TESTED'
    assert d['review_findings']['hzt_comparison'] == 'NOT_PERFORMED'
    assert d['review_findings']['physical_evidence_effect'] == 'NONE'
    assert d['gate_disposition']['AIP-G6'] == 'NOT_TESTED_REAL_DATA_EXECUTION_NOT_AUTHORIZED_BY_THIS_REVIEW'
    assert d['gate_disposition']['AIP-G7'] == 'NOT_REACHED'
    dec = d['decision']
    assert dec['n1_result_accepted'] is True
    assert dec['n2_protocol_preparation_eligible'] is True
    assert dec['n2_real_data_execution_authorized'] is False
    assert dec['next_candidate'] == 'AIP-LENS-01-NULL-N2-PROTOCOL-FREEZE'
    gov = d['governance_firewall']
    assert gov['new_model_training'] is False
    assert gov['real_data_execution'] is False
    assert gov['hzt_comparison'] is False
    assert gov['solver_state_modified'] is False
    assert gov['likelihood_modified'] is False
    assert gov['physical_parameters_modified'] is False
    assert gov['topology_modified'] is False
    assert gov['WP4'] == 'BLOCKED'
    assert gov['K1-D'] == 'NOT_RELEASED'
    assert gov['K1-E'] == 'NOT_ADMISSIBLE'
    assert gov['physical_evidence_effect'] == 'NONE'
    print('AIP-LENS-01-NULL-N1 result review: PASS')


if __name__ == '__main__':
    main()
