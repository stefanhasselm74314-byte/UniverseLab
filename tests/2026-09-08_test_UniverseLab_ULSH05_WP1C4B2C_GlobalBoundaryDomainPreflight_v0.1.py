from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.json"
DOC = ROOT / "science/solver-hub/2026-09-08_UniverseLab_ULSH05_WP1C4B2C_GlobalBoundaryDomainPreflight_v0.1.md"
PREV = ROOT / "registry/2026-09-08_UniverseLab_ULSH05_WP1C4B2B_ComponentBoundaryResidualLinearization_v0.1.json"
PARENT = ROOT / "SCI-001-002_v0.1_Canonical_6D_Parent_Action_and_Boundary_Closure.md"


def close(a: float, b: float, *, atol: float = 1e-12) -> None:
    assert abs(a - b) <= atol, (a, b, a - b)


def boundary_form(u, up, v, vp, a: float, b: float) -> float:
    return (-u(b) * vp(b) + up(b) * v(b)) - (-u(a) * vp(a) + up(a) * v(a))


def test_contract_and_firewalls() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    prev = json.loads(PREV.read_text(encoding="utf-8"))
    doc = DOC.read_text(encoding="utf-8")
    parent = PARENT.read_text(encoding="utf-8")

    assert reg["work_package"] == "ULSH-05/WP1C4B2C"
    assert reg["basis_main"] == "eab0866b80bbc21730c2af89b54d5ba177c5113a"
    assert reg["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert reg["physical_gate_effect"] == "NONE"
    assert reg["physical_evidence_effect"] == "NONE"
    assert reg["solver_authorized"] is False

    assert prev["next_block"]["id"] == "ULSH-05/WP1C4B2C"
    assert "boundary" in prev["next_block"]["title"].lower()
    assert "GHY" in parent
    assert "Junction" in parent or "junction" in parent

    gates = reg["gate_state"]
    assert gates["WP1_global_domain_preflight"] == "COMPLETED_CONDITIONAL_NO_PHYSICAL_DOMAIN_RELEASE"
    assert gates["WP1_physical_boundary_domain"] == "BLOCKED_UNESTABLISHED_BACKGROUND_AND_GLOBAL_CORNER_DATA"
    assert gates["WP1_full_global_boundary_hessian"] == "NOT_CLOSED_PHYSICAL_DOMAIN_NOT_RELEASED"
    assert gates["WP1_full_quadratic_action"] == "NOT_CLOSED"
    assert gates["PERTURBED_JUNCTION_SYSTEM"] == "NOT_RELEASED"
    assert gates["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert gates["FM-G0"] == "OPEN"
    assert gates["AuthorizationDecision"] == "NOT_CREATED"
    assert gates["SingleUseGrant"] == "NOT_CREATED"
    assert gates["BACKEND_IMPORT"] == "NOT_EXECUTED"
    assert gates["SOLVER_EXECUTION"] == "NOT_EXECUTED"
    assert gates["PHYSICAL_RESPONSE_RANK"] == "NOT_EXECUTED"
    assert gates["K1-D"] == "NOT_RELEASED"
    assert gates["K1-E"] == "NOT_ADMISSIBLE"

    assert reg["physical_domain_blocker"]["status"] == "PHYSICAL_BOUNDARY_DOMAIN_NOT_FIXABLE_BEFORE_BACKGROUND_CAUSAL_STRUCTURE"
    assert reg["corner_joint_preflight"]["gap"] == "MISSING_GLOBAL_CORNER_COMPLETION_OR_ZERO_VARIATION_CONDITION"
    assert reg["green_identity"]["component_status"] == "GLOBAL_C_PHYS_M1_BOUNDARY_CONCOMITANT_NOT_YET_COMPONENTIZED"
    assert reg["domain_candidates"]["D0_local_test"]["physical_release"] is False
    assert reg["domain_candidates"]["D4_radiative"]["status"] == "NOT_DEFINABLE_BEFORE_BACKGROUND_CAUSAL_STRUCTURE"

    for token in (
        "PHYSICAL\\_BOUNDARY\\_DOMAIN\\_NOT\\_FIXABLE\\_BEFORE\\_BACKGROUND\\_CAUSAL\\_STRUCTURE",
        "MISSING_GLOBAL_CORNER_COMPLETION_OR_ZERO_VARIATION_CONDITION",
        "formale Symmetrie",
        "Ghostfreiheit",
        "2\\pi",
        "S/V/T",
        "operatorname{int}M_4",
    ):
        assert token in doc, token


def test_finite_boundary_d0_requires_interior_support() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    d0 = reg["domain_candidates"]["D0_local_test"]
    geom = reg["geometric_domain"]

    assert "C_c^infinity(int M4)" in d0["definition"]
    assert "partialM4!=empty" in d0["definition"]
    assert "compactly contained in int(M4)" in d0["finite_boundary_semantics"]
    assert "compactly contained in int(M4)" in geom["local_test_support_convention"]
    assert d0["boundary_flux"] == "VANISHES_BY_INTERIOR_COMPACT_SUPPORT_OR_BOUNDARYLESS_COMPACT_SUPPORT_AND_CHI_PERIODICITY"


def test_unrestricted_interval_counterexample() -> None:
    # L=-d^2/dx^2, u=x, v=x^2.  On compact [0,1] these functions
    # are naively compactly supported, but they are not supported in int([0,1])
    # and do not have zero boundary trace.
    u = lambda x: x
    up = lambda x: 1.0
    v = lambda x: x * x
    vp = lambda x: 2.0 * x

    lhs = -1.0
    rhs = boundary_form(u, up, v, vp, 0.0, 1.0)
    close(lhs, -1.0)
    close(rhs, -1.0)
    close(lhs, rhs)
    assert rhs != 0.0


def test_dirichlet_control_kills_boundary_form() -> None:
    u = lambda x: x * (1.0 - x)
    up = lambda x: 1.0 - 2.0 * x
    v = lambda x: x * x * (1.0 - x)
    vp = lambda x: 2.0 * x - 3.0 * x * x
    rhs = boundary_form(u, up, v, vp, 0.0, 1.0)
    close(rhs, 0.0)


def test_periodic_chi_control() -> None:
    u = math.sin
    up = math.cos
    v = math.cos
    vp = lambda x: -math.sin(x)
    rhs = boundary_form(u, up, v, vp, 0.0, 2.0 * math.pi)
    close(rhs, 0.0, atol=2e-15)


def test_domain_classes_are_fail_closed() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    d = reg["domain_candidates"]
    assert d["D0_local_test"]["status"] == "PROVEN_ANALYTIC_TEST_DOMAIN"
    assert d["D1_finite_slab_fixed_variations"]["status"].endswith("NOT_PHYSICAL_RELEASE")
    assert d["D2_asymptotic_falloff"]["status"] == "NOT_SPECIFIED_BACKGROUND_DEPENDENT"
    assert d["D3_flux_free_mixed"]["status"] == "TARGET_ONLY_REQUIRES_COMPONENT_GREEN_FORM_AND_BACKGROUND"
    assert d["D4_radiative"]["status"] == "NOT_DEFINABLE_BEFORE_BACKGROUND_CAUSAL_STRUCTURE"
    assert all(entry["physical_release"] is False for entry in d.values())


def test_successor_id_is_not_invented() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    cont = reg["continuation"]
    assert cont["next_exact_work_package_id"] == "TO_BE_ASSIGNED_BY_SUCCESSOR_CONTRACT_AFTER_THIS_PREFLIGHT"
    assert "S/V/T" in cont["fallback_if_physical_domain_requires_unreleased_background"]


if __name__ == "__main__":
    test_contract_and_firewalls()
    test_finite_boundary_d0_requires_interior_support()
    test_unrestricted_interval_counterexample()
    test_dirichlet_control_kills_boundary_form()
    test_periodic_chi_control()
    test_domain_classes_are_fail_closed()
    test_successor_id_is_not_invented()
    print("WP1C4B2C global boundary-domain preflight controls: PASS")
