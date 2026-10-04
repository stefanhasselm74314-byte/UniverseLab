#!/usr/bin/env python3
"""Validate the bounded, nonphysical quantum-method integration contract."""
from __future__ import annotations

import argparse
import copy
from datetime import date, datetime
import hashlib
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BASE = 'registry/2026-09-28_UL-SING_QuantumClosure_MethodGates_v1.0.json'
GATES = 'registry/2026-09-28_UL-SING_QuantumClosure_MethodGates_v1.1.json'
CROSS = 'registry/2026-10-03_UL-SING_QuantumClosure_MethodIntegration_v1.0.json'
DOC = 'governance/2026-10-03_UL-SING_QuantumClosure_MethodIntegration_v1.0.md'
BASE_SHA256 = '395b0b709e3b5189a0c513c42ff42ccc0e53f72395f3d74ffd653bc75d4a3de4'
IDS = {'QG-PI-01', 'QG-GAP-01', 'KK-CTP-01'}
CONSUMERS = {'ULSH-07': 'ulsh07', 'ULSH-08': 'ulsh08', 'FM-0': 'fm0_inventory'}
PRESERVED = {
    'current_state', 'site_state', 'checkpoint', 'checkpoint_alias', 'ulsh07',
    'ulsh08', 'solver_program', 'fm0_inventory', 'fm0_gaps',
    'adopted_method_registry', 'adopted_method_document',
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def file_path(root: Path, relative: str) -> Path:
    require(isinstance(relative, str) and bool(relative), 'empty source path')
    p = PurePosixPath(relative)
    require(not p.is_absolute() and '..' not in p.parts and '\\' not in relative,
            'unsafe source path: ' + relative)
    path = (root / relative).resolve()
    require(path.is_relative_to(root.resolve()) and path.is_file(),
            'missing or unsafe source: ' + relative)
    return path


def read(root: Path, relative: str) -> dict:
    value = json.loads(file_path(root, relative).read_text(encoding='utf-8'))
    require(isinstance(value, dict), 'JSON object required: ' + relative)
    return value


def resolve_pointer(root: Path, reference: str):
    path, separator, fragment = reference.partition('#')
    require(separator == '#' and fragment.startswith('/'), 'JSON pointer required')
    value = read(root, path)
    for token in fragment[1:].split('/'):
        token = token.replace('~1', '/').replace('~0', '~')
        value = value[int(token)] if isinstance(value, list) else value[token]
    return value


def validate(root: Path = ROOT) -> None:
    root = root.resolve()
    require(hashlib.sha256(file_path(root, BASE).read_bytes()).hexdigest() == BASE_SHA256,
            'adopted baseline hash changed')
    base, gates, cross = read(root, BASE), read(root, GATES), read(root, CROSS)
    file_path(root, DOC)
    require(gates['version'] == '1.1.0' and gates['supersedes'] == BASE, 'successor identity')
    require(gates['updated'] == '2026-10-03', 'successor update date')
    rev = gates['revision_provenance']
    require(rev['basis_main_commit'] == cross['basis_main_commit'] ==
            '312e767628f003494a51edf685cf679469e35f13', 'basis main')
    require(rev['adopted_method_semantics_changed'] is False and
            rev['global_state_reconciliation_claimed'] is False, 'revision scope')
    require(rev['integration_authority'] == 'CANONICAL_ONLY_AFTER_THIS_SUCCESSOR_IS_MERGED',
            'merge authority boundary')
    require(rev['document'] == DOC and rev['integration_registry'] == CROSS, 'revision links')
    require(len(gates['gates']) == 3 and {g['gate_id'] for g in gates['gates']} == IDS,
            'gate identity set')

    # Compare the entire inherited contract, not just a short list of statuses.
    inherited = copy.deepcopy(gates)
    for key in ('updated', 'supersedes', 'revision_provenance'):
        inherited.pop(key)
    inherited['version'] = base['version']
    for current, previous in zip(inherited['gates'], base['gates']):
        current['source'] = {key: current['source'].get(key) for key in previous['source']}
    require(inherited == base, 'inherited method semantics or physical status changed')

    for gate in gates['gates']:
        source = gate['source']
        require(source['source_version'] == 'v1', 'source version')
        identifier = source['arxiv'] + source['source_version']
        require(source['source_identifier'] == 'arXiv:' + identifier, 'source identifier')
        require(source['source_version_url'] == 'https://arxiv.org/html/' + identifier,
                'versioned primary source URL')
        require(source['metadata_url'] in ('https://arxiv.org/abs/' + identifier,
                                          'https://arxiv.org/abs/' + source['arxiv']),
                'primary metadata URL')
        submitted = datetime.fromisoformat(source['source_version_date'].replace('Z', '+00:00'))
        require(submitted.utcoffset() is not None, 'source timestamp timezone')
        retrieved = date.fromisoformat(source['retrieval_date'])
        require(submitted.date() <= retrieved == date(2026, 10, 3), 'retrieval chronology')
        require(source['source_version_date_semantics'] == 'ARXIV_V1_SUBMISSION_TIMESTAMP_UTC',
                'submission and publication date distinction')
        require(source['retrieval_status'] == 'PRIMARY_METADATA_AND_VERSIONED_HTML_RETRIEVED',
                'retrieval status')
        for field in ('retrieval_scope', 'locator_provenance', 'source_revision_policy'):
            require(isinstance(source[field], str) and bool(source[field].strip()), 'missing ' + field)
        require(source['historical_review_retrieval_date'] == 'UNKNOWN_NOT_RECONSTRUCTED',
                'historical retrieval must not be invented')
        require(source['publication_date'] == 'UNKNOWN_PUBLIC_ANNOUNCEMENT_DATE_NOT_SEPARATELY_VERIFIED'
                and source['journal_publication_date'] == 'UNKNOWN_NOT_VERIFIED', 'publication date scope')
        require(source['observation_date'] == 'NOT_APPLICABLE_THEORETICAL_PREPRINT', 'observation date')
        require(isinstance(source['source_locators'], list) and source['source_locators'] and
                all(isinstance(x, str) and x.strip() for x in source['source_locators']), 'source locators')
        for value in gate.get('repository_links', {}).values():
            file_path(root, value)

    require(cross['schema'] == 'universelab.ul-sing.quantum-closure-method-integration.v1', 'crosswalk schema')
    require(cross['method_gate_registry'] == GATES and cross['document'] == DOC, 'crosswalk links')
    require(cross['architecture'] == base['architecture'], 'architecture')
    require(cross['canonical_effect'] == 'ONLY_AFTER_MERGE_NO_PHYSICAL_PROMOTION', 'crosswalk authority')
    require(cross['physical_gate_effect'] == cross['physical_evidence_effect'] == 'NONE', 'crosswalk effects')
    require(cross['scope'] == {
        'global_current_state_reconciliation': False, 'physical_gate_override': False,
        'new_physical_fm0_blockers': 0, 'activation_is_closure': False,
        'closure_is_physical_authorization': False, 'applies_by_method_not_project_level': True,
    }, 'crosswalk scope')
    sources = cross['preserved_sources']
    require(set(sources) == PRESERVED, 'preserved source coverage')
    for label, record in sources.items():
        payload = file_path(root, record['path']).read_bytes()
        require(hashlib.sha256(payload).hexdigest() == record['sha256'], 'preserved source hash: ' + label)

    manifest, hub = read(root, 'project-manifest.json'), read(root, 'solver-hub-manifest.json')
    for section in ('current_status_sources', 'central_registries'):
        require(manifest[section]['quantum_closure_method_gates'] == GATES and
                manifest[section]['quantum_closure_method_integration'] == CROSS, 'manifest entry points')
    method = manifest['method_governance']
    require(method['registry'] == GATES and method['integration_registry'] == CROSS, 'method entry point')
    require(method['scope'] == 'METHOD_ADDENDUM_ONLY_EXISTING_GLOBAL_SNAPSHOT_DATE_UNCHANGED', 'snapshot scope')
    require(method['physical_gate_effect'] == method['physical_evidence_effect'] == 'NONE', 'method effects')
    require(hub['governance']['conditional_method_dependency_registry'] == CROSS, 'solver entry point')
    for obj in (manifest, hub):
        status = obj.get('gates', obj.get('governance'))
        require(status['K1-D'] == 'NOT_RELEASED' and status['K1-E'] == 'NOT_ADMISSIBLE'
                and status['physical_evidence_effect'] == 'NONE', 'physical firewall')
    require(manifest['gates']['PHYSICAL_BACKGROUND'] == 'NOT_ESTABLISHED' and
            manifest['gates']['PHYSICAL_RESPONSE_RANK'] == 'NOT_EXECUTED', 'physical execution firewall')
    require(manifest['gates']['FM-G0'] == 'OPEN' and manifest['gates']['FM0_BLOCKING_GAPS'] == 10,
            'FM0 physical status')
    modules = {m['roadmap_id']: m for m in hub['modules']}
    require(all(modules[k]['status'] == 'PLANNED' for k in ('ULSH-07', 'ULSH-08')), 'solver status')
    require(manifest['canonical_state'] == sources['current_state']['path'] and
            manifest['site_state'] == sources['site_state']['path'] and
            manifest['session_checkpoint'] == sources['checkpoint']['path'], 'global snapshot pointers')
    inventory = read(root, sources['fm0_inventory']['path'])
    gaps = read(root, sources['fm0_gaps']['path'])
    require(inventory['gap_register'] == sources['fm0_gaps']['path'], 'FM0 gap pointer')
    require((gaps['blocking_gap_count'], gaps['partially_resolved_blocking_gap_count'],
             gaps['fully_unresolved_blocking_gap_count']) == (10, 3, 7), 'FM0 gap counts')

    deps = cross['conditional_dependencies']
    require(len(deps) == 3 and {d['consumer_id'] for d in deps} == set(CONSUMERS), 'consumer coverage')
    kk = next(g for g in gates['gates'] if g['gate_id'] == 'KK-CTP-01')
    adopted_targets = {
        'ULSH-07': kk['repository_links']['ulsh07_kk_roadmap'],
        'ULSH-08': kk['repository_links']['ulsh08_radion_roadmap'],
        'FM-0': kk['repository_links']['fm0_inventory'],
    }
    for dep in deps:
        require(dep['gate_id'] == kk['gate_id'], 'consumer gate identity')
        require(dep['consumer_ref'] == sources[CONSUMERS[dep['consumer_id']]]['path'] ==
                adopted_targets[dep['consumer_id']], 'consumer source identity')
        file_path(root, dep['consumer_ref'])
        for field, target in (('applicability_ref', 'applicability'), ('requirements_ref', 'closure_evidence_required')):
            require(dep[field] == GATES + '#/gates/2/' + target, 'consumer pointer identity')
            require(resolve_pointer(root, dep[field]) == kk[target], 'consumer pointer resolution')
        require(dep['current_activation_state'] == kk['activation_state'] and
                dep['current_closure_status'] == kk['closure_status'], 'consumer activation/closure')
        require(dep['existing_release_gate_replaced'] is False, 'release gate replacement')
        if dep['consumer_id'] == 'FM-0':
            require(dep['gap_register'] == sources['fm0_gaps']['path'], 'consumer gap registry')
            pairs = {(x['observable_id'], x['gap_id']) for x in dep['observable_gap_refs']}
            require(len(dep['observable_gap_refs']) == 4 and pairs == {
                ('O_cosmo','FM0-GAP-007'), ('O_growth','FM0-GAP-008'),
                ('O_lensing','FM0-GAP-009'), ('O_GW','FM0-GAP-010'),
            }, 'observable gap identity')
            require(pairs <= {(x['item'], x['id']) for x in gaps['gaps']}, 'observable gap resolution')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    validate(args.root)
    print('UL-SING conditional method integration QA: PASS; physical effects NONE')


if __name__ == '__main__':
    main()
