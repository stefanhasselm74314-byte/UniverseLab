#!/usr/bin/env python3
"""RC16: adversarial tests for unselected authorization policy alternatives.

The RC13 production candidate is intentionally NOT modified or replaced by
this test suite. Passing mocks do not authorize changes to main or rulesets.
"""
from __future__ import annotations
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/"tools/2026-11-03_UniverseLab_RC16_AuthorizationModel_v1.0.py"
spec=importlib.util.spec_from_file_location("universe_rc16_policy",MODULE)
m=importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
import sys
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def candidate():
    return m.Changed(
        "drafts/2026-11-03_UniverseLab_RC16_Example_v1.0_DRAFT.json",
        "added",
        (json.dumps({"schema":"test.rc16","status":"DRAFT_NOT_CANONICAL",
          "physical_gate_effect":"NONE","physical_evidence_effect":"NONE",
          "canonical_promotion":"BLOCKED","solver_execution":"NOT_AUTHORIZED"})+"\n").encode()
    )

def enforcement():
    return m.Enforcement(
        guard_installed_on_main=True,
        event_policy_allows_trusted_workflow=True,
        required_pull_request=True,
        required_status_check_unique=True,
        required_status_check_strict=True,
        required_status_check_bound_to_expected_app=True,
        required_status_check_for_current_head=True,
        pr_head_and_base_unchanged=True,
        independent_human_security_review_completed=False,
        independent_approving_review_required=False,
        native_approving_review_at_current_head=False,
        native_dismiss_stale_approvals=False,
        protected_ruleset_current=True
    )

def ctx(mode="RC16-B_SOLO_HOLD",changes=None,owner=False,e=None,draft=False):
    if changes is None:changes=(candidate(),)
    if e is None:e=enforcement()
    return m.Context(mode,draft,tuple(changes),e,owner)

