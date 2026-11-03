#!/usr/bin/env python3
"""RC10: simulate a release pointer migration in RAM; NEVER write or promote files.

The simulated bundle is deliberately NOT releaseable: timestamps, owner
ratification and release commit are unresolved. It tests reference integrity
and preserves all science/authorization firewalls.
"""
from __future__ import annotations
import copy
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CONTRACT="drafts/2026-11-03_UniverseLab_RC10_ReleaseMigrationContract_v1.0_DRAFT.json"
BASE="51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
TREE="65f423f04bbb2f1462f120a6b31073644cdc28cc"
TIME_TOKEN="__RELEASE_TIMESTAMP_NOT_ASSIGNED__"
DATE_TOKEN="__RELEASE_DATE_NOT_ASSIGNED__"

def read_json(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))

def encode(obj):
    return (json.dumps(obj,ensure_ascii=False,indent=2)+"\n").encode("utf-8")

def replace_once(text,before,after,minimum=1):
    assert before!=after
    assert text.count(before)>=minimum,(before,text.count(before))
    return text.replace(before,after)

def retarget_active(obj,mapping,skip_history=True):
    """Rewrite exact pointer values only; retain declared historical metadata."""
    def walk(value,key=""):
        if key in {"supersedes","reconciliation_addendum","history_rule",
                   "merged_analysis_blocks","open_noncanonical_work"} and skip_history:
            return value
        if isinstance(value,dict):
            return {k:walk(v,k) for k,v in value.items()}
        if isinstance(value,list):
            return [walk(v) for v in value]
        if isinstance(value,str):
            return mapping.get(value,value)
        return value
    return walk(obj)

def active_strings(obj):
    def walk(v,key=""):
        if key in {"supersedes","reconciliation_addendum","history_rule",
                   "merged_analysis_blocks","open_noncanonical_work"}:
            return
        if isinstance(v,dict):
            for k,x in v.items():
                yield from walk(x,k)
        elif isinstance(v,list):
            for x in v:yield from walk(x)
        elif isinstance(v,str):
            yield v
    return list(walk(obj))

def live_consumers(old):
    """Scan all tracked HTML and JS; fail closed on additional live consumers."""
    keep={"research-status.html","research-status-en.html",
          "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"}
    tracked=subprocess.check_output(["git","ls-files","-z"]).decode().split("\x00")
    active=[]
    for p in tracked:
        if not p or not p.endswith((".html",".js")):continue
        if p.startswith(("drafts/","tests/",".github/","node_modules/")):continue
        f=ROOT/p
        if not f.is_file():continue
        text=f.read_text(encoding="utf-8",errors="replace")
        hits={k:text.count(old[k]) for k in ("state","checkpoint","site") if old[k] in text}
        if hits:active.append((p,hits))
    unexpected=[p for p,_ in active if p not in keep]
    assert not unexpected,("Unmapped additional HTML/JS live consumers",unexpected)
    assert {p for p,_ in active}==keep,(active,keep)
    return active

