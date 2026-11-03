#!/usr/bin/env python3
"""RC11 fail-closed source, branch, PR and release-authority drift guard.

Checks this exact draft PR against an immutable Git baseline and the LIVE
read-only remote refs. Passing does not authorize a release or validate
mathematical/physical claims.
"""
from __future__ import annotations

import copy
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "drafts/2026-11-03_UniverseLab_RC11_ReleaseDriftGuard_v1.0_DRAFT.json"
EXPECTED_REPO = "stefanhasselm74314-byte/UniverseLab"

def read_contract():
    return json.loads((ROOT / CONTRACT).read_text(encoding="utf-8"))

def run_git(*args, timeout=25):
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, timeout=timeout,
        stderr=subprocess.PIPE
    ).strip()

def current_remote_sha(ref):
    output = run_git("ls-remote", "--exit-code", "origin", ref, timeout=30)
    lines = [line.split() for line in output.splitlines() if line.strip()]
    assert len(lines) == 1 and len(lines[0]) == 2 and lines[0][1] == ref, (
        "ambiguous remote ref", ref, lines
    )
    sha = lines[0][0]
    assert re.fullmatch(r"[0-9a-f]{40}", sha), ("invalid remote SHA", ref, sha)
    return sha

def changed_entries(base_sha):
    output = run_git("diff", "--name-status", "--no-renames", base_sha, "HEAD")
    return [line.split("\t", 1) for line in output.splitlines() if line.strip()]

def validate_contract(contract):
    assert contract["schema"] == "universelab.rc11.draft-release-drift-guard.v1"
    assert contract["status"] == "DRAFT_GUARD_ONLY_RELEASE_HOLD"
    assert contract["repository"] == EXPECTED_REPO
    assert contract["protected_main_branch"] == "main"
    assert contract["tracked_draft_pr"] == 263
    assert contract["draft_pr_head_branch"] == "audit/rc-validation-06-successor-candidates-20261103"
    assert contract["pinned_merged_main_commit"] == "51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
    assert contract["pinned_merged_main_tree"] == "65f423f04bbb2f1462f120a6b31073644cdc28cc"
    assert contract["effect"] == {
        "writes_to_main": False,
        "writes_to_registry": False,
        "solver_execution": False,
        "physical_gate_effect": "NONE",
        "physical_evidence_effect": "NONE",
        "canonical_promotion": False
    }
    expected_gates = {
        "FM-G0": "OPEN", "K1-D": "NOT_RELEASED",
        "K1-E": "NOT_ADMISSIBLE",
        "PHYSICAL_BACKGROUND": "NOT_ESTABLISHED",
        "PHYSICAL_RESPONSE_RANK": "NOT_EXECUTED",
        "AuthorizationDecision": "NOT_CREATED",
        "SingleUseGrant": "NOT_CREATED",
        "BACKEND_IMPORT": "NOT_EXECUTED",
        "SOLVER_EXECUTION": "NOT_EXECUTED"
    }
    assert contract["positive_gate_values_forbidden"] == expected_gates
    assert "OWNER_SCOPED_RATIFICATION_NOT_RECORDED_FOR_THIS_RELEASE" in contract["current_release_blockers"]
    assert "RELEASE_COMMIT_NONEXISTENT" in contract["current_release_blockers"]
    assert "PUBLIC_POINTER_CHAIN_NOT_PROMOTED" in contract["current_release_blockers"]
    assert "PROTECTED_MAIN_WORKFLOW_OR_REQUIRED_CHECK_POLICY_NOT_VERIFIED" in contract["current_release_blockers"]
    assert all(value is True for value in contract["checks"].values())
    assert len(contract["candidate_file_group"]) == 4
    assert len(contract["mandatory_predecessor_test_modules"]) == 4
    for path in contract["candidate_file_group"] + contract["mandatory_predecessor_test_modules"]:
        assert (ROOT / path).is_file(), path

def validate_context(contract, event, live_main, live_head, parents, actual_tree, changes):
    validate_contract(contract)
    base = contract["pinned_merged_main_commit"]
    assert event.get("repository", {}).get("full_name") == EXPECTED_REPO
    pr = event["pull_request"]
    assert pr["number"] == contract["tracked_draft_pr"]
    assert pr["state"] == "open"
    assert pr["draft"] is True, "Ready-for-review is NOT owner release authorization"
    assert pr.get("merged") is not True
    assert pr["base"]["ref"] == contract["protected_main_branch"]
    assert pr["base"]["repo"]["full_name"] == EXPECTED_REPO
    assert pr["base"]["sha"] == base, "PR event base SHA drift"
    assert live_main == base, "LIVE main SHA drift"
    assert pr["head"]["repo"]["full_name"] == EXPECTED_REPO
    assert pr["head"]["ref"] == contract["draft_pr_head_branch"]
    assert live_head == pr["head"]["sha"], "Draft head changed while guard ran"
    assert len(parents) == 2 and parents[0] == live_main and parents[1] == live_head, (
        "PR checkout must be the exact two-parent synthetic merge"
    )
    assert actual_tree == contract["pinned_merged_main_tree"], "Pinned Git object tree changed"
    allowed = [re.compile(pattern) for pattern in contract["allowed_additions"].values()]
    assert len(changes) >= 10, "PR diff unexpectedly empty / incomplete"
    for status, path in changes:
        assert status == "A", ("Existing or renamed file edited", status, path)
        assert any(pattern.fullmatch(path) for pattern in allowed), (
            "Protected or out-of-scope path modified", path
        )
    for path in contract["candidate_file_group"]:
        assert ["A",path] in changes, ("Required draft candidate missing from PR diff", path)

