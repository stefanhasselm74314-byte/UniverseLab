import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/2026-09-07_UniverseLab_ULSH05_WP1C2_FixedInterfaceCapHessian_v0.1.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_contract_status_and_scope():
    c = load(REG)
    assert c["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert c["work_package"] == "ULSH-05/WP1C2"
    assert c["status"] == "DERIVED_OFFSHELL_FIXED_INTERFACE_LOCALIZED_CAP_HESSIAN_BENDING_AND_PERTURBED_JUNCTIONS_OPEN"
    assert c["classification"] == "FORMAL_SECOND_VARIATION_ONLY"
    assert c["physical_gate_effect"] == "NONE"
    assert c["physical_evidence_effect"] == "NONE"
    assert c["solver_authorized"] is False
    assert c["fixed_interface_perturbation_path"]["interface_embedding"] == "FIXED"
    assert c["fixed_interface_perturbation_path"]["bending_mode"] == "EXCLUDED_NOT_SET_TO_ZERO_PHYSICALLY"


def analytic_d2(hbar_diag, qdiag, w, d, lam, z):
    hinv = [1.0 / x for x in hbar_diag]
    qtrace = sum(hi * qi for hi, qi in zip(hinv, qdiag))
    q2 = sum((hi * qi) ** 2 for hi, qi in zip(hinv, qdiag))
    n1 = 0.5 * qtrace
    n2 = 0.125 * qtrace * qtrace - 0.25 * q2

    x0 = sum(hi * wi * wi for hi, wi in zip(hinv, w))
    x1 = (
        2.0 * sum(hi * wi * di for hi, wi, di in zip(hinv, w, d))
        - sum((hi * hi) * qi * wi * wi for hi, qi, wi in zip(hinv, qdiag, w))
    )
    x2 = (
        sum(hi * di * di for hi, di in zip(hinv, d))
        - 2.0 * sum((hi * hi) * qi * wi * di for hi, qi, wi, di in zip(hinv, qdiag, w, d))
        + sum((hi ** 3) * (qi ** 2) * wi * wi for hi, qi, wi in zip(hinv, qdiag, w))
    )
    l0 = -lam - 0.5 * z * x0
    l1 = -0.5 * z * x1
    l2 = -0.5 * z * x2
    return l2 + n1 * l1 + n2 * l0


def exact_density(eps, hbar_diag, qdiag, w, d, lam, z):
    h = [hb + eps * q for hb, q in zip(hbar_diag, qdiag)]
    det = math.prod(h)
    assert det < 0.0
    sqrt_minus_h = math.sqrt(-det)
    x = sum(((wi + eps * di) ** 2) / hi for hi, wi, di in zip(h, w, d))
    return sqrt_minus_h * (-lam - 0.5 * z * x)


def test_independent_lorentzian_finite_difference_reconstruction():
    # 5D induced Lorentz signature control; last entry is a non-unit circle metric component.
    hbar = [-1.0, 1.3, 0.9, 1.7, 4.0]
    q = [0.07, -0.11, 0.05, 0.09, 0.31]
    w = [0.12, -0.23, 0.08, 0.17, 0.61]
    d = [-0.04, 0.07, 0.03, -0.02, 0.13]
    lam = 0.73
    z = 1.41

    d2 = analytic_d2(hbar, q, w, d, lam, z)
    sqrt0 = math.sqrt(-math.prod(hbar))
    expected_density_coeff = sqrt0 * d2

    # Moderate epsilon minimizes cancellation while retaining O(eps^2) convergence.
    errors = []
    for eps in (2.0e-3, 1.0e-3, 5.0e-4):
        fp = exact_density(+eps, hbar, q, w, d, lam, z)
        fm = exact_density(-eps, hbar, q, w, d, lam, z)
        f0 = exact_density(0.0, hbar, q, w, d, lam, z)
        fd = (fp + fm - 2.0 * f0) / (2.0 * eps * eps)
        errors.append(abs(fd - expected_density_coeff))
    assert errors[-1] < 2.0e-7
    assert errors[-1] < errors[0]


def test_fixed_metric_limit():
    hbar = [-1.0, 1.0, 1.2, 0.8, 3.0]
    q = [0.0] * 5
    w = [0.2, -0.1, 0.05, 0.3, 0.7]
    d = [0.04, 0.02, -0.03, 0.01, -0.08]
    lam, z = 0.9, 1.7
    got = analytic_d2(hbar, q, w, d, lam, z)
    expected = -0.5 * z * sum((di * di) / hi for hi, di in zip(hbar, d))
    assert math.isclose(got, expected, rel_tol=0.0, abs_tol=1e-14)


def test_linearized_u1_gauge_invariant_combination():
    q_sigma = 1.9
    ds = [0.2, -0.3, 0.1, 0.0, 0.4]
    a = [-0.1, 0.07, 0.03, -0.02, 0.11]
    dalpha = [0.04, -0.09, 0.08, 0.13, -0.05]
    d_before = [x - q_sigma * y for x, y in zip(ds, a)]
    ds_after = [x + q_sigma * da for x, da in zip(ds, dalpha)]
    a_after = [x + da for x, da in zip(a, dalpha)]
    d_after = [x - q_sigma * y for x, y in zip(ds_after, a_after)]
    for x, y in zip(d_before, d_after):
        assert math.isclose(x, y, rel_tol=0.0, abs_tol=1e-15)


def test_m1_cap_functions_are_constant_in_phi():
    ff = load(ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json")
    assert ff["model_id"] == "HZT-M0-S6-C-PHYS-M1"
    assert ff["exact_functions"]["lambda"]["derivatives"]["d_lambda_dphi"] == "0"
    assert ff["exact_functions"]["lambda"]["derivatives"]["d2_lambda_dphi2"] == "0"
    assert ff["exact_functions"]["Z_sigma"]["derivatives"]["d_Z_sigma_dphi"] == "0"
    assert ff["exact_functions"]["Z_sigma"]["derivatives"]["d2_Z_sigma_dphi2"] == "0"


def test_upstream_hessian_chain_exists_and_wp1_not_overpromoted():
    required = [
        "registry/2026-09-07_UniverseLab_ULSH05_WP1_QuadraticActionReadiness_v0.1.json",
        "registry/2026-09-07_UniverseLab_ULSH05_WP1A_FixedMetricScalarMaxwellHessian_v0.1.json",
        "registry/2026-09-07_UniverseLab_ULSH05_WP1B_EHGHYHessianMaster_v0.1.json",
        "registry/2026-09-07_UniverseLab_ULSH05_WP1C1_BulkMetricMatterHessian_v0.1.json",
    ]
    for rel in required:
        assert (ROOT / rel).is_file(), rel
    c = load(REG)
    assert c["gate_state"]["WP1_bulk_gravity_matter_hessian"] == "ASSEMBLABLE_OFFSHELL"
    assert c["gate_state"]["WP1_full_boundary_hessian"].startswith("NOT_CLOSED")
    assert c["gate_state"]["WP1_full_quadratic_action"] == "NOT_CLOSED"


def test_physical_and_execution_firewalls_unchanged():
    g = load(REG)["gate_state"]
    assert g["PHYSICAL_BACKGROUND"] == "NOT_ESTABLISHED"
    assert g["FM_G0"] == "OPEN"
    assert g["AuthorizationDecision"] == "NOT_CREATED"
    assert g["SingleUseGrant"] == "NOT_CREATED"
    assert g["BACKEND_IMPORT"] == "NOT_EXECUTED"
    assert g["SOLVER_EXECUTION"] == "NOT_EXECUTED"
    assert g["PHYSICAL_RESPONSE_RANK"] == "NOT_EXECUTED"
    assert g["K1-D"] == "NOT_RELEASED"
    assert g["K1-E"] == "NOT_ADMISSIBLE"
