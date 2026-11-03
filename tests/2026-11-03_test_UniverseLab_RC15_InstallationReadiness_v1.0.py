#!/usr/bin/env python3
"""RC15 installation readiness: current GitHub API + anti-false-positive tests.

Green means HOLD is correctly diagnosed, never that installation is authorized.
"""
import copy, json, os, sys, urllib.request, urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REPO="stefanhasselm74314-byte/UniverseLab"
BASE="51bcc8fccb092c104ac0fca5fc98a5b996dcb914"
CANDIDATE="96225f051830735ffc2d5b22581cd66a1a333846"
ID=24417933
E=ROOT/"drafts/2026-11-03_UniverseLab_RC15_InstallationReadinessEvidence_v1.0_DRAFT.json"
D=ROOT/"governance/2026-11-03_UniverseLab_RC15_InstallationReadinessRunbook_v1.0.md"
TRUSTED=".github/workflows/2026-11-03_UniverseLab_RC13_TrustedReleaseGate_v1.0.yml"

def require(expr,reason):
    if not expr:raise AssertionError(reason)

def validate(x):
    require(x["schema"]=="universelab.rc15.installation-readiness-evidence.v1","schema")
    require(x["repository"]==REPO and x["baseline_main_sha"]==BASE,"baseline")
    require(x["status"]=="DRAFT_READINESS_HOLD","draft status")
    require(x["overall_verdict"]=="NOT_READY_FOR_INSTALLATION","false readiness")
    require(x["tracked_audit_pr"]=={"number":263,"release_state":"DRAFT_UNMERGED"},"audit pr")
    require(x["tracked_gate_pr"]=={"number":264,"head_sha":CANDIDATE,"state":"DRAFT_UNMERGED"},"gate pr")
    o=x["observed_github"]
    r=o["ruleset"]
    require(r["id"]==ID and r["enforcement"]=="active","ruleset")
    require(sorted(r["rule_types"])==["deletion","non_fast_forward"],"baseline protections")
    require(r["required_pull_request"] is False and r["required_status_checks"] is False,"missing check")
    q=o["trusted_check"]
    require(q["installed_in_main"] is False and q["verified_as_required"] is False
            and q["observed_on_pr264_head"] is False,"faked trusted gate")
    q=o["candidate_ci"]
    require(q["head_sha"]==CANDIDATE and q["check_run_app_id"]==15368
            and q["check_run_app_slug"]=="github-actions"
            and q["job"]=="rc13-candidate-selftest" and q["conclusion"]=="success","candidate source")
    gates={g["id"]:g["result"] for g in x["readiness_gates"]}
    require(len(gates)==len(x["readiness_gates"])==12,"readiness coverage")
    for key in ("R15-C","R15-D","R15-E","R15-F","R15-G","R15-H","R15-I","R15-J","R15-K"):
        require(gates[key].startswith(("BLOCKED","UNVERIFIED","NOT_PERFORMED")),"promoted gate "+key)
    op=x["operational_model"]
    require(op["check_sha_association"]=="REQUIRES_CANARY_VERIFICATION","check SHA")
    require(op["comment_revocation_after_green"]=="UNMITIGATED_IN_PERSISTENT_REQUIRED_CHECK","revocation")
    require(op["required_check_app_id"]==15368 and op["required_check_strict"] is True,"app/strict")
    fw=x["nonoperational_firewalls"]
    require(fw["main_mutation"]==fw["ruleset_mutation"]=="NONE","unapproved mutation")
    require(fw["trusted_guard_installation"]=="NOT_AUTHORIZED" and
            fw["pr263_merge"]==fw["pr264_merge"]=="BLOCKED","owner decision")
    require(fw["physical_gate_effect"]==fw["physical_evidence_effect"]=="NONE"
            and fw["canonical_promotion"]=="BLOCKED","false physical evidence")
    t=(ROOT/TRUSTED).read_text()
    require("pull_request_target:" in t and
            ("ref: "+chr(36)+"{{ github.event.pull_request.base.sha }}") in t,"trusted base checkout")
    require("persist-credentials: false" in t and "contents: read" in t
            and "issues: read" in t and "pull-requests: read" in t,"privileged workflow")
    require("NOT_READY_FOR_INSTALLATION" in D.read_text(),"runbook not HOLD")
    return gates

