#!/usr/bin/env python3
from __future__ import annotations
import importlib.util
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
VALIDATOR=ROOT/"tools/2026-08-05_validate_g0_three_track_sync_v1.18.py"

def main():
    s=importlib.util.spec_from_file_location("g0_v118_test",VALIDATOR)
    if s is None or s.loader is None: raise RuntimeError("validator import failed")
    m=importlib.util.module_from_spec(s); sys.modules[s.name]=m; s.loader.exec_module(m)
    r=m.validate()
    assert r["status"]=="PASS"
    assert r["release"]==m.RELEASE and r["decision"]==m.DECISION and r["checkpoint"]==m.CHECKPOINT
    assert r["review_status"]==m.DENIAL and r["execution_authorized"] is False
    assert r["physical_solver_calls"]==0 and r["cp01r1_attempts"]==0
    assert r["physical_evidence_effect"]=="NONE" and r["next_block"]==m.NEXT
    assert m.find_exact({"x":m.OLD_NEXT},m.OLD_NEXT)==["$.x"]
    assert m.LATEST.read_bytes()==m.SNAPSHOT.read_bytes()
    print("PASS: G0 v1.18 Background-3C7 regression tests")
if __name__=="__main__": main()