def simulate(contract):
    assert contract["schema"]=="universelab.rc10.hypothetical-migration-contract.v1"
    assert contract["status"]=="DRAFT_SIMULATION_ONLY_NOT_A_RELEASE"
    assert contract["source_verified_main_commit"]==BASE
    assert contract["source_verified_tree"]==TREE
    assert contract["physical_gate_effect"]==contract["physical_evidence_effect"]=="NONE"
    assert not any(contract["no_write_policy"][k] for k in (
        "writes_to_registry","writes_to_project_manifest","writes_to_public_html",
        "writes_to_shell","writes_to_checkpoint_alias","merge_permission"))
    assert "EXPLICIT_OWNER_SCOPED_RATIFICATION_ABSENT" in contract["release_blockers"]
    old,new,inp=(contract[k] for k in ("historical_live_paths",
                                        "proposed_future_targets","draft_inputs"))
    mapping={}
    for key in ("state","checkpoint","site"):
        mapping[old[key]]=new[key]
        mapping[inp[key]]=new[key]
    data={key:retarget_active(read_json(inp[key]),mapping) for key in inp}
    data["state"]["version"]="1.4.0-SIMULATION"
    data["site"]["version"]="1.5.0-SIMULATION"
    data["checkpoint"]["checkpoint_id"]="UL-CHK-20261103-035-SIMULATION"
    data["manifest"]["release"]="2.35-reconciliation-SIMULATION"
    data["state"]["snapshot_timestamp"]=TIME_TOKEN
    data["site"]["snapshot_timestamp"]=TIME_TOKEN
    data["checkpoint"]["timestamp"]=TIME_TOKEN
    data["state"]["snapshot_date"]=DATE_TOKEN
    data["site"]["snapshot_date"]=DATE_TOKEN
    data["manifest"]["release_date"]=DATE_TOKEN
    data["checkpoint"]["canonical_snapshot"]=new["checkpoint"]
    for item in data.values():
        assert item["physical_gate_effect"]==item["physical_evidence_effect"]=="NONE"
    assert data["state"]["basis_main_commit"]==data["site"]["basis_main_commit"]==data["manifest"]["basis_main_commit"]==data["checkpoint"]["basis_commit"]==BASE
    assert data["state"]["basis_main_tree"]==data["site"]["basis_main_tree"]==data["manifest"]["basis_main_tree"]==data["checkpoint"]["basis_tree"]==TREE
    assert data["manifest"]["gates"]["K1-D"]=="NOT_RELEASED"
    assert data["manifest"]["gates"]["K1-E"]=="NOT_ADMISSIBLE"
    assert data["manifest"]["gates"]["FM-G0"]=="OPEN"
    assert data["state"]["physical_governance"]["physical_background"]=="NOT_ESTABLISHED"
    assert data["state"]["physical_governance"]["physical_response_rank"]=="NOT_EXECUTED"
    assert data["checkpoint"]["gate_state"]["AuthorizationDecision"]=="NOT_CREATED"
    assert data["checkpoint"]["gate_state"]["SingleUseGrant"]=="NOT_CREATED"

    de=(ROOT/old["de"]).read_text(encoding="utf-8")
    en=(ROOT/old["en"]).read_text(encoding="utf-8")
    js=(ROOT/old["shell"]).read_text(encoding="utf-8")
    for key in ("state","site","checkpoint"):
        de=replace_once(de,old[key],new[key])
        en=replace_once(en,old[key],new[key])
    for a,b in (("Canonical State v1.3","Canonical State v1.4"),
                ("SiteState v1.4","SiteState v1.5"),
                ("Checkpoint v1.34","Checkpoint v1.35")):
        de=de.replace(a,b)
        en=en.replace(a,b)
    js=replace_once(js,"./"+old["site"],"./"+new["site"])
    js=replace_once(js,"const VERSION='1.1.6';","const VERSION='1.1.7-SIMULATION';")
    files={
        new["state"]:encode(data["state"]),
        new["checkpoint"]:encode(data["checkpoint"]),
        new["site"]:encode(data["site"]),
        new["manifest"]:encode(data["manifest"]),
        new["alias"]:encode(data["checkpoint"]),
        new["de"]:de.encode("utf-8"),
        new["en"]:en.encode("utf-8"),
        new["shell"]:js.encode("utf-8"),
    }
    assert len(files)==8
    return files,data

