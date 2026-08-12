#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / 'tafelwerk.html'
MODULE = ROOT / 'assets/2026-08-12_UniverseLab_TafelwerkAllFormulaExport_v1.0.js'


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    page = PAGE.read_text(encoding='utf-8')
    js = MODULE.read_text(encoding='utf-8')

    generic = './assets/2026-08-05_UniverseLab_Export_v1.0.js'
    addon = './assets/2026-08-12_UniverseLab_TafelwerkAllFormulaExport_v1.0.js'
    require(generic in page and addon in page, 'Tafelwerk export scripts are not both loaded')
    require(page.index(generic) < page.index(addon), 'all-formula module must load after generic export module')

    for marker in (
        'collectAllFormulaRecords',
        'saveUiState',
        'restoreUiState',
        'applyAllFilter',
        'formula_count',
        'numerically_calculable',
        'unit_dimension',
        'validity',
        'limit_note',
        'Tafelwerk komplett',
        'Alle Formeln · PDF/Drucken',
        'Alle Formeln · HTML',
        'Alle Formeln · Markdown',
        'Alle Formeln · JSON',
        'Alle Formeln · CSV',
        'Vollständigkeitsprüfung fehlgeschlagen',
        'data-tafelwerk-export-action',
        'A4',
    ):
        require(marker in js, f'missing export invariant: {marker}')

    for control in ('search', 'category', 'statusFilter', 'calcOnly', 'formulaList'):
        require(f"$('{control}')" in js, f'UI state control not covered: {control}')

    require("inputValues" in js and "dispatchEvent(new Event('input'" in js,
            'current formula input state is not restored')
    require("records.length !== expected" in js,
            'full-catalog count is not checked against Tafelwerk totalCount')
    require("result !== 'symbolische Referenz'" in js,
            'numeric/symbolic classification is not exported')
    require("dataset.noExport = 'true'" in js,
            'all-formula controls must stay out of generic document exports')

    forbidden = ('fetch(', 'XMLHttpRequest', 'WebSocket(', 'sendBeacon(', 'EventSource(')
    for token in forbidden:
        require(token not in js, f'network primitive forbidden in browser-only exporter: {token}')

    require("F.push" not in js and "const F" not in js,
            'export module must not duplicate or mutate the formula registry')

    print('PASS_TAFELWERK_ALL_FORMULA_EXPORT_STATIC_REGRESSION')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
