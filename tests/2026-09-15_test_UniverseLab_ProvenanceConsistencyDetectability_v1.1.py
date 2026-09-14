#!/usr/bin/env python3
"""Documentation consistency checks, not a scientific evidence evaluator."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'registry/2026-09-14_UniverseLab_ProvenanceConsistencyDetectabilityContract_v1.1.json'


def validate(contract: dict, markdown: str) -> None:
    fields = contract['evidence_record_required_fields']
    assert len(fields) == len(set(fields)), 'duplicate required fields'
    dates = {'source_version_date', 'observation_date', 'publication_date', 'retrieval_date'}
    assert dates <= set(fields), ('missing separate date', dates - set(fields))
    assert 'observation_publication_and_retrieval_dates' not in fields
    assert 'Versions-, Beobachtungs-, Publikations- und Abrufdatum werden getrennt' in markdown
    rules = contract['rules']
    for key in ('automatic_geometry_priority', 'universal_echo_requirement',
                'universal_counterimage_requirement', 'missing_test_means_pass',
                'double_count_fit_data_as_independent_evidence'):
        assert rules[key] is False, key
    assert contract['gate_inheritance']['is_gate_snapshot'] is False
    assert contract['gate_inheritance']['overrides'] == {}
    assert contract['gate_inheritance']['read_entire_applicable_canonical_contract'] is True
    effects = contract['effects']
    assert effects['physical_gate_effect'] == 'NONE'
    assert effects['physical_evidence_effect'] == 'NONE'
    for key in ('solver_authorized', 'creates_authorization_decision', 'creates_single_use_grant',
                'authorizes_backend_import', 'authorizes_physical_solver_execution', 'assigns_ulsh_successor'):
        assert effects[key] is False, key
    assert contract['technical_clarifications']['status'] == 'EDITORIAL_PROPOSALS_NOT_SEPARATE_USER_RATIFICATION'
    assert contract['a1_baseline']['primary_version_verified_at_creation'] is False
    assert contract['implementation']['global_pipeline_enforcement'] is False
    assert contract['implementation']['automatic_evidence_evaluator'] is False


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))
    document = ROOT / contract['document']
    assert document.is_file(), document
    assert (ROOT / contract['gate_inheritance']['source']).is_file()
    markdown = document.read_text(encoding='utf-8')
    validate(contract, markdown)
    # Mutations must fail: absent date is not saved by generic unknown-field rules.
    for field in ('source_version_date', 'observation_date', 'publication_date', 'retrieval_date'):
        broken = json.loads(json.dumps(contract))
        broken['evidence_record_required_fields'].remove(field)
        try:
            validate(broken, markdown)
        except AssertionError:
            pass
        else:
            raise AssertionError(f'undetected missing required field: {field}')
    print('PASS documentation contract plus four missing-date mutations; no physical inference')


if __name__ == '__main__':
    main()
