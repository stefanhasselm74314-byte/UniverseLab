#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path

TOOL = Path('tools/2026-08-12_validate_aip_lens_01_null_n1_result_review_v0.1.py')

spec = importlib.util.spec_from_file_location('n1_review_validator', TOOL)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)
mod.main()
print('AIP-LENS-01-NULL-N1 result-review regression: PASS')
