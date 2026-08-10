from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TARGET = ROOT / "registry/2026-08-10_ULSH-01_MD2S-BVP_WP1_TargetBoundaryContract_v1.0.json"
MASTER = ROOT / "registry/2026-08-10_ULSH_MasterBuildOrder_v1.0.json"
FUNCTION = ROOT / "registry/2026-08-03_HZT_M0_S6_C_PHYS_M1_FunctionFreezeContract_v0.1.json"
CONVENTION = ROOT / "registry/2026-08-03_MD2S_R1_C_PHYS_GlobalConventionFreezeContract_v0.1.json"
OP2A = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2AContract_v0.1.json"
OP2B = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Operator2BFunctionSpaceTraceContract_v0.1.json"
TOPO = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3ATopologyCorrectionContract_v0.2.json"
ASSEMBLY = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3AAssemblyCorrectionContract_v0.3.json"
AUTH = ROOT / "registry/2026-08-05_HZT_M0_S6_C_PHYS_M1_Background3C11RealBackendControlAuthorizationReview_v0.1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def norm(expr: str) -> str:
    expr = expr.replace(" ", "").replace("\n", "").replace("_s", "")
    if expr.endswith("=0"):
        expr = expr[:-2]
    return expr


target = load(TARGET)
master = load(MASTER)
function = load(FUNCTION)
convention = load(CONVENTION)
op2a = load(OP2A)
op2b = load(OP2B)
topo = load(TOPO)
assembly = load(ASSEMBLY)
auth = load(AUTH)

assert target["schema"] == "universelab.ulsh-01.md2s-bvp.wp1-target-boundary-contract.v1"
assert target["version"] == "1.0.0"
assert target["solver_id"] == "ULSH-01"
assert target["module_id"] == "MD2S-BVP"
assert target["work_package"] == "WP1"
assert target["model_id"] == "HZT-M0-S6-C-PHYS-M1"
assert target["status"] == "WP1_TARGET_EQUATION_AND_BOUNDARY_CONTRACT_CLOSED_SPECIFICATION_ONLY"

# Master-order binding: WP1 is exactly the currently active theory/contract task.
ulsh01 = next(s for s in master["solvers"] if s["id"] == "ULSH-01")
assert ulsh01["work_packages"][0].startswith("WP1 Targetgleichungs- und Randbedingungsvertrag")
assert master["status"] == "PLANNING_EXECUTION_ORDER_NO_SOLVER_EXECUTION"

# Exact M1 model parameter order and domains remain external to the BVP unknown vector.
assert target["exact_m1_model"]["external_model_parameter_order"] == function[
    "dimensionless_model_parameter_vector"
]["ordered_parameters"]
assert target["exact_m1_model"]["silent_promotion_to_bvp_unknowns"] is False

# Exact independent continuum equations are copied from the canonical M1 operator, not reconstructed ad hoc.
for target_name, source_name in [
    ("E_A_s", "E_A"),
    ("E_ell_s", "E_ell"),
    ("E_varphi_s", "E_varphi"),
    ("E_gauge_s", "E_gauge"),
]:
    assert norm(target["bulk_target_equation_contract"]["equations"][target_name]) == norm(
        op2a["independent_bulk_residuals"][source_name]
    )

assert norm(target["constraint_contract"]["C_rr_s"]) == norm(op2a["radial_constraint"]["C_rr"])
assert norm(target["constraint_contract"]["off_shell_identity"]) == norm(
    op2a["radial_constraint"]["off_shell_identity"]
)
assert target["constraint_contract"]["role"] == "PROPAGATED_QA_CHANNEL_NOT_ADDITIONAL_ENDPOINT_OR_NONLINEAR_RESIDUAL"

# Pole chart and 8D augmented parameter vector are inherited exactly from Operator-2B.
assert target["profile_and_augmented_unknowns"]["augmented_continuous_unknown_order"] == op2b[
    "augmented_parameter_space"
]["continuous_vector_order"]
assert target["profile_and_augmented_unknowns"]["augmented_continuous_unknown_count"] == 8
assert target["operator_function_space_contract"]["regional_profile_domain"] == op2b[
    "little_holder_spaces"
]["regional_profile_domain"]
assert target["boundary_and_global_residual_contract"]["residual_order"] == op2b[
    "nonlinear_boundary_map"
]["residual_order"]

