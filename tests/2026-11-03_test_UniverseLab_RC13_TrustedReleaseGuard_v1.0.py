#!/usr/bin/env python3
"""Unit tests for the *candidate* RC13 trusted-base release guard.

Mocks GitHub REST responses; these tests validate code logic only. They cannot
demonstrate that a future pull_request_target job is enforced by main rulesets.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
from unittest import TestCase, main as unit_main
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/2026-11-03_UniverseLab_RC13_TrustedReleaseGuard_v1.0.py"
spec = importlib.util.spec_from_file_location("universelab_rc13_guard", SCRIPT)
g = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(g)

BASE="a"*40
HEAD="b"*40
TREE="c"*40
DATE="2026-11-03"
TIME="2026-11-03T12:00:00+01:00"
OLD_STATE="registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json"
OLD_CP="registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json"
OLD_SITE="registry/2026-09-04_UniverseLab_SiteState_v1.4.json"
STATE="registry/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4.json"
CP="registry/2026-11-03_UniverseLab_SessionCheckpoint_v1.35.json"
SITE="registry/2026-11-03_UniverseLab_SiteState_v1.5.json"
MANIFEST="project-manifest.json"
ALIAS="registry/session-checkpoint-latest.json"
SHELL="assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"

def encoded(obj):
    return (json.dumps(obj,ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")

def fixture():
    oldphysical={"K1-D":"NOT_RELEASED","K1-E":"NOT_ADMISSIBLE",
                 "physical_background":"NOT_ESTABLISHED",
                 "physical_response_rank":"NOT_EXECUTED"}
    fields={"physical_gate_effect":"NONE","physical_evidence_effect":"NONE"}
    oldmanifest={"canonical_state":OLD_STATE,"session_checkpoint":OLD_CP,
                 "site_state":OLD_SITE,"gates":copy.deepcopy(g.GATE_EXPECTED)}
    newmanifest={
        **fields,"canonical_state":STATE,"session_checkpoint":CP,"site_state":SITE,
        "release_date":DATE,"basis_main_commit":BASE,"basis_main_tree":TREE,
        "gates":copy.deepcopy(g.GATE_EXPECTED),
        "current_status_sources":{"canonical_state":STATE,"site_state":SITE,
                                  "session_checkpoint":CP},
        "central_registries":{"current_main_canonical_state":STATE,
                              "site_state":SITE,"session_checkpoint":CP}
    }
    state={**fields,"status":"POST_STATE_RECONCILED",
           "basis_main_commit":BASE,"basis_main_tree":TREE,
           "snapshot_date":DATE,"snapshot_timestamp":TIME,
           "physical_governance":copy.deepcopy(oldphysical),
           "status_sources":{"site_state":SITE,"session_checkpoint":CP}}
    cp={**fields,"basis_commit":BASE,"basis_tree":TREE,
        "timestamp":TIME,"canonical_snapshot":CP,
        "canonical_state":STATE,"site_state":SITE,
        "gate_state":copy.deepcopy(g.GATE_EXPECTED)}
    site={**fields,"basis_main_commit":BASE,"basis_main_tree":TREE,
          "snapshot_date":DATE,"snapshot_timestamp":TIME,"canonical_state":STATE,
          "status_sources":{"canonical_state":STATE,"session_checkpoint":CP},
          "governance":copy.deepcopy(oldphysical)}
    de=("\n".join([STATE,CP,SITE])).encode("utf-8")
    en=de
    script=("./"+SITE+"\n").encode("utf-8")
    contents={
        (MANIFEST,BASE):encoded(oldmanifest),
        (OLD_STATE,BASE):encoded({"physical_governance":oldphysical}),
        (OLD_CP,BASE):encoded({"gate_state":copy.deepcopy(g.GATE_EXPECTED)}),
        (OLD_SITE,BASE):encoded({"governance":copy.deepcopy(oldphysical)}),
        (MANIFEST,HEAD):encoded(newmanifest),
        (STATE,HEAD):encoded(state),
        (CP,HEAD):encoded(cp),
        (SITE,HEAD):encoded(site),
        (ALIAS,HEAD):encoded(cp),
        ("research-status.html",HEAD):de,
        ("research-status-en.html",HEAD):en,
        (SHELL,HEAD):script,
    }
    filelist=[
        {"filename":MANIFEST,"status":"modified"},
        {"filename":ALIAS,"status":"modified"},
        {"filename":"research-status.html","status":"modified"},
        {"filename":"research-status-en.html","status":"modified"},
        {"filename":SHELL,"status":"modified"},
        {"filename":STATE,"status":"added"},
        {"filename":CP,"status":"added"},
        {"filename":SITE,"status":"added"}
    ]
    return contents,filelist,oldmanifest

class FakeAPI:
    def __init__(self, contents=None, files=None, scopes=None, comment=True):
        self.contents_map, self.files, _=fixture()
        if contents:
            self.contents_map.update(contents)
        if files is not None:
            self.files=files
        self.scopes=scopes or {"STATE_RELEASE"}
        self.number=999
        self.head=HEAD
        self.base=BASE
        self.draft=False
        self.main_sha=BASE
        self.ruleset_enabled=True
        self.check_enabled=True
        self.ruleset_bypass=False
        self.ruleset_exclude_main=False
        self.comment_owner=True
        self.comment_exact=comment
        self.pr_calls=0
        self.race_after_first=False
        self.tree_items=[
            {"type":"blob","path":"research-status.html","sha":"d"*40},
            {"type":"blob","path":"research-status-en.html","sha":"e"*40},
            {"type":"blob","path":SHELL,"sha":"f"*40},
        ]
        self.blobs={"d"*40:self.contents_map[("research-status.html",HEAD)],
                    "e"*40:self.contents_map[("research-status-en.html",HEAD)],
                    "f"*40:self.contents_map[(SHELL,HEAD)]}

    def pr(self):
        head=("0"*40 if self.race_after_first and self.pr_calls>1
              else self.head)
        return {
            "number":self.number,"state":"open","draft":self.draft,
            "base":{"ref":"main","sha":self.base,
                    "repo":{"full_name":g.REPO}},
            "head":{"sha":head,"repo":{"full_name":g.REPO}},
        }

    def get(self,path):
        if path=="/pulls/999":
            self.pr_calls+=1
            return self.pr()
        if path=="/branches/main":
            return {"commit":{"sha":self.main_sha}}
        if path=="/git/commits/"+BASE:
            return {"sha":BASE,"tree":{"sha":TREE}}
        if path=="/rulesets/42":
            return {
                "target":"branch","enforcement":"active",
                "conditions":{"ref_name":{"include":["refs/heads/main"],"exclude":[
                    "refs/heads/main"] if self.ruleset_exclude_main else []}},
                "bypass_actors":[{"actor_id":1}] if self.ruleset_bypass else [],
                "rules":[
                    {"type":"pull_request"},
                    *([{"type":"required_status_checks",
                        "parameters":{"required_status_checks":[
                            {"context":g.TRUSTED_JOB}]}}] if self.check_enabled else [])
                ],
            }
        raise AssertionError("Unexpected GET: "+path)

    def paged(self,path,limit):
        if path.startswith("/pulls/999/files"):
            return self.files
        if path.startswith("/issues/999/comments"):
            author=("stefanhasselm74314-byte" if self.comment_owner
                    else "unknown-reviewer")
            sha=HEAD if self.comment_exact else "0"*40
            return [{"user":{"login":author},"author_association":"OWNER",
                     "body":g.approval_message(999,sha,self.scopes)}]
        if path.startswith("/rulesets?"):
            return ([{"id":42,"enforcement":"active"}]
                    if self.ruleset_enabled else [])
        raise AssertionError("Unexpected paging: "+path)

    def contents(self,path,sha):
        return self.contents_map[(path,sha)]

    def tree(self,sha):
        return self.tree_items

    def blob(self,sha):
        return self.blobs[sha]

def event_for(api):
    return {"pull_request":{
        "number":999,
        "base":{"sha":BASE},
        "head":{"sha":HEAD},
        "draft":api.draft,
    }}

class TrustGateTests(TestCase):
    def setUp(self):
        self.env=patch.dict(os.environ,{
            "GITHUB_EVENT_NAME":"pull_request_target",
            "GITHUB_REPOSITORY":g.REPO,"GITHUB_REF":"refs/heads/main",
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()

    def test_01_scope_classifier(self):
        self.assertEqual(g.classify("drafts/2026-11-03_Test_DRAFT.json"),set())
        self.assertEqual(g.classify("project-manifest.json"),{"STATE_RELEASE"})
        self.assertEqual(g.classify(g.TRUSTED_WORKFLOW),{"CONTROL_PLANE"})
        self.assertEqual(g.classify("registry/session-checkpoint-latest.json"),{"STATE_RELEASE"})
        with self.assertRaises(g.GateError):
            g.classify("../registry/site.json")

    def test_02_ordinary_pr_not_release(self):
        api=FakeAPI(files=[{"filename":"README.md","status":"modified"}])
        self.assertIn("PASS_ORDINARY",g.run_event(event_for(api),api))

    def test_03_owner_control_plane_explicit_scope(self):
        api=FakeAPI(files=[{"filename":g.TRUSTED_WORKFLOW,"status":"modified"}],
                    scopes={"CONTROL_PLANE"})
        self.assertIn("CONTROL_PLANE_OWNER_ACK",
                      g.run_event(event_for(api),api))

    def test_04_atomic_state_release(self):
        api=FakeAPI()
        self.assertIn("8-file atomic release checked",
                      g.run_event(event_for(api),api))

    def test_05_controls_negative(self):
        cases=[]
        def case(name,alter):
            api=FakeAPI()
            alter(api)
            cases.append((name,api))
        case("draft_release",lambda a:setattr(a,"draft",True))
        case("missing_owner_ack",lambda a:setattr(a,"comment_exact",False))
        case("untrusted_comment_author",lambda a:setattr(a,"comment_owner",False))
        case("no_active_ruleset",lambda a:setattr(a,"ruleset_enabled",False))
        case("no_required_check",lambda a:setattr(a,"check_enabled",False))
        case("ruleset_bypass_present",lambda a:setattr(a,"ruleset_bypass",True))
        case("ruleset_excludes_main",lambda a:setattr(a,"ruleset_exclude_main",True))
        case("live_main_drift",lambda a:setattr(a,"main_sha","0"*40))
        case("live_head_drift",lambda a:setattr(a,"head","0"*40))
        case("missing_checkpoint_alias_change",lambda a:setattr(
            a,"files",[f for f in a.files if f["filename"]!=ALIAS]))
        case("alias_content_mismatch",lambda a:a.contents_map.__setitem__(
            (ALIAS,HEAD),b"{}"))
        def promote(a):
            o=json.loads(a.contents_map[(MANIFEST,HEAD)])
            o["gates"]["K1-D"]="RELEASED"
            a.contents_map[(MANIFEST,HEAD)]=encoded(o)
        case("physical_gate_promotion",promote)
        def inject_other_gate(a):
            obj=json.loads(a.contents_map[(MANIFEST,HEAD)])
            obj["gates"]["OTHER_METHOD_GATE"]="RELEASED"
            a.contents_map[(MANIFEST,HEAD)]=encoded(obj)
        case("extra_promoted_manifest_gate",inject_other_gate)
        def inject_runtime_authorization(a):
            obj=json.loads(a.contents_map[(CP,HEAD)])
            obj["gate_state"]["AuthorizationDecision"]="CREATED"
            a.contents_map[(CP,HEAD)]=encoded(obj)
        case("checkpoint_runtime_authorization",inject_runtime_authorization)
        def inject_site_governance(a):
            obj=json.loads(a.contents_map[(SITE,HEAD)])
            obj["governance"]["RATIFIED_HUMAN_TRUST_ROOT"]="RATIFIED"
            a.contents_map[(SITE,HEAD)]=encoded(obj)
        case("site_governance_promotion",inject_site_governance)
        def change_timestamp(a):
            obj=json.loads(a.contents_map[(STATE,HEAD)])
            obj["snapshot_timestamp"]="2026-09-04T12:00:00+02:00"
            a.contents_map[(STATE,HEAD)]=encoded(obj)
        case("old_timestamp",change_timestamp)
        def change_pointer(a):
            obj=json.loads(a.contents_map[(MANIFEST,HEAD)])
            obj["canonical_state"]=OLD_STATE
            a.contents_map[(MANIFEST,HEAD)]=encoded(obj)
        case("stale_manifest_pointer",change_pointer)
        def old_de_link(a):
            a.contents_map[("research-status.html",HEAD)]=OLD_STATE.encode()
        case("old_de_link",old_de_link)
        def old_en_link(a):
            a.contents_map[("research-status-en.html",HEAD)]=OLD_CP.encode()
        case("old_en_link",old_en_link)
        def old_shell(a):
            a.contents_map[(SHELL,HEAD)]=OLD_SITE.encode()
        case("old_shell_link",old_shell)
        def extra_web(a):
            a.tree_items.append({"type":"blob","path":"navigator.html","sha":"1"*40})
            a.blobs["1"*40]=b"historical "+OLD_STATE.encode()
        case("unmapped_old_web_link",extra_web)
        case("mid_validation_head_changed",lambda a:setattr(
            a,"race_after_first",True))
        case("unexpected_file_status",lambda a:a.files.append(
            {"filename":"README.md","status":"malformed"}))
        for name,api in cases:
            with self.subTest(name=name):
                with self.assertRaises((g.GateError,KeyError)):
                    g.run_event(event_for(api),api)

    def test_06_ordinary_PR_race_is_fail_closed(self):
        api=FakeAPI(files=[{"filename":"README.md","status":"modified"}])
        api.race_after_first=True
        with self.assertRaises(g.GateError):
            g.run_event(event_for(api),api)

    def test_07_no_owner_scope_shortcuts(self):
        msg=g.approval_message(999,HEAD,{"CONTROL_PLANE","STATE_RELEASE"})
        comment={"user":{"login":g.OWNER_LOGIN},"author_association":"OWNER",
                 "body":msg}
        self.assertTrue(g.has_scoped_owner_approval(
            [comment],999,HEAD,{"CONTROL_PLANE","STATE_RELEASE"}))
        self.assertFalse(g.has_scoped_owner_approval(
            [comment],999,HEAD,{"CONTROL_PLANE"}))
        self.assertFalse(g.has_scoped_owner_approval(
            [comment],999,"0"*40,{"CONTROL_PLANE","STATE_RELEASE"}))

    def test_08_no_pr_script_execution(self):
        source=SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("subprocess",source)
        self.assertNotIn("os.system",source)
        self.assertNotIn("exec(",source)
        self.assertNotIn("eval(",source)
        self.assertIn("def validate_live_release",source)
        self.assertIn("def validate_ruleset_enforcement",source)

if __name__ == "__main__":
    unit_main(verbosity=2)
