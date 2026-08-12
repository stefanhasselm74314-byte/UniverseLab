#!/usr/bin/env python3
from pathlib import Path

path = Path('tafelwerk.html')
text = path.read_text(encoding='utf-8')
marker = '<script src="./assets/2026-08-05_UniverseLab_Export_v1.0.js" defer></script>'
include = '<script src="./assets/2026-08-12_UniverseLab_TafelwerkAllFormulaExport_v1.0.js" defer></script>'
if include in text:
    print('include already present')
elif marker not in text:
    raise SystemExit('generic export marker missing; refusing to patch')
else:
    text = text.replace(marker, marker + '\n' + include, 1)
    path.write_text(text, encoding='utf-8')
    print('tafelwerk all-formula export include inserted')
