#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path

REG = Path('registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N2_BridgeContract_v0.1.json')


def main() -> None:
    d = json.loads(REG.read_text())

    eqs = ' '.join(str(x.get('equation', '')) for x in d['forward_chain'])
    for token in ('P_delta', 'C_ell', 'xi_plus', 'xi_minus', 'E_n'):
        assert token in eqs or token in json.dumps(d['forward_chain'])

    required = set(d['transfer_and_domain_shift']['required_pre_real_data_checks'])
    for item in (
        'physical-engine cross-check on a declared cosmology grid',
        'observable-vector ordering check',
        'tomography ordering check',
        'source-nz perturbation stress',
        'intrinsic-alignment stress',
        'shape-noise stress',
        'predeclared OOD abstention threshold',
    ):
        assert item in required

    forbidden = set(d['forbidden_inferences'])
    assert 'NO_DIRECT_N1_TOY_WEIGHTS_ON_KIDS_DATA' in forbidden
    assert 'NO_REAL_KIDS_DATA_ACCESS_FROM_THIS_STAGE' in forbidden
    assert 'NO_AIP_G2_PASS_FROM_CONTRACT_ONLY' in forbidden

    metrics = d['acceptance_metrics_to_freeze_before_physical_run']
    assert all(str(v).startswith('TO_BE_PREDECLARED') for v in metrics.values())

    print('AIP-LENS-01-NULL-N2 bridge regression: PASS')


if __name__ == '__main__':
    main()
