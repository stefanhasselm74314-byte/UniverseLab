#!/usr/bin/env python3
"""Negative controls for explicit review transfer and complete-history lastmod."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = module('claim_binding', 'tools/2026-10-03_validate_UniverseLab_ClaimProvenanceBinding_v1.0.py')
SITEMAP = module('sitemap_history', 'tools/2026-09-03_generate_UniverseLab_SitemapLastmod_v1.0.py')


class BindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        gitdir = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', '--absolute-git-dir'], text=True).strip()
        (self.root / '.git').write_text('gitdir: ' + gitdir + '\n')

    def change(self, path, mutate):
        obj = MOD.load(self.root, path)
        mutate(obj)
        (self.root / path).write_text(json.dumps(obj), encoding='utf-8')

    def reject(self, path, mutate, reason):
        self.change(path, mutate)
        with self.assertRaisesRegex(ValueError, reason):
            MOD.validate(self.root)

    def test_verified_mapping_passes(self):
        result = MOD.validate(self.root)
        self.assertEqual((result['direct_historical_ids'], result['explicit_landing_aliases'], result['status_delta_ids']), (37, 2, 7))

    def test_missing_alias_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['bindings'].pop(), 'ONLY_TWO_EXPLICIT')

    def test_duplicate_alias_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['bindings'].append(d['bindings'][0]), 'ONLY_TWO_EXPLICIT')

    def test_wrong_historical_claim_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['bindings'][0]['historical_candidate'].update(claim_id='UL-CLAIM-CANDIDATE-UNKNOWN'), 'ONLY_TWO_EXPLICIT')

    def test_forged_original_text_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['bindings'][0]['historical_candidate'].update(text='HZT is proven.'), 'BINDING_SOURCE_MISMATCH')

    def test_stale_current_hash_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['bindings'][0]['current_candidate'].update(source_sha256='0'*64), 'BINDING_SOURCE_MISMATCH')

    def test_changed_live_text_fails(self):
        p = self.root / 'index-en.html'
        p.write_text(p.read_text().replace('speculative 6D Hyperzeit hypotheses', 'confirmed 6D Hyperzeit physics'))
        with self.assertRaisesRegex(ValueError, 'LIVE_MATERIALIZATION_MISMATCH'):
            MOD.validate(self.root)

    def test_additional_high_claim_fails(self):
        p = self.root / 'googlebc3b5b4a4888e35c.html'
        p.write_text(p.read_text() + '<p>HZT proves and explains dark matter.</p>')
        with self.assertRaisesRegex(ValueError, 'LIVE_MATERIALIZATION_MISMATCH'):
            MOD.validate(self.root)

    def test_live_inventory_cannot_be_reduced_to_72(self):
        self.reject(MOD.REGISTRY, lambda d: d['inventory'].update(current_html_count=72), 'HTML_INVENTORY_CHANGED')

    def test_retrospective_ledger_edit_fails(self):
        self.reject(MOD.COMPLETION, lambda d: d['records'][0].update(adjudication='PHYSICALLY_CONFIRMED'), 'HISTORICAL_SOURCE_CHANGED')

    def test_forged_ledger_hash_does_not_override_git(self):
        self.change(MOD.COMPLETION, lambda d: d.update(physical_evidence_effect='PROMOTED'))
        self.reject(MOD.REGISTRY, lambda d: d['protected_sources'].update({MOD.COMPLETION: MOD.sha((self.root / MOD.COMPLETION).read_bytes())}), 'HISTORICAL_SOURCE_CHANGED')

    def test_removing_historical_protection_fails(self):
        self.reject(MOD.REGISTRY, lambda d: d['protected_sources'].pop(MOD.DELTA), 'PROTECTED_SOURCE_SET_CHANGED')

    def test_coordinated_materialization_cannot_transfer_changed_context(self):
        p = self.root / 'index-en.html'
        p.write_text(p.read_text().replace('NOT RELEASED', 'RELEASED'))
        rows, summary = MOD.scan(self.root)
        self.change(MOD.CANDIDATES, lambda d: d.update(candidates=rows))
        self.change(MOD.SUMMARY, lambda d: d.update(summary))
        with self.assertRaisesRegex(ValueError, 'REVIEWED_MEDIUM_CORPUS_CHANGED'):
            MOD.validate(self.root)

    def test_physical_release_fails(self):
        self.reject('project-manifest.json', lambda d: d['gates'].update({'K1-D': 'RELEASED'}), 'GATE_CHANGED')

    def test_missing_binding_pointer_fails(self):
        self.reject('project-manifest.json', lambda d: d.update(public_claim_binding_addendum='other.json'), 'BINDING_POINTER_CHANGED')

    def test_missing_historical_objects_fails_closed(self):
        with patch.object(MOD.subprocess, 'run', return_value=subprocess.CompletedProcess([], 128, b'', b'missing')):
            with self.assertRaisesRegex(ValueError, 'GIT_PROVENANCE_UNAVAILABLE'):
                MOD.validate(self.root)

    def test_sitemap_rejects_shallow_history_before_writing(self):
        original = (self.root / 'sitemap.xml').read_bytes()
        with patch.object(SITEMAP.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, 'true\n', '')):
            with self.assertRaisesRegex(SITEMAP.SitemapError, 'COMPLETE_GIT_HISTORY_REQUIRED'):
                SITEMAP.generate(self.root, self.root / 'sitemap.xml')
        self.assertEqual((self.root / 'sitemap.xml').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
