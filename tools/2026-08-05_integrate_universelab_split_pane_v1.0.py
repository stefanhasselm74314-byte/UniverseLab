#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STYLE = '<link rel="stylesheet" href="./assets/2026-08-05_UniverseLab_SplitPane_v1.0.css">'
SCRIPT = '<script src="./assets/2026-08-05_UniverseLab_SplitPane_v1.0.js" defer></script>'


def insert_head_assets(text: str) -> str:
    if STYLE not in text:
        text = text.replace('</head>', f'{STYLE}\n{SCRIPT}\n</head>', 1)
    elif SCRIPT not in text:
        text = text.replace(STYLE, f'{STYLE}\n{SCRIPT}', 1)
    return text


def integrate_observatory(text: str) -> str:
    text = insert_head_assets(text)
    text = text.replace(
        '<div class="layout">',
        '<div class="layout" data-ul-split data-ul-split-key="observatory" '
        'data-ul-split-label="Parameter" data-ul-split-default="300" '
        'data-ul-split-min="240" data-ul-split-max="520" data-ul-split-end-min="520">',
        1,
    )
    text = text.replace(
        '<aside class="panel controls">',
        '<aside class="panel controls" data-ul-pane="start">',
        1,
    )
    marker = '</aside>\n<section class="panel">'
    replacement = '</aside>\n<section class="panel" data-ul-pane="end">'
    if marker in text:
        text = text.replace(marker, replacement, 1)
    return text


def integrate_tafelwerk(text: str) -> str:
    text = insert_head_assets(text)
    text = text.replace(
        '<section class="workspace">',
        '<section class="workspace" data-ul-split data-ul-split-key="tafelwerk" '
        'data-ul-split-label="Formelauswahl" data-ul-split-default="360" '
        'data-ul-split-min="280" data-ul-split-max="580" data-ul-split-end-min="560">',
        1,
    )
    text = text.replace(
        '<aside class="panel sticky">',
        '<aside class="panel sticky" data-ul-pane="start">',
        1,
    )
    marker = '</aside>\n<section class="panel" aria-live="polite">'
    replacement = '</aside>\n<section class="panel" aria-live="polite" data-ul-pane="end">'
    if marker in text:
        text = text.replace(marker, replacement, 1)
    return text


def update(relative: str, transform) -> None:
    path = ROOT / relative
    original = path.read_text(encoding='utf-8')
    updated = transform(original)
    if updated == original:
        print(f'UNCHANGED {relative}')
        return
    path.write_text(updated, encoding='utf-8')
    print(f'UPDATED {relative}')


def verify() -> None:
    checks = {
        'observatory.html': (
            'data-ul-split-key="observatory"',
            'data-ul-pane="start"',
            'data-ul-pane="end"',
        ),
        'tafelwerk.html': (
            'data-ul-split-key="tafelwerk"',
            'data-ul-pane="start"',
            'data-ul-pane="end"',
        ),
    }
    for relative, tokens in checks.items():
        text = (ROOT / relative).read_text(encoding='utf-8')
        if text.count(STYLE) != 1 or text.count(SCRIPT) != 1:
            raise AssertionError(f'asset integration drift in {relative}')
        for token in tokens:
            if text.count(token) != 1:
                raise AssertionError(f'{token} integration drift in {relative}')


if __name__ == '__main__':
    update('observatory.html', integrate_observatory)
    update('tafelwerk.html', integrate_tafelwerk)
    verify()
    print('PASS: UniverseLab split-pane integration v1.0')
