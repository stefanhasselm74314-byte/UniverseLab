#!/usr/bin/env python3
"""RC09 noncanonical four-way draft pointer consistency and deliberate release blockers."""
from __future__ import annotations
import copy
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE="51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
TREE="65f423f04bbb2f1462f120a6b31073644cdc28cc"
S="drafts/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4_DRAFT.json"
C="drafts/2026-11-03_UniverseLab_SessionCheckpoint_v1.35_DRAFT.json"
T="drafts/2026-11-03_UniverseLab_SiteState_v1.5_DRAFT.json"
M="drafts/2026-11-03_UniverseLab_ProjectManifest_v2.35_DRAFT.json"
OLD_T="registry/2026-09-04_UniverseLab_SiteState_v1.4.json"
OLD_S="registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json"
OLD_C="registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json"
PRE="drafts/2026-11-03_UniverseLab_RC09_PromotionPreflight_v1.0_DRAFT.md"

def read(p):
    return json.loads((ROOT/p).read_text(encoding="utf-8"))

def verify(s,c,t,m,old_site):
    for x in (s,c,t,m):
        assert x["physical_gate_effect"]==x["physical_evidence_effect"]=="NONE"
    assert s["basis_main_commit"]==c["basis_commit"]==t["basis_main_commit"]==m["basis_main_commit"]==BASE
    assert s["basis_main_tree"]==c["basis_tree"]==t["basis_main_tree"]==m["basis_main_tree"]==TREE
    assert set(old_site).issubset(set(t)), "SiteState lost existing top-level fields"
    for key in ("governance","analysis_state","pages","modules"):
        assert old_site[key]==t[key], "SiteState field silently changed: "+key
    assert t["version"]=="1.5.0-DRAFT"
    assert t["supersedes"]==OLD_T
    assert s["status_sources"]["site_state"]==T
    assert c["site_state"]==T
    assert m["site_state"]==m["central_registries"]["site_state"]==m["current_status_sources"]["site_state"]==T
    assert m["platform_governance"]["site_state"]==T
    assert t["canonical_state"]==t["status_sources"]["canonical_state"]==c["canonical_state"]==m["canonical_state"]==S
    assert t["status_sources"]["session_checkpoint"]==m["session_checkpoint"]==m["current_status_sources"]["session_checkpoint"]==C
    assert t["reconciliation_addendum"]["status"]=="DRAFT_NOT_CANONICAL"
    assert t["reconciliation_addendum"]["public_references"]=="STILL_POINT_TO_SEPTEMBER_CHAIN_NOT_UPDATED"
    assert t["reconciliation_addendum"]["snapshot_timestamp_status"]=="INHERITED_SOURCE_VALUE_UNSUITABLE_FOR_CANONICAL_PROMOTION"
    assert t["snapshot_timestamp"]==old_site["snapshot_timestamp"]=="2026-09-04T12:46:00+02:00"
    assert s["snapshot_timestamp"]=="2026-09-04T12:46:00+02:00"
    assert c["canonical_snapshot"]==OLD_C, "historical checkpoint pointer must remain marked unresolved until promotion"
    assert s["reconciliation_addendum"]["public_status_pointers"]=="SEPTEMBER_LIVE_UNCHANGED_RELEASE_BLOCKER"
    assert c["reconciliation_addendum"]["public_status_pointers"]=="SEPTEMBER_LIVE_UNCHANGED_RELEASE_BLOCKER"
    assert m["reconciliation_addendum"]["public_status_pointers"]=="SEPTEMBER_LIVE_UNCHANGED_RELEASE_BLOCKER"
    assert s["active_analysis_block"]["blocking_scientific_or_empirical_gaps"]==10
    assert t["governance"]["K1-D"]==s["physical_governance"]["K1-D"]==c["gate_state"]["K1-D"]==m["gates"]["K1-D"]=="NOT_RELEASED"
    assert t["governance"]["K1-E"]==s["physical_governance"]["K1-E"]==c["gate_state"]["K1-E"]==m["gates"]["K1-E"]=="NOT_ADMISSIBLE"
    assert c["gate_state"]["FM-G0"]==m["gates"]["FM-G0"]=="OPEN"
    for x in (s,c,m):
        assert x["reconciliation_addendum"]["site_state_draft"]==T
        assert x["reconciliation_addendum"]["rc09_source_contract"]=="drafts/2026-11-03_UniverseLab_RC09_SemanticSourceContract_v1.0_DRAFT.json"

def negatives(s,c,t,m,old_site):
    mods=[
        ("bad_state_pointer",lambda s,c,t,m:t.__setitem__("canonical_state",OLD_S)),
        ("missing_site_binding",lambda s,c,t,m:m.__setitem__("site_state",OLD_T)),
        ("false_public_repair",lambda s,c,t,m:t["reconciliation_addendum"].__setitem__("public_references","UPDATED")),
        ("wrong_tree",lambda s,c,t,m:t.__setitem__("basis_main_tree","0"*40)),
        ("physical_gate_promotion",lambda s,c,t,m:t["governance"].__setitem__("K1-D","RELEASED")),
        ("ghosted_historical_timestamp",lambda s,c,t,m:t.__setitem__("snapshot_timestamp","2026-11-03T00:00:00+01:00")),
        ("incomplete_site_fields",lambda s,c,t,m:t.pop("pages")),
        ("fake_new_canonical_checkpoint",lambda s,c,t,m:c.__setitem__("canonical_snapshot","registry/not-yet-ratified.json")),
    ]
    for name, fn in mods:
        a,b,d,e=copy.deepcopy((s,c,t,m))
        fn(a,b,d,e)
        try:verify(a,b,d,e,old_site)
        except (AssertionError,KeyError):print("PASS negative:",name)
        else:raise AssertionError("False positive in negative control "+name)

def main():
    s,c,t,m=[read(p) for p in (S,C,T,M)]
    old=read(OLD_T)
    assert subprocess.check_output(["git","hash-object",str(ROOT/OLD_T)],text=True).strip()=="d44ace0fc5c2c5ad530439627daafb1f437436ae"
    assert (ROOT/PRE).is_file()
    verify(s,c,t,m,old)
    for p,needle in (("research-status.html",OLD_S),("research-status.html",OLD_C),("research-status-en.html",OLD_S),("research-status-en.html",OLD_C),("assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js",OLD_T)):
        assert needle in (ROOT/p).read_text(encoding="utf-8"),"Public old pointer unexpectedly changed: "+p
    alias=(ROOT/"registry/session-checkpoint-latest.json").read_bytes()
    orig=(ROOT/OLD_C).read_bytes()
    assert alias==orig,"Historical checkpoint alias changed outside this draft"
    negatives(s,c,t,m,old)
    print("PASS: four-way draft state/checkpoint/site/manifest pointer contract")
    print("PASS: public links still historical and properly classified as release blockers")
    print("PASS: 8 negative controls")
    print("RELEASE_STATUS = HOLD; no live pointer changes and no physical gate promotion")

if __name__=="__main__":
    main()