class PolicyDecisionTests(unittest.TestCase):
    def test_01_counterexample_old_comment_is_temporally_unsafe(self):
        scenario=m.revoked_comment_counterexample()
        self.assertIn("SUCCESS",scenario["counterexample"])
        self.assertIn("no current comment authorization",scenario["counterexample"])
        self.assertIn("HOLD",scenario["repair"])

    def test_02_path_scope_is_fail_closed(self):
        expected=[
            ("index.html","PUBLIC_SURFACE"),
            ("README.md","PUBLIC_SURFACE"),
            ("navigator.html","PUBLIC_SURFACE"),
            ("assets/plots/predict.png","PUBLIC_SURFACE"),
            ("src/physics.fits","CONTROL_PLANE"),
            (".github/workflows/a.yml","CONTROL_PLANE"),
            ("registry/2026-11-03_UniverseLab_Claim_v0.1.json","CONTROL_PLANE"),
            ("registry/session-checkpoint-latest.json","STATE_RELEASE"),
            ("project-manifest.json","STATE_RELEASE"),
            ("research-status-en.html","STATE_RELEASE"),
            ("registry/2026-11-03_UniverseLab_CurrentMainCanonicalState_v1.4.json","STATE_RELEASE"),
        ]
        for name,scope in expected:
            with self.subTest(name=name):
                self.assertEqual(m.classify(m.Changed(name,"modified")),scope)

    def test_03_strict_noncanonical_draft_exception(self):
        self.assertEqual(m.classify(candidate()),m.SAFE_CODE)
        defects=[
            replace(candidate(),status="modified"),
            replace(candidate(),status="removed"),
            replace(candidate(),source_bytes=None),
            replace(candidate(),source_bytes=b"<script>alert(1)</script>"),
            replace(candidate(),path="drafts/2026-11-03_Test.py"),
            replace(candidate(),path="drafts/2026-11-03_UniverseLab_Ex_DRAFT.md"),
            replace(candidate(),source_bytes=json.dumps(
                {"status":"RATIFIED","physical_gate_effect":"NONE",
                 "physical_evidence_effect":"NONE"}).encode()),
            replace(candidate(),source_bytes=json.dumps(
                {"status":"DRAFT","physical_gate_effect":"PROMOTED",
                 "physical_evidence_effect":"NONE"}).encode()),
            replace(candidate(),source_bytes=json.dumps(
                {"status":"DRAFT","physical_gate_effect":"NONE",
                 "physical_evidence_effect":"CONFIRMED"}).encode()),
            replace(candidate(),source_bytes=json.dumps(
                {"status":"DRAFT","physical_gate_effect":"NONE",
                 "physical_evidence_effect":"NONE","canonical_promotion":True}).encode()),
            replace(candidate(),source_bytes=json.dumps(
                {"status":"DRAFT","physical_gate_effect":"NONE",
                 "physical_evidence_effect":"NONE","solver_execution":True}).encode()),
        ]
        for i,doc in enumerate(defects):
            with self.subTest(negative=i):
                self.assertNotEqual(m.classify(doc),m.SAFE_CODE)

    def test_04_routine_no_owner_comment_needed_when_native_rules_verified(self):
        first=m.decide(ctx(owner=False))
        second=m.decide(ctx(owner=True))
        self.assertEqual(first,"PASS_ROUTINE_NONCANONICAL_DRAFT_ONLY")
        self.assertEqual(first,second)

    def test_05_all_real_prs_blocked_before_installation(self):
        self.assertEqual(m.decide(ctx(e=replace(enforcement(),
            guard_installed_on_main=False))),"HOLD_NATIVE_ENFORCEMENT_NOT_VERIFIED")
        self.assertEqual(m.decide(ctx(e=replace(enforcement(),
            event_policy_allows_trusted_workflow=False))),"HOLD_NATIVE_ENFORCEMENT_NOT_VERIFIED")

    def test_06_solo_sensitive_never_green_because_of_owner_comment(self):
        cases=[
            ("research-status.html","modified"),
            ("index.html","added"),
            ("governance/2026-11-03_UniverseLab_Rule_v1.0.md","added"),
            ("tests/2026-11-03_UniverseLab_Test_v1.0.py","added"),
            ("project-manifest.json","modified"),
            (".github/workflows/2026-11-03_UniverseLab_Gate.yml","modified"),
        ]
        for path,status in cases:
            for comment in (False,True):
                with self.subTest(path=path,owner_comment=comment):
                    decision=m.decide(ctx(changes=(m.Changed(path,status),),owner=comment))
                    self.assertEqual(decision,"HOLD_SENSITIVE_SOLO_NO_DURABLE_GRANT")

    def test_07_comment_removal_after_green_cannot_create_sensitive_pass(self):
        c=ctx(changes=(m.Changed("index.html","modified"),),owner=True)
        granted=m.decide(c)
        revoked=m.decide(replace(c,owner_issue_comment_present=False))
        self.assertEqual(granted,revoked)
        self.assertNotIn("PASS",revoked)

    def test_08_native_review_requires_real_durable_github_rules(self):
        sensitive=(m.Changed("project-manifest.json","modified"),)
        reviewed=replace(enforcement(),
            independent_human_security_review_completed=True,
            independent_approving_review_required=True,
            native_approving_review_at_current_head=True,
            native_dismiss_stale_approvals=True)
        ok=m.decide(ctx(mode="RC16-A_NATIVE_REVIEW",changes=sensitive,e=reviewed))
        self.assertEqual(ok,"PASS_CONDITIONAL_NATIVE_REVIEW_GATE")
        for key in (
            "independent_human_security_review_completed",
            "independent_approving_review_required",
            "native_approving_review_at_current_head",
            "native_dismiss_stale_approvals",
        ):
            with self.subTest(removed=key):
                d=m.decide(ctx(mode="RC16-A_NATIVE_REVIEW",changes=sensitive,
                    e=replace(reviewed,**{key:False}),owner=True))
                self.assertNotIn("PASS",d)

    def test_09_any_missing_native_control_blocks_routine_and_sensitive(self):
        keys=(
            "guard_installed_on_main",
            "event_policy_allows_trusted_workflow",
            "required_pull_request",
            "required_status_check_unique",
            "required_status_check_strict",
            "required_status_check_bound_to_expected_app",
            "required_status_check_for_current_head",
            "pr_head_and_base_unchanged",
            "protected_ruleset_current",
        )
        for key in keys:
            with self.subTest(blocker=key):
                e=replace(enforcement(),**{key:False})
                decision=m.decide(ctx(e=e))
                self.assertEqual(decision,"HOLD_NATIVE_ENFORCEMENT_NOT_VERIFIED")

    def test_10_mixed_routine_and_public_changes_are_sensitive(self):
        d=ctx(changes=(candidate(),m.Changed("index.html","modified")))
        self.assertEqual(m.classify_pr(d.changes),
            {m.SAFE_CODE,"PUBLIC_SURFACE"})
        self.assertEqual(m.decide(d),"HOLD_SENSITIVE_SOLO_NO_DURABLE_GRANT")

    def test_11_invalid_or_duplicate_paths_fail_closed(self):
        changes=(
            (m.Changed("../project-manifest.json","modified"),),
            (m.Changed("/registry/file.json","added"),),
            (m.Changed("index.html","symlink"),),
            (candidate(),candidate()),
            (),
        )
        for batch in changes:
            with self.subTest(batch=str(batch)[:50]):
                self.assertEqual(m.decide(ctx(changes=batch)),
                                 "HOLD_INVALID_CHANGE_SET")

    def test_12_unknown_mode_and_draft_state_hard_stop(self):
        self.assertEqual(m.decide(ctx(mode="RC16-C_UNSAFE_COMMENT")),
                         "HOLD_MODE_NOT_SELECTED")
        self.assertEqual(m.decide(ctx(draft=True)),"HOLD_DRAFT_PR")

if __name__=="__main__":
    unittest.main(verbosity=2)
