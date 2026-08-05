#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"tools/2026-08-05_validate_g0_three_track_sync_v1.20.py"
def main():
    spec=importlib.util.spec_from_file_location("g0_v120_test",VALIDATOR)
    if spec is None or spec.loader is None: raise RuntimeError("validator import failed")
    module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=module; spec.loader.exec_module(module)
    result=module.validate()
    assert result["status"]=="PASS"
    assert result["release"]==module.RELEASE and result["decision"]==module.DECISION and result["checkpoint"]==module.CHECKPOINT
    assert result["review_status"]==module.DENIAL and result["execution_authorized"] is False
    assert result["physical_backend_imported"] is False and result["physical_solver_calls"]==0 and result["cp01r1_attempts"]==0
    assert result["physical_evidence_effect"]=="NONE" and result["next_block"]==module.NEXT
    assert module.find_exact({"x":module.OLD_NEXT},module.OLD_NEXT)==["$.x"]
    assert module.LATEST.read_bytes()==module.SNAPSHOT.read_bytes()
    print("PASS: G0 v1.20 Background-3C9 regression tests")
if __name__=="__main__": main()
