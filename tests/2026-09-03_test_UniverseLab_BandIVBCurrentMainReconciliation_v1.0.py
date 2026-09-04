#!/usr/bin/env python3
"""Successor-aware Band IV-B current-main reconciliation QA.

Band IV-B numerical invariants remain frozen evidence. Current-state/public
semantics resolve through the active checkpoint alias so later append-only
successors do not fail merely because their dated status page is newer.
No physical execution is performed.
"""
from __future__ import annotations

from datetime import date
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
    except Exception as exc:  # noqa: BLE001
        report["status"] = "FAIL"
        report["checks"].append({"name": name, "status": "FAIL", "error": f"{type(exc).__name__}: {exc}"})


def load(name: str) -> dict[str, Any]:
    value = json.loads(PATHS[name].read_text(encoding="utf-8"))
    assert isinstance(value, dict), name
    return value


def load_rel(value: str, context: str) -> dict[str, Any]:
    assert isinstance(value, str) and value and not value.startswith("/"), context
    path = ROOT / value
    assert path.is_file(), f"{context}: missing {value}"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict), context
    return data


def active_chain() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    latest = load("latest")
    checkpoint = load_rel(latest["canonical_snapshot"], "latest.canonical_snapshot")
    current = load_rel(latest["canonical_state"], "latest.canonical_state")
    site = load_rel(latest["site_state"], "latest.site_state")
    assert latest == checkpoint
    assert PATHS["latest"].read_bytes() == (ROOT / latest["canonical_snapshot"]).read_bytes()
    return latest, checkpoint, current, site


def text(name: str) -> str:
    return PATHS[name].read_text(encoding="utf-8")


def check_paths() -> dict[str, Any]:
    missing = [str(path.relative_to(ROOT)) for path in PATHS.values() if not path.is_file()]
    assert not missing, missing
    latest = load("latest")
    active = [latest["canonical_snapshot"], latest["canonical_state"], latest["site_state"]]
    assert all((ROOT / value).is_file() for value in active)
    return {"required_static_paths": len(PATHS), "active_pointer_paths": active}


def check_reference_closure() -> dict[str, Any]:
    values = {"Or": .000092, "Om": .315, "Ode": .684908, "Ok": 0.0}
    closure = sum(values.values())
    assert abs(closure - 1.0) < 1e-15
    for name in ("observatory_audit", "compare_audit"):
        source = text(name)
        for token in ("recovered.params.Or-.000092", "recovered.params.Ode-.684908", "recovered.params.Ok", "closure-1"):
            assert token in source, (name, token)
        assert "recovered.params.Ode-.685" not in source
    return {**values, "closure": closure}


