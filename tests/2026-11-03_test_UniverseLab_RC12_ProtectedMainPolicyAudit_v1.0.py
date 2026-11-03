#!/usr/bin/env python3
"""RC12: live READ-ONLY GitHub ruleset audit.

Passing means observed *missing* mandatory protections were reported accurately.
It is NEVER release approval. GitHub authorization/owner ratification is separate.
"""
from __future__ import annotations
import copy
import json
import os
import re
import sys
from datetime import datetime
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = "drafts/2026-11-03_UniverseLab_RC12_ProtectedMainPolicyEvidence_v1.0_DRAFT.json"
REPO = "stefanhasselm74314-byte/UniverseLab"
BASE = "51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
RULESET_ID = 24417933
API = "https://api.github.com/repos/" + REPO

def load():
    return json.loads((ROOT / REPORT).read_text(encoding="utf-8"))

def get_json(path):
    assert path in ("", "/branches/main", "/rulesets?includes_parents=true",
                    "/rulesets/" + str(RULESET_ID)), path
    headers = {"Accept":"application/vnd.github+json",
               "X-GitHub-Api-Version":"2022-11-28",
               "User-Agent":"UniverseLab-RC12-ReadOnly-Audit"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request(API + path, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            assert response.status == 200, ("GitHub API HTTP", response.status)
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError) as exc:
        raise AssertionError(f"Live policy unreadable; hold release: {path}: {exc}") from exc

def guard(observation, report):
    repo, branch, listed, ruleset = observation
    assert report["schema"] == "universelab.rc12.protected-main-policy-evidence.v1"
    assert report["status"] == "DRAFT_READ_ONLY_POLICY_AUDIT_RELEASE_HOLD"
    assert report["repository"] == REPO
    assert report["pinned_source_main_commit"] == BASE
    assert report["owner_release_ratification"] == "NOT_REQUESTED"
    assert report["canonical_promotion"] == "BLOCKED"
    assert report["physical_gate_effect"] == report["physical_evidence_effect"] == "NONE"
    assert repo["full_name"] == REPO and repo["default_branch"] == "main"
    assert repo["private"] is False
    assert branch["name"] == "main"
    assert branch["commit"]["sha"] == BASE, "LIVE main advanced: baseline re-review required"
    assert report["observed_main"]["sha"] == BASE
    assert branch["protected"] is report["observed_main"]["protected"] is True
    summ = branch["protection"]
    stored = report["observed_main"]["legacy_protection_summary"]
    assert summ["enabled"] is stored["enabled"] is False
    assert summ["required_status_checks"] == stored["required_status_checks"]
    assert summ["required_status_checks"]["enforcement_level"] == "off"
    assert summ["required_status_checks"]["checks"] == []
    assert summ["required_status_checks"]["contexts"] == []

    assert isinstance(listed, list)
    assert len(listed) == report["ruleset_collection"]["count"] == 1
    assert listed[0]["id"] == report["ruleset_collection"]["items"][0]["id"] == RULESET_ID
    assert listed[0]["enforcement"] == "active"
    assert ruleset["id"] == report["active_ruleset"]["id"] == RULESET_ID
    assert ruleset["name"] == report["active_ruleset"]["name"]
    assert ruleset["target"] == report["active_ruleset"]["target"] == "branch"
    assert ruleset["source_type"] == report["active_ruleset"]["source_type"] == "Repository"
    assert ruleset["source"] == report["active_ruleset"]["source"] == REPO
    assert ruleset["enforcement"] == report["active_ruleset"]["enforcement"] == "active"
    assert ruleset["conditions"] == report["active_ruleset"]["conditions"]
    assert ruleset["conditions"]["ref_name"]["include"] == ["refs/heads/main"]
    assert ruleset["conditions"]["ref_name"]["exclude"] == []
    types = sorted(item["type"] for item in ruleset["rules"])
    assert types == sorted(report["active_ruleset"]["rule_types"]) == ["deletion","non_fast_forward"]
    assert ruleset.get("bypass_actors", []) == report["active_ruleset"]["bypass_actors"] == []
    assert ruleset.get("current_user_can_bypass") == report["active_ruleset"]["current_user_can_bypass"] == "never"
    # GitHub can serialize an identical instant in UTC (seconds precision) or local-offset milliseconds.
    instant = lambda x: datetime.fromisoformat(x.replace("Z", "+00:00"))
    assert abs((instant(ruleset["updated_at"]) - instant(report["active_ruleset"]["last_updated_at"])).total_seconds()) < 1.0, "Ruleset timestamp materially changed"
    assessment = report["required_enforcement_assessment"]
    assert assessment["verdict"] == "BLOCKED_NO_VERIFIED_MANDATORY_PR_OR_STATUS_CHECK_GATES"
    for field in ("required_pull_request_rule_present_in_readable_active_ruleset",
                  "required_status_checks_rule_present_in_readable_active_ruleset",
                  "required_approving_reviews_rule_present_in_readable_active_ruleset",
                  "legacy_summary_required_checks_active",
                  "immutable_release_check_enforcement_verified"):
        assert assessment[field] is False, field
    assert assessment["deletion_protected_by_ruleset"] is True
    assert assessment["non_fast_forward_protected_by_ruleset"] is True
    assert report["legacy_branch_protection_details"]["result"] == (
        "HTTP_403_RESOURCE_NOT_ACCESSIBLE_BY_INTEGRATION"
    )
    assert len(report["candidate_existing_always_on_checks"]) == 2
    for item in report["candidate_existing_always_on_checks"]:
        assert item["pr_trigger"] == "UNFILTERED" and item["is_required_now"] is False
        content = (ROOT / item["workflow"]).read_text(encoding="utf-8")
        assert re.search(r"^on:\s*\n\s{2}pull_request:\s*\n\s{2}push:", content, re.M)
        assert re.search(r"^\s{2}" + re.escape(item["job_id"]) + r":\s*$", content, re.M)
    conditional = report["conditional_canonical_check"]
    assert conditional["pr_trigger"] == "PATH_FILTERED"
    content = (ROOT / conditional["workflow"]).read_text(encoding="utf-8")
    assert re.search(r"^\s{2}pull_request:\s*\n\s{4}paths:", content, re.M)
    assert re.search(r"^\s{2}" + re.escape(conditional["job_id"]) + r":\s*$", content, re.M)
    assert report["actions_taken"] == ["READ_ONLY_RULESET_AUDIT", "DRAFT_POLICY_EVIDENCE_ONLY"]
    return types

def sample(report):
    return (
        {"full_name":REPO, "default_branch":"main", "private":False},
        {"name":"main", "commit":{"sha":BASE}, "protected":True,
         "protection":copy.deepcopy(report["observed_main"]["legacy_protection_summary"])},
        [dict(report["ruleset_collection"]["items"][0])],
        {
            **copy.deepcopy(report["active_ruleset"]),
            "conditions":copy.deepcopy(report["active_ruleset"]["conditions"]),
            "rules":[{"type":"deletion"},{"type":"non_fast_forward"}],
            "updated_at":report["active_ruleset"]["last_updated_at"]
        }
    )

def negative_tests(report):
    source = sample(report)
    guard(source, report)
    def mutation(name, mutate):
        observed, documented = copy.deepcopy((source, report))
        observed, documented = mutate(observed, documented)
        try:
            guard(observed, documented)
        except AssertionError:
            print("PASS negative:", name)
        else:
            raise AssertionError("False positive when tampering policy: "+name)
    negative = [
        ("live_main_moved",lambda o,r:((o[0],{**o[1],"commit":{"sha":"0"*40}},o[2],o[3]),r)),
        ("private_repo",lambda o,r:(({**o[0],"private":True},o[1],o[2],o[3]),r)),
        ("ruleset_disabled",lambda o,r:((o[0],o[1],o[2],{**o[3],"enforcement":"disabled"}),r)),
        ("ruleset_changed_scope",lambda o,r:((o[0],o[1],o[2],{**o[3],"conditions":{"ref_name":{"include":["refs/heads/test"],"exclude":[]}}}),r)),
        ("ruleset_removes_force_push_block",lambda o,r:((o[0],o[1],o[2],{**o[3],"rules":[{"type":"deletion"}]}),r)),
        ("mandatory_checks_added_without_review",lambda o,r:((o[0],o[1],o[2],{**o[3],"rules":o[3]["rules"]+[{"type":"required_status_checks"}]}),r)),
        ("unreviewed_ruleset_added",lambda o,r:((o[0],o[1],o[2]+[{"id":42}],o[3]),r)),
        ("bypass_added",lambda o,r:((o[0],o[1],o[2],{**o[3],"bypass_actors":[{"actor_id":1}]}),r)),
        ("required_check_summary_changed",lambda o,r:((o[0],{**o[1],"protection":{**o[1]["protection"],"enabled":True}},o[2],o[3]),r)),
        ("faked_policy_readiness",lambda o,r:(o,{**r,"required_enforcement_assessment":{**r["required_enforcement_assessment"],"immutable_release_check_enforcement_verified":True}})),
        ("faked_owner_ratification",lambda o,r:(o,{**r,"owner_release_ratification":"RECORDED"})),
        ("faked_scientific_evidence",lambda o,r:(o,{**r,"physical_evidence_effect":"CONFIRMED"})),
    ]
    for name, mutate in negative:
        mutation(name,mutate)
    print("RC12 UNIT PASS: 12/12 policy and interpretation negative controls")

def main():
    report = load()
    negative_tests(report)
    if "--live" not in sys.argv:
        print("UNIT ONLY — live rulesets not rechecked")
        return
    assert os.environ.get("GITHUB_EVENT_NAME")=="pull_request"
    assert os.environ.get("GITHUB_BASE_REF")=="main"
    assert os.environ.get("GITHUB_HEAD_REF")=="audit/rc-validation-06-successor-candidates-20261103"
    assert os.environ.get("GITHUB_REPOSITORY")==REPO
    observation=tuple(get_json(path) for path in (
        "", "/branches/main", "/rulesets?includes_parents=true",
        "/rulesets/" + str(RULESET_ID)
    ))
    rules=guard(observation,report)
    print("RC12 LIVE PASS: active main ruleset matches documented evidence:",rules)
    print("RC12 LIVE PASS: always-on naming and governance workflows confirmed; path-filtered check not generally required")
    print("RELEASE_STATUS=BLOCKED; missing mandatory PR + required status-check enforcement")
    print("LEGACY_BRANCH_PROTECTION_DETAIL=403_IN_CONNECTOR; NOT FULLY AUDITABLE")
    print("PHYSICAL_GATE_EFFECT=NONE; PHYSICAL_EVIDENCE_EFFECT=NONE")

if __name__=="__main__":
    main()
