#!/usr/bin/env python3
"""G0 three-track validator v1.1 with append-only decision-log compatibility."""

from __future__ import annotations

import importlib.util
import json
import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_TOOL = ROOT / "tools" / "2026-08-03_validate_g0_three_track_sync_v1.0.py"

_spec = importlib.util.spec_from_file_location("g0_three_track_validator_v1_0", BASE_TOOL)
if _spec is None or _spec.loader is None:
    raise RuntimeError("unable to import G0 v1.0 validator")
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)

ContractError = _base.ContractError
load_json = _base.load_json
canonical_json_hash = _base.canonical_json_hash
require = _base.require


def validate_decision_log() -> None:
    """Preserve UL-DEC-0014 while allowing later append-only decisions."""
    path = ROOT / "registry/decision-log.jsonl"
    if not path.is_file():
        raise ContractError("missing decision log")

    decisions: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ContractError(f"invalid decision-log JSON at line {line_number}: {exc}") from exc
        if not isinstance(value, dict):
            raise ContractError(f"decision-log entry at line {line_number} must be an object")
        decisions.append(value)

    ids = [entry.get("decision_id") for entry in decisions]
    require(all(isinstance(item, str) for item in ids), "every decision requires a string decision_id")
    require(len(ids) == len(set(ids)), "duplicate decision ids")
    require("UL-DEC-0014" in ids, "UL-DEC-0014 must remain in the append-only decision log")

    numeric_ids: list[int] = []
    for decision_id in ids:
        match = re.fullmatch(r"UL-DEC-(\d{4})", decision_id)
        require(match is not None, f"invalid decision id: {decision_id}")
        numeric_ids.append(int(match.group(1)))
    require(numeric_ids == sorted(numeric_ids), "decision log must remain monotonically append-only")

    decision = decisions[ids.index("UL-DEC-0014")]
    require(decision["status"] == "ACTIVE", "UL-DEC-0014 must remain active")
    require(
        decision["evidence_effect"] == "GOVERNANCE_ONLY",
        "UL-DEC-0014 must retain governance-only evidence effect",
    )


_base.validate_decision_log = validate_decision_log

validate = _base.validate
main = _base.main


if __name__ == "__main__":
    raise SystemExit(main())
