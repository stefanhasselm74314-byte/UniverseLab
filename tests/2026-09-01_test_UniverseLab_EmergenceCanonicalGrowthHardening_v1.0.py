#!/usr/bin/env python3
"""Regression checks added after real Chromium and Codex Emergence audits."""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'emergence.html'
ADAPTER = ROOT / 'assets/2026-09-01_UniverseLab_EmergenceAdapter_v1.0.js'
CONTRACT = ROOT / 'registry/2026-09-01_UniverseLab_EmergenceCanonicalGrowthAdapterContract_v1.0.json'
OR = 9.2e-5
OM = .315
ODE = .684908


def independent_scale_after_delta_tau(delta_tau: float = .002, steps: int = 20000) -> float:
    ok = 1.0 - OR - OM - ODE
    a0 = max(1e-3, 10 * OR / OM)
    x = math.log(a0)
    h = delta_tau / steps

    def rhs(X: float) -> float:
        a = math.exp(X)
        return math.sqrt(OR/a**4 + OM/a**3 + ok/a**2 + ODE)

    for _ in range(steps):
        k1 = rhs(x)
        k2 = rhs(x + h*k1/2)
        k3 = rhs(x + h*k2/2)
        k4 = rhs(x + h*k3)
        x += h * (k1 + 2*k2 + 2*k3 + k4) / 6
    return math.exp(x)


def main() -> None:
    html = HTML.read_text(encoding='utf-8')
    adapter = ADAPTER.read_text(encoding='utf-8')
    contract = json.loads(CONTRACT.read_text(encoding='utf-8'))

    assert 'id="ol" type="range" min="0" max="1.2" step="0.000001" value="0.684908"' in html
    assert "const VERSION='1.0.3'" in adapter
    for token in (
        'function buildTimeMap',
        'function tauAtScaleFactor',
        'function scaleFactorAtTau',
        'state.timeMap',
        "const x1=i===points-1?0:x+dx",
        "rows.push({x,a:i===points-1?1:Math.exp(x),tau})",
        "if($('#eraBars'))$('#eraBars').innerHTML=''",
        'state.history.length===0',
        'function displayGridSize',
        'state.displayN=renderN',
        'function applySavedInputs',
        'LEGACY_SETTINGS_TO_INPUTS',
        "const parameterIds=['h0','om','or','ol']",
        'let timer=0'
    ):
        assert token in adapter, token
    for forbidden in (
        'const derivative=x=>C.E',
        'state.history.length<2',
        'resizeGrid(',
        'setN(',
        'if(target>state.N)'
    ):
        assert forbidden not in adapter, forbidden

    assert contract['version'] == '1.0.3'
    assert contract['background_contract']['display_time_integrator'] == 'PRECOMPUTED_MONOTONE_SIMPSON_TAU_OF_LN_A_MAP'
    assert contract['background_contract']['display_time_endpoint'] == 'EXACT_X_0_A_1_Z_0'
    assert contract['background_contract']['maximum_time_amplification'] == 100
    assert contract['fail_closed_ui']['stale_epoch_bars_cleared'] is True
    assert contract['fail_closed_ui']['debounce_timer_declared'] is True
    assert contract['architecture']['cosmology_mutates_simulation_grid_size'] is False
    assert contract['architecture']['display_resampling_mutates_simulation_state'] is False
    assert contract['persistence']['current_state_schema'] == 'universelab.emergence-state.v2'
    assert contract['persistence']['legacy_pre_schema_control_field'] == 'settings'
    assert 'maximum_time_amplification_stays_in_domain' in contract['qa']['required_checks']
    assert 'exact_present_endpoint' in contract['qa']['required_checks']
    assert 'deterministic_cell_update_independent_of_cosmology_mode' in contract['qa']['required_checks']
    assert 'legacy_settings_payload_migrates_explicitly' in contract['qa']['required_checks']

    assert abs(1.0 - OR - OM - ODE) < 1e-15
    a_after = independent_scale_after_delta_tau()
    assert abs(a_after - .01518354918) < 2e-8, a_after

    print('UniverseLab Emergence canonical growth hardening regression: PASS')


if __name__ == '__main__':
    main()
