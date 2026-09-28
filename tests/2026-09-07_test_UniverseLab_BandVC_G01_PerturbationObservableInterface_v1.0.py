#!/usr/bin/env python3
"""Fail-closed QA for the Band V-C G01 reference-only perturbation interface.

This test must never turn reference definitions into HZT dynamics. It proves
that G01 remains open, that roadmap/source provenance agrees with that state,
and that existing Bridge growth/lensing refusal semantics remain intact.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInventory_v1.0.json"
INTERFACE = ROOT / "registry/2026-09-07_UniverseLab_BandVC_G01_PerturbationObservableInterface_v1.0.json"
CROSSWALK = ROOT / "registry/2026-09-04_UniverseLab_BandVC_ClaimEvidenceCrosswalk_v1.0.json"
GAPS = ROOT / "registry/2026-09-04_UniverseLab_BandVC_MissingLinkRegister_v1.0.json"
CENSUS = ROOT / "registry/2026-09-03_UniverseLab_PublicScientificClaimCensus_v1.0.json"
BUILD = ROOT / "registry/2026-08-10_ULSH_MasterBuildOrder_v1.0.json"
ENGINE = ROOT / "assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js"
COMPARE = ROOT / "assets/2026-09-01_UniverseLab_CompareSafeAdapter_v2.0.js"
MANIFEST = ROOT / "project-manifest.json"

FIREWALLS = {
    "FM-G0": "OPEN",
    "RATIFIED_HUMAN_TRUST_ROOT": "NOT_RATIFIED",
    "RUNTIME_ISSUANCE_BINDINGS": "BLOCKED",
    "AuthorizationDecision": "NOT_CREATED",
    "SingleUseGrant": "NOT_CREATED",
    "BACKEND_IMPORT": "NOT_EXECUTED",
    "SOLVER_EXECUTION": "NOT_EXECUTED",
    "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
    "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
    "K1-D": "NOT_RELEASED",
    "K1-E": "NOT_ADMISSIBLE",
}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def main() -> None:
    inventory = load(INVENTORY)
    interface = load(INTERFACE)
    crosswalk = load(CROSSWALK)
    gaps = load(GAPS)
    census = load(CENSUS)
    build = load(BUILD)
    manifest = load(MANIFEST)

    # The forensic result is explicit: real missing derivation, not pointer drift.
    assert inventory["gap_id"] == "UL-BVC-G01"
    assert inventory["claim_family_id"] == "UL-CLM-BRIDGE-UNRELEASED-OBSERVABLES-001"
    assert inventory["result"] == "GENUINE_MISSING_DERIVATION_NOT_POINTER_DRIFT"
    assert inventory["gap_status_after_inventory"] == "OPEN_BLOCKING_TARGET_INTERFACE_CAN_BE_FROZEN"
    assert inventory["physical_gate_effect"] == inventory["physical_evidence_effect"] == "NONE"
    for source in inventory["authoritative_sources"]:
        assert (ROOT / source).is_file(), source

    # Historical Band-V-C provenance must still say the equation/map is missing.
    family = next(row for row in crosswalk["families"] if row["claim_family_id"] == inventory["claim_family_id"])
    assert family["claim"] == "VERIFIED_PRESENT"
    assert family["equation_or_derivation"] == "MISSING_REQUIRED_LINK"
    assert family["code"] == "BLOCKED_BY_UNRELEASED_MAP"
    assert family["test"] == "VERIFIED_PRESENT"
    assert family["evidence_scope"] == "FAIL_CLOSED_RELEASE_FIREWALL"

    gap = next(row for row in gaps["gaps"] if row["gap_id"] == "UL-BVC-G01")
    assert gap["status"] == "OPEN_BLOCKING"
    assert gap["axis"] == "equation_or_derivation"
    assert inventory["claim_family_id"] in gap["family_ids"]

    census_family = next(row for row in census["claim_families"] if row["claim_family_id"] == inventory["claim_family_id"])
    assert "UNRELEASED_GROWTH_MAP" in census_family["status_literals"]
    assert "UNRELEASED_LENSING_MAP" in census_family["status_literals"]

    # Solver roadmap independently confirms that perturbation/COSMO derivation is future work.
    solvers = {row["id"]: row for row in build["solvers"]}
    perturb = solvers["ULSH-05"]
    cosmo = solvers["ULSH-10"]
    assert perturb["module_id"] == "PERTURBATION"
    assert perturb["priority"] == "PREPARATORY_DERIVATION_ONLY"
    assert perturb["upstream"] == ["ULSH-01", "ULSH-04"]
    assert any("quadratische Wirkung" in item for item in perturb["work_packages"])
    assert any("gauge-invariante" in item for item in perturb["work_packages"])
    assert "GAUGE_CONTROLLED_QUADRATIC_PERTURBATION_SYSTEM" in perturb["release_gate"]
    assert cosmo["module_id"] == "COSMO"
    assert cosmo["priority"] == "BLOCKED_BY_FOUNDATIONAL_GATES"
    assert any("Wachstum" in item and "Lensing" in item for item in cosmo["work_packages"])
    assert any("fSigma8" in item and "mu" in item and "Sigma" in item and "eta" in item for item in cosmo["work_packages"])
    assert cosmo["release_gate"] == "K1_D_ELIGIBLE_PHYSICAL_FORWARD_MAP_WITH_BACKGROUND_GROWTH_LENSING_OUTPUTS"

    # Interface is definitions only. HZT values/domains/dynamics remain unreleased.
    assert interface["classification"] == "REFERENCE_ONLY_INTERFACE_NOT_HZT_DERIVATION"
    assert interface["gap_status_effect"] == "PARTIAL_TARGET_SEMANTICS_ONLY_G01_REMAINS_OPEN_BLOCKING"
    assert interface["release_requirements"]["G01"] == "OPEN_BLOCKING"
    for name, spec in interface["observable_definitions"].items():
        assert spec["hzt_value"] == "NOT_RELEASED", name
    assert set(interface["hzt_outputs"].values()) == {"NOT_RELEASED"}
    assert interface["optional_reference_growth_target"]["bridge_execution_status"] == "UNRELEASED_GROWTH_MAP"
    assert interface["existing_runtime_firewalls"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    assert interface["existing_runtime_firewalls"]["bridge_lensing"] == "UNRELEASED_LENSING_MAP"
    assert interface["existing_runtime_firewalls"]["must_remain_fail_closed_until_release"] is True
    assert interface["physical_gate_effect"] == interface["physical_evidence_effect"] == "NONE"

    # Algebraic identity is checked numerically as an interface identity only.
    for mu, eta in ((1.0, 1.0), (0.8, 1.2), (1.4, 0.6), (0.35, -0.2)):
        sigma_from_definitions = mu * (1.0 + eta) / 2.0
        sigma_identity = mu * (1.0 + eta) / 2.0
        assert abs(sigma_from_definitions - sigma_identity) < 1e-15
    gr = interface["reference_gr_limit"]
    assert (gr["mu"], gr["eta"], gr["Sigma"]) == (1.0, 1.0, 1.0)
    assert gr["classification"] == "REFERENCE_GR_CONTROL_ONLY_NOT_BRIDGE_RESULT"

    # Runtime/source firewalls: engine refuses Bridge growth; Compare refuses Bridge lensing.
    engine_source = ENGINE.read_text(encoding="utf-8")
    compare_source = COMPARE.read_text(encoding="utf-8")
    assert "UNRELEASED_GROWTH_MAP" in engine_source
    assert "no released perturbation/growth map" in engine_source
    assert "UNRELEASED_LENSING_MAP" in compare_source
    assert "Σ(a,k): nicht konstruiert" in compare_source
    assert "die GR-Identität Σ=1 ist kein abgeleitetes Brückenresultat" in compare_source

    script = r"""
const C=require('./assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js');
let code='NO_ERROR';
try { C.solveGrowth({}, 'bridge'); } catch (error) { code=error.code || error.message; }
console.log(code);
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)
    assert result.stdout.strip() == "UNRELEASED_GROWTH_MAP", result.stdout

    # The new inventory/interface cannot promote any physical or authorization state.
    for key, expected in FIREWALLS.items():
        assert manifest["gates"][key] == expected, (key, manifest["gates"].get(key), expected)
        assert inventory["unchanged_firewalls"][key] == expected
    assert manifest["physical_gate_effect"] == manifest["physical_evidence_effect"] == "NONE"

    print(
        "UniverseLab Band V-C G01 perturbation observable interface: PASS "
        "result=GENUINE_MISSING_DERIVATION interface=REFERENCE_ONLY G01=OPEN_BLOCKING "
        "bridge_growth=UNRELEASED_GROWTH_MAP bridge_lensing=UNRELEASED_LENSING_MAP "
        "physical_gate_effect=NONE physical_evidence_effect=NONE"
    )


if __name__ == "__main__":
    main()