def assert_preview(files,data,contract):
    old,new=(contract[x] for x in ("historical_live_paths","proposed_future_targets"))
    assert files[new["checkpoint"]]==files[new["alias"]],"checkpoint alias not byte-identical"
    for key in ("state","site","checkpoint","manifest"):
        assert data[key]["reconciliation_addendum"]["status"]=="DRAFT_NOT_CANONICAL"
        for value in active_strings(data[key]):
            assert value not in [old[k] for k in ("state","site","checkpoint")]
            assert value not in [contract["draft_inputs"][k] for k in ("state","site","checkpoint")]
    state,cp,site,manifest=(data[x] for x in ("state","checkpoint","site","manifest"))
    assert state["status_sources"]["session_checkpoint"]==new["checkpoint"]
    assert state["status_sources"]["site_state"]==new["site"]
    assert cp["canonical_state"]==site["canonical_state"]==manifest["canonical_state"]==new["state"]
    assert cp["site_state"]==manifest["site_state"]==new["site"]
    assert cp["canonical_snapshot"]==manifest["session_checkpoint"]==new["checkpoint"]
    assert site["status_sources"]["session_checkpoint"]==new["checkpoint"]
    assert manifest["central_registries"]["current_main_canonical_state"]==new["state"]
    assert manifest["central_registries"]["site_state"]==new["site"]
    assert manifest["central_registries"]["session_checkpoint"]==new["checkpoint"]
    for lang in ("de","en"):
        html=files[new[lang]].decode("utf-8")
        for key in ("state","site","checkpoint"):
            assert new[key] in html
            assert old[key] not in html
    js=files[new["shell"]].decode("utf-8")
    assert "./"+new["site"] in js and old["site"] not in js
    assert state["snapshot_timestamp"]==site["snapshot_timestamp"]==cp["timestamp"]==TIME_TOKEN
    assert state["snapshot_date"]==site["snapshot_date"]==manifest["release_date"]==DATE_TOKEN
    assert "SIMULATION" in state["version"]
    assert "SIMULATION" in site["version"]
    assert "SIMULATION" in cp["checkpoint_id"]
    assert "SIMULATION" in manifest["release"]
    assert contract["timing"]["snapshot_timestamp"]==TIME_TOKEN
    assert contract["timing"]["checkpoint_timestamp"]==TIME_TOKEN
    assert contract["timing"]["release_date"]==DATE_TOKEN
    return True

def negatives(files,data,contract):
    old,new=(contract[x] for x in ("historical_live_paths","proposed_future_targets"))
    tests=[
      ("broken_checkpoint_alias",lambda f,d,c:f.__setitem__(new["alias"],b"not equal")),
      ("old_de_status_link",lambda f,d,c:f.__setitem__(new["de"],f[new["de"]].replace(new["site"].encode(),old["site"].encode()))),
      ("old_en_status_link",lambda f,d,c:f.__setitem__(new["en"],f[new["en"]].replace(new["checkpoint"].encode(),old["checkpoint"].encode()))),
      ("stale_shell_site",lambda f,d,c:f.__setitem__(new["shell"],f[new["shell"]].replace(new["site"].encode(),old["site"].encode()))),
      ("manifest_old_state",lambda f,d,c:d["manifest"].__setitem__("canonical_state",old["state"])),
      ("fake_release_clock",lambda f,d,c:d["state"].__setitem__("snapshot_timestamp","2026-11-03T00:00:00+01:00")),
      ("promoted_gate",lambda f,d,c:d["manifest"]["gates"].__setitem__("K1-D","RELEASED")),
      ("false_owner_authorization",lambda f,d,c:c["release_blockers"].remove("EXPLICIT_OWNER_SCOPED_RATIFICATION_ABSENT")),
    ]
    for name,mutate in tests:
        f,d,c=copy.deepcopy((files,data,contract))
        mutate(f,d,c)
        try:
            # Ensure metadata mutations are also covered.
            assert "EXPLICIT_OWNER_SCOPED_RATIFICATION_ABSENT" in c["release_blockers"]
            assert d["manifest"]["gates"]["K1-D"]=="NOT_RELEASED"
            assert_preview(f,d,c)
        except (AssertionError,KeyError):
            print("PASS negative:",name)
        else:
            raise AssertionError("Negative simulation accepted "+name)

def main():
    c=read_json(CONTRACT)
    active=live_consumers(c["historical_live_paths"])
    files,data=simulate(c)
    assert_preview(files,data,c)
    negatives(files,data,c)
    print("RC10 PASS: 8 hypothetical outputs (memory only), full active HTML/JS consumer scan")
    print("RC10 PASS: original live consumers =",active)
    print("RC10 PASS: 8 negative controls")
    print("RELEASE_STATUS=BLOCKED; TIMESTAMP=UNASSIGNED; OWNER_RATIFICATION=ABSENT")
    print("NO_FILES_WRITTEN=TRUE; NO_SCIENTIFIC_GATE_PROMOTION=TRUE")

if __name__=="__main__":
    main()
