#!/usr/bin/env python3
"""Fail-closed, bounded claim-identity bridge; requires historical Git objects.

The live scanner remains authoritative for inventory. No fuzzy matching, automatic
review transfer, physical evidence promotion or global snapshot refresh occurs.
"""
from __future__ import annotations
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = 'registry/2026-10-03_UniverseLab_ClaimProvenanceBinding_v1.0.json'
CANDIDATES = 'registry/2026-09-03_UniverseLab_PublicScientificClaimLexicalCandidates_v0.1.json'
SUMMARY = 'registry/2026-09-03_UniverseLab_PublicScientificClaimExtractionSummary_v0.1.json'
PRIORITY = 'registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json'
COMPLETION = 'registry/2026-09-04_UniverseLab_PublicScientificMediumCompletionAdjudication_v1.0.json'
DELTA = 'registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json'
BASE = '312e767628f003494a51edf685cf679469e35f13'
PROTECTED = {
    'registry/2026-09-03_UniverseLab_PublicScientificHighClaimAdjudication_v1.0.json',
    'registry/2026-09-04_UniverseLab_BandVC_G11_StateFreshnessClosure_v1.0.json',
    'registry/2026-09-04_UniverseLab_BandVC_StatusPageMediumDeltaAdjudication_v1.0.json',
    'registry/2026-09-04_UniverseLab_CurrentMainCanonicalState_v1.3.json',
    'registry/2026-09-04_UniverseLab_PublicScientificMediumAdjudicationSummary_v1.0.json',
    'registry/2026-09-04_UniverseLab_PublicScientificMediumCompletionAdjudication_v1.0.json',
    'registry/2026-09-04_UniverseLab_PublicScientificMediumPriorityAdjudication_v1.0.json',
    'registry/2026-09-04_UniverseLab_SessionCheckpoint_v1.34.json',
    'registry/2026-09-04_UniverseLab_SiteState_v1.4.json',
    'registry/session-checkpoint-latest.json',
}
ALIASES = {
    'UL-CLAIM-CANDIDATE-8DA35AA2283D9C5F': 'UL-CLAIM-CANDIDATE-2A5F574A7ED88849',
    'UL-CLAIM-CANDIDATE-2A1B5F591D31DF61': 'UL-CLAIM-CANDIDATE-7FAC1625FAAC6926',
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return sha(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode())


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, check=False)
    require(result.returncode == 0, 'GIT_PROVENANCE_UNAVAILABLE: fetch complete history')
    return result.stdout


def load(root, path):
    return json.loads((root / path).read_text(encoding='utf-8'))


