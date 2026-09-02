#!/usr/bin/env python3
"""Band IV-B current-main reconciliation QA.

This test validates numerical-contract, status-pointer, public-semantics and
firewall consistency. It deliberately performs no physical backend import or
solver execution.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "band-ivb-current-main-reconciliation-report.json"

PATHS = {
    "contract": ROOT / "registry/2026-09-03_UniverseLab_BandIVBCurrentMainReconciliationContract_v1.0.json",
    "current": ROOT / "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.1.json",
    "site": ROOT / "registry/2026-09-03_UniverseLab_SiteState_v1.2.json",
    "checkpoint": ROOT / "registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.32.json",
    "latest": ROOT / "registry/session-checkpoint-latest.json",
    "manifest": ROOT / "project-manifest.json",
    "engine_contract": ROOT / "registry/2026-09-01_UniverseLab_CanonicalCosmologyEngineContract_v1.0.json",
    "observatory_contract": ROOT / "registry/2026-09-01_UniverseLab_ObservatoryMigrationContract_v1.5.json",
    "compare_contract": ROOT / "registry/2026-09-01_UniverseLab_CompareSafeMigrationContract_v2.0.json",
    "emergence_contract": ROOT / "registry/2026-09-01_UniverseLab_EmergenceCanonicalGrowthAdapterContract_v1.0.json",
    "engine": ROOT / "assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js",
    "observatory_audit": ROOT / "tools/2026-09-01_UniverseLab_ObservatoryMigrationAudit_v1.5.mjs",
    "compare_audit": ROOT / "tools/2026-09-01_UniverseLab_CompareSafeMigrationAudit_v2.0.mjs",
    "emergence": ROOT / "emergence.html",
    "research_de": ROOT / "research-status.html",
    "research_en": ROOT / "research-status-en.html",
    "global_shell": ROOT / "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js",
    "sitemap": ROOT / "sitemap.xml",
    "old_current": ROOT / "registry/2026-09-01_UniverseLab_CurrentMainCanonicalState_v1.0.json",
    "old_site": ROOT / "registry/2026-09-01_UniverseLab_SiteState_v1.1.json",
    "old_checkpoint": ROOT / "registry/2026-09-01_UniverseLab_SessionCheckpoint_v1.31.json",
}

report: dict[str, Any] = {
    "schema": "universelab.band-ivb-current-main-reconciliation-test-result.v1",
    "status": "PASS",
    "checks": [],
    "physical_gate_effect": "NONE",
    "physical_evidence_effect": "NONE",
}


def add(name: str, fn: Callable[[], Any]) -> None:
    try:
        detail = fn()
        report["checks"].append({"name": name, "status": "PASS", "detail": detail or {}})
    except Exception as exc:  # noqa: BLE001 - report every fail-closed witness
        report["status"] = "FAIL"
        report["checks"].append({"name": name, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})


def load(name: str) -> dict[str, Any]:
    value = json.loads(PATHS[name].read_text(encoding="utf-8"))
    assert isinstance(value, dict), name
    return value


def text(name: str) -> str:
    return PATHS[name].read_text(encoding="utf-8")


def check_paths() -> dict[str, Any]:
    missing = [str(path.relative_to(ROOT)) for path in PATHS.values() if not path.is_file()]
    assert not missing, missing
    return {"required_paths": len(PATHS)}


def check_reference_closure() -> dict[str, Any]:
    values = {"Or": .000092, "Om": .315, "Ode": .684908, "Ok": 0.0}
    closure = sum(values.values())
    assert abs(closure - 1) < 1e-15
    for name in ("observatory_audit", "compare_audit"):
        source = text(name)
        for token in (
            "recovered.params.Or-.000092",
            "recovered.params.Ode-.684908",
            "recovered.params.Ok",
            "closure-1",
        ):
            assert token in source, (name, token)
        assert "recovered.params.Ode-.685" not in source
    return {**values, "closure": closure}


def check_bridge_scale() -> dict[str, Any]:
    source = text("engine")
    assert "const REVISION='1.0.2'" in source
    assert "function bridgeScale(p){return p.ac??p.Rchi/(p.Rchi+2.5);}" in source
    assert "Math.max(0.02,p.Rchi)" not in source
    assert "Math.max(0.02, p.Rchi)" not in source
    script = r"""
