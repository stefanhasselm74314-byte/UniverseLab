#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "compare-safe.html"

CSS_TAG = '<link rel="stylesheet" href="./assets/2026-08-06_UniverseLab_SplitPane_v1.1.css">'
JS_TAG = '<script src="./assets/2026-08-05_UniverseLab_SplitPane_v1.0.js" defer></script>'
ROOT_OPEN = (
    '<section class="compare-workspace" data-ul-split '
    'data-ul-split-key="compare-safe" data-ul-split-label="Parameter" '
    'data-ul-split-default="340" data-ul-split-min="280" '
    'data-ul-split-max="560" data-ul-split-end-min="600">\n'
)
START_OPEN = '<details class="panel params" data-ul-pane="start" open>'
END_OPEN = '<div class="compare-results" data-ul-pane="end">\n'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PAGE.read_text(encoding="utf-8")

    if 'data-ul-split-key="compare-safe"' in text:
        if text.count(CSS_TAG) != 1 or text.count(JS_TAG) != 1:
            raise RuntimeError("existing comparison split integration has asset drift")
        print("Comparison split-pane integration already current.")
        return

    text = replace_once(
        text,
        '<link rel="stylesheet" href="./assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css">',
        '<link rel="stylesheet" href="./assets/2026-08-01_UniverseLab_MobileTypography_v1.1.css">\n'
        + CSS_TAG + '\n' + JS_TAG,
        "asset insertion",
    )

    text = replace_once(
        text,
        '<details class="panel params">',
        ROOT_OPEN + START_OPEN,
        "parameter pane opening",
    )

    text = replace_once(
        text,
        '</details>\n<section id="view-compare"',
        '</details>\n' + END_OPEN + '<section id="view-compare"',
        "result pane opening",
    )

    marker = '</section>\n</main>\n<script>'
    index = text.rfind(marker)
    if index < 0:
        raise RuntimeError("comparison workspace closing marker not found")
    text = text[:index] + '</section>\n</div>\n</section>\n</main>\n<script>' + text[index + len(marker):]

    required = {
        CSS_TAG: 1,
        JS_TAG: 1,
        'data-ul-split-key="compare-safe"': 1,
        'data-ul-pane="start"': 1,
        'data-ul-pane="end"': 1,
    }
    for token, expected in required.items():
        actual = text.count(token)
        if actual != expected:
            raise RuntimeError(f"postcondition failed for {token}: {actual} != {expected}")

    PAGE.write_text(text, encoding="utf-8")
    print("Integrated comparison calculator split-pane workspace v1.1.")


if __name__ == "__main__":
    main()