def negatives(e):
    def t(name,fn):
        c=copy.deepcopy(e);fn(c)
        try: validate(c)
        except AssertionError: print("PASS negative:",name)
        else:raise AssertionError("Accepted unsafe readiness mutation: "+name)
    for name,fn in [
        ("fake_ready",lambda v:v.__setitem__("overall_verdict","READY")),
        ("fake_install",lambda v:v["observed_github"]["trusted_check"].__setitem__("installed_in_main",True)),
        ("fake_required_check",lambda v:v["observed_github"]["trusted_check"].__setitem__("verified_as_required",True)),
        ("fake_active_rules",lambda v:v["observed_github"]["ruleset"].__setitem__("rule_types",["pull_request"])),
        ("wrong_main",lambda v:v.__setitem__("baseline_main_sha","0"*40)),
        ("owner_installed",lambda v:v["nonoperational_firewalls"].__setitem__("trusted_guard_installation","AUTHORIZED")),
        ("comment_revoke_solved",lambda v:v["operational_model"].__setitem__("comment_revocation_after_green","SOLVED")),
        ("check_sha_fake",lambda v:v["operational_model"].__setitem__("check_sha_association","VERIFIED")),
        ("app_source_spoofed",lambda v:v["observed_github"]["candidate_ci"].__setitem__("check_run_app_id",12345)),
        ("remove_security_review_block",lambda v:v["readiness_gates"].__setitem__(10,{**v["readiness_gates"][10],"result":"PASS"})),
        ("incomplete_gate_matrix",lambda v:v["readiness_gates"].pop()),
        ("fake_physical_evidence",lambda v:v["nonoperational_firewalls"].__setitem__("physical_evidence_effect","CONFIRMED")),
    ]:t(name,fn)
    print("RC15 NEGATIVES PASS: 12/12")

def get(route,token,absent_is_ok=False):
    require(route.startswith("/") and ".." not in route and "\n" not in route,"unsafe URL")
    rq=urllib.request.Request("https://api.github.com/repos/"+REPO+route,method="GET",headers={
        "Accept":"application/vnd.github+json",
        "X-GitHub-Api-Version":"2022-11-28",
        "Authorization":"Bearer "+token,
        "User-Agent":"UniverseLab-RC15-ReadOnly-Audit"
    })
    try:
        with urllib.request.urlopen(rq,timeout=25) as resp:
            require(resp.status==200,"unexpected API status")
            data=resp.read(4_000_001)
            require(len(data)<=4_000_000,"API too large")
            return json.loads(data.decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code==404 and absent_is_ok:return None
        raise AssertionError("GitHub API access error: "+str(err)) from err
    except (urllib.error.URLError,ValueError,UnicodeError) as err:
        raise AssertionError("GitHub API failed: "+str(err)) from err

def live(e):
    require(os.environ.get("GITHUB_EVENT_NAME")=="pull_request"
            and os.environ.get("GITHUB_REPOSITORY")==REPO
            and os.environ.get("GITHUB_BASE_REF")=="main","wrong event")
    token=os.environ.get("GITHUB_TOKEN","")
    require(bool(token),"missing token")
    require(get("/branches/main",token)["commit"]["sha"]==BASE,"main moved")
    rules=get("/rulesets?includes_parents=true",token)
    require(len(rules)==1 and rules[0]["id"]==ID,"ruleset count")
    rule=get("/rulesets/"+str(ID),token)
    require(rule["enforcement"]=="active" and
            sorted(r["type"] for r in rule["rules"])==["deletion","non_fast_forward"],"ruleset drift")
    for n in (263,264):
        pr=get("/pulls/"+str(n),token)
        require(pr["draft"] is True and pr["state"]=="open"
                and pr["base"]["sha"]==BASE,"PR lifecycle drift")
    checks=get("/commits/"+CANDIDATE+"/check-runs?per_page=100",token)
    require(checks["total_count"]<=100,"check-run pagination")
    matches=[c for c in checks["check_runs"] if c["name"]=="rc13-candidate-selftest"]
    require(len(matches)==1 and matches[0]["conclusion"]=="success"
            and matches[0]["head_sha"]==CANDIDATE
            and matches[0]["app"]["id"]==15368,"candidate check attribution")
    on_main=get("/contents/"+TRUSTED+"?ref=main",token,absent_is_ok=True)
    require(on_main is None,"trusted guard installed but report still says absent")
    print("RC15 LIVE PASS: main/rulesets/PRs/check provider confirmed; guard NOT installed")
    print("RC15_INSTALLATION_READINESS=NOT_READY | NO_MAIN_OR_RULESET_CHANGES")

def main():
    e=json.loads(E.read_text())
    validate(e);negatives(e)
    if "--live" in sys.argv:live(e)
    else:print("RC15 UNIT_ONLY: live readiness unverified")

if __name__=="__main__":main()
