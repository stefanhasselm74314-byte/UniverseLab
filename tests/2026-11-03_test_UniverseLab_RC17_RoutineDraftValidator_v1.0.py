#!/usr/bin/env python3
"""RC17: adversarial mock regression for routine-only Draft JSON exceptions."""
from __future__ import annotations

from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"tools/2026-11-03_UniverseLab_RC17_RoutineDraftValidator_v1.0.py"
spec=importlib.util.spec_from_file_location("universelab_rc17_policy",TARGET)
assert spec and spec.loader
mod=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=mod
spec.loader.exec_module(mod)

MAIN="a"*40
FILE="drafts/2026-11-03_UniverseLab_RC17_AnalyticNotes_v1.0_DRAFT.json"

def envelope(**overrides):
    doc={
      "schema":"universelab.rc17.routine-note.v1",
      "status":"DRAFT_NONCANONICAL",
      "date":"2026-11-03",
      "title":"Reviewvorbereitung ohne physikalische Freigabe",
      "basis_main_commit":MAIN,
      "physical_gate_effect":"NONE",
      "physical_evidence_effect":"NONE",
      "authority_status":"NO_AUTHORITY",
      "publication_status":"NOT_PUBLISHED",
      "scientific_evidence_status":"NOT_VALIDATED",
      "solver_execution":"NOT_AUTHORIZED",
      "notes":["Kinematische Gleichungen werden separat geprueft",
               "Kein Hintergrund, keine Ghostfreiheit oder Observablen-Freigabe belegt"]
    }
    doc.update(overrides)
    return doc

def make_blob(doc=None,path=FILE,status="added",mode="100644",content=None,
              tree_type="blob",sha=None):
    if content is None:
        content=(json.dumps(doc if doc is not None else envelope(),
                 ensure_ascii=False,sort_keys=True)+"\n").encode("utf-8")
    return mod.AddedBlob(path,status,mode,
        sha if sha is not None else mod.git_blob_sha(content),content,tree_type)

def pass_all_prereqs():
    return mod.NativePrerequisites(**{name:True for name in
        mod.NativePrerequisites.__dataclass_fields__})