# Global conventions: frame, normal signs, patch relation and 8-by-8 structural count.
assert target["regional_geometry_and_orientation"]["local_outward_cap_normals"]["n_N_x"] == convention[
    "regional_coordinates_and_orientations"
]["outward_boundary_normals_in_local_coordinates"]["n_N^r"]
assert target["regional_geometry_and_orientation"]["local_outward_cap_normals"]["n_S_x"] == convention[
    "regional_coordinates_and_orientations"
]["outward_boundary_normals_in_local_coordinates"]["n_S^r"]
assert target["regional_geometry_and_orientation"]["global_two_form_orientation"]["epsilon_N"] == convention[
    "regional_coordinates_and_orientations"
]["global_two_form_orientation_signs"]["epsilon_N"]
assert target["regional_geometry_and_orientation"]["global_two_form_orientation"]["epsilon_S"] == convention[
    "regional_coordinates_and_orientations"
]["global_two_form_orientation_signs"]["epsilon_S"]
assert target["profile_and_augmented_unknowns"]["augmented_continuous_unknown_count"] == convention[
    "continuous_unknown_roles"
]["count"]
assert target["boundary_and_global_residual_contract"]["independent_residual_count"] == len(
    convention["independent_boundary_residuals"]
)

# The corrected single-cap-phase topology is the only admissible discrete schema.
assert target["profile_and_augmented_unknowns"]["fixed_discrete_sector_order"] == topo[
    "canonical_effective_topological_input"
]["ordered_vector"]
raw_target = TARGET.read_text(encoding="utf-8")
for forbidden in topo["forbidden_regional_expansion"]["forbidden_labels"]:
    assert f'"{forbidden}"' not in raw_target

# Corrected square collocation assembly: all regularized bulk rows plus eight appended boundary rows.
assert target["assembly_contract"]["augmented_unknowns"] == assembly["counting_audit"]["augmented_unknowns"]
assert target["assembly_contract"]["boundary_global_residuals"] == assembly["counting_audit"][
    "cap_and_global_boundary_residuals"
]
assert target["assembly_contract"]["total_unknowns"] == assembly["counting_audit"]["total_unknowns"]
assert target["assembly_contract"]["total_residuals"] == assembly["counting_audit"]["total_residuals"]
assert target["assembly_contract"]["constraint_appended"] is False

# No double counting of global flux and no rr constraint promoted to a ninth/tenth boundary residual.
assert target["boundary_and_global_residual_contract"]["residual_order"] == [
    "R_A",
    "R_ell",
    "R_varphi",
    "R_patch",
    "R_4d",
    "R_chi",
    "R_scalar",
    "R_gauge_local",
]
assert "R_flux" not in target["boundary_and_global_residual_contract"]["residual_order"]
assert "C_rr" not in target["boundary_and_global_residual_contract"]["residual_order"]

# Unit and domain hygiene.
assert target["field_and_unit_contract"]["dimensional"]["r"] == "M^-1"
assert target["field_and_unit_contract"]["dimensional"]["L"] == "M^-1"
assert target["field_and_unit_contract"]["dimensional"]["phi"] == "M^2"
assert target["field_and_unit_contract"]["dimensional"]["Q_s"] == "M^3"
assert target["field_and_unit_contract"]["dimensionless"]["x_s"] == "M6*r_s"
assert target["exact_m1_model"]["domains"]["a_F"] == "strictly_positive_in_active_M1_branch"

# Governance firewall: WP1 closes specification only.
assert target["solver_authorized"] is False
assert target["physical_target_solve_authorized"] is False
assert target["cp01r1_authorized"] is False
assert target["physical_evidence_effect"] == "NONE"
assert target["release_state"]["ULSH_01_WP1"] == "CLOSED_SPECIFICATION_ONLY"
assert target["release_state"]["ULSH_01_WP2"] == "NEXT_ACTIVE_NOT_RELEASED"
assert target["release_state"]["ULSH_01_RELEASE_GATE"] == "NOT_RELEASED"
assert target["release_state"]["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED"
assert target["release_state"]["CP01R1"] == "NOT_AUTHORIZED"
assert target["release_state"]["K1-D"] == "NOT_RELEASED"
assert target["release_state"]["K1-E"] == "NOT_ADMISSIBLE"
assert target["release_state"]["physical_evidence_effect"] == "NONE"

# Latest pre-WP1 authorization review remains denied and is not silently overridden.
assert auth["authorization_decision"]["authorized"] is False
assert auth["authorization_decision"]["cp01r1_attempted"] is False
assert auth["authorization_decision"]["target_a_F_one_quarter_solve_attempted"] is False
assert auth["gate_state"]["BACKGROUND_SOLVER_EXECUTION"] == "NOT_AUTHORIZED"

print("ULSH-01 WP1 TargetBoundaryContract v1.0: PASS")
print("equations=4_per_region regions=2")
print("augmented_unknowns=8 boundary_residuals=8")
print("topology=(N_F,N_sigma,m_sigma)")
print("constraint=QA_ONLY")
print("WP1=CLOSED_SPECIFICATION_ONLY WP2=NOT_RELEASED")
print("K1-D=NOT_RELEASED K1-E=NOT_ADMISSIBLE physical_evidence_effect=NONE")
