#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "registry/2026-08-04_UniverseLab_SessionCheckpoint_v1.15.json"
ALIAS = ROOT / "registry/session-checkpoint-latest.json"
OPERATOR_2B_MERGE_COMMIT = "9c2cbb44a841f0a63f5f1d3c5fc92a96eb1ffbc6"

checkpoint = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
checkpoint["basis_commit"] = OPERATOR_2B_MERGE_COMMIT
checkpoint["correction_note"] = (
    "v1.14 contained the Operator-2B scientific state but was not installed as the stable alias and referenced a nonexistent v1.13. "
    "v1.15 is the first canonical alias-backed Operator-2B checkpoint; its basis_commit is the durable PR #39 merge commit."
)
text = json.dumps(checkpoint, indent=2, ensure_ascii=False) + "\n"
SNAPSHOT.write_text(text, encoding="utf-8")
ALIAS.write_text(text, encoding="utf-8")