const C=require('./assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js');
const values=[.1,.02,.01,1e-4,1e-8].map(Rchi=>({Rchi,ac:C.bridgeScale(C.normalizeParams({Rchi})),expected:Rchi/(Rchi+2.5)}));
let invalid=null;try{C.normalizeParams({Rchi:0});}catch(error){invalid=error.code;}
console.log(JSON.stringify({version:C.VERSION,revision:C.REVISION,values,invalid}));
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data["version"] == "1.0.0"
    assert data["revision"] == "1.0.2"
    assert data["invalid"] == "INVALID_RCHI"
    for row in data["values"]:
        assert abs(row["ac"] - row["expected"]) <= 2e-16 * max(1.0, abs(row["expected"]))
    ratio = data["values"][-1]["ac"] / data["values"][-1]["Rchi"]
    assert abs(ratio - .4) < 2e-9
    return {"values": data["values"], "small_Rchi_ratio": ratio}


def check_engine_contract() -> dict[str, Any]:
    value = load("engine_contract")
    assert value["version"] == "1.0.2"
    assert value["engine"]["api_version"] == "1.0.0"
    assert value["engine"]["implementation_revision"] == "1.0.2"
    bridge = value["models"]["bridge"]
    assert bridge["a_c"] == "Rchi/(Rchi+2.5)"
    assert bridge["Rchi_domain"] == "Rchi > 0"
    assert bridge["hidden_Rchi_floor"] is False
    assert value["migration"]["review_pending_pages"] == []
    assert value["migration"]["remaining_independent_cosmology_engines"] == []
    assert value["physical_gate_effect"] == "NONE"
    assert value["physical_evidence_effect"] == "NONE"
    return {"version": value["version"], "migration_stage": value["migration"]["stage"]}


