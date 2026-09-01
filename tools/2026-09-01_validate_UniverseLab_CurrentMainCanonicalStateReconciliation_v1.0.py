#!/usr/bin/env python3
"""Fail-closed QA for the 2026-09-01 UniverseLab current-main state reconciliation."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
DATE = '2026-09-01'
BASE_COMMIT = '46579b58b8ca2ae3fb4ba7726446c5871d84da79'
BASE_TREE = '06e7e6671abe3a3c5fab232837178cadb2ea11ff'
CURRENT_STATE = Path('registry/2026-09-01_UniverseLab_CurrentMainCanonicalState_v1.0.json')
SITE_STATE = Path('registry/2026-09-01_UniverseLab_SiteState_v1.1.json')
CHECKPOINT = Path('registry/2026-09-01_UniverseLab_SessionCheckpoint_v1.31.json')
CHECKPOINT_ALIAS = Path('registry/session-checkpoint-latest.json')
MANIFEST = Path('project-manifest.json')
RESEARCH_STATUS = Path('research-status.html')
GLOBAL_SHELL = Path('assets/2026-08-16_UniverseLab_GlobalShell_v1.1.js')


def load_json(root: Path, rel: Path) -> dict[str, Any]:
    with (root / rel).open('r', encoding='utf-8') as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise AssertionError(f'{rel} must contain a JSON object')
    return data


def assert_firewalls(obj: dict[str, Any], *, context: str) -> None:
    # Allow the fields to live either at top level or in the canonical nested blocks.
    physical = obj.get('physical_governance', obj.get('gates', obj.get('governance', {})))
    assert physical.get('K1-D') == 'NOT_RELEASED', f'{context}: K1-D promotion detected'
    assert physical.get('K1-E') == 'NOT_ADMISSIBLE', f'{context}: K1-E promotion detected'
    evidence = physical.get('physical_evidence_effect', obj.get('physical_evidence_effect'))
    assert evidence == 'NONE', f'{context}: physical evidence effect must remain NONE'


def validate(root: Path = DEFAULT_ROOT, *, strict_source_existence: bool = False) -> None:
    state = load_json(root, CURRENT_STATE)
    site = load_json(root, SITE_STATE)
    checkpoint = load_json(root, CHECKPOINT)
    alias = load_json(root, CHECKPOINT_ALIAS)
    manifest = load_json(root, MANIFEST)

    assert state['snapshot_date'] == DATE
    assert state['basis_main_commit'] == BASE_COMMIT
    assert state['basis_main_tree'] == BASE_TREE
    assert state['authority']['open_pull_requests_have_canonical_effect'] is False
    assert state['physical_governance']['solver_authorized'] is False
    assert state['physical_governance']['solver_execution'] == 'NOT_EXECUTED'
    assert state['physical_governance']['backend_import'] == 'NOT_EXECUTED'
    assert state['physical_governance']['operative_authorization_decision'] == 'NOT_CREATED'
    assert state['physical_governance']['operative_single_use_grant'] == 'NOT_CREATED'
    assert state['physical_governance']['physical_background'] == 'NOT_ESTABLISHED'
    assert state['physical_governance']['physical_response_rank'] == 'NOT_EXECUTED'
    assert state['program']['gate'] == 'FM-G0'
    assert state['program']['gate_status'] == 'OPEN'
    assert state['program']['blocking_gap_count'] == 10
    assert state['program']['partially_resolved_blocking_gap_count'] == 3
    assert state['program']['fully_unresolved_blocking_gap_count'] == 7
    assert state['physical_gate_effect'] == 'NONE'
    assert state['physical_evidence_effect'] == 'NONE'
    assert state['open_noncanonical_work'][0]['pull_request'] == 137
    assert state['open_noncanonical_work'][0]['canonical_effect'].startswith('NONE_')
    assert state['open_noncanonical_work'][0]['merge_tree_audited_against_basis_main'] is False
    assert_firewalls(state, context='current state')

    assert site['snapshot_date'] == DATE
    assert site['basis_main_commit'] == BASE_COMMIT
    assert site['canonical_state'] == CURRENT_STATE.as_posix()
    assert site['freshness']['status'] == 'CURRENT_FOR_BASIS_MAIN'
    assert site['governance']['open_pull_requests_have_canonical_effect'] is False
    assert_firewalls(site, context='site state')
    module_ids = {m['module_id'] for m in site['modules']}
    assert {'ULSH-01','HZT-M0-FM0'} <= module_ids

    assert checkpoint['timestamp'].startswith(DATE)
    assert checkpoint['basis_commit'] == BASE_COMMIT
    assert checkpoint['canonical_state'] == CURRENT_STATE.as_posix()
    assert checkpoint['site_state'] == SITE_STATE.as_posix()
    assert checkpoint['physical_gate_effect'] == 'NONE'
    assert checkpoint['physical_evidence_effect'] == 'NONE'
    assert_firewalls(checkpoint, context='checkpoint')

    dated_bytes = (root / CHECKPOINT).read_bytes()
    alias_bytes = (root / CHECKPOINT_ALIAS).read_bytes()
    assert dated_bytes == alias_bytes, 'session-checkpoint-latest.json must be byte-identical to the dated canonical snapshot'
    assert alias == checkpoint

    assert manifest['release_date'] == DATE, 'project manifest release_date must match reconciliation date'
    assert manifest['basis_main_commit'] == BASE_COMMIT
    assert manifest['canonical_state'] == CURRENT_STATE.as_posix()
    assert manifest['site_state'] == SITE_STATE.as_posix()
    assert manifest['session_checkpoint'] == CHECKPOINT.as_posix()
    assert manifest['gates']['FM-G0'] == 'OPEN'
    assert manifest['gates']['FM0_BLOCKING_GAPS'] == 10
    assert manifest['gates']['official_MD2S_solver'] == 'NOT_AUTHORIZED'
    assert manifest['c_phys_operator_entry']['solver_authorized'] is False
    assert_firewalls(manifest, context='project manifest')

    html = (root / RESEARCH_STATUS).read_text(encoding='utf-8')
    assert '1. September 2026' in html
    assert CURRENT_STATE.as_posix() in html
    assert 'Offene Pull Requests besitzen keine kanonische Wirkung' in html
    assert 'K1-D' in html and 'NOT RELEASED' in html
    assert 'K1-E' in html and 'NOT ADMISSIBLE' in html
    assert '3. August 2026' not in html

    shell = (root / GLOBAL_SHELL).read_text(encoding='utf-8')
    assert SITE_STATE.as_posix() in shell
    assert '2026-08-16_UniverseLab_SiteState_v1.0.json' not in shell
    assert "const VERSION='1.1.2'" in shell

    # Monotone dated snapshot families. Newer successors must force an explicit update.
    registry = root / 'registry'
    families = {
        'CurrentMainCanonicalState': CURRENT_STATE.name,
        'UniverseLab_SiteState': SITE_STATE.name,
        'UniverseLab_SessionCheckpoint': CHECKPOINT.name,
    }
    for token, expected in families.items():
        names = [p.name for p in registry.glob('*.json') if token in p.name]
        dates = sorted((m.group(1), name) for name in names if (m := re.match(r'^(\d{4}-\d{2}-\d{2})', name)))
        assert dates, f'No dated snapshots found for {token}'
        assert dates[-1][1] == expected, f'{expected} is no longer the newest {token} snapshot'

    if strict_source_existence:
        for label, path in state['status_sources'].items():
            candidate = root / path
            assert candidate.exists(), f'missing status source {label}: {path}'

    print('UniverseLab current-main canonical state reconciliation: PASS')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=DEFAULT_ROOT)
    parser.add_argument('--strict-source-existence', action='store_true')
    args = parser.parse_args()
    validate(args.root.resolve(), strict_source_existence=args.strict_source_existence)


if __name__ == '__main__':
    main()
