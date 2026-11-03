#!/usr/bin/env python3
"""RC16 deliberately NON-INSTALLED authorization research model.

Not referenced by any main release job. Evaluate a simple, fail-closed policy
choice without conflating a mutable GitHub comment with durable branch review.

Not a cryptographic proof, not production authorization, not a physics result.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Mapping, Sequence

DRAFT_JSON = re.compile(
    r"drafts/\d{4}-\d{2}-\d{2}_UniverseLab_[A-Za-z0-9_.-]+_DRAFT\.json\Z"
)
SAFE_CODE = "ROUTINE_DRAFT_ONLY"
SENSITIVE = frozenset({"STATE_RELEASE","CONTROL_PLANE","PUBLIC_SURFACE"})
RELEASE_FAMILY = frozenset({
    "project-manifest.json",
    "registry/session-checkpoint-latest.json",
    "research-status.html",
    "research-status-en.html",
    "assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js",
})
RELEASE_REGISTRY = (
    re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_CurrentMainCanonicalState_v\d+\.\d+\.json\Z"),
    re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_SessionCheckpoint_v\d+\.\d+\.json\Z"),
    re.compile(r"registry/\d{4}-\d{2}-\d{2}_UniverseLab_SiteState_v\d+\.\d+\.json\Z"),
)
PUBLIC_EXTS = (".html",".htm",".md",".mdx",".js",".mjs",".css",
               ".svg",".png",".jpg",".jpeg",".webp")

class PolicyError(ValueError):
    pass

@dataclass(frozen=True)
class Changed:
    path: str
    status: str  # added, modified, removed or renamed
    source_bytes: bytes | None = None

@dataclass(frozen=True)
class Enforcement:
    guard_installed_on_main: bool
    event_policy_allows_trusted_workflow: bool
    required_pull_request: bool
    required_status_check_unique: bool
    required_status_check_strict: bool
    required_status_check_bound_to_expected_app: bool
    required_status_check_for_current_head: bool
    pr_head_and_base_unchanged: bool
    independent_human_security_review_completed: bool
    independent_approving_review_required: bool = False
    native_approving_review_at_current_head: bool = False
    native_dismiss_stale_approvals: bool = False
    protected_ruleset_current: bool = False

@dataclass(frozen=True)
class Context:
    mode: str
    pr_is_draft: bool
    changes: tuple[Changed,...]
    enforcement: Enforcement
    owner_issue_comment_present: bool  # deliberately ignored as durable grant

def nonoperative_json(content: bytes | None) -> bool:
    if not isinstance(content,bytes) or not content or len(content)>1_000_000:
        return False
    try:
        value=json.loads(content.decode("utf-8"))
    except (UnicodeError,ValueError):
        return False
    return (
        isinstance(value,dict) and
        "DRAFT" in str(value.get("status","")).upper() and
        value.get("physical_gate_effect")=="NONE" and
        value.get("physical_evidence_effect")=="NONE" and
        value.get("canonical_promotion",False) in (False,"BLOCKED",None) and
        value.get("solver_execution",False) in (False,"NOT_AUTHORIZED",None)
    )

def classify(change: Changed) -> str:
    name=change.path
    if not isinstance(name,str) or not name or name.startswith("/") or ".." in name.split("/") or "\\" in name:
        raise PolicyError("Invalid or escaping Git path")
    if change.status not in ("added","modified","removed","renamed"):
        raise PolicyError("Unknown Git status")
    if DRAFT_JSON.fullmatch(name) and change.status=="added" and nonoperative_json(change.source_bytes):
        return SAFE_CODE
    if name in RELEASE_FAMILY or any(pattern.fullmatch(name) for pattern in RELEASE_REGISTRY):
        return "STATE_RELEASE"
    if name.startswith((".github/","registry/","governance/","schemas/","tools/","tests/")):
        return "CONTROL_PLANE"
    if name.endswith(PUBLIC_EXTS) or name.startswith(("assets/","public/","docs/","site/")):
        return "PUBLIC_SURFACE"
    return "CONTROL_PLANE"

def classify_pr(changes: Sequence[Changed]) -> set[str]:
    if not changes or len(changes)>1000:
        raise PolicyError("Missing/oversized change list")
    paths=set()
    scopes=set()
    for change in changes:
        if change.path in paths:
            raise PolicyError("Duplicated changed path")
        paths.add(change.path)
        scopes.add(classify(change))
    return scopes

def decide(context: Context) -> str:
    """A mock policy verdict; a PASS is only conditional on asserted preconditions."""
    if context.mode not in ("RC16-A_NATIVE_REVIEW","RC16-B_SOLO_HOLD"):
        return "HOLD_MODE_NOT_SELECTED"
    try:
        scopes=classify_pr(context.changes)
    except PolicyError:
        return "HOLD_INVALID_CHANGE_SET"

    if context.pr_is_draft:
        return "HOLD_DRAFT_PR"
    e=context.enforcement
    mandatory=(
        e.guard_installed_on_main,
        e.event_policy_allows_trusted_workflow,
        e.required_pull_request,
        e.required_status_check_unique,
        e.required_status_check_strict,
        e.required_status_check_bound_to_expected_app,
        e.required_status_check_for_current_head,
        e.pr_head_and_base_unchanged,
        e.protected_ruleset_current,
    )
    if not all(mandatory):
        return "HOLD_NATIVE_ENFORCEMENT_NOT_VERIFIED"
    if scopes=={SAFE_CODE}:
        return "PASS_ROUTINE_NONCANONICAL_DRAFT_ONLY"
    if context.mode=="RC16-B_SOLO_HOLD":
        return "HOLD_SENSITIVE_SOLO_NO_DURABLE_GRANT"
    # Native approval is a platform-level merge invariant, not a mutable PR
    # issue comment read once and cached into a status-check result.
    if not e.independent_human_security_review_completed:
        return "HOLD_SECURITY_REVIEW_ABSENT"
    if not all((e.independent_approving_review_required,
                e.native_approving_review_at_current_head,
                e.native_dismiss_stale_approvals)):
        return "HOLD_NATIVE_APPROVAL_NOT_VERIFIED"
    return "PASS_CONDITIONAL_NATIVE_REVIEW_GATE"

def revoked_comment_counterexample() -> dict:
    """Explicitly exhibit TOCTOU for the old 'owner issue comment' design."""
    return {
        "t0": "Owner issue-comment exists for PR/head",
        "t1": "One-shot PR check reads comment and reports SUCCESS",
        "t2": "Owner edits/deletes the comment; no compatible PR check is guaranteed to rerun",
        "t3": "Previous SUCCESS can still be displayed for the same head",
        "safety_property": "MERGE_AUTHORIZED_IMPLIES_CURRENT_OWNER_GRANT",
        "counterexample": "t3 has SUCCESS but no current comment authorization",
        "repair": "Do not treat issue comments as the durable merge grant. Use native protected reviews or HOLD."
    }

if __name__ == "__main__":
    print("RC16 prototype only; this code is not installed as a release guard.")