class RoutineDraftTests(unittest.TestCase):
    def test_01_single_regular_draft_QA_is_not_merge_authorization(self):
        data=mod.evaluate_routine_qa([make_blob()],MAIN)
        self.assertEqual(data["status"],"ROUTINE_QA_PASS_NOT_MERGE_AUTHORIZATION")
        self.assertEqual(data["files"],1)
        self.assertEqual(data["verified_blobs"][0]["status"],"QA_VALID_ONLY_NONCANONICAL")

    def test_02_bounded_multi_draft_QA(self):
        files=[make_blob(path=f"drafts/2026-11-03_UniverseLab_RC17_Note_{i}_v1.0_DRAFT.json")
               for i in range(1,13)]
        self.assertEqual(mod.evaluate_routine_qa(files,MAIN)["files"],12)
        with self.assertRaises(mod.RoutineHold):
            mod.evaluate_routine_qa(files+[make_blob(path=
                "drafts/2026-11-03_UniverseLab_RC17_Note_13_v1.0_DRAFT.json")],MAIN)

    def test_03_field_status_and_embedded_claim_attempts(self):
        defects=[
          ("ratified_status",{"status":"RATIFIED"}),
          ("active_status",{"status":"ACTIVE"}),
          ("fake_physical_gate",{"physical_gate_effect":"PROMOTED"}),
          ("fake_empirical_evidence",{"physical_evidence_effect":"CONFIRMED"}),
          ("fake_owner_authority",{"authority_status":"OWNER_RATIFIED"}),
          ("fake_publication",{"publication_status":"PUBLISHED"}),
          ("fake_science",{"scientific_evidence_status":"VERIFIED"}),
          ("fake_solver",{"solver_execution":"EXECUTED"}),
          ("extra_claim_field",{"physical_claims":{"ghost_free":True}}),
          ("extra_workflow_field",{"run":"python exploit.py"}),
          ("missing_field",{ "notes": None }),
          ("nested_object_notes",{"notes":[{"status":"PASS"}]}),
          ("empty_notes",{"notes":[]}),
          ("many_notes",{"notes":["a"]*17}),
          ("long_note",{"notes":["a"*1601]}),
          ("long_title",{"title":"A"*121}),
          ("script_text",{"notes":["<script>alert(1)</script>"]}),
          ("javascript_uri",{"notes":["javascript:alert(1)"]}),
          ("control_chars",{"notes":["a\u0001b"]}),
          ("stale_main",{"basis_main_commit":"b"*40}),
          ("date_mismatch",{"date":"2026-11-02"}),
        ]
        for label,mods in defects:
            with self.subTest(label=label):
                item=make_blob(envelope(**mods))
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa([item],MAIN)

    def test_04_strict_git_modes_path_and_status(self):
        deviations=[
          ("modified_existing",replace(make_blob(),status="modified")),
          ("deleted_existing",replace(make_blob(),status="removed")),
          ("symlink",replace(make_blob(),mode="120000")),
          ("submodule",replace(make_blob(),mode="160000",tree_type="commit")),
          ("executable",replace(make_blob(),mode="100755")),
          ("blob_sha_mismatch",replace(make_blob(),blob_sha="0"*40)),
          ("registry_path",replace(make_blob(),path=
            "registry/2026-11-03_UniverseLab_RC17_AnalyticNotes_v1.0_DRAFT.json")),
          ("plain_md",replace(make_blob(),path=
            "drafts/2026-11-03_UniverseLab_RC17_AnalyticNotes_v1.0_DRAFT.md")),
          ("path_escape",replace(make_blob(),path="../project-manifest.json")),
          ("invalid_filename_date",replace(make_blob(),path=
            "drafts/2026-02-30_UniverseLab_RC17_AnalyticNotes_v1.0_DRAFT.json")),
          ("bad_filename",replace(make_blob(),path="drafts/RC17.json"))
        ]
        for label,item in deviations:
            with self.subTest(label=label):
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa([item],MAIN)

    def test_05_duplicate_case_collisions_and_mixed_prs(self):
        items=[
            (make_blob(),make_blob()),
            (make_blob(),replace(make_blob(),path=FILE.lower())),
            (make_blob(),replace(make_blob(),path="project-manifest.json")),
        ]
        for pair in items:
            with self.subTest(paths=[p.path for p in pair]):
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa(list(pair),MAIN)

    def test_06_invalid_json_parser_semantics(self):
        invalid=[
          ("duplicate_key",b'{"status":"DRAFT_NONCANONICAL","status":"RATIFIED"}'),
          ("nonfinite",b'{"x":NaN}'),
          ("syntax",b'{not_json'),
          ("empty",b''),
          ("huge",b'{"a":"'+b'a'*33000+b'"}'),
          ("deep",b'{"a":{"b":{"c":{"d":1}}}}'),
          ("array_top",b'[]'),
          ("invalid_utf8",b'\xff\xfe'),
        ]
        for label,data in invalid:
            with self.subTest(label=label):
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa([make_blob(content=data)],MAIN)

    def test_07_source_binding_and_blob_integrity(self):
        item=make_blob()
        self.assertEqual(mod.git_blob_sha(item.contents),item.blob_sha)
        for bad in ("", "MOVED", "g"*40,"b"*40):
            with self.subTest(main=bad):
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa([item],bad)
        # A candidate cannot copy its own content from a different tree blob
        stale=replace(item,contents=item.contents+b" ")
        with self.assertRaises(mod.RoutineHold):
            mod.evaluate_routine_qa([stale],MAIN)

    def test_08_draft_QA_allowed_merge_always_held(self):
        qa=mod.evaluate_routine_qa([make_blob()],MAIN)
        self.assertEqual(mod.evaluate_routine_merge(
          qa,pass_all_prereqs(),True,True,"RC16-B_SOLO_HOLD"),
          "HOLD_DRAFT_PR_NOT_MERGEABLE")
        self.assertEqual(mod.evaluate_routine_merge(
          qa,pass_all_prereqs(),False,True,"NOT_SELECTED"),
          "HOLD_POLICY_NOT_INSTALLED_OR_SELECTED")
        self.assertEqual(mod.evaluate_routine_merge(
          qa,pass_all_prereqs(),False,True,"RC16-B_SOLO_HOLD"),
          "CONDITIONAL_ROUTINE_MERGE_ELIGIBLE_NEVER_AUTO_MERGE")

    def test_09_every_missing_platform_control_blocks(self):
        qa=mod.evaluate_routine_qa([make_blob()],MAIN)
        for key in mod.NativePrerequisites.__dataclass_fields__:
            p=replace(pass_all_prereqs(),**{key:False})
            with self.subTest(missing=key):
                self.assertEqual(mod.evaluate_routine_merge(
                    qa,p,False,True,"RC16-B_SOLO_HOLD"),
                    "HOLD_NATIVE_REQUIRED_CHECKS_OR_CANARY_NOT_VERIFIED")
        self.assertEqual(mod.evaluate_routine_merge(
            qa,pass_all_prereqs(),False,False,"RC16-B_SOLO_HOLD"),
            "HOLD_GITHUB_STATE_NOT_VERIFIED")

    def test_10_sensitive_pr_never_gets_routine_QA(self):
        protected=[
          "index.html","research-status.html","registry/session-checkpoint-latest.json",
          "project-manifest.json",".github/workflows/any.yml",
          "tools/2026-11-03_script.py","tests/2026-11-03_test.py",
          "governance/2026-11-03_rule.md","drafts/2026-11-03_Claim.png",
        ]
        for path in protected:
            with self.subTest(path=path):
                with self.assertRaises(mod.RoutineHold):
                    mod.evaluate_routine_qa([make_blob(path=path)],MAIN)

    def test_11_recovery_never_bypasses_main(self):
        for cause in (
            "INVALID_JSON","STALE_SOURCE_MAIN_COMMIT","NOT_REGULAR_GIT_BLOB",
            "FORBIDDEN_STATUS_OR_AUTHORITY","BLOB_SHA_MISMATCH",
            "PATH_OUTSIDE_ROUTINE_EXCEPTION","UNKNOWN_FAILURE"
        ):
            with self.subTest(cause=cause):
                result=mod.recovery_for(cause)
                self.assertEqual(result["status"],"RECOVERY_PROPOSAL_ONLY")
                for key in ("bypass_allowed","direct_push_to_main",
                            "disable_required_checks","solver_execution",
                            "canonical_promotion"):
                    self.assertIs(result[key],False)
                self.assertNotIn("PASS",result["action"])

    def test_12_noninstalled_guard_has_no_unsafe_side_effects(self):
        source=TARGET.read_text(encoding="utf-8")
        for dangerous in ("subprocess","os.system(", "requests.post(",
                          "exec(", "eval(", "create_pull_request"):
            self.assertNotIn(dangerous,source)
        self.assertIn("ROUTINE_QA_PASS_NOT_MERGE_AUTHORIZATION",source)

if __name__=="__main__":
    unittest.main(verbosity=2)
