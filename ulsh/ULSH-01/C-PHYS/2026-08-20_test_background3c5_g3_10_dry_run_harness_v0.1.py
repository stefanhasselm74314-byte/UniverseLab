#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
HARNESS=ROOT/"2026-08-20_background3c5_g3_10_dry_run_harness_v0.1.py"
CONTRACT=ROOT/"2026-08-19_Background3C5_G3_9_Functional_Jacobian_Evaluation_Preregistration_v0.1.json"
spec=importlib.util.spec_from_file_location("g310",HARNESS); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
c=json.loads(CONTRACT.read_text(encoding="utf-8")); jobs=mod.make_plan(c,2,1,0)
assert len(jobs)==81
assert sum(j["kind"]=="baseline" for j in jobs)==1
assert sum(j["solver_profile_metadata_only"]=="nominal" and j["kind"]=="perturbation" for j in jobs)==60
assert sum(j["solver_profile_metadata_only"]=="refined_h3" for j in jobs)==20
assert all(j["execute"] is False and j["evidence_effect"]=="NONE" for j in jobs)
for j in jobs:
    assert not (mod.FORBIDDEN_KEYS & set(j))
    b=j["branch_lock"]
    assert b["n_N"]-b["n_S"]==b["m_layer"]*b["N_F"]
assert {j["coordinate"] for j in jobs if j["coordinate"]}==set(c["operator"]["coordinates"])
assert {j["step_magnitude"] for j in jobs if j["step_magnitude"] is not None}=={0.01,0.005,0.0025}
print("G3.10 dry-run harness QA: PASS")
