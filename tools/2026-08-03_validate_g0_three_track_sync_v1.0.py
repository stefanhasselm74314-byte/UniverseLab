#!/usr/bin/env python3
"""Fail-closed validator for the UniverseLab G0 three-track synchronization."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


class ContractError(RuntimeError):
    """Raised when a G0 governance invariant is violated."""


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    if not path.is_file():
        raise ContractError(f"missing required artifact: {relative_path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON in {relative_path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"top-level JSON object required: {relative_path}")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def canonical_json_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_three_track_contract() -> dict[str, Any]:
    contract = load_json("registry/2026-08-03_UniverseLab_ThreeTrackContract_v1.0.json")
    require(
        contract["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"],
        "program architecture must be HPVS -> HZT-M0 -> HZT-Full",
    )
    track_ids = [track["track_id"] for track in contract["tracks"]]
    require(
        track_ids == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "three-track order or identifiers are inconsistent",
    )
    legacy, physical, verification = contract["tracks"]
    require(
        legacy["status"] == "BLOCKED_BY_MISSING_PRIMARY_SOURCES",
        "legacy track must remain source-blocked",
    )
    require(
        legacy["benchmark_label"] == "REPORTED_NOT_INDEPENDENTLY_REPRODUCED",
        "historical benchmark evidence label is not corrected",
    )
    require(
        physical["status"] == "MODEL_FREEZE_INCOMPLETE",
        "C-PHYS model freeze must remain incomplete",
    )
    require(
        verification["classification"] == "MANUFACTURED_VERIFICATION_MODEL",
        "C1 must be classified as a manufactured verification model",
    )
    require(
        verification["anchor_classification"] == "EXACT_MANUFACTURED_VERIFICATION_BACKGROUND",
        "C1 anchor classification is incorrect",
    )
    require(verification["k4_anchor"] == 0.25, "C1 anchor k4 must be 1/4")
    require(
        verification["low_curvature_interpretation"] == "FORBIDDEN",
        "C1 low-curvature interpretation must be forbidden",
    )
    require(
        verification["physical_evidence_effect"] == "NONE",
        "C1 physical evidence effect must be NONE",
    )
    gate = contract["gate_state"]
    require(gate["K1-D"] == "NOT_RELEASED", "K1-D drift")
    require(gate["K1-E"] == "NOT_ADMISSIBLE", "K1-E drift")
    require(gate["R1.1"] == "BLOCKED", "R1.1 drift")
    require(gate["official_MD2S_solver"] == "NOT_AUTHORIZED", "solver authorization drift")
    require(gate["physical_evidence_effect"] == "NONE", "physical evidence drift")
    return contract


def validate_claim_register() -> dict[str, Any]:
    claims = load_json("registry/2026-08-03_UniverseLab_ClaimRegister_G0_v1.0.json")
    correction = claims["superseded_claims"]["MD2S-BG-001"]
    require(correction["prior_status"] == "NUMERICALLY_CONFIRMED", "prior A0 status not recorded")
    require(correction["status"] == "OPEN", "A0 claim must be OPEN")
    require(
        correction["canonical_label"] == "REPORTED_NOT_INDEPENDENTLY_REPRODUCED",
        "A0 benchmark label drift",
    )
    entries = {entry["claim_id"]: entry for entry in claims["claims"]}
    expected = {
        "C1-V-CLAIM-001",
        "C1-V-CLAIM-002",
        "C1-V-CLAIM-003",
        "C1-V-CLAIM-004",
    }
    require(set(entries) == expected, "C1-V claim set is incomplete or contains drift")
    require(entries["C1-V-CLAIM-001"]["status"] == "PROVEN", "C1-V anchor claim status drift")
    require(
        entries["C1-V-CLAIM-001"]["evidence_effect"] == "NUMERICAL_IMPLEMENTATION_QA_ONLY",
        "C1-V anchor evidence effect drift",
    )
    require(
        entries["C1-V-CLAIM-002"]["evidence_effect"] == "DISCRETE_QA_ONLY",
        "C1-V Jacobian evidence effect drift",
    )
    require(
        entries["C1-V-CLAIM-003"]["evidence_effect"] == "BACKEND_CROSSCHECK_ONLY",
        "C1-V backend evidence effect drift",
    )
    require(entries["C1-V-CLAIM-004"]["status"] == "OPEN", "C1-V identity must remain OPEN")
    require(
        entries["C1-V-CLAIM-004"]["identity_label"] == "NOT_CLAIMED",
        "C1-V identity label drift",
    )
    return claims


def validate_phase_separation() -> dict[str, Any]:
    manifest = load_json(
        "registry/2026-08-03_UniverseLab_ResearchContinuationManifest_v0.2.json"
    )
    require(
        manifest["physical_r1_phases"]
        == {
            "R1.0": "SOURCE_RECONSTRUCTION_AND_MODEL_FREEZE_ACTIVE",
            "R1.1": "BLOCKED",
            "R1.2": "BLOCKED",
            "R1.3": "BLOCKED",
        },
        "physical R1 phase matrix drift",
    )
    require(
        manifest["c1_verification_phases"]
        == {
            "C1-V0": "PASS",
            "C1-V1": "PASS_DIAGNOSTIC",
            "C1-V2": "PASS_DIAGNOSTIC",
            "C1-V3": "PARTIAL",
            "C1-V4": "NOT_STARTED",
        },
        "C1-V phase matrix drift",
    )
    require(
        manifest["open_pr_disposition"]["PR-1"]["decision"] == "SUPERSEDE",
        "PR #1 disposition drift",
    )
    require(
        manifest["open_pr_disposition"]["PR-2"]["decision"] == "REBASE_AND_REPLACE",
        "PR #2 disposition drift",
    )
    require(
        manifest["next_recommended_block"]["gate"] == "G1.1",
        "next recommended block must be G1.1",
    )
    return manifest


def validate_r1_gate() -> dict[str, Any]:
    gate = load_json("science/hzt-m0/md2s/2026-08-03_MD2S_R1_ThreeTrackGate_v1.0.json")
    require(gate["legacy_track"]["track_id"] == "MD2S-R1-L", "legacy R1 track drift")
    require(
        gate["physical_rebuild_track"]["track_id"] == "MD2S-R1-C-PHYS",
        "physical R1 track drift",
    )
    require(
        gate["verification_track"]["track_id"] == "HZT-M0-S6-C1-V",
        "verification track drift",
    )
    require(
        gate["verification_track"]["excluded_from_physical_r1_path"] is True,
        "C1-V must be excluded from physical R1 phases",
    )
    require(gate["gate_state"]["R1.1"] == "BLOCKED", "R1.1 gate drift")
    require(
        gate["gate_state"]["official_MD2S_solver"] == "NOT_AUTHORIZED",
        "official solver gate drift",
    )
    return gate


def validate_c1_successors() -> dict[str, Any]:
    model = load_json("registry/2026-08-03_HZT_M0_S6_C1_V_ModelContract_v0.2.json")
    jacobian = load_json(
        "registry/2026-08-03_HZT_M0_S6_C1_V_DimensionlessJacobianContract_v0.2.json"
    )
    backend = load_json(
        "registry/2026-08-03_HZT_M0_S6_C1_V_BackendTangentContract_v0.2.json"
    )
    require(model["classification"] == "MANUFACTURED_VERIFICATION_MODEL", "C1-V model drift")
    require(
        model["anchor"]["classification"] == "EXACT_MANUFACTURED_VERIFICATION_BACKGROUND",
        "C1-V anchor drift",
    )
    require(model["anchor"]["k4"] == 0.25, "C1-V k4 drift")
    require(
        model["verification_simplifications"]["transfer_to_C_PHYS"]
        == "FORBIDDEN_WITHOUT_DERIVATION",
        "C1-V parameter migration firewall drift",
    )
    require(jacobian["phase"] == "C1-V1", "C1-V Jacobian phase drift")
    require(jacobian["phase_status"] == "PASS_DIAGNOSTIC", "C1-V1 phase status drift")
    require(jacobian["result"]["rank"] == 8, "declared discrete rank drift")
    require(jacobian["continuum_BVP_Jacobian"] == "NOT_PROVEN", "continuum rank drift")
    require(backend["verification_phases"]["C1-V2"] == "PASS_DIAGNOSTIC", "C1-V2 drift")
    require(backend["verification_phases"]["C1-V3"] == "PARTIAL", "C1-V3 drift")
    require(backend["validated_results"]["local_first_tangent_only"] is True, "tangent scope drift")
    require(backend["nonlinear_solution_family"] == "NOT_ESTABLISHED", "branch claim drift")
    for artifact in (model, jacobian, backend):
        require(artifact["K1-D"] == "NOT_RELEASED", "C1 successor K1-D drift")
        require(artifact["K1-E"] == "NOT_ADMISSIBLE", "C1 successor K1-E drift")
        require(artifact["official_solver_authorized"] is False, "C1 solver authorization drift")
    return {"model": model, "jacobian": jacobian, "backend": backend}


def validate_project_manifest_and_checkpoint() -> dict[str, Any]:
    project = load_json("project-manifest.json")
    require(
        project["architecture"]["program_chain"] == ["HPVS", "HZT-M0", "HZT-Full"],
        "project manifest program chain drift",
    )
    tracks = project["architecture"]["research_tracks"]
    require(
        [track["id"] for track in tracks]
        == ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "project manifest research tracks drift",
    )
    require(project["gates"]["K1-D"] == "NOT_RELEASED", "manifest K1-D drift")
    require(project["gates"]["K1-E"] == "NOT_ADMISSIBLE", "manifest K1-E drift")
    require(project["gates"]["R1.1"] == "BLOCKED", "manifest R1.1 drift")
    require(project["gates"]["official_MD2S_solver"] == "NOT_AUTHORIZED", "manifest solver drift")
    require(project["gates"]["physical_evidence_effect"] == "NONE", "manifest evidence drift")

    dated = load_json("registry/2026-08-03_UniverseLab_SessionCheckpoint_v1.7.json")
    latest = load_json("registry/session-checkpoint-latest.json")
    require(dated == latest, "stable checkpoint alias must be byte-semantically identical to v1.7")
    require(latest["checkpoint_id"] == "UL-CHK-20260803-007", "checkpoint id drift")
    require(latest["current_workstream"] == "G1_C1_V_VERIFICATION_COMPLETION", "workstream drift")
    gate = latest["gate_state"]
    require(gate["MD2S-R1-L"] == "BLOCKED_BY_MISSING_PRIMARY_SOURCES", "checkpoint legacy drift")
    require(gate["MD2S-R1-C-PHYS"] == "MODEL_FREEZE_INCOMPLETE", "checkpoint C-PHYS drift")
    require(gate["HZT-M0-S6-C1-V"] == "MANUFACTURED_VERIFICATION_MODEL", "checkpoint C1-V drift")
    require(gate["C1-V3"] == "PARTIAL", "checkpoint C1-V3 drift")
    require(gate["C1-V4"] == "NOT_STARTED", "checkpoint C1-V4 drift")
    require(gate["K1-D"] == "NOT_RELEASED", "checkpoint K1-D drift")
    require(gate["K1-E"] == "NOT_ADMISSIBLE", "checkpoint K1-E drift")
    return {"project": project, "checkpoint": latest}


def validate_decision_log() -> None:
    path = ROOT / "registry/decision-log.jsonl"
    if not path.is_file():
        raise ContractError("missing decision log")
    decisions = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            decisions.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
    ids = [entry["decision_id"] for entry in decisions]
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    require(ids[-1] == "UL-DEC-0014", "UL-DEC-0014 must be the latest append-only decision")
    decision = decisions[-1]
    require(decision["status"] == "ACTIVE", "UL-DEC-0014 must be active")
    require(
        decision["evidence_effect"] == "GOVERNANCE_ONLY",
        "UL-DEC-0014 must have governance-only evidence effect",
    )


def validate() -> dict[str, Any]:
    contract = validate_three_track_contract()
    claims = validate_claim_register()
    manifest = validate_phase_separation()
    r1_gate = validate_r1_gate()
    c1 = validate_c1_successors()
    state = validate_project_manifest_and_checkpoint()
    validate_decision_log()

    hashes = {
        "three_track_contract": canonical_json_hash(contract),
        "claim_register_g0": canonical_json_hash(claims),
        "continuation_manifest_v0_2": canonical_json_hash(manifest),
        "r1_three_track_gate": canonical_json_hash(r1_gate),
        "c1_v_model": canonical_json_hash(c1["model"]),
        "c1_v_jacobian": canonical_json_hash(c1["jacobian"]),
        "c1_v_backend": canonical_json_hash(c1["backend"]),
        "project_manifest": canonical_json_hash(state["project"]),
        "checkpoint": canonical_json_hash(state["checkpoint"]),
    }
    return {
        "status": "PASS",
        "contract": "G0_THREE_TRACK_SYNCHRONIZATION",
        "tracks": ["MD2S-R1-L", "MD2S-R1-C-PHYS", "HZT-M0-S6-C1-V"],
        "physical_r1": manifest["physical_r1_phases"],
        "c1_verification": manifest["c1_verification_phases"],
        "gate_state": contract["gate_state"],
        "hashes": hashes,
        "next_recommended_block": manifest["next_recommended_block"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()
    try:
        result = validate()
    except ContractError as exc:
        if args.json:
            print(json.dumps({"status": "FAIL", "error": str(exc)}, indent=2))
        else:
            print(f"G0_THREE_TRACK_CONTRACT = FAIL: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("G0_THREE_TRACK_CONTRACT = PASS")
        print("K1-D = NOT_RELEASED")
        print("K1-E = NOT_ADMISSIBLE")
        print("R1.1 = BLOCKED")
        print("PHYSICAL_EVIDENCE_EFFECT = NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