def scan(root):
    path = root / 'tools/2026-09-03_extract_UniverseLab_PublicScientificClaims_v1.0.py'
    spec = importlib.util.spec_from_file_location('ul_binding_scanner', path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    rows, summary = mod.extract(root)
    return [asdict(row) for row in rows], summary


def candidate_id(row):
    key = f"{row['path']}\0{row['source_line']}\0{row['tag']}\0{row['text']}"
    return 'UL-CLAIM-CANDIDATE-' + sha(key.encode())[:16].upper()


def validate(root=ROOT):
    root = Path(root)
    record = load(root, REGISTRY)
    require(record['basis_main_commit'] == BASE, 'BASIS_CHANGED')
    require(record['physical_gate_effect'] == record['physical_evidence_effect'] == 'NONE', 'EFFECT_CHANGED')
    require(set(record['protected_sources']) == PROTECTED, 'PROTECTED_SOURCE_SET_CHANGED')
    for path, expected in record['protected_sources'].items():
        historical = git(root, 'show', BASE + ':' + path)
        require(sha(historical) == expected == sha((root / path).read_bytes()), 'HISTORICAL_SOURCE_CHANGED: ' + path)
    require({PRIORITY, COMPLETION, DELTA} <= set(record['protected_sources']), 'LEDGER_PROTECTION_MISSING')
    manifest = load(root, 'project-manifest.json')
    require(manifest['public_claim_binding_addendum'] == REGISTRY, 'BINDING_POINTER_CHANGED')
    original_manifest = json.loads(git(root, 'show', BASE + ':project-manifest.json'))
    require(manifest['gates'] == original_manifest['gates'], 'PHYSICAL_OR_AUTHORIZATION_GATE_CHANGED')
    require(manifest['public_claim_audit'] == original_manifest['public_claim_audit'], 'HISTORICAL_AUDIT_CHANGED')
    require(manifest['release_date'] == '2026-09-04', 'GLOBAL_SNAPSHOT_NOT_REFRESHED_BY_THIS_ADDENDUM')
    require(manifest['physical_gate_effect'] == manifest['physical_evidence_effect'] == 'NONE', 'MANIFEST_EFFECT_CHANGED')

    rows, summary = scan(root)
    materialized = load(root, CANDIDATES)
    require(rows == materialized['candidates'], 'LIVE_MATERIALIZATION_MISMATCH')
    stored_summary = load(root, SUMMARY)
    for key in ('tracked_html_files', 'claim_candidates', 'risk_classes', 'page_index'):
        require(summary[key] == stored_summary[key], 'SUMMARY_MISMATCH: ' + key)
    inventory = record['inventory']
    paths = sorted(row['path'] for row in summary['page_index'])
    require(paths == inventory['current_html_paths'] and len(paths) == inventory['current_html_count'] == 73, 'HTML_INVENTORY_CHANGED')
    old_paths = {p for p in git(root, 'ls-tree', '-r', '--name-only', '5d6cc496b08879bdf4cf9bd8c08ef1c04fe35dcf').decode().splitlines() if p.endswith('.html')}
    extra = inventory['added_nonclaim_html']
    require(len(old_paths) == inventory['historical_html_count'] == 72 and set(paths) - old_paths == {extra['path']} and not old_paths - set(paths), 'HTML_INVENTORY_DELTA_CHANGED')
    require(sha((root / extra['path']).read_bytes()) == extra['sha256'], 'VERIFICATION_SOURCE_CHANGED')
    require(extra['claim_candidates'] == 0 and not any(r['path'] == extra['path'] for r in rows), 'VERIFICATION_HAS_CLAIMS')
    medium = {r['claim_id']: r for r in rows if r['preliminary_risk_class'] == 'MEDIUM'}
    require(len(rows) == 993 and len(medium) == 46 and not any(r['preliminary_risk_class'] == 'HIGH' for r in rows), 'CORPUS_COUNTS_CHANGED')
    require(digest(sorted(medium.values(), key=lambda r: r['claim_id'])) == record['live_medium_sha256'], 'REVIEWED_MEDIUM_CORPUS_CHANGED')

    source = record['historical_candidate_source']
    completion = load(root, COMPLETION)
    require(source['commit'] == completion['basis_main_commit'] and source['path'] == CANDIDATES, 'ORIGINAL_SOURCE_CHANGED')
    historical_bytes = git(root, 'show', source['commit'] + ':' + source['path'])
    require(sha(historical_bytes) == source['sha256'], 'ORIGINAL_CANDIDATES_HASH_CHANGED')
    historical_doc = json.loads(historical_bytes)
    require(historical_doc['basis_commit'] == source['basis_commit'], 'ORIGINAL_EXTRACTION_BASIS_CHANGED')
    original = {r['claim_id']: r for r in historical_doc['candidates']}
    ledger = {r['claim_id']: r for r in completion['records']}
    bindings = record['bindings']
    actual = {r['current_candidate']['claim_id']: r['historical_candidate']['claim_id'] for r in bindings}
    require(len(bindings) == 2 and actual == ALIASES, 'ONLY_TWO_EXPLICIT_ALIASES_ALLOWED')
    ignored = {'claim_id', 'source_line', 'source_sha256'}
    for binding in bindings:
        old, new = binding['historical_candidate'], binding['current_candidate']
        require(old == original[old['claim_id']] and new == medium[new['claim_id']], 'BINDING_SOURCE_MISMATCH')
        require(candidate_id(old) == old['claim_id'] and candidate_id(new) == new['claim_id'], 'CANDIDATE_ID_MISMATCH')
        require({k:v for k,v in old.items() if k not in ignored} == {k:v for k,v in new.items() if k not in ignored}, 'SEMANTIC_OR_SCOPE_CHANGE_REQUIRES_NEW_REVIEW')
        require(sha(git(root, 'show', source['commit'] + ':' + old['path'])) == old['source_sha256'], 'ORIGINAL_PAGE_HASH_CHANGED')
        require(sha((root / new['path']).read_bytes()) == new['source_sha256'], 'CURRENT_PAGE_HASH_CHANGED')
        require(binding['adjudication_ledger'] == COMPLETION and binding['adjudication'] == ledger[old['claim_id']]['adjudication'] == 'METADATA_OR_SCOPE_DESCRIPTION', 'ADJUDICATION_CHANGED')

    historical_ids = {r['claim_id'] for r in load(root, PRIORITY)['records'] + completion['records']}
    delta_ids = {r['claim_id'] for r in load(root, DELTA)['records']}
    normalized = {ALIASES.get(key, key) for key in medium}
    require(len(normalized) == 46 and len(historical_ids & set(medium)) == 37, 'RAW_ID_COVERAGE_CHANGED')
    require(len(normalized & historical_ids) == 39 and len(historical_ids - normalized) == 3 and normalized - historical_ids == delta_ids and len(delta_ids) == 7, 'UNCOVERED_MEDIUM_CLAIM')
    expected = dict(claim_candidates=993, high_candidates=0, medium_candidates=46, direct_historical_ids=37, explicit_landing_aliases=2, historical_status_ids_retired=3, status_delta_ids=7, covered_medium_ids=46, unbound_medium_ids=0, physical_claim_promotions=0)
    require(record['current_coverage'] == expected, 'COVERAGE_REPORT_CHANGED')
    return {'historical_id_view': normalized, 'tracked_html_files': 73, **expected}


if __name__ == '__main__':
    result = validate()
    print('Claim provenance binding: PASS raw=37+2+7 medium=46/46 high=0 html=73 historical_snapshot=2026-09-04 physical_effects=NONE')