def check_state_successors() -> dict[str, Any]:
    current, site, checkpoint, latest, manifest = map(load, ("current", "site", "checkpoint", "latest", "manifest"))
    assert current["supersedes"].endswith("CurrentMainCanonicalState_v1.0.json")
    assert site["supersedes"].endswith("SiteState_v1.1.json")
    assert checkpoint["supersedes"].endswith("SessionCheckpoint_v1.31.json")
    assert latest["canonical_snapshot"] == "registry/2026-09-03_UniverseLab_SessionCheckpoint_v1.32.json"
    assert latest["canonical_state"] == "registry/2026-09-03_UniverseLab_CurrentMainCanonicalState_v1.1.json"
    assert latest["site_state"] == "registry/2026-09-03_UniverseLab_SiteState_v1.2.json"
    assert manifest["canonical_state"] == latest["canonical_state"]
    assert manifest["site_state"] == latest["site_state"]
    assert manifest["session_checkpoint"] == latest["canonical_snapshot"]
    assert manifest["public_numerical_platform"]["implementation_revision"] == "1.0.2"
    assert manifest["public_numerical_platform"]["remaining_independent_engines"] == 0
    assert manifest["public_numerical_platform"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    assert current["basis_main_commit"] == "30b781f84d9c7c9fc74fac1adb34e4d935b1679b"
    assert site["basis_main_commit"] == current["basis_main_commit"]
    assert checkpoint["basis_commit"] == current["basis_main_commit"]
    return {
        "current": PATHS["current"].name,
        "site": PATHS["site"].name,
        "checkpoint": PATHS["checkpoint"].name,
    }


def check_historical_snapshots() -> dict[str, Any]:
    # Presence plus self-declared older version/date guards against accidental deletion
    # or replacement by the latest-pointer update.
    old_current, old_site, old_checkpoint = map(load, ("old_current", "old_site", "old_checkpoint"))
    assert old_current["version"].startswith("1.0")
    assert old_site["version"].startswith("1.1")
    assert old_checkpoint["checkpoint_id"].endswith("031")
    assert old_current.get("snapshot_date") == "2026-09-01"
    return {"preserved": [path.name for key, path in PATHS.items() if key.startswith("old_")]}


def check_migration_contracts() -> dict[str, Any]:
    observatory, compare, emergence = map(load, ("observatory_contract", "compare_contract", "emergence_contract"))
    assert observatory["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    assert compare["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    assert emergence["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    assert observatory["reference_closure"]["Omega_DE"] == .684908
    assert compare["reference_closure"]["Omega_DE"] == .684908
    assert emergence["canonical_engine_revision"] == "1.0.2"
    assert compare["growth_contract"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    for value in (observatory, compare, emergence):
        assert value["physical_gate_effect"] == "NONE"
        assert value["physical_evidence_effect"] == "NONE"
    return {"observatory": observatory["status"], "compare": compare["status"], "emergence": emergence["status"]}


def check_public_semantics() -> dict[str, Any]:
    emergence = text("emergence")
    assert "user-scalable=no" not in emergence
    assert "ΛCDM-Anzeigezeit (Referenz)" in emergence
    assert "Physikalisch: ΛCDM" not in emergence
    for name in ("research_de", "research_en"):
        source = text(name)
        assert "2026-09-03" in source
        assert "NOT_RATIFIED" in source
        assert "NOT_RELEASED" in source
        assert "NOT_ADMISSIBLE" in source
        assert "UNRELEASED_GROWTH_MAP" in source
    shell = text("global_shell")
    assert "2026-09-03_UniverseLab_SiteState_v1.2.json" in shell
    return {"mobile_zoom": "RESTORED", "emergence_label": "REFERENCE", "status_languages": ["de", "en"]}


def check_sitemap_shape() -> dict[str, Any]:
    source = text("sitemap")
    locations = re.findall(r"<loc>([^<]+)</loc>", source)
    dates = re.findall(r"<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>", source)
    assert locations and len(locations) == len(dates)
    assert len(locations) == len(set(locations))
    assert all(location.startswith("https://stefanhasselm74314-byte.github.io/UniverseLab/") for location in locations)
    return {"entries": len(locations), "distinct_lastmod_dates": sorted(set(dates))}


def check_firewalls() -> dict[str, Any]:
    contract, current, site, latest, manifest = map(load, ("contract", "current", "site", "latest", "manifest"))
    sources = [contract["gate_state"], current["physical_governance"], latest["physical_governance"], manifest["gates"]]
    for gates in sources:
        assert gates.get("ratified_human_trust_root", gates.get("RATIFIED_HUMAN_TRUST_ROOT")) == "NOT_RATIFIED"
        assert gates.get("runtime_issuance_bindings", gates.get("RUNTIME_ISSUANCE_BINDINGS")) == "BLOCKED"
        assert gates.get("operative_authorization_decision", gates.get("AuthorizationDecision")) == "NOT_CREATED"
        assert gates.get("operative_single_use_grant", gates.get("SingleUseGrant")) == "NOT_CREATED"
        assert gates.get("backend_import", gates.get("BACKEND_IMPORT")) == "NOT_EXECUTED"
        assert gates.get("solver_execution", gates.get("SOLVER_EXECUTION")) == "NOT_EXECUTED"
        assert gates["K1-D"] == "NOT_RELEASED"
        assert gates["K1-E"] == "NOT_ADMISSIBLE"
    assert contract["parked_external_human_action"]["affects_band_ivb_completion"] is False
    assert contract["physical_gate_effect"] == "NONE"
    assert contract["physical_evidence_effect"] == "NONE"
    assert current["physical_evidence_effect"] == "NONE"
    assert site["physical_evidence_effect"] == "NONE"
    return {"checked_gate_sources": len(sources), "physical_gate_effect": "NONE", "physical_evidence_effect": "NONE"}


add("required_paths_exist", check_paths)
add("radiation_inclusive_flat_reset_closure", check_reference_closure)
add("bridge_scale_exact_domain_and_asymptotic", check_bridge_scale)
add("canonical_engine_contract_reconciled", check_engine_contract)
add("dated_state_successors_and_pointers", check_state_successors)
add("historical_state_snapshots_preserved", check_historical_snapshots)
add("page_migration_contracts_reconciled", check_migration_contracts)
add("public_semantics_and_accessibility", check_public_semantics)
add("sitemap_structure", check_sitemap_shape)
add("physical_and_authorization_firewalls", check_firewalls)

REPORT.write_text(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(report, sort_keys=True, indent=2, ensure_ascii=False))
if report["status"] != "PASS":
    sys.exit(1)
