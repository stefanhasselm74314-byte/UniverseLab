from __future__ import annotations

import json
from pathlib import Path

P = Path('registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json')


def main() -> None:
    d = json.loads(P.read_text(encoding='utf-8'))
    print('work_package:', d['work_package'])
    print('status:', d['status'])
    print('gauge_operator:', d['gauge_operator']['form'])
    print('ker_G:', d['kernel_registry']['ker_G'])
    print('full_projector_inverse:', d['gate_state']['WP1D1_full_projector_inverse'])
    print('constraint_elimination:', d['gate_state']['WP1D_constraint_elimination'])
    print('physical_background:', d['gate_state']['PHYSICAL_BACKGROUND'])
    print('solver_execution:', d['gate_state']['SOLVER_EXECUTION'])
    print('physical_gate_effect:', d['physical_gate_effect'])
    print('physical_evidence_effect:', d['physical_evidence_effect'])


if __name__ == '__main__':
    main()
