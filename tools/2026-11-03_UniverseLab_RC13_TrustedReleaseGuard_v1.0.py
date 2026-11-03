#!/usr/bin/env python3
"""UniverseLab RC13 — trusted-base PR gate candidate, read-only.

Intended ONLY for a future workflow on the protected base branch triggered by
pull_request_target.  Never checkout, import or execute code from PR head.
All PR metadata, comments, head files and tree contents are untrusted input.
Neither this script nor a green CI run attests physics or substitutes for
an explicit owner ratification.  This candidate is not active on main.
"""
from __future__ import annotations

import base64
import datetime as dt
import json
import os
from pathlib import PurePosixPath, Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO = "stefanhasselm74314-byte/UniverseLab"
OWNER_LOGIN = "stefanhasselm74314-byte"
API_ROOT = "https://api.github.com/repos/" + REPO
MAX_PR_FILES = 1000
MAX_COMMENTS = 500
MAX_TREE_ITEMS = 15000
MAX_LIVE_WEB_FILES = 250
MAX_BLOB_BYTES = 1_000_000
MAIN = "main"
TRUSTED_JOB = "trusted-release-gate"
GITHUB_ACTIONS_APP_ID = 15368  # expected required-check source, not "any source"
TRUSTED_WORKFLOW = ".github/workflows/2026-11-03_UniverseLab_RC13_TrustedReleaseGate_v1.0.yml"
TRUSTED_GUARD = "tools/2026-11-03_UniverseLab_RC13_TrustedReleaseGuard_v1.0.py"
RELEASE_REQUIRED = frozenset({
    "project-manifest.json",
    "registry/session-checkpoint-latest.json",
    "research-status.html",
    "research-status-en.html",
    "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js",
})
SNAPSHOT_PATTERNS = {
    "state": re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_CurrentMainCanonicalState_v\d+\.\d+\.json\Z"),
    "checkpoint": re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_SessionCheckpoint_v\d+\.\d+\.json\Z"),
    "site": re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_SiteState_v\d+\.\d+\.json\Z"),
}
BLOCKED_TOKENS = ("__RELEASE_TIMESTAMP_NOT_ASSIGNED__",
                  "__RELEASE_DATE_NOT_ASSIGNED__", "DRAFT_NOT_CANONICAL")
GATE_EXPECTED = {"K1-D": "NOT_RELEASED", "K1-E": "NOT_ADMISSIBLE",
                 "FM-G0": "OPEN"}

class GateError(RuntimeError):
    pass

def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)

def safe_path(path: str) -> str:
    require(isinstance(path, str) and 0 < len(path) < 500, "Invalid path type or length")
    parsed = PurePosixPath(path)
    require(not parsed.is_absolute() and str(parsed) == path
            and ".." not in parsed.parts and "\\" not in path,
            "Unsafe path")
    return path

def classify(path: str) -> set[str]:
    """Conservative default: no repository path can evade sensitive review.

    State release has an exact eight-file contract. Other web publications
    are PUBLIC_SURFACE; all remaining paths are CONTROL_PLANE, including
    unrecognized registry/source or binary artifacts. This may deliberately
    require more owner acknowledgments than ordinary development would.
    """
    path = safe_path(path)
    if (path in RELEASE_REQUIRED or
        any(p.fullmatch(path) for p in SNAPSHOT_PATTERNS.values())):
        return {"STATE_RELEASE"}
    if path.startswith("assets/") and "GlobalShell" in path:
        return {"STATE_RELEASE"}
    if path.startswith("research-status") and path.endswith(".html"):
        return {"STATE_RELEASE"}
    if (path.endswith((".html", ".htm", ".js", ".mjs", ".css",
                       ".md", ".mdx", ".svg", ".webp", ".png",
                       ".jpg", ".jpeg")) or
        path.startswith(("assets/", "public/", "site/", "docs/"))):
        return {"PUBLIC_SURFACE"}
    return {"CONTROL_PLANE"}

