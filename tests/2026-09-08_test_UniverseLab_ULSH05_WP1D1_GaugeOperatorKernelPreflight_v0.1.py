from __future__ import annotations

import json
from pathlib import Path

REG = Path('registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json')


def load():
    return json.loads(REG.read_text(encoding='utf-8'))


def test_inherited_conditional_domain_is_explicit():
    d = load()
    assert 'registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.json' in d['dependencies']
    assert 'registry/2026-09-08_UniverseLab_ULSH05_WP1D_ConditionalSVTGaugeConstraintReduction_v0.1.json' in d['dependencies']
    dom = d['inherited_conditional_domain']
    assert dom['name'] == 'D_cond'
    assert dom['status'] == 'FROZEN_CONDITIONAL'
    assert dom['tangential_support_finite_boundary_M4'] == 'support compactly contained in int(M4)'
    assert dom['physical_release'] is False
    assert d['quotient']['domain_source'] == 'inherited_conditional_domain'


def test_upstream_boundary_gate_snapshot_is_inherited():
    g = load()['gate_state']
    assert g['WP1_boundary_residual_linearizations'] == 'COMPONENTIZED_LOCAL_INTERFACE_OPERATOR'
    assert g['WP1_local_weak_boundary_hessian'] == 'SYMMETRIC_ON_DECLARED_TEST_DOMAIN'
    assert g['WP1_global_domain_preflight'] == 'COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE'
    assert g['WP1_physical_boundary_domain'] == 'BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA'
    assert g['WP1_full_global_boundary_hessian'] == 'NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED'


def test_full_predecessor_gate_snapshot_is_inherited():
    g = load()['gate_state']
    assert g['WP1D_successor_identifier'] == 'FROZEN_BY_THIS_SUCCESSOR_CONTRACT'
    assert g['WP1D_analytic_field_domain'] == 'FROZEN_CONDITIONAL'
    assert g['WP1D_4D_covariant_SVT_bookkeeping'] == 'DEFINED_CONDITIONAL_PROJECTOR_KERNELS_OPEN'
    assert g['WP1D_gauge_action'] == 'DEFINED_KINEMATICALLY_WITH_INDEPENDENT_SURFACE_REPARAMETERIZATION'
    assert g['WP1D_constraint_elimination'] == 'BLOCKED_BY_ULSH04_AND_UNFROZEN_PHYSICAL_TIME_SLICING'
    assert g['WP1D_physical_3plus1_SVT'] == 'NOT_RELEASED'
    assert g['WP1D_physical_DOF_count'] == 'NOT_RELEASED'
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


def test_interface_rows_are_componentized():
    d = load()
    g = d['gauge_operator']
    assert g['row_completeness'] == 'ALL_DECLARED_BULK_INTERFACE_PRIMARY_AND_DERIVED_OR_GENERIC_PULLBACK_ROWS_HAVE_COLUMN_ACTIONS'
    assert d['field_space']['interface_primary'] == ['s', 'xi_shape', 'tau_a']
    assert d['field_space']['interface_derived_or_pullback_rows'] == ['H_ab', 'Acal_a', 'd_a', 'generic_moving_pullback_DeltaSigma_T']
    z = g['bulk_diffeomorphism']['interface_rows']
    assert z['xi_shape'] == 'delta xi_shape=-zeta_perp'
    assert z['tau_a'] == 'delta tau_a=-zeta_parallel_a'
    assert z['cap_phase_s_direct'] == 'delta s=0 for the pure bulk-diffeomorphism column in the independent intrinsic surface-field representation'
    assert z['induced_metric_H_ab'] == 'delta H_ab=0'
    assert z['pulled_gauge_oneform_Acal_a'] == 'delta Acal_a=0 under the paired pure bulk-diffeomorphism/embedding transformation'
    assert z['cap_oneform_d_a'] == 'delta d_a=0 under the paired pure bulk-diffeomorphism/embedding transformation'
    assert z['generic_moving_pullback_DeltaSigma_T'] == 'delta_zeta DeltaSigma(X* T)=0 under the paired bulk-field/embedding diffeomorphism convention'
    u = g['u1']['interface_rows']
    assert u['xi_shape'] == '0'
    assert u['tau_a'] == '0'
    assert u['induced_metric_H_ab'] == '0'
    assert u['pulled_gauge_oneform_Acal_a'] == 'delta Acal_a=D_a lambda'
    assert u['cap_phase_s'] == 'delta s=q_sigma lambda'
    assert u['cap_oneform_d_a'] == 'delta d_a=0'
    r = g['intrinsic_interface_reparametrization']['interface_rows']
    assert r['xi_shape'] == 'delta xi_shape=0'
    assert r['tau_a'] == 'delta tau^a=rho^a'
    assert r['induced_metric_H_ab'] == 'delta H_ab=Lie_rho hbar_ab=2 D_(a rho_b)'
    assert r['cap_phase_s'] == 'delta s=rho^a D_a sigma_bar'
    assert r['pulled_gauge_oneform_Acal_a'] == 'delta Acal_a=(Lie_rho Abarcal)_a'
    assert r['cap_oneform_d_a'] == 'delta d_a=(Lie_rho wbar)_a with wbar_a=D_a sigma_bar-q_sigma Abarcal_a'
    assert d['gate_state']['WP1D1_gauge_operator_interface_rows'] == 'COMPONENTIZED_ALL_DECLARED_ROWS'


def test_columnwise_not_full_invariance():
    d = load()['columnwise_invariants']
    assert d['selected_not_exhaustive'] is True
    assert d['H_ab_under_bulk_diffeomorphism'] == 'PROVEN_G_zeta_H_EQUALS_ZERO'
    assert d['d_a_under_bulk_diffeomorphism'] == 'PROVEN_G_zeta_d_EQUALS_ZERO_FROM_PAIRED_MOVING_PULLBACK_RULE'
    assert d['d_a_under_u1'] == 'PROVEN_G_lambda_d_EQUALS_ZERO'
    assert d['H_ab_under_full_G'] == 'NOT_INVARIANT_IN_GENERAL_RHO_COLUMN_NONZERO'
    assert d['d_a_under_full_G'] == 'NOT_INVARIANT_IN_GENERAL_RHO_COLUMN_NONZERO'


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
    assert 'exact upstream physical boundary-domain blocker remains unresolved' in d['ulsh04_handoff']['inputs']
    assert 'G_zeta G_lambda G_rho separated operator including all declared interface primary/derived rows and generic pullback rule' in d['ulsh04_handoff']['inputs']
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
    assert g['WP1_physical_boundary_domain'] == 'BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA'
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
    test_upstream_boundary_gate_snapshot_is_inherited()
    test_full_predecessor_gate_snapshot_is_inherited()
    test_separate_gauge_columns()
    test_interface_rows_are_componentized()
    test_columnwise_not_full_invariance()
    test_projector_zero_modes_fail_closed()
    test_cokernel_requires_closed_range()
    test_ulsh04_handoff_is_not_constraint_closure()
    test_physical_firewalls()
    print('WP1D1 gauge-operator/kernel preflight controls: PASS')
