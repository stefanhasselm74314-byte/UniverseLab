from __future__ import annotations

import json
from pathlib import Path

P = Path('registry/2026-09-08_UniverseLab_ULSH05_WP1D1_GaugeOperatorKernelPreflight_v0.1.json')


def main() -> None:
    d = json.loads(P.read_text(encoding='utf-8'))
    print('work_package:', d['work_package'])
    print('status:', d['status'])
    print('conditional_domain:', d['inherited_conditional_domain']['name'])
    print('conditional_domain_status:', d['inherited_conditional_domain']['status'])
    print('conditional_domain_physical_release:', d['inherited_conditional_domain']['physical_release'])
    print('gauge_operator:', d['gauge_operator']['form'])
    print('ker_G:', d['kernel_registry']['ker_G'])
    print('closed_range_of_G:', d['cokernel_registry']['closed_range_status'])
    print('fredholm_property_of_G:', d['cokernel_registry']['fredholm_status'])
    print('full_projector_inverse:', d['gate_state']['WP1D1_full_projector_inverse'])
    print('constraint_elimination:', d['gate_state']['WP1D_constraint_elimination'])
    print('physical_3plus1_SVT:', d['gate_state']['WP1D_physical_3plus1_SVT'])
    print('FM-G0:', d['gate_state']['FM-G0'])
    print('physical_background:', d['gate_state']['PHYSICAL_BACKGROUND'])
    print('solver_execution:', d['gate_state']['SOLVER_EXECUTION'])
    print('physical_gate_effect:', d['physical_gate_effect'])
    print('physical_evidence_effect:', d['physical_evidence_effect'])


if __name__ == '__main__':
    main()
