#!/usr/bin/env python3
"""Fail-closed QA for canonical UL-SING quantum-closure method gates v1.0."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry/2026-09-28_UL-SING_QuantumClosure_MethodGates_v1.0.json"

EXPECTED_IDS = {"QG-PI-01", "QG-GAP-01", "KK-CTP-01"}


def main() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    assert data["schema"] == "universelab.ul-sing.quantum-closure-method-gates.v1"
    assert data["version"] == "1.0.0"
    assert data["status"] == "OWNER_ADOPTED_CANONICAL_METHOD_GATES"
    assert data["classification"] == "CANONICAL_METHOD_GOVERNANCE_NO_PHYSICAL_PROMOTION"

    review = data["source_review"]
    assert review["pull_request"] == 249
    assert review["head_sha"] == "f2a9a16413cf0659bc05ffdb07b1be8c410bb2b8"
    assert review["merge_commit"] == "97f12c99d2c4c68881ebae4170567a15eec3eaf6"

    adoption = data["owner_adoption"]
    assert adoption["pull_request"] == 250
    assert adoption["merge_commit"] == "21655418df14874857cfbfa189fdd43a9c0d54c6"
    assert adoption["decision_text"] == "Alle drei adoptieren"
    assert adoption["normalized_decision"] == "ADOPT_AS_CANONICAL_METHOD_GATE"
    assert adoption["explicit_owner_decision_requirement"] == "SATISFIED"

    gates = data["gates"]
    assert len(gates) == 3
    by_id = {gate["gate_id"]: gate for gate in gates}
    assert set(by_id) == EXPECTED_IDS

    for gate in gates:
        assert gate["canonical_status"] == "ADOPTED_CANONICAL_METHOD_GATE"
        assert gate["source"]["publication_status"] == "PREPRINT"
        assert gate["source"]["direct_hzt_evidence"] is False
        assert gate["physical_gate_effect"] == "NONE"
        assert gate["physical_evidence_effect"] == "NONE"
        assert gate["forbidden_inferences"]

    qg_pi = by_id["QG-PI-01"]
    assert qg_pi["applicability"] == "FUTURE_QUANTUM_BOUNCE_NO_BOUNDARY_OR_EUCLIDEAN_COMPLEX_SADDLE_BRANCH"
    assert "ONE_REGULAR_SADDLE_PROVES_QUANTUM_CONSISTENCY" in qg_pi["forbidden_inferences"]
    assert qg_pi["closure_status"] == "NOT_EVALUATED_CURRENTLY_NOT_APPLICABLE_TO_CLASSICAL_HZT_STATE"

    qg_gap = by_id["QG-GAP-01"]
    assert qg_gap["applicability"] == "ONLY_IF_HZT_CLAIMS_A_FUNDAMENTAL_MINIMUM_RADIUS_AREA_OR_VOLUME"
    assert "NUMERICAL_CUTOFF_EQUALS_PHYSICAL_GEOMETRIC_GAP" in qg_gap["forbidden_inferences"]
    assert "EVERY_VALID_BOUNCE_REQUIRES_A_GEOMETRIC_GAP" in qg_gap["forbidden_inferences"]

    kk = by_id["KK-CTP-01"]
    assert kk["applicability"] == "QUANTUM_REDUCTION_OF_UNOBSERVED_KK_RADION_OR_BULK_MODES_TO_4D_COSMOLOGICAL_OBSERVABLES"
    assert kk["hzt_screening_condition"]["status"] == "CONSERVATIVE_HZT_SCREENING_CANDIDATE_NOT_SOURCE_THEOREM"
    assert "M_HEAVY_GREATER_THAN_H_ALONE_IS_UNIVERSALLY_SUFFICIENT" in kk["forbidden_inferences"]
    assert kk["closure_status"] == "NOT_EVALUATED_NO_RELEASED_QUANTUM_6D_TO_4D_OBSERVABLE_REDUCTION"

    rules = data["canonical_rules"]
    assert rules["method_gate_adoption_is_physical_evidence"] is False
    assert rules["method_gate_adoption_opens_physical_release_gate"] is False
    assert rules["method_gate_adoption_retroactively_promotes_historical_claims"] is False
    assert rules["preprint_source_status_must_remain_visible"] is True
    assert rules["applicability_conditions_are_binding"] is True
    assert rules["forbidden_inferences_are_binding"] is True

    current = data["unchanged_current_state"]
    assert current["physical_background"] == "NOT_ESTABLISHED"
    assert current["physical_response_rank"] == "NOT_EXECUTED"
    assert current["K1-D"] == "NOT_RELEASED"
    assert current["K1-E"] == "NOT_ADMISSIBLE"
    assert current["FM_G0"] == "OPEN"

    assert data["physical_gate_effect"] == "NONE"
    assert data["physical_evidence_effect"] == "NONE"

    print("UL-SING quantum-closure canonical method-gate QA: PASS")


if __name__ == "__main__":
    main()