def scopes_for_files(files: list[dict]) -> set[str]:
    require(len(files) > 0 and len(files) <= MAX_PR_FILES, "Unexpected PR file count")
    seen = set()
    scopes: set[str] = set()
    for item in files:
        name = safe_path(item.get("filename"))
        require(name not in seen, "Duplicate path in GitHub PR files")
        seen.add(name)
        status = item.get("status")
        require(status in {"added", "modified", "removed", "renamed", "copied", "changed"},
                "Unknown PR file status")
        if status == "renamed":
            scopes.update(classify(safe_path(item.get("previous_filename"))))
        scopes.update(classify(name))
    return scopes

def approval_message(number: int, head_sha: str, scopes: set[str]) -> str:
    require(isinstance(number, int) and number > 0, "Invalid PR number")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", head_sha)), "Invalid SHA")
    require(scopes and scopes <= {"STATE_RELEASE", "CONTROL_PLANE", "PUBLIC_SURFACE"},
            "Invalid scope")
    return ("UniverseLab RC13 RELEASE-AUTHORIZATION\n"
            f"PR: #{number}\nHEAD: {head_sha}\nSCOPE: {','.join(sorted(scopes))}\n"
            "DECISION: APPROVE THIS EXACT HEAD")

def has_scoped_owner_approval(comments: list[dict], number: int,
                              head_sha: str, scopes: set[str]) -> bool:
    target = approval_message(number, head_sha, scopes)
    for c in comments:
        if (c.get("user", {}).get("login") == OWNER_LOGIN
            and c.get("author_association") == "OWNER"
            and c.get("body", "").strip() == target.strip()):
            return True
    return False

class GitHubReadOnly:
    def __init__(self, token: str):
        require(token and len(token) >= 10, "Read-only GitHub token missing")
        self.token = token

    def get(self, api_path: str):
        require(api_path.startswith("/") and "://" not in api_path
                and ".." not in api_path and "\n" not in api_path,
                "Invalid API path")
        req = urllib.request.Request(
            API_ROOT + api_path,
            headers={"Accept": "application/vnd.github+json",
                     "X-GitHub-Api-Version": "2022-11-28",
                     "Authorization": "Bearer " + self.token,
                     "User-Agent": "UniverseLab-RC13-TrustedReleaseGuard/1.0"},
            method="GET")
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                require(r.status == 200, "GitHub API returned non-200")
                data = r.read(8_000_000 + 1)
                require(len(data) <= 8_000_000, "GitHub API response too large")
                return json.loads(data.decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                UnicodeError, ValueError) as exc:
            raise GateError("Unable to verify live GitHub API data: " + str(exc)) from exc

    def paged(self, prefix: str, limit: int) -> list[dict]:
        result: list[dict] = []
        for page in range(1, limit // 100 + 2):
            obj = self.get(prefix + ("&" if "?" in prefix else "?")
                           + "per_page=100&page=" + str(page))
            require(isinstance(obj, list), "API list endpoint returned non-list")
            result.extend(obj)
            require(len(result) <= limit, "API pagination cap reached")
            if len(obj) < 100:
                return result
        raise GateError("Pagination incomplete")

    def contents(self, path: str, sha: str) -> bytes:
        path = safe_path(path)
        require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "Bad head commit")
        url_path = urllib.parse.quote(path, safe="/")
        d = self.get("/contents/" + url_path + "?ref=" + sha)
        require(isinstance(d, dict) and d.get("type") == "file"
                and d.get("encoding") == "base64", "Unexpected content representation")
        raw = base64.b64decode(d.get("content", ""), validate=False)
        require(len(raw) <= MAX_BLOB_BYTES, "File exceeds bounded review limit")
        return raw

    def tree(self, commit_sha: str) -> list[dict]:
        commit = self.get("/git/commits/" + commit_sha)
        require(commit.get("sha") == commit_sha, "Wrong Git commit object")
        tree_sha = commit.get("tree", {}).get("sha")
        require(bool(re.fullmatch(r"[0-9a-f]{40}", str(tree_sha))), "Invalid Git tree")
        tree = self.get("/git/trees/" + tree_sha + "?recursive=1")
        require(tree.get("truncated") is False, "Recursive Git tree truncated")
        items = tree.get("tree", [])
        require(isinstance(items, list) and len(items) <= MAX_TREE_ITEMS,
                "Git tree oversized or invalid")
        return items

    def blob(self, sha: str) -> bytes:
        require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "Invalid blob SHA")
        d = self.get("/git/blobs/" + sha)
        require(d.get("encoding") == "base64", "Non-base64 Git blob")
        content = base64.b64decode(d.get("content", ""), validate=False)
        require(len(content) <= MAX_BLOB_BYTES, "Web blob too large")
        return content

