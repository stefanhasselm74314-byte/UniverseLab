#!/usr/bin/env python3
"""Regression tests for the UniverseLab current-main state reconciliation."""
from __future__ import annotations

import importlib.util
import json
import shutil
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / 'tools/2026-09-01_validate_UniverseLab_CurrentMainCanonicalStateReconciliation_v1.0.py'
spec = importlib.util.spec_from_file_location('ul_state_reconcile', VALIDATOR_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def expect_failure(root: Path, needle: str) -> None:
    try:
        module.validate(root)
    except AssertionError as exc:
        assert needle in str(exc), (needle, str(exc))
    else:
        raise AssertionError(f'expected fail-closed rejection containing {needle!r}')


def copy_minimal_root(dst: Path) -> None:
    paths = [
        module.CURRENT_STATE,
        module.SITE_STATE,
        module.CHECKPOINT,
        module.CHECKPOINT_ALIAS,
        module.MANIFEST,
        module.RESEARCH_STATUS,
        module.GLOBAL_SHELL,
    ]
    for rel in paths:
        target = dst / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target)


def main() -> None:
    module.validate(ROOT)

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        copy_minimal_root(tmp)
        state_path = tmp / module.CURRENT_STATE
        state = json.loads(state_path.read_text(encoding='utf-8'))
        state['physical_governance']['K1-D'] = 'RELEASED'
        state_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
        expect_failure(tmp, 'K1-D')

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        copy_minimal_root(tmp)
        alias_path = tmp / module.CHECKPOINT_ALIAS
        alias_path.write_text(alias_path.read_text(encoding='utf-8') + '\n', encoding='utf-8')
        expect_failure(tmp, 'byte-identical')

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        copy_minimal_root(tmp)
        manifest_path = tmp / module.MANIFEST
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['release_date'] = '2026-08-05'
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        expect_failure(tmp, 'release_date')

    print('UniverseLab current-main reconciliation regression tests: PASS')


if __name__ == '__main__':
    main()
