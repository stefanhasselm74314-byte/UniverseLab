from __future__ import annotations

import json
from pathlib import Path

REG = Path('registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json')


def load():
    return json.loads(REG.read_text(encoding='utf-8'))


def test_separate_gauge_columns():
    d = load()
    g = d['gauge_operator']
    assert g['form'] == 'G=(G_zeta,G_lambda,G_rho)'
    assert g['columns_separated'] is True
    assert g['intrinsic_interface_reparametrization']['independent_of_zeta_parallel'] is True


def test_columnwise_not_full_invariance():
    d = load()['columnwise_invariants']
    assert d['H_ab_under_bulk_diffeomorphism'] == 'PROVEN_G_zeta_H_EQUALS_ZERO'
    assert d['d_a_under_u1'] == 'PROVEN_G_lambda_d_EQUALS_ZERO'
    assert d['H_ab_under_full_G'] == 'NOT_INVARIANT_IN_GENERAL_RHO_COLUMN_NONZERO'
    assert d['d_a_under_full_G'] == 'NOT_CLAIMED'


def test_projector_zero_modes_fail_closed():
    d = load()['kernel_registry']
    assert d['global_inverse_frozen'] is False
    assert d['projector_zero_mode_implies_gauge_mode'] is False
    assert d['ker_G'] == 'BACKGROUND_AND_DOMAIN_DEPENDENT_NOT_COUNTED'


def test_cokernel_not_claimed():
    d = load()['cokernel_registry']
    assert d['G_dagger_frozen'] is False
    assert d['count'] == 'NOT_AVAILABLE'


def test_ulsh04_handoff_is_not_constraint_closure():
    d = load()
    assert d['ulsh04_handoff']['status'] == 'DEFINED_FAIL_CLOSED'
    g = d['gate_state']
    assert g['WP1D_constraint_elimination'] == 'BLOCKED'
    assert g['WP1D_physical_DOF_count'] == 'NOT_RELEASED'


def test_physical_firewalls():
    d = load()
    assert d['solver_authorized'] is False
    assert d['physical_gate_effect'] == 'NONE'
    assert d['physical_evidence_effect'] == 'NONE'
    g = d['gate_state']
    assert g['PHYSICAL_BACKGROUND'] == 'NOT_ESTABLISHED'
    assert g['WP1_physical_boundary_domain'] == 'BLOCKED'
    assert g['WP1_full_quadratic_action'] == 'NOT_CLOSED'
    assert g['PERTURBED_JUNCTION_SYSTEM'] == 'NOT_RELEASED'
    assert g['PHYSICAL_RESPONSE_RANK'] == 'NOT_EXECUTED'
    assert g['K1-D'] == 'NOT_RELEASED'
    assert g['K1-E'] == 'NOT_ADMISSIBLE'
    assert g['AuthorizationDecision'] == 'NOT_CREATED'
    assert g['SingleUseGrant'] == 'NOT_CREATED'
    assert g['BACKEND_IMPORT'] == 'NOT_EXECUTED'
    assert g['SOLVER_EXECUTION'] == 'NOT_EXECUTED'


if __name__ == '__main__':
    test_separate_gauge_columns()
    test_columnwise_not_full_invariance()
    test_projector_zero_modes_fail_closed()
    test_cokernel_not_claimed()
    test_ulsh04_handoff_is_not_constraint_closure()
    test_physical_firewalls()
    print('WP1D1 gauge-operator/kernel preflight controls: PASS')