def decode_json(data: bytes, label: str) -> dict:
    try:
        result = json.loads(data.decode("utf-8"))
    except (UnicodeError, ValueError) as exc:
        raise GateError("Invalid JSON: " + label) from exc
    require(isinstance(result, dict), "Expected JSON object: " + label)
    return result

def allow_only_declared_changes(before: dict, after: dict,
                                allowed: set[str], name: str) -> None:
    """Fail closed on any undeclared top-level ledger change or key removal."""
    require(set(before) - set(after) == set(), name + " removed a baseline field")
    for key in set(before) | set(after):
        if key not in allowed:
            require(key in before and key in after and before[key] == after[key],
                    name + " changed non-pointer field without independent review: " + key)

def require_timestamp(value: str, expected_date: str) -> None:
    require(isinstance(value, str) and
            re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?[+-]\d\d:\d\d", value),
            "Timestamp must include explicit timezone offset")
    try:
        timestamp = dt.datetime.fromisoformat(value)
        date = dt.date.fromisoformat(expected_date)
    except ValueError as exc:
        raise GateError("Invalid calendar timestamp or date") from exc
    require(timestamp.utcoffset() is not None and timestamp.date() == date,
            "Snapshot timestamp date mismatch")
    require(dt.datetime.now(dt.timezone.utc) >= timestamp.astimezone(dt.timezone.utc),
            "Snapshot timestamp is in the future")

