#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

TOOL = Path("tools/2026-08-12_execute_aip_lens_01_null_n1_v0.1.py")
CONTRACT = Path("registry/2026-08-12_UniverseLab_AIP-LENS-01-NULL-N1_ExecutionContract_v0.1.json")


def load_module():
    spec = importlib.util.spec_from_file_location("aip_lens_n1", TOOL)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def main():
    mod = load_module()
    contract = json.loads(CONTRACT.read_text())
    assert contract["status"] == "AUTHORIZED_FOR_DETERMINISTIC_SYNTHETIC_EXECUTION"
    assert contract["generator"]["physical_simulator"] is False
    assert contract["hzt_comparison"] is False
    assert contract["physical_evidence_effect"] == "NONE"
    assert contract["split"]["seeds"] == mod.SEEDS
    assert contract["split"]["sizes"] == mod.SIZES

    splits_a = {name: mod.generate_split(name) for name in mod.SIZES}
    splits_b = {name: mod.generate_split(name) for name in mod.SIZES}
    assert mod.canonical_json(splits_a) == mod.canonical_json(splits_b)

    all_ids = [row["id"] for rows in splits_a.values() for row in rows]
    assert len(all_ids) == len(set(all_ids))
    for name, rows in splits_a.items():
        assert len(rows) == mod.SIZES[name]
        assert all(row["id"].startswith(name + ":") for row in rows)

    for row in splits_a["TRAIN"][:32]:
        om = row["targets"]["Omega_m"]
        sig = row["diagnostic"]["sigma8"]
        expected = sig * (om / 0.3) ** 0.5
        assert abs(row["targets"]["S8"] - expected) < 1e-14

    src = TOOL.read_text().lower()
    for forbidden in ("import numpy", "import sklearn", "import torch", "import tensorflow", "import jax"):
        assert forbidden not in src

    summary_a, _, _ = mod.run_pipeline("PR_REHEARSAL")
    summary_b, _, _ = mod.run_pipeline("PR_REHEARSAL")
    assert mod.canonical_json(summary_a) == mod.canonical_json(summary_b)
    assert summary_a["run_class"] == "PR_REHEARSAL"
    assert summary_a["physical_simulator"] is False
    assert summary_a["hzt_comparison"] is False
    assert summary_a["governance"]["WP4"] == "BLOCKED"
    assert summary_a["governance"]["K1-D"] == "NOT_RELEASED"
    assert summary_a["governance"]["K1-E"] == "NOT_ADMISSIBLE"
    assert summary_a["governance"]["physical_evidence_effect"] == "NONE"
    assert summary_a["gate_claims"]["AIP-G6"] == "NOT_TESTED_REAL_DATA_BLOCKED"
    assert summary_a["gate_claims"]["AIP-G7"] == "SEPARATE_REVIEW_REQUIRED"
    print("AIP-LENS-01-NULL-N1 regression: PASS")


if __name__ == "__main__":
    main()
