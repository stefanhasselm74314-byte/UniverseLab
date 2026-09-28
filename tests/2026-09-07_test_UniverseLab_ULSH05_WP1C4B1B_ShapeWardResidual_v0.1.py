#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'registry/2026-09-07_UniverseLab_ULSH05_WP1C4B1B_ShapeWardResidual_v0.1.json'
DOC = ROOT / 'science/solver-hub/2026-09-07_UniverseLab_ULSH05_WP1C4B1B_ShapeWardResidual_v0.1.md'


def main() -> None:
    d = json.loads(CONTRACT.read_text())
    text = DOC.read_text()

    assert d['model_id'] == 'HZT-M0-S6-C-PHYS-M1'
    assert d['work_package'] == 'ULSH-05/WP1C4B1B'
    assert d['status'] == 'DERIVED_CONDITIONAL_SHAPE_REDUNDANCY_FULL_COMPONENT_SHAPE_RESIDUAL_NOT_ASSEMBLED'
    assert d['diffeomorphism_ward_contract']['conditional_redundancy'].startswith('if every regional bulk Euler-Lagrange residual')
    assert 'Israel alone does not imply R_perp=0' in d['diffeomorphism_ward_contract']['critical_nonimplications']
    assert d['passive_equation_status']['component_formula'] == 'NOT_FROZEN'
    assert d['gate_state']['WP1_shape_Ward_identity'] == 'DERIVED_CONDITIONAL_REDUNDANCY'
    assert d['gate_state']['WP1_full_shape_residual'] == 'NOT_ASSEMBLED_COMPONENTWISE'

    # Dependency closure is contract-driven: every declared dependency must exist.
    deps = d.get('dependencies')
    assert isinstance(deps, list) and len(deps) == 5, deps
    assert len(deps) == len(set(deps)), deps
    for rel in deps:
        path = ROOT / rel
        assert path.is_file(), path

    required_dependencies = {
        'registry/2026-09-07_UniverseLab_ULSH05_WP1C4A_GluingNormalFluxJunctions_v0.1.json',
        'registry/2026-09-07_UniverseLab_ULSH05_WP1C4B0_SecondOrderEmbeddingPathContract_v0.1.json',
        'registry/2026-09-07_UniverseLab_ULSH05_WP1C4B1A_MovingDomainTransportMaster_v0.1.json',
        'registry/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.json',
        'science/hzt-m0/md2s/2026-08-03_MD2S_BulkLocalizedActionAndJunctionLedger_v0.1.md',
    }
    assert set(deps) == required_dependencies, (set(deps), required_dependencies)

    # Finite-dimensional Noether/Ward control: S(q,X)=1/2(q-X)^2.
    for q, X in [(2.5, -0.7), (0.0, 1.2), (-3.1, -3.1)]:
        Eq = q - X
        EX = -(q - X)
        assert abs(Eq + EX) < 1e-15
        if abs(Eq) < 1e-15:
            assert abs(EX) < 1e-15

    # Israel-alone negative control in abstract residual algebra.
    # Ward: R_perp + B + H = 0. H models the Israel/metric interface residual.
    H = 0.0
    B = 1.75
    R_perp = -(B + H)
    assert H == 0.0
    assert R_perp != 0.0
    assert abs(R_perp + B + H) < 1e-15

    # Full-system control.
    H = 0.0
    B = 0.0
    R_perp = -(B + H)
    assert R_perp == 0.0

    # Common-normal orientation inherited from C4A/C4B0.
    beta = 0.37
    beta_N = +beta
    beta_S = -beta
    assert abs(beta_N + beta_S) < 1e-15

    g = d['gate_state']
    expected = {
        'WP1_full_boundary_hessian': 'NOT_CLOSED',
        'WP1_full_quadratic_action': 'NOT_CLOSED',
        'PERTURBED_JUNCTION_SYSTEM': 'NOT_RELEASED',
        'PHYSICAL_BACKGROUND': 'NOT_ESTABLISHED',
        'FM-G0': 'OPEN',
        'AuthorizationDecision': 'NOT_CREATED',
        'SingleUseGrant': 'NOT_CREATED',
        'BACKEND_IMPORT': 'NOT_EXECUTED',
        'SOLVER_EXECUTION': 'NOT_EXECUTED',
        'PHYSICAL_RESPONSE_RANK': 'NOT_EXECUTED',
        'K1-D': 'NOT_RELEASED',
        'K1-E': 'NOT_ADMISSIBLE',
    }
    for key, value in expected.items():
        assert g[key] == value, (key, g[key], value)

    assert d['physical_gate_effect'] == 'NONE'
    assert d['physical_evidence_effect'] == 'NONE'
    assert d['solver_authorized'] is False
    assert 'Israel allein genügt dafür nicht' in text
    assert 'PHYSICAL_BACKGROUND             NOT_ESTABLISHED' in text

    print('ULSH-05 WP1C4B1B shape Ward residual preflight: PASS')


if __name__ == '__main__':
    main()