def validate_live_release(files: list[dict], base_sha: str, head_sha: str,
                          api: GitHubReadOnly) -> str:
    """Validate *only* an eight-file atomic release, without executing PR code."""
    changed = {x["filename"]: x["status"] for x in files}
    require(all(x.get("status") not in ("removed","renamed","copied")
                for x in files), "Release bundle cannot rename/delete paths")
    required = set(RELEASE_REQUIRED)
    require(required <= set(changed), "Incomplete canonical/website release bundle")
    for path in required:
        require(changed[path] == "modified", "Active release consumer must be modified")
    new_snapshots = {}
    for key, pattern in SNAPSHOT_PATTERNS.items():
        matches = [name for name in changed if pattern.fullmatch(name)]
        require(len(matches) == 1 and changed[matches[0]] == "added",
                "Exactly one new dated " + key + " required")
        new_snapshots[key] = matches[0]
    require(set(changed) == set(required) | set(new_snapshots.values()),
            "Release PR must contain exactly eight declared files; no mixed changes")

    base = decode_json(api.contents("project-manifest.json", base_sha),
                       "baseline manifest")
    base_checkpoint = decode_json(api.contents(base["session_checkpoint"], base_sha),
                                   "baseline checkpoint")
    base_site = decode_json(api.contents(base["site_state"], base_sha),
                             "baseline site")
    base_state = decode_json(api.contents(base["canonical_state"], base_sha),
                              "baseline state")
    manifest_bytes = api.contents("project-manifest.json", head_sha)
    manifest = decode_json(manifest_bytes, "release manifest")
    state_p, cp_p, site_p = (new_snapshots[x] for x in ("state","checkpoint","site"))
    state = decode_json(api.contents(state_p, head_sha), "new state")
    cp_bytes = api.contents(cp_p, head_sha)
    cp = decode_json(cp_bytes, "new checkpoint")
    site = decode_json(api.contents(site_p, head_sha), "new site")
    alias_bytes = api.contents("registry/session-checkpoint-latest.json", head_sha)
    require(alias_bytes == cp_bytes, "Checkpoint alias not byte-identical")

    require(manifest.get("canonical_state") == state_p
            and manifest.get("session_checkpoint") == cp_p
            and manifest.get("site_state") == site_p, "Manifest pointer mismatch")
    require(cp.get("canonical_snapshot") == cp_p
            and cp.get("canonical_state") == site.get("canonical_state") == state_p
            and cp.get("site_state") == site_p, "Checkpoint/site pointers mismatch")
    require(site.get("status_sources", {}).get("canonical_state") == state_p
            and site.get("status_sources", {}).get("session_checkpoint") == cp_p,
            "SiteState references inconsistent")
    require(state.get("status_sources", {}).get("site_state") == site_p
            and state.get("status_sources", {}).get("session_checkpoint") == cp_p,
            "CurrentState references inconsistent")
    for name in ("canonical_state", "site_state", "session_checkpoint"):
        require(manifest.get("current_status_sources", {}).get(name)
                == manifest.get(name), "Manifest secondary pointer mismatch")
    for alias_key, canonical_key in (
        ("current_main_canonical_state","canonical_state"),
        ("site_state","site_state"),
        ("session_checkpoint","session_checkpoint")):
        require(manifest.get("central_registries",{}).get(alias_key)
                == manifest.get(canonical_key), "Manifest registry pointer mismatch")

    base_tree = api.get("/git/commits/" + base_sha).get("tree",{}).get("sha")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", str(base_tree))), "Base tree unavailable")
    require(manifest.get("basis_main_commit") == state.get("basis_main_commit")
            == site.get("basis_main_commit") == cp.get("basis_commit") == base_sha,
            "Unverified predecessor main commit")
    require(manifest.get("basis_main_tree") == state.get("basis_main_tree")
            == site.get("basis_main_tree") == cp.get("basis_tree") == base_tree,
            "Unverified predecessor tree")

    date = manifest.get("release_date")
    require(isinstance(date,str) and bool(re.fullmatch(r"\d{4}-\d\d-\d\d",date)),
            "Manifest release date invalid")
    require(state.get("snapshot_date") == site.get("snapshot_date") == date,
            "Dates disagree")
    for t in (state.get("snapshot_timestamp"), site.get("snapshot_timestamp"),
              cp.get("timestamp")):
        require_timestamp(t, date)

    for obj in (state, cp, site, manifest):
        require(obj.get("physical_gate_effect") == "NONE"
                and obj.get("physical_evidence_effect") == "NONE",
                "Physical evidence/gates may not be promoted")
        serialized = json.dumps(obj, ensure_ascii=False)
        require(not any(tok in serialized for tok in BLOCKED_TOKENS),
                "DRAFT marker or unresolved release timestamp in release output")
    allow_only_declared_changes(base_state, state, {
        "version", "snapshot_date", "snapshot_timestamp", "basis_main_commit",
        "basis_main_tree", "basis_semantics", "supersedes", "status_sources",
        "active_analysis_block", "reconciliation_addendum"
    }, "CurrentMainCanonicalState")
    allow_only_declared_changes(base_checkpoint, cp, {
        "checkpoint_id", "timestamp", "basis_commit", "basis_tree",
        "basis_semantics", "canonical_snapshot", "supersedes",
        "canonical_state", "site_state", "entry_points", "active_block",
        "confirmed_defects", "reconciliation_addendum"
    }, "SessionCheckpoint")
    allow_only_declared_changes(base_site, site, {
        "version", "snapshot_date", "snapshot_timestamp", "basis_main_commit",
        "basis_main_tree", "basis_semantics", "canonical_state", "supersedes",
        "status_sources", "reconciliation_addendum"
    }, "SiteState")
    allow_only_declared_changes(base, manifest, {
        "release", "release_date", "basis_main_commit", "basis_main_tree",
        "basis_semantics", "canonical_base", "canonical_state",
        "site_state", "session_checkpoint", "current_status_sources",
        "central_registries", "platform_governance", "supersedes_release",
        "reconciliation_addendum"
    }, "ProjectManifest")
    require(state.get("physical_governance") == base_state.get("physical_governance"),
            "State physical governance changed")
    # RC14: a governance-only pointer repair cannot manufacture a result by
    # changing another status field while leaving K1-D/K1-E untouched.
    for key in ("scientific_open_state", "merged_analysis_blocks",
                "active_program", "public_claim_governance",
                "public_numerical_platform", "open_noncanonical_work"):
        require(key in base_state and state.get(key) == base_state[key],
                "Scientific state ledger changed without a separate review: " + key)
    active_old = dict(base_state.get("active_analysis_block",{}))
    active_new = dict(state.get("active_analysis_block",{}))
    active_old.pop("governance_provenance_gap", None)
    active_new.pop("governance_provenance_gap", None)
    require(active_new == active_old,
            "Scientific missing-link/claim status changed in active analysis block")
    for key in ("public_claim_audit", "current_program", "architecture",
                "public_numerical_platform", "c_phys_operator_entry"):
        require(key in base and manifest.get(key) == base[key],
                "Manifest science or public-claim ledger changed: " + key)
    for key in ("analysis_state", "pages", "modules"):
        require(key in base_site and site.get(key) == base_site[key],
                "SiteState scientific or publication ledger changed: " + key)
    for key in ("verified_results", "open_blockers", "completed_blocks",
                "active_program", "active_assumptions", "forbidden_inferences",
                "physical_governance"):
        require(key in base_checkpoint and cp.get(key) == base_checkpoint[key],
                "Checkpoint evidence or blocker ledger changed: " + key)
    require(base_state.get("active_analysis_block",{}).get(
                "blocking_scientific_or_empirical_gaps") == 10,
            "Unknown baseline scientific missing-link count")
    require(state.get("active_analysis_block",{}).get(
                "blocking_scientific_or_empirical_gaps") == 10,
            "Ten scientific missing links were unjustifiably closed")
    require(site.get("analysis_state",{}).get("physical_claim_promotions") == 0,
            "Physical claims were promoted through a non-gate field")
    # Checkpoint is a historical/provenance document: the only permitted
    # exceptions are the explicitly reviewed G11 governance status transitions
    # and replacements of the state/site entry-point paths.
    old_block = dict(base_checkpoint.get("active_block",{}))
    new_block = dict(cp.get("active_block",{}))
    require(bool(old_block), "Missing predecessor active-block ledger")
    before_action = old_block.pop("state_freshness_action", None)
    after_action = new_block.pop("state_freshness_action", None)
    require(new_block == old_block, "Checkpoint scientific active-block fields changed")
    require(before_action == "APPEND_ONLY_SUCCESSOR_CHAIN_AND_PUBLIC_POINTER_REPAIR",
            "Unexpected predecessor G11 repair action")
    require(after_action in (
        "PR210_MERGED_SEPTEMBER_CHAIN_NEW_RC08_CANONICAL_RECONCILIATION_PENDING",
        "PR210_MERGED_SEPTEMBER_CHAIN_POINTER_RECONCILIATION_COMPLETE_NO_PHYSICAL_EFFECT"
    ), "Unreviewed G11 repair-status promotion")
    old_defects = base_checkpoint.get("confirmed_defects")
    new_defects = cp.get("confirmed_defects")
    require(isinstance(old_defects,list) and len(old_defects) == 1
            and isinstance(new_defects,list) and len(new_defects) == 1,
            "Checkpoint must preserve exactly the reviewed G11 defect")
    old_defect, new_defect = dict(old_defects[0]), dict(new_defects[0])
    require(old_defect.get("defect_id") == new_defect.get("defect_id") == "UL-BVC-G11",
            "Checkpoint G11 defect identity changed")
    old_defect.pop("repair_status", None)
    new_status = new_defect.pop("repair_status", None)
    require(old_defect == new_defect
            and new_status in (
              "MERGED_PR210_HISTORICAL_SCOPE_ONLY_RC08_NEW_SNAPSHOT_PENDING",
              "MERGED_PR210_HISTORICAL_SCOPE_CURRENT_POINTERS_RECONCILED_NO_PHYSICAL_EFFECT"
            ), "Unreviewed checkpoint defect/evidence claim")
    require(isinstance(base_checkpoint.get("entry_points"),list)
            and isinstance(cp.get("entry_points"),list),
            "Checkpoint entry-point list missing")
    entry_map = {
        base["canonical_state"]: state_p,
        base["site_state"]: site_p,
        base["session_checkpoint"]: cp_p,
    }
    require(cp["entry_points"] == [
        entry_map.get(p,p) for p in base_checkpoint["entry_points"]
    ], "Checkpoint entry points changed beyond verified pointer migration")

    require(manifest.get("gates") == base.get("gates"),
            "Full manifest gate ledger changed during governance-only release")
    require(cp.get("gate_state") == base_checkpoint.get("gate_state"),
            "Full checkpoint gate ledger changed during governance-only release")
    require(site.get("governance") == base_site.get("governance"),
            "SiteState governance ledger changed during governance-only release")
    for k, value in GATE_EXPECTED.items():
        require(manifest.get("gates", {}).get(k) == base.get("gates", {}).get(k) == value,
                "Manifest scientific gate promotion")
        require(cp.get("gate_state", {}).get(k) == value,
                "Checkpoint scientific gate promotion")
    require(site.get("governance", {}).get("K1-D") == "NOT_RELEASED"
            and site.get("governance", {}).get("K1-E") == "NOT_ADMISSIBLE"
            and site.get("governance",{}).get("physical_background") == "NOT_ESTABLISHED"
            and site.get("governance",{}).get("physical_response_rank") == "NOT_EXECUTED",
            "SiteState physical gate promotion")

    baseline_state_p = base["canonical_state"]
    baseline_site_p = base["site_state"]
    baseline_cp_p = base["session_checkpoint"]
    target_map = {baseline_state_p:state_p, baseline_site_p:site_p,
                  baseline_cp_p:cp_p}
    # A pointer-only release must not secretly rewrite the scientific story
    # in public HTML or run arbitrary JavaScript under the same eight-file PR.
    label_changes = (
        ("Canonical State v1.3", "Canonical State v1.4"),
        ("SiteState v1.4", "SiteState v1.5"),
        ("Checkpoint v1.34", "Checkpoint v1.35"),
    )
    for page in ("research-status.html", "research-status-en.html"):
        baseline_page = api.contents(page, base_sha).decode("utf-8")
        expected_page = baseline_page
        for old,new in target_map.items():
            require(old in expected_page,
                    "Baseline public page lacks old reference: " + page)
            expected_page = expected_page.replace(old,new)
        for old,new in label_changes:
            expected_page = expected_page.replace(old,new)
        actual_page = api.contents(page, head_sha).decode("utf-8")
        require(actual_page == expected_page,
                "Public release page has unauthorized non-pointer content edits: " + page)
    script_path = "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js"
    baseline_script = api.contents(script_path, base_sha).decode("utf-8")
    script = api.contents(script_path, head_sha).decode("utf-8")
    version_pattern = r"const VERSION='(\d+)\.(\d+)\.(\d+)';"
    old_versions = list(re.finditer(version_pattern, baseline_script))
    new_versions = list(re.finditer(version_pattern, script))
    require(len(old_versions)==len(new_versions)==1,
            "GlobalShell needs exactly one conventional version declaration")
    old_version = tuple(int(x) for x in old_versions[0].groups())
    new_version = tuple(int(x) for x in new_versions[0].groups())
    require(new_version > old_version, "GlobalShell version must increase")
    require("./"+baseline_site_p in baseline_script,
            "Baseline GlobalShell lacks the expected old SiteState")
    expected_script = baseline_script.replace(
        "./"+baseline_site_p, "./"+site_p)
    expected_script = expected_script.replace(
        old_versions[0].group(0), new_versions[0].group(0))
    require(script == expected_script,
            "GlobalShell contains unauthorized code edits beyond path/version")

    # Recursively scan the *entire tracked HTML/JS tree* for stale active
    # state references. The GitHub tree and blobs are read; never executed.
    tree = api.tree(head_sha)
    web_files = [x for x in tree if x.get("type") == "blob" and
                 x.get("path", "").endswith((".html",".js",".mjs")) and
                 not x.get("path", "").startswith(
                    ("drafts/","tests/","node_modules/",".github/"))]
    require(len(web_files) <= MAX_LIVE_WEB_FILES, "Too many live web files for scan")
    old_tokens = tuple(target_map)
    for item in web_files:
        contents = api.blob(item.get("sha"))
        for stale in old_tokens:
            require(stale.encode("utf-8") not in contents,
                    "Stale active public reference in " + item["path"])
    return f"8-file atomic release checked; {len(web_files)} live web blobs scanned"