def check_bridge_scale() -> dict[str, Any]:
    source = text("engine")
    assert "const REVISION='1.0.2'" in source
    assert "function bridgeScale(p){return p.ac??p.Rchi/(p.Rchi+2.5);}" in source
    assert "Math.max(0.02,p.Rchi)" not in source
    script = r"""
const C=require('./assets/2026-09-01_UniverseLab_CosmologyEngine_v1.0.js');
const values=[.1,.02,.01,1e-4,1e-8].map(Rchi=>({Rchi,ac:C.bridgeScale(C.normalizeParams({Rchi})),expected:Rchi/(Rchi+2.5)}));
let invalid=null;try{C.normalizeParams({Rchi:0});}catch(error){invalid=error.code;}
console.log(JSON.stringify({version:C.VERSION,revision:C.REVISION,values,invalid}));
"""
    result = subprocess.run(["node", "-e", script], cwd=ROOT, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    assert data["version"] == "1.0.0" and data["revision"] == "1.0.2"
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
    assert value["physical_gate_effect"] == value["physical_evidence_effect"] == "NONE"
    return {"version": value["version"], "migration_stage": value["migration"]["stage"]}


def check_state_successors() -> dict[str, Any]:
    ivb_current, ivb_site, ivb_checkpoint = map(load, ("current", "site", "checkpoint"))
    assert ivb_current["supersedes"].endswith("CurrentMainCanonicalState_v1.0.json")
    assert ivb_site["supersedes"].endswith("SiteState_v1.1.json")
    assert ivb_checkpoint["supersedes"].endswith("SessionCheckpoint_v1.31.json")
    assert ivb_current["basis_main_commit"] == "30b781f84d9c7c9fc74fac1adb34e4d935b1679b"
    assert ivb_site["basis_main_commit"] == ivb_current["basis_main_commit"]
    assert ivb_checkpoint["basis_commit"] == ivb_current["basis_main_commit"]

    latest, checkpoint, current, site = active_chain()
    manifest = load("manifest")
    assert manifest["canonical_state"] == latest["canonical_state"]
    assert manifest["site_state"] == latest["site_state"]
    assert manifest["session_checkpoint"] == latest["canonical_snapshot"]
    assert site["canonical_state"] == latest["canonical_state"]
    assert checkpoint["canonical_state"] == latest["canonical_state"]
    assert checkpoint["site_state"] == latest["site_state"]
    assert checkpoint["canonical_snapshot"] == latest["canonical_snapshot"]
    assert site["basis_main_commit"] == current["basis_main_commit"] == checkpoint["basis_commit"] == manifest["basis_main_commit"]
    assert manifest["public_numerical_platform"]["implementation_revision"] == "1.0.2"
    assert manifest["public_numerical_platform"]["remaining_independent_engines"] == 0
    assert manifest["public_numerical_platform"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    assert current["public_numerical_platform"]["implementation_revision"] == "1.0.2"
    assert current["public_numerical_platform"]["remaining_independent_public_cosmology_engines"] == 0
    assert current["public_numerical_platform"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    return {
        "band_ivb_snapshots": [PATHS["current"].name, PATHS["site"].name, PATHS["checkpoint"].name],
        "active_current": latest["canonical_state"],
        "active_site": latest["site_state"],
        "active_checkpoint": latest["canonical_snapshot"],
        "active_basis": current["basis_main_commit"],
    }


def check_historical_snapshots() -> dict[str, Any]:
    old_current, old_site, old_checkpoint = map(load, ("old_current", "old_site", "old_checkpoint"))
    assert old_current["version"].startswith("1.0")
    assert old_site["version"].startswith("1.1")
    assert old_checkpoint["checkpoint_id"].endswith("031")
    assert old_current.get("snapshot_date") == "2026-09-01"
    for name in ("current", "site", "checkpoint"):
        assert PATHS[name].is_file()
    return {"preserved": [path.name for key, path in PATHS.items() if key.startswith("old_")] + [PATHS[key].name for key in ("current", "site", "checkpoint")]}


def check_migration_contracts() -> dict[str, Any]:
    observatory, compare, emergence = map(load, ("observatory_contract", "compare_contract", "emergence_contract"))
    assert observatory["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    assert compare["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    assert emergence["status"] == "ACTIVE_MERGED_QA_RECONCILED"
    obs_ref = observatory["background_contract"]["reference_state"]
    cmp_ref = compare["background_contract"]["reference_state"]
    em_ref = emergence["background_contract"]["reference_parameters"]
    for reference, de_key in ((obs_ref, "Omega_DE"), (cmp_ref, "Omega_DE"), (em_ref, "Omega_Lambda")):
        assert reference["Omega_r"] == .000092
        assert reference["Omega_m"] == .315
        assert reference[de_key] == .684908
        assert reference["Omega_k"] == 0.0
    assert compare["models"]["bridge_scale_hidden_floor"] is False
    assert compare["observable_firewalls"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    assert emergence["growth_contract"]["bridge_growth"] == "UNRELEASED_GROWTH_MAP"
    assert emergence["public_semantics"]["former_ambiguous_label_removed"] is True
    assert emergence["accessibility"]["mobile_zoom_allowed"] is True
    for value in (observatory, compare, emergence):
        assert value["physical_gate_effect"] == value["physical_evidence_effect"] == "NONE"
    return {"observatory": observatory["status"], "compare": compare["status"], "emergence": emergence["status"]}


def check_public_semantics() -> dict[str, Any]:
    emergence = text("emergence")
    assert "user-scalable=no" not in emergence
    assert "ΛCDM-Anzeigezeit (Referenz)" in emergence
    assert "Physikalisch: ΛCDM" not in emergence

    latest, checkpoint, current, _site = active_chain()
    current_path = latest["canonical_state"]
    site_path = latest["site_state"]
    de = text("research_de")
    en = text("research_en")
    snapshot_date = current["snapshot_date"]
    assert snapshot_date == checkpoint["timestamp"][:10]
    y, m, d = map(int, snapshot_date.split("-"))
    de_date = f"{d}. September {y}" if m == 9 else snapshot_date
    en_date = f"{d} September {y}" if m == 9 else snapshot_date

    for source in (de, en):
        assert current_path in source
        assert "NOT RELEASED" in source
        assert "NOT ADMISSIBLE" in source
        assert "NOT RATIFIED" in source
    assert de_date in de
    assert en_date in en
    assert "Bridge-Growth und Bridge-Lensing bleiben ausdrücklich unveröffentlicht" in de or "Bridge-Growth" in de and "Bridge-Lensing" in de
    assert "Bridge growth and bridge lensing remain unreleased" in en
    assert "keine Evidenz für HZT" in de
    assert "not evidence for HZT" in en

    shell = text("global_shell")
    assert site_path in shell
    return {
        "mobile_zoom": "RESTORED",
        "emergence_label": "REFERENCE",
        "status_languages": ["de", "en"],
        "snapshot_date": snapshot_date,
        "machine_state_source": current_path,
        "shell_site_state_source": site_path,
    }


def check_sitemap_shape() -> dict[str, Any]:
    source = text("sitemap")
    locations = re.findall(r"<loc>([^<]+)</loc>", source)
    dates = re.findall(r"<lastmod>(\d{4}-\d{2}-\d{2})</lastmod>", source)
    assert locations and len(locations) == len(dates)
    assert len(locations) == len(set(locations))
    assert all(location.startswith("https://stefanhasselm74314-byte.github.io/UniverseLab/") for location in locations)
    return {"entries": len(locations), "distinct_lastmod_dates": sorted(set(dates))}


def check_firewalls() -> dict[str, Any]:
    contract = load("contract")
    _latest, checkpoint, current, site = active_chain()
    manifest = load("manifest")
    sources = [contract["gate_state"], current["physical_governance"], checkpoint["physical_governance"], manifest["gates"]]
    for g in sources:
        assert g.get("ratified_human_trust_root", g.get("RATIFIED_HUMAN_TRUST_ROOT")) == "NOT_RATIFIED"
        assert g.get("runtime_issuance_bindings", g.get("RUNTIME_ISSUANCE_BINDINGS")) == "BLOCKED"
        assert g.get("operative_authorization_decision", g.get("AuthorizationDecision")) == "NOT_CREATED"
        assert g.get("operative_single_use_grant", g.get("SingleUseGrant")) == "NOT_CREATED"
        assert g.get("backend_import", g.get("BACKEND_IMPORT")) == "NOT_EXECUTED"
        assert g.get("solver_execution", g.get("SOLVER_EXECUTION")) == "NOT_EXECUTED"
        assert g["K1-D"] == "NOT_RELEASED"
        assert g["K1-E"] == "NOT_ADMISSIBLE"
    assert site["governance"]["physical_evidence_effect"] == "NONE"
    assert manifest["physical_gate_effect"] == manifest["physical_evidence_effect"] == "NONE"
    return {"active_current_state": load("latest")["canonical_state"], "checked_full_gate_sources": len(sources), "site_governance_checked": True, "physical_gate_effect": "NONE", "physical_evidence_effect": "NONE"}


def main() -> None:
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

    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
