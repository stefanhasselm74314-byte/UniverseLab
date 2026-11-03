#!/usr/bin/env python3
"""Adversarial regressions for the conditional quantum-method integration."""
from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'tools/2026-10-03_validate_UL-SING_QuantumClosure_MethodIntegration_v1.0.py'
SPEC = importlib.util.spec_from_file_location('quantum_method_integration', TOOL)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        cross = MOD.read(ROOT, MOD.CROSS)
        paths = {MOD.BASE, MOD.GATES, MOD.CROSS, MOD.DOC,
                 'project-manifest.json', 'solver-hub-manifest.json'}
        paths.update(r['path'] for r in cross['preserved_sources'].values())
        for path in paths:
            target = self.root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / path, target)

    def change(self, path, mutate):
        data = MOD.read(self.root, path)
        mutate(data)
        (self.root / path).write_text(json.dumps(data), encoding='utf-8')

    def reject(self, path, mutate, message):
        self.change(path, mutate)
        with self.assertRaisesRegex(ValueError, message):
            MOD.validate(self.root)

    def test_current_contract_passes(self):
        MOD.validate(self.root)

    def test_dangling_roadmap_rejected(self):
        path = MOD.read(self.root, MOD.CROSS)['preserved_sources']['ulsh07']['path']
        (self.root / path).unlink()
        with self.assertRaisesRegex(ValueError, 'missing or unsafe source'):
            MOD.validate(self.root)

    def test_retargeted_roadmap_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][2]['repository_links'].update(
            ulsh07_kk_roadmap='science/solver-hub/DOES_NOT_EXIST.md'), 'inherited method')

    def test_empty_requirements_rejected_for_each_gate(self):
        original = (self.root / MOD.GATES).read_bytes()
        for index in range(3):
            with self.subTest(gate=index):
                (self.root / MOD.GATES).write_bytes(original)
                self.reject(MOD.GATES, lambda d: d['gates'][index].update(closure_evidence_required=[]),
                            'inherited method')

    def test_dormant_cannot_be_promoted(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0].update(activation_state='ACTIVE'), 'inherited method')

    def test_missing_applicability_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][1].pop('applicability'), 'inherited method')

    def test_forged_closure_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][2].update(closure_status='PASS'), 'inherited method')

    def test_source_version_missing_rejected(self):
        self.change(MOD.GATES, lambda d: d['gates'][0]['source'].pop('source_version'))
        with self.assertRaises(KeyError):
            MOD.validate(self.root)

    def test_unversioned_source_url_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0]['source'].update(
            source_version_url='https://arxiv.org/html/2609.29859'), 'versioned primary')

    def test_historical_retrieval_fabrication_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0]['source'].update(
            historical_review_retrieval_date='2026-09-28'), 'historical retrieval')

    def test_publication_submission_conflation_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0]['source'].update(
            publication_date='2026-09-24'), 'publication date scope')

    def test_failed_retrieval_not_silently_passed(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0]['source'].update(
            retrieval_status='NOT_RETRIEVED'), 'retrieval status')

    def test_source_direct_evidence_promotion_rejected(self):
        self.reject(MOD.GATES, lambda d: d['gates'][0]['source'].update(direct_hzt_evidence=True),
                    'inherited method')

    def test_baseline_and_successor_cannot_change_together(self):
        self.change(MOD.BASE, lambda d: d['gates'][0].update(closure_evidence_required=[]))
        self.reject(MOD.GATES, lambda d: d['gates'][0].update(closure_evidence_required=[]), 'baseline hash')

    def test_missing_central_pointer_rejected(self):
        self.change('project-manifest.json', lambda d: d['central_registries'].pop('quantum_closure_method_gates'))
        with self.assertRaises(KeyError):
            MOD.validate(self.root)

    def test_historical_pointer_rejected(self):
        self.reject('project-manifest.json', lambda d: d['current_status_sources'].update(
            quantum_closure_method_gates=MOD.BASE), 'manifest entry')

    def test_missing_consumer_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['conditional_dependencies'].pop(), 'consumer coverage')

    def test_existing_wrong_consumer_even_with_fresh_hash_rejected(self):
        def mutate(data):
            wrong = data['preserved_sources']['ulsh08']['path']
            data['preserved_sources']['ulsh07'] = {
                'path': wrong,
                'sha256': hashlib.sha256((self.root / wrong).read_bytes()).hexdigest(),
            }
            data['conditional_dependencies'][0]['consumer_ref'] = wrong
        self.reject(MOD.CROSS, mutate, 'consumer source identity')

    def test_wrong_gap_identity_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['conditional_dependencies'][2]['observable_gap_refs'][0].update(
            gap_id='FM0-GAP-010'), 'observable gap identity')

    def test_wrong_pointer_gate_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['conditional_dependencies'][0].update(
            requirements_ref=MOD.GATES + '#/gates/0/closure_evidence_required'), 'consumer pointer identity')

    def test_crosswalk_activation_drift_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['conditional_dependencies'][0].update(
            current_activation_state='ACTIVE'), 'consumer activation')

    def test_release_gate_replacement_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['conditional_dependencies'][0].update(
            existing_release_gate_replaced=True), 'release gate replacement')

    def test_global_freshness_overclaim_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['scope'].update(global_current_state_reconciliation=True), 'crosswalk scope')

    def test_new_physical_blocker_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['scope'].update(new_physical_fm0_blockers=3), 'crosswalk scope')

    def test_physical_promotion_rejected(self):
        self.reject('project-manifest.json', lambda d: d['gates'].update({'K1-D': 'RELEASED'}), 'physical firewall')

    def test_solver_promotion_rejected(self):
        self.reject('solver-hub-manifest.json', lambda d: next(
            m for m in d['modules'] if m['roadmap_id']=='ULSH-07').update(status='RELEASED'), 'solver status')

    def test_source_traversal_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['preserved_sources']['ulsh07'].update(path='../outside.md'), 'unsafe source')

    def test_absolute_source_rejected(self):
        self.reject(MOD.CROSS, lambda d: d['preserved_sources']['ulsh07'].update(path='/etc/passwd'), 'unsafe source')

    def test_modified_snapshot_rejected(self):
        path = MOD.read(self.root, MOD.CROSS)['preserved_sources']['current_state']['path']
        self.reject(path, lambda d: d.update(snapshot_date='2026-10-03'), 'preserved source hash')


if __name__ == '__main__':
    unittest.main(verbosity=2)
