#!/usr/bin/env python3
"""RC17: bounded, NONINSTALLED routine-only Draft artifact validator.

Strictly validates *new* untrusted JSON notes as regular Git blobs.
Never imports/executes submitted content; no GitHub API writes or auto-merge.
Passing means a candidate may receive technical QA, not scientific evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
import datetime as dt
import hashlib
import json
import re
from typing import Sequence

SCHEMA = "universelab.rc17.routine-note.v1"
CONTRACT = "universelab.rc17.solo-routine-safety-contract.v1"
FILE_RE = re.compile(
    r"drafts/(\d{4}-\d{2}-\d{2})_UniverseLab_([A-Za-z][A-Za-z0-9_-]{2,69})_v(\d+)\.(\d+)_DRAFT\.json\Z"
)
REQUIRED = frozenset({
    "schema","status","date","title","basis_main_commit",
    "physical_gate_effect","physical_evidence_effect",
    "authority_status","publication_status","scientific_evidence_status",
    "solver_execution","notes",
})
FROZEN = {
    "schema":SCHEMA,
    "status":"DRAFT_NONCANONICAL",
    "physical_gate_effect":"NONE",
    "physical_evidence_effect":"NONE",
    "authority_status":"NO_AUTHORITY",
    "publication_status":"NOT_PUBLISHED",
    "scientific_evidence_status":"NOT_VALIDATED",
    "solver_execution":"NOT_AUTHORIZED",
}
MAX_FILES=12
MAX_BYTES=32768
MAX_TITLE=120
MAX_NOTES=16
MAX_NOTE_CHARS=1600
MAX_NOTES_TOTAL=12000
MAX_DEPTH=3

class RoutineHold(ValueError):
    def __init__(self, code:str):
        super().__init__(code)
        self.code=code

@dataclass(frozen=True)
class AddedBlob:
    path:str
    status:str
    mode:str
    blob_sha:str
    contents:bytes
    tree_type:str="blob"

@dataclass(frozen=True)
class NativePrerequisites:
    installed_main_trusted_guard:bool=False
    event_policy_compatible:bool=False
    owner_accepted_exception:bool=False
    main_required_pull_request:bool=False
    strict_unique_current_head_check:bool=False
    check_pinned_to_correct_app:bool=False
    protected_ruleset_current:bool=False
    canary_blocks_invalid_merge:bool=False
    no_bypass_actors:bool=False

def fail(code:str):
    raise RoutineHold(code)

def git_blob_sha(contents:bytes)->str:
    if not isinstance(contents,bytes):
        fail("INVALID_BLOB_CONTENT")
    data=b"blob "+str(len(contents)).encode("ascii")+b"\x00"+contents
    return hashlib.sha1(data).hexdigest()

def no_duplicates(pairs):
    obj={}
    for key,value in pairs:
        if key in obj:
            fail("DUPLICATE_JSON_KEY")
        obj[key]=value
    return obj

def constant_forbidden(value):
    fail("NONFINITE_JSON_NUMBER")

def json_depth(value, n=0):
    if n>MAX_DEPTH:
        fail("JSON_DEPTH_LIMIT")
    if isinstance(value,dict):
        for v in value.values():
            json_depth(v,n+1)
    elif isinstance(value,list):
        for v in value:
            json_depth(v,n+1)

def parse_document(contents:bytes):
    if not isinstance(contents,bytes) or len(contents)==0 or len(contents)>MAX_BYTES:
        fail("DOC_SIZE_LIMIT")
    try:
        obj=json.loads(contents.decode("utf-8"),
                       object_pairs_hook=no_duplicates,
                       parse_constant=constant_forbidden)
    except RoutineHold:
        raise
    except (ValueError,UnicodeError,TypeError,OverflowError):
        fail("INVALID_JSON")
    json_depth(obj)
    if not isinstance(obj,dict):
        fail("JSON_NOT_OBJECT")
    if set(obj)!=REQUIRED:
        fail("FIELDS_NOT_STRICT_ENVELOPE")
    for key,value in FROZEN.items():
        if obj.get(key)!=value:
            fail("FORBIDDEN_STATUS_OR_AUTHORITY")
    return obj

def safe_text(value:str, limit:int, multiline:bool)->bool:
    if not isinstance(value,str) or not value or len(value)>limit:
        return False
    if any((ord(c)<32 and c not in ("\n","\t")) or ord(c)==127 for c in value):
        return False
    if not multiline and any(c in value for c in "\n\r\t"):
        return False
    if "<script" in value.lower() or "javascript:" in value.lower():
        return False
    return True

def validate_single(item:AddedBlob, current_main_commit:str):
    if not isinstance(current_main_commit,str) or not re.fullmatch(r"[0-9a-f]{40}",current_main_commit):
        fail("MAIN_COMMIT_UNVERIFIED")
    if not isinstance(item.path,str):
        fail("PATH_INVALID")
    match=FILE_RE.fullmatch(item.path)
    if match is None:
        fail("PATH_OUTSIDE_ROUTINE_EXCEPTION")
    if item.status!="added":
        fail("NOT_NEW_FILE")
    if item.mode!="100644" or item.tree_type!="blob":
        fail("NOT_REGULAR_GIT_BLOB")
    if not isinstance(item.blob_sha,str) or len(item.blob_sha)!=40:
        fail("BLOB_SHA_MISSING")
    if git_blob_sha(item.contents)!=item.blob_sha:
        fail("BLOB_SHA_MISMATCH")
    try:
        file_date=dt.date.fromisoformat(match.group(1))
    except ValueError:
        fail("INVALID_FILENAME_DATE")
    obj=parse_document(item.contents)
    if obj["date"]!=file_date.isoformat():
        fail("DATE_FIELD_DISAGREES")
    if obj["basis_main_commit"]!=current_main_commit:
        fail("STALE_SOURCE_MAIN_COMMIT")
    if not safe_text(obj["title"],MAX_TITLE,multiline=False):
        fail("TITLE_INVALID")
    notes=obj["notes"]
    if not isinstance(notes,list) or not (1<=len(notes)<=MAX_NOTES):
        fail("NOTES_LIST_INVALID")
    if any(not safe_text(note,MAX_NOTE_CHARS,multiline=True) for note in notes):
        fail("NOTE_INVALID")
    if sum(len(note) for note in notes)>MAX_NOTES_TOTAL:
        fail("NOTES_TOTAL_LIMIT")
    return {"path":item.path,"sha":item.blob_sha,
            "status":"QA_VALID_ONLY_NONCANONICAL",
            "notes":len(notes)}

def evaluate_routine_qa(files:Sequence[AddedBlob], current_main_commit:str):
    """May run on a *Draft PR*. Never returns authorization to merge."""
    if not isinstance(files,(list,tuple)) or not (1<=len(files)<=MAX_FILES):
        fail("PR_FILE_COUNT_OR_TYPE_INVALID")
    seen=set()
    result=[]
    for item in files:
        if not isinstance(item,AddedBlob):
            fail("PR_ENTRY_TYPE_INVALID")
        key=item.path.casefold() if isinstance(item.path,str) else ""
        if key in seen:
            fail("DUPLICATE_OR_CASE_COLLIDING_PATH")
        seen.add(key)
        result.append(validate_single(item,current_main_commit))
    return {"status":"ROUTINE_QA_PASS_NOT_MERGE_AUTHORIZATION",
            "files":len(result),"verified_blobs":result}

def evaluate_routine_merge(qa_result:dict, prereq:NativePrerequisites,
                           pr_is_draft:bool, pr_base_and_head_current:bool,
                           selected_policy:str):
    """A future *model* for GitHub-native gating; no control-plane write."""
    if (not isinstance(qa_result,dict) or
        qa_result.get("status")!="ROUTINE_QA_PASS_NOT_MERGE_AUTHORIZATION"):
        return "HOLD_INVALID_OR_UNPROVEN_QA"
    if selected_policy!="RC16-B_SOLO_HOLD":
        return "HOLD_POLICY_NOT_INSTALLED_OR_SELECTED"
    if pr_is_draft:
        return "HOLD_DRAFT_PR_NOT_MERGEABLE"
    if not isinstance(prereq,NativePrerequisites) or not pr_base_and_head_current:
        return "HOLD_GITHUB_STATE_NOT_VERIFIED"
    if not all(vars(prereq).values()):
        return "HOLD_NATIVE_REQUIRED_CHECKS_OR_CANARY_NOT_VERIFIED"
    return "CONDITIONAL_ROUTINE_MERGE_ELIGIBLE_NEVER_AUTO_MERGE"

def recovery_for(code:str)->dict:
    routes={
       "INVALID_JSON":("FIX_FILE","Correct JSON in same branch, re-run QA"),
       "DUPLICATE_JSON_KEY":("FIX_FILE","Eliminate duplicates, verify original content"),
       "STALE_SOURCE_MAIN_COMMIT":("REBASE_RECHECK","Use current verified main and rerun all checks"),
       "BLOB_SHA_MISMATCH":("FETCH_CORRECT_BLOB","Re-read exact PR-head blob/tree, do not trust cached content"),
       "NOT_REGULAR_GIT_BLOB":("RECREATE_REGULAR_FILE","Reject symlink/submodule, create a new regular JSON blob"),
       "NOT_NEW_FILE":("SENSITIVE_HOLD","Editing existing files is not a routine exemption"),
       "FIELDS_NOT_STRICT_ENVELOPE":("SENSITIVE_HOLD","New semantic fields require separate review"),
       "FORBIDDEN_STATUS_OR_AUTHORITY":("SENSITIVE_HOLD","Do not promote canonical or physical status through routine notes"),
       "PR_FILE_COUNT_OR_TYPE_INVALID":("SPLIT_AND_REVIEW","Separate large or mixed changes into bounded PRs"),
       "PATH_OUTSIDE_ROUTINE_EXCEPTION":("SENSITIVE_HOLD","Use separate protected review for non-routine paths"),
       "MAIN_COMMIT_UNVERIFIED":("HOLD_RETRY_READ_ONLY","Check live GitHub main, no guess"),
    }
    action,description=routes.get(code,("HOLD_INVESTIGATE","Do not override failing or unknown security check"))
    return {"status":"RECOVERY_PROPOSAL_ONLY","cause":code,
            "action":action,"procedure":description,
            "bypass_allowed":False,"direct_push_to_main":False,
            "disable_required_checks":False,"solver_execution":False,
            "canonical_promotion":False}

if __name__=="__main__":
    print("RC17 noninstalled routine QA model. Use mock tests; no GitHub write.")