def validate_ruleset_enforcement(rulesets: list[dict], trusted_job: str) -> None:
    """Requires active main rules with pull_request and this specific check."""
    require(isinstance(rulesets, list), "No ruleset data")
    pr_rule = False
    check_rule = False
    for ruleset in rulesets:
        if ruleset.get("enforcement") != "active" or ruleset.get("target") != "branch":
            continue
        conditions = ruleset.get("conditions",{}).get("ref_name",{})
        if ("refs/heads/main" not in conditions.get("include", []) or
            "refs/heads/main" in conditions.get("exclude", []) or
            ruleset.get("bypass_actors") or
            ruleset.get("current_user_can_bypass") != "never"):
            continue
        types = {r.get("type") for r in ruleset.get("rules",[])}
        pr_rule = pr_rule or ("pull_request" in types)
        for r in ruleset.get("rules",[]):
            if r.get("type") != "required_status_checks":
                continue
            parameters = r.get("parameters",{})
            required = parameters.get("required_status_checks",[])
            if (parameters.get("strict_required_status_checks_policy") is True and
                any(x.get("context") == trusted_job and
                    x.get("integration_id") == GITHUB_ACTIONS_APP_ID
                    for x in required)):
                check_rule = True
    require(pr_rule and check_rule,
            "Trusted release gate is not mandatory in active main rulesets")