def fixture(c):
    base=c["pinned_merged_main_commit"]
    head="1"*40
    event={"repository":{"full_name":EXPECTED_REPO},"pull_request":{
        "number":263,"state":"open","draft":True,"merged":False,
        "base":{"ref":"main","sha":base,"repo":{"full_name":EXPECTED_REPO}},
        "head":{"ref":c["draft_pr_head_branch"],"sha":head,
                "repo":{"full_name":EXPECTED_REPO}}
    }}
    changes=[["A",p] for p in c["candidate_file_group"]]
    changes+= [["A","drafts/2026-11-03_UniverseLab_RC11_ReleaseDriftGuard_v1.0_DRAFT.json"]]
    changes+= [["A",f"tests/2026-11-03_test_UniverseLab_RC{n}_Guard_v1.0.py"] for n in range(8,14)]
    return event,base,head,[base,head],c["pinned_merged_main_tree"],changes

def unit_tests(c):
    event,main,head,parents,tree,changes=fixture(c)
    validate_context(c,event,main,head,parents,tree,changes)
    tests=[
      ("live_main_changed",lambda c,e,m,h,p,t,f:(c,e,"2"*40,h,p,t,f)),
      ("event_main_changed",lambda c,e,m,h,p,t,f:(c,{**e,"pull_request":{**e["pull_request"],"base":{**e["pull_request"]["base"],"sha":"2"*40}}},m,h,p,t,f)),
      ("pr_head_changed",lambda c,e,m,h,p,t,f:(c,e,m,"2"*40,p,t,f)),
      ("synthetic_second_parent_mismatch",lambda c,e,m,h,p,t,f:(c,e,m,h,[m,"2"*40],t,f)),
      ("synthetic_base_parent_mismatch",lambda c,e,m,h,p,t,f:(c,e,m,h,["2"*40,h],t,f)),
      ("draft_changed_to_ready",lambda c,e,m,h,p,t,f:(c,{**e,"pull_request":{**e["pull_request"],"draft":False}},m,h,p,t,f)),
      ("changed_canonical_manifest",lambda c,e,m,h,p,t,f:(c,e,m,h,p,t,f+[["M","project-manifest.json"]])),
      ("changed_registry_snapshot",lambda c,e,m,h,p,t,f:(c,e,m,h,p,t,f+[["A","registry/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4.json"]])),
      ("mutated_existing_draft",lambda c,e,m,h,p,t,f:(c,e,m,h,p,t,f+[["M",c["candidate_file_group"][0]]])),
      ("git_tree_mismatch",lambda c,e,m,h,p,t,f:(c,e,m,h,p,"2"*40,f)),
      ("owner_safeguard_removed",lambda c,e,m,h,p,t,f:({**c,"current_release_blockers":[]},e,m,h,p,t,f)),
      ("fake_physical_evidence",lambda c,e,m,h,p,t,f:({**c,"effect":{**c["effect"],"physical_evidence_effect":"CONFIRMED"}},e,m,h,p,t,f)),
    ]
    for label,mutate in tests:
        args=copy.deepcopy((c,event,main,head,parents,tree,changes))
        corrupted=mutate(*args)
        try:
            validate_context(*corrupted)
        except AssertionError:
            print("PASS negative:",label)
        else:
            raise AssertionError("Fail-closed RC11 guard accepted mutation: " + label)
    print("RC11 UNIT PASS: 12/12 drift and authority negative controls")

def ci_main(c):
    assert os.environ.get("GITHUB_EVENT_NAME") == "pull_request", (
        "No PR event; release watch does not infer context"
    )
    assert os.environ.get("GITHUB_BASE_REF") == "main"
    assert os.environ.get("GITHUB_HEAD_REF") == c["draft_pr_head_branch"]
    assert os.environ.get("GITHUB_REF") == "refs/pull/263/merge"
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    assert event_path and Path(event_path).is_file()
    event = json.loads(Path(event_path).read_text(encoding="utf-8"))
    main=current_remote_sha("refs/heads/main")
    head=current_remote_sha("refs/heads/"+c["draft_pr_head_branch"])
    parents=run_git("show","-s","--format=%P","HEAD").split()
    tree=run_git("rev-parse",c["pinned_merged_main_commit"]+"^{tree}")
    changes=changed_entries(c["pinned_merged_main_commit"])
    validate_context(c,event,main,head,parents,tree,changes)
    assert not run_git("diff","--name-only","--"), "Worktree has tracked modifications"
    for script in c["mandatory_predecessor_test_modules"]:
        out=subprocess.run([sys.executable,script],cwd=ROOT,check=True,
                            capture_output=True,text=True,timeout=120)
        assert "PASS" in out.stdout, (script, "PASS marker missing")
        print("PASS prior guard:",script)
    # Repeat remote source freshness after potentially lengthy predecessor QA.
    assert current_remote_sha("refs/heads/main")==main, "main changed while validating"
    assert current_remote_sha("refs/heads/"+c["draft_pr_head_branch"])==head, "PR head changed while validating"
    print(f"RC11 CI PASS: main={main[:12]} head={head[:12]}, {len(changes)} scoped additions")
    print("PASS: 39 source assertions, RC08/RC09/RC10 predecessors, and 12 negative controls")
    print("HOLD: draft only, no canon promotion, no delegated release authorization")

def main():
    c=read_contract()
    validate_contract(c)
    unit_tests(c)
    if "--ci" in sys.argv:
        ci_main(c)
    else:
        print("UNIT ONLY: live GitHub refs NOT checked; add --ci inside a PR workflow")

if __name__=="__main__":
    main()
