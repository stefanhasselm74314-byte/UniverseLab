#!/usr/bin/env python3
"""Canonical G0 v1.16 validator after Background-3C5 authorization denial."""
from __future__ import annotations
import argparse, importlib.util, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE = "2.16-c-phys-m1-background-3c5-authorization-denied-v0.1"
DECISION = "UL-DEC-0031"
CHECKPOINT = "UL-CHK-20260804-024"
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.24.json"
LATEST = ROOT / "registry/session-checkpoint-latest.json"
MANIFEST = ROOT / "project-manifest.json"
DECISIONS = ROOT / "registry/decision-log.jsonl"
REVIEW = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3C5ExecutionPackageAuthorizationReview_v0.1.json"
REVIEW_VALIDATOR = ROOT / "tools/2026-08-04_validate_hzt_m0_s6_c_phys_m1_background_3c5_v0.1.py"
GRANT = ROOT / "registry/2026-08-04_HZT_M0_S6_C_PHYS_M1_Background3CExecutionAuthorization_v0.2.json"
ARTIFACT = ROOT / "artifacts/hzt-m0/md2s/background3c/HZT-M0-S6-C-PHYS-M1-BG3B-CP01R1"
NEXT = "C-PHYS-R1.0-BACKGROUND-3C6_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_ONLY"


def load(path): return json.loads(path.read_text(encoding="utf-8"))

def load_validator():
    spec = importlib.util.spec_from_file_location("bg3c5_g0", REVIEW_VALIDATOR)
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module; spec.loader.exec_module(module)
    return module

def validate():
    manifest, latest, snapshot, review = load(MANIFEST), load(LATEST), load(SNAPSHOT), load(REVIEW)
    decisions = [json.loads(line) for line in DECISIONS.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert manifest["release"] == RELEASE
    assert latest == snapshot and latest["checkpoint_id"] == CHECKPOINT
    assert latest["current_workstreams"][0]["next_block"] == NEXT
    assert len([d for d in decisions if d.get("decision_id") == DECISION]) == 1
    gates = manifest["gates"]
    expected = {
      "R1.0":"ACTIVE_INTEGRATED_EXECUTION_RELEASE_IMPLEMENTATION_REMAINING",
      "BACKGROUND_SOLVER_IMPLEMENTATION":"EXECUTION_PACKAGE_COMPONENTS_AUDITED_INTEGRATED_RELEASE_INCOMPLETE",
      "BACKGROUND_3C5_AUTHORIZATION_REVIEW":"DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE",
      "BACKGROUND_3C6_EXECUTION_RELEASE":"NOT_STARTED",
      "BACKGROUND_3C_EXECUTION":"NOT_AUTHORIZED",
      "BACKGROUND_SOLVER_EXECUTION":"NOT_AUTHORIZED",
      "PHYSICAL_BACKGROUND":"NOT_ESTABLISHED",
      "R1.1":"BLOCKED","R1.2":"BLOCKED",
      "official_MD2S_solver":"NOT_AUTHORIZED",
      "K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE",
      "physical_evidence_effect":"NONE"
    }
    for key, value in expected.items(): assert gates[key] == value, (key, gates.get(key), value)
    assert review["status"] == "DENIED_INTEGRATED_EXECUTION_RELEASE_INCOMPLETE"
    assert review["authorization_decision"]["authorized"] is False
    assert review["solver_executed"] is False and review["result_artifact_created"] is False
    assert load_validator().validate()["status"] == "PASS"
    assert not GRANT.exists() and not ARTIFACT.exists()
    blockers = {b["blocker_id"] for b in latest["open_blockers"]}
    assert "UL-BLK-C-PHYS-BACKGROUND-3C5-001" not in blockers
    assert "UL-BLK-C-PHYS-BACKGROUND-3C6-001" in blockers
    return {"status":"PASS","release":RELEASE,"decision":DECISION,"checkpoint":CHECKPOINT,"execution_authorized":False,"solver_calls":0,"physical_evidence_effect":"NONE","next_block":NEXT}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--json",action="store_true"); a=p.parse_args(); r=validate(); print(json.dumps(r,indent=2,sort_keys=True) if a.json else "PASS: G0 v1.16")
if __name__ == "__main__": main()