def run_event(event: dict, api: GitHubReadOnly) -> str:
    require(os.environ.get("GITHUB_EVENT_NAME") == "pull_request_target",
            "Must execute ONLY from trusted base pull_request_target")
    require(os.environ.get("GITHUB_REPOSITORY") == REPO,
            "Wrong repository")
    require(os.environ.get("GITHUB_REF") == "refs/heads/main",
            "Must run from main base")
    payload = event.get("pull_request",{})
    number = payload.get("number")
    require(isinstance(number,int) and number > 0,"PR number missing")
    live_pr = api.get("/pulls/" + str(number))
    require(live_pr.get("number") == number and live_pr.get("state") == "open",
            "PR was closed or changed")
    base = live_pr.get("base",{})
    head = live_pr.get("head",{})
    require(base.get("repo",{}).get("full_name") == REPO
            and base.get("ref") == MAIN, "PR base not this repository/main")
    branch = api.get("/branches/main")
    base_sha = base.get("sha")
    head_sha = head.get("sha")
    require(branch.get("commit",{}).get("sha") == base_sha
            == payload.get("base",{}).get("sha"),
            "Base/main drift; rerun on new baseline")
    require(head_sha == payload.get("head",{}).get("sha")
            and bool(re.fullmatch(r"[0-9a-f]{40}",str(head_sha))),
            "PR changed during inspection")
    require(payload.get("draft") == live_pr.get("draft"), "PR draft state changed")
    files = api.paged("/pulls/" + str(number) + "/files", MAX_PR_FILES)
    scopes = scopes_for_files(files)
    if not scopes:
        latest = api.get("/pulls/" + str(number))
        require(latest.get("head",{}).get("sha") == head_sha and
                latest.get("base",{}).get("sha") == base_sha and
                latest.get("draft") == payload.get("draft"),
                "Ordinary PR changed mid-validation")
        require(api.get("/branches/main").get("commit",{}).get("sha") == base_sha,
                "main changed mid-validation")
        return "PASS_ORDINARY_NONRELEASE_PR_NO_OWNER_RELEASE_CLAIM"
    require(live_pr.get("draft") is False,
            "Sensitive PR is Draft; cannot be treated as a release")
    comments = api.paged("/issues/" + str(number) + "/comments", MAX_COMMENTS)
    require(has_scoped_owner_approval(comments,number,head_sha,scopes),
            "Missing exact authenticated owner release acknowledgment for PR/head/scope")
    active = api.paged("/rulesets?includes_parents=true", 100)
    rulesets = []
    for item in active:
        if item.get("enforcement") == "active":
            rulesets.append(api.get("/rulesets/" + str(item["id"])))
    validate_ruleset_enforcement(rulesets,TRUSTED_JOB)
    if "STATE_RELEASE" in scopes:
        result = validate_live_release(files,base_sha,head_sha,api)
    else:
        # Governance/test/workflow changes still require exact owner
        # authorization; only safe finite list of statuses is accepted.
        require(all(item.get("status") in ("added","modified") for item in files),
                "No rename/removal of trusted control-plane paths")
        result = "NONSTATE_SENSITIVE_OWNER_ACK_BOUND_TO_EXACT_PR_HEAD"
    # Re-read the live PR and baseline to detect a mid-validation race.
    latest = api.get("/pulls/" + str(number))
    require(latest.get("head",{}).get("sha") == head_sha
            and latest.get("base",{}).get("sha") == base_sha
            and latest.get("draft") is False, "PR changed mid-validation")
    require(api.get("/branches/main").get("commit",{}).get("sha") == base_sha,
            "main changed mid-validation")
    # Approval comments and required-check enforcement are mutable while CI
    # runs. Re-read both sources immediately before reporting a green result.
    final_comments = api.paged("/issues/" + str(number) + "/comments", MAX_COMMENTS)
    require(has_scoped_owner_approval(final_comments,number,head_sha,scopes),
            "Owner acknowledgment was withdrawn during validation")
    final_list = api.paged("/rulesets?includes_parents=true", 100)
    final_rulesets = [api.get("/rulesets/" + str(item["id"]))
                      for item in final_list
                      if item.get("enforcement") == "active"]
    validate_ruleset_enforcement(final_rulesets,TRUSTED_JOB)
    return "PASS_TECHNICAL_PREMERGE_GATE: " + result

def main() -> None:
    try:
        event_path = os.environ.get("GITHUB_EVENT_PATH")
        require(event_path and Path(event_path).is_file(),
                "Missing GitHub event JSON")
        event = json.loads(Path(event_path).read_text(encoding="utf-8"))
        api = GitHubReadOnly(os.environ.get("GITHUB_TOKEN",""))
        result = run_event(event,api)
        print(result)
        print("NO_PHYSICAL_EVIDENCE_OR_GATE_PROMOTION_CONFERRED")
    except (GateError, KeyError, TypeError, ValueError, UnicodeError) as exc:
        print("RC13 FAIL_CLOSED:",str(exc),file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
