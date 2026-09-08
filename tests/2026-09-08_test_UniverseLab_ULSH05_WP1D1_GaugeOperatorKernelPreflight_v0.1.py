from __future__ import annotations

import json
from pathlib import Path

REG = Path('registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json')


def load():
    return json.loads(REG.read_text(encoding='utf-8'))


def test_inherited_conditional_domain_is_explicit():
    d = load()
    assert 'registry/2026-09-08_UniverseLab_ULSH05_WP1D_ConditionalSVTGaugeConstraintReduction_v0.1.json' in d['dependencies']
    dom = d['inherited_conditional_domain']
    assert dom['name'] == 'D_cond'
    assert dom['status'] == 'FROZEN_CONDITIONAL'
    assert dom['tangential_support_finite_boundary_M4'] == 'support compactly contained in int(M4)'
    assert dom['physical_release'] is False
    assert d['quotient']['domain_source'] == 'inherited_conditional_domain'


def test_full_predecessor_gate_snapshot_is_inherited():
    g = load()['gate_state']
    assert g['WP1D_successor_identifier'] == 'FROZEN_BY_THIS_SUCCESSOR_CONTRACT'
    assert g['WP1D_analytic_field_domain'] == 'FROZEN_CONDITIONAL'
    assert g['WP1D_4D_covariant_SVT_bookkeeping'] == 'DEFINED_CONDITIONAL_PROJECTOR_KERNELS_OPEN'
    assert g['WP1D_gauge_action'] == 'DEFINED_KINEMATICALLY_WITH_INDEPENDENT_SURFACE_REPARAMETERIZATION'
    assert g['WP1D_constraint_elimination'] == 'BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING'
    assert g['WP1D_physical_3plus1_SVT'] == 'NOT_RELEASED'
    assert g['WP1D_physical_DOF_count'] == 'NOT_RELEASED'
    assert g['WP1_full_global_boundary_hessian'] == 'NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED'
    assert g['WP1_full_quadratic_action'] == 'NOT_CLOSED'
    assert g['PERTURBED_JUNCTION_SYSTEM'] == 'NOT_RELEASED'
    assert g['PHYSICAL_BACKGROUND'] == 'NOT_ESTABLISHED'
    assert g['FM-G0'] == 'OPEN'


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


def test_cokernel_requires_closed_range():
    d = load()['cokernel_registry']
    assert d['ordinary_cokernel'] == 'codomain(G)/im G'
    assert d['adjoint_identity_after_pairing_domain_freeze'] == 'ker G^dagger=(closure(im G))^perp'
    assert d['ordinary_cokernel_equals_adjoint_kernel_requires'] == 'CLOSED_RANGE_OF_G_OR_STRONGER_FREDHOLM_SETTING'
    assert d['reduced_cokernel'] == 'codomain(G)/closure(im G)'
    assert d['closed_range_status'] == 'NOT_PROVEN'
    assert d['fredholm_status'] == 'NOT_PROVEN'
    assert d['G_dagger_frozen'] is False
    assert d['count'] == 'NOT_AVAILABLE'


def test_ulsh04_handoff_is_not_constraint_closure():
    d = load()
    assert d['ulsh04_handoff']['status'] == 'DEFINED_FAIL_CLOSED'
    assert 'inherited WP1D D_cond field/domain contract' in d['ulsh04_handoff']['inputs']
    assert 'closed-range/Fredholm status of G remains unproven' in d['ulsh04_handoff']['inputs']
    assert 'physical 3+1/SVT gate remains NOT_RELEASED' in d['ulsh04_handoff']['inputs']
    g = d['gate_state']
    assert g['WP1D1_closed_range_of_G'] == 'NOT_PROVEN'
    assert g['WP1D1_Fredholm_property_of_G'] == 'NOT_PROVEN'
    assert g['WP1D_constraint_elimination'] == 'BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING'
    assert g['WP1D_physical_3plus1_SVT'] == 'NOT_RELEASED'
    assert g['WP1D_physical_DOF_count'] == 'NOT_RELEASED'


def test_physical_firewalls():
    d = load()
    assert d['solver_authorized'] is False
    assert d['physical_gate_effect'] == 'NONE'
    assert d['physical_evidence_effect'] == 'NONE'
    g = d['gate_state']
    assert g['FM-G0'] == 'OPEN'
    assert g['PHYSICAL_BACKGROUND'] == 'NOT_ESTABLISHED'
    assert g['WP1_full_quadratic_action'] == 'NOT_CLOSED'
    assert g['WP1D_constraint_elimination'] == 'BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING'
    assert g['WP1D_physical_3plus1_SVT'] == 'NOT_RELEASED'
    assert g['PERTURBED_JUNCTION_SYSTEM'] == 'NOT_RELEASED'
    assert g['PHYSICAL_RESPONSE_RANK'] == 'NOT_EXECUTED'
    assert g['K1-D'] == 'NOT_RELEASED'
    assert g['K1-E'] == 'NOT_ADMISSIBLE'
    assert g['AuthorizationDecision'] == 'NOT_CREATED'
    assert g['SingleUseGrant'] == 'NOT_CREATED'
    assert g['BACKEND_IMPORT'] == 'NOT_EXECUTED'
    assert g['SOLVER_EXECUTION'] == 'NOT_EXECUTED'


if __name__ == '__main__':
    test_inherited_conditional_domain_is_explicit()
    test_full_predecessor_gate_snapshot_is_inherited()
    test_separate_gauge_columns()
    test_columnwise_not_full_invariance()
    test_projector_zero_modes_fail_closed()
    test_cokernel_requires_closed_range()
    test_ulsh04_handoff_is_not_constraint_closure()
    test_physical_firewalls()
    print('WP1D1 gauge-operator/kernel preflight controls: PASS')
