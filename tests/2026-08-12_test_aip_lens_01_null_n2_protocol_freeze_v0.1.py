#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REG = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_ProtocolFreeze_v0.1.json')
DOC = Path('science/ai-for-physics/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_ProtocolFreeze_v0.1.md')
VALIDATOR = Path('tools/2026-08-12_validate_aip_lens_01_null_n2_protocol_freeze_v0.1.py')


def main() -> None:
    for p in (REG, DOC, VALIDATOR):
        assert p.exists(), p

    data = json.loads(REG.read_text())
    assert data['real_data_control_class'] == 'PUBLISHED_REPRODUCTION_CONTROL_NOT_DISCOVERY_BLIND'
    assert data['dataset']['dataset_id'] == 'KIDS1000_DR4_COSMIC_SHEAR_ASGARI2021'
    assert data['frozen_observable_scope']['primary_statistic'] == 'COSEBIs'
    assert data['execution_state']['execution_authorized'] is False
    assert data['execution_state']['real_data_inference_performed'] is False
    assert data['n1_to_n2_transfer_firewall']['n1_model_direct_application_to_real_data'] == 'FORBIDDEN'
    assert data['gate_disposition']['AIP-G6'] == 'NOT_TESTED_REAL_DATA_EXECUTION_BLOCKED'
    assert data['governance_firewall']['physical_evidence_effect'] == 'NONE'

    text = DOC.read_text()
    for required in (
        'AIP-LENS-01-NULL-N2-BRIDGE',
        'KiDS1000_cosmic_shear_data_release.tgz',
        'COSEBIs',
        'published reproduction/control exercise',
        'synthetic feature similarity != physical observable equivalence',
        'K1-D` remains `NOT_RELEASED',
        'K1-E` remains `NOT_ADMISSIBLE',
    ):
        assert required in text, required

    cp = subprocess.run([sys.executable, str(VALIDATOR)], check=True, capture_output=True, text=True)
    assert 'protocol freeze: PASS' in cp.stdout
    print('AIP-LENS-01-NULL-N2 protocol regression: PASS')


if __name__ == '__main__':
    main()
